# Copyright 2023 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from hashlib import sha256
import json
import re
import subprocess

from grpc import StatusCode
from importlib_resources import files


def read_linguist_languages(path):
    res = {}
    with path.open() as langf:
        for name, details in json.load(langf).items():
            color = details.get('color')
            if color is not None:
                res[name] = color
    return res


LANGUAGE_COLORS = read_linguist_languages(
    files(__name__).joinpath('languages.json'))

TOKEI_VERSION_RX = re.compile(r'tokei (\d+)\.(\d+)\.(\d+)(\s|$)')
TOKEI_VERSIONS = {}


def language_color(lang_name):
    """Perform the same defaulting as in Gitaly.

    This is not thread-safe, because it actually updates
    :data:`LANGUAGE_COLORS` due to defaulting in case the detected language
    does not have a color there. That is not a problem: HGitaly is not
    multithreaded (or rather uses a unique service thread at a given time,
    out of the pool still created by grpcio).

    As of this writing, go-enry v2.8.3 (already used by Gitaly to return the
    color) defaults to `#cccccc`:

      // GetColor returns a HTML color code of a given language.
      func GetColor(language string) string {
        if color, ok := data.LanguagesColor[language]; ok {
            return color
        }

        if color, ok := data.LanguagesColor[GetLanguageGroup(language)]; ok {
            return color
        }

        return "#cccccc"
      }

    Gitaly then concludes with (from internal/gitaly/linguist/linguist.go) ::

      // Color returns the color Linguist has assigned to language.
      func Color(language string) string {
        if color := enry.GetColor(language); color != "#cccccc" {
            return color
        }

        colorSha := sha256.Sum256([]byte(language))
        return fmt.Sprintf("#%x", colorSha[0:3])
      }
    """
    color = LANGUAGE_COLORS.get(lang_name)
    if color is not None:
        return color

    color_sha = sha256(lang_name.encode('utf-8')).hexdigest()
    color = '#' + color_sha[:6]
    LANGUAGE_COLORS[lang_name] = color
    return color


class TokeiVersionParseError(RuntimeError):
    """Indicates that `tokei --version` could not be parsed.

    It is possible that the executable is just not Tokei
    """


def parse_tokei_version(out):
    """Parse the given ``out``, expected to be output of ``tokei --version``

    :returns: a triple of integers
    :raises: :class:TokeiVersionParseError

    Currently tested versions::

      >>> parse_tokei_version("tokei 12.0.4")
      (12, 0, 4)
      >>> parse_tokei_version("tokei 12.1.2")
      (12, 1, 2)

    Errors::

      >>> try: parse_tokei_version("Unrelated")
      ... except Exception as exc: print(repr(exc))
      TokeiVersionParseError('Unrelated')
    """
    match = TOKEI_VERSION_RX.search(out)
    if match is None:
        raise TokeiVersionParseError(out)
    return tuple(int(match.group(i)) for i in (1, 2, 3))


def tokei_version(bin_path):
    version = TOKEI_VERSIONS.get(bin_path)
    if version is not None:
        return version

    tokei = subprocess.run((bin_path, '--version'),
                           encoding='utf-8',
                           check=True,
                           capture_output=True
                           )
    version = parse_tokei_version(tokei.stdout.strip())
    TOKEI_VERSIONS[bin_path] = version
    return version


def language_stats(bin_path, path, context):
    """Return the full language stats working directory at given path.

    :param str bin_path: path to the Tokei executable
    :param path: the directory to analyze as a :class:`pathlib.Path` instance.
    """
    try:
        version = tokei_version(bin_path)  # may invoke Tokei
        options = []
        if version >= (12, 1):
            options.append('--compact')

        cmd = [bin_path]
        cmd.extend(options)
        cmd.extend(('-o', 'json', path))
        tokei = subprocess.run(
            cmd,
            encoding='utf-8',
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as exc:
        # in Gitaly 15.5, the resulting error code is 'INTERNAL', with
        # details 'language stats: waiting for linguist: exit status %d'
        context.abort(
            StatusCode.INTERNAL,
            "CommitLanguages: tokei error status code=%d stderr=%r" % (
                exc.returncode, exc.stderr))
    except FileNotFoundError:
        # in Gitaly 15.5, if `gitaly-linguist` cannot be found, the resulting
        # error code is `INTERNAL`, with details 'language stats: waiting
        # for linguist: exit status 127' (same as rewrapping in a shell)
        context.abort(
            StatusCode.INTERNAL,
            "language stats: tokei executable '%s' not found" % bin_path)
    except PermissionError:
        # Gitaly 15.5 behaves similarly in this case as in the not found case,
        # only with exit status 126 in details (same as in a shell, again)
        context.abort(
            StatusCode.INTERNAL,
            "language stats: permission denied to run "
            "tokei executable '%s'" % bin_path)
    except TokeiVersionParseError as exc:
        context.abort(
            StatusCode.INTERNAL,
            "language stats: could not parse Tokei version for executable "
            "'%s' (got %r). Is it even Tokei?" % (bin_path, exc.args[0]))

    # overriding variable also to free buffer immediately, as it can be
    # fairly big, e.g. 10MB for heptapod-rails
    tokei = json.loads(tokei.stdout)

    stats = {}
    total = 0

    for lang_name, details in tokei.items():
        # We can't use the `Total` entry because the ratios we have
        # to produce are expressed in bytes, not lines.
        if lang_name == 'Total':
            continue

        per_file = details['reports']
        total_bytes = 0
        for report in per_file:
            total_bytes += (path / report['name']).stat().st_size
        stats[lang_name] = dict(files=len(per_file),
                                total_bytes=total_bytes,
                                )
        total += total_bytes
    return stats, total
