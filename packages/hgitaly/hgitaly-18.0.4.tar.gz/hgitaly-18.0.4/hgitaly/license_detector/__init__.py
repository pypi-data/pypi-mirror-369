# Copyright 2023 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import json
import subprocess

from grpc import StatusCode
from importlib_resources import files


def read_spdx_licenses(path):
    with path.open() as licf:
        return {lic['licenseId'].lower(): lic
                for lic in json.load(licf)['licenses']}


DATA_DIR = files(__name__)
SPDX_LICENSES = read_spdx_licenses(DATA_DIR.joinpath('spdx-licenses.json'))
"""Official SPDX licenses file, by lowercase id.

The `spdx` Python package is clearly outdated,
the `spdx-tools` Python package is so complex it is not even clear in
a few minutes if it contains the information we need.
"""

LICENSE_ID_TO_NICK_NAMES = {
    "agpl-3.0": "GNU AGPLv3",
    "lgpl-3.0": "GNU LGPLv3",
    "bsd-3-clause-clear": "Clear BSD",
    "odbl-1.0": "ODbL",
    "ncsa": "UIUC/NCSA",
    "lgpl-2.1": "GNU LGPLv2.1",
    "gpl-3.0": "GNU GPLv3",
    "gpl-2.0": "GNU GPLv2",
}
"""Same as in Gitaly's implementation, we need a mapping of nicknames

See commment (as of Gitaly 16.2) in
/internal/gitaly/service/repository/license.go

It is not fully clear what this nickname is supposed to be, as it is not
a SPDX concept, could be GitLab-specific or carried over from a previous
system (Ruby gem from GitHub?)
"""

DEPRECATED_PREFIX = 'deprecated_'

COMMON_LICENSE_FILES = ('LICENSE', 'COPYING')


def license_content(name):
    """Return the full test content of one of the licenses we ship.

    Intended for gRPC tests and Gitaly comparison tests.
    """
    return (DATA_DIR / (name + '.sample')).read_text()


def strip_deprecated_prefix(name):
    if name.startswith(DEPRECATED_PREFIX):
        return name[len(DEPRECATED_PREFIX):]
    return name


def match_sort_key(match):
    return (match['confidence'],
            strip_deprecated_prefix(match['license']).lower())


def detect_license(bin_path, path, context):
    """Return the full language stats working directory at given path.

    :param str bin_path: path to the Go `license-detector` executable
    :param path: the directory to analyze as a :class:`pathlib.Path` instance.
    """
    try:
        detector = subprocess.run(
            (bin_path, '-f', 'json', path),
            encoding='utf-8',
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as exc:
        # in Gitaly 15.5, the resulting error code is 'INTERNAL', with
        # details 'language stats: waiting for linguist: exit status %d'
        context.abort(
            StatusCode.INTERNAL,
            "detect_license: Go `license-detector` error "
            "status code=%d stderr=%r" % (
                exc.returncode, exc.stderr))
    except FileNotFoundError:
        context.abort(
            StatusCode.INTERNAL,
            "detect_license: Go `license-detector` executable '%s' "
            "not found" % bin_path)
    except PermissionError:
        # Gitaly 15.5 behaves similarly in this case as in the not found case,
        # only with exit status 126 in details (same as in a shell, again)
        context.abort(
            StatusCode.INTERNAL,
            "detect_license: permission denied to run "
            "Go `license-detector` executable '%s'" % bin_path)

    detected = json.loads(detector.stdout)[0]
    error = detected.get('error')
    if error is not None:
        if error != 'no license file was found':
            context.abort(StatusCode.INTERNAL, "detect_license: " + error)

        for fname in COMMON_LICENSE_FILES:
            if (path / fname).exists():
                return dict(spdx_id='other',
                            full_name='Other',
                            file=fname,
                            nickname='LICENSE')
        return None

    # TODO same as Gitaly, sort by identifier, same reason: reproducibility
    # in case of equal confidence score.
    matches = detected['matches']
    matches.sort(key=match_sort_key)
    detected = matches[0]
    spdx_id = strip_deprecated_prefix(detected['license']).lower()
    detected['spdx_id'] = spdx_id

    spdx = SPDX_LICENSES.get(spdx_id)
    if spdx is not None:  # TODO what if not found?
        detected['full_name'] = spdx['name']
        # this is far from correct (e.g., it returns the text of GPL-2.0
        # for GPL-2.0+) but this is what Gitaly seems to do.
        detected['url'] = spdx['seeAlso'][0]

    detected['nickname'] = LICENSE_ID_TO_NICK_NAMES.get(spdx_id, "")
    return detected
