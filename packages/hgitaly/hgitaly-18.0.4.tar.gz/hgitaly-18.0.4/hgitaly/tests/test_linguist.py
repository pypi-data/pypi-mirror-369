# Copyright 2023 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import pytest
from grpc import StatusCode

from ..linguist import (
    language_stats,
)
from ..testing.context import (
    FakeContextAborter as FakeContext,
    FakeContextAbort,
)


def test_tokei_subprocesss_errors(tmpdir):
    bin_path = tmpdir / 'tokei'
    context = FakeContext()
    with pytest.raises(FakeContextAbort):
        language_stats(bin_path, tmpdir / 'tree', context)
    assert context.code() == StatusCode.INTERNAL
    assert "not found" in context.details()

    bin_path.write_binary(b'#!/bin/sh\n\n echo "oops" >&2; exit 3\n')
    with pytest.raises(FakeContextAbort):
        language_stats(bin_path, tmpdir / 'tree', context)
    assert "permission denied" in context.details()

    bin_path.chmod(0o755)

    with pytest.raises(FakeContextAbort):
        language_stats(bin_path, tmpdir / 'tree', context)
    assert context.code() == StatusCode.INTERNAL
    assert "status code=3" in context.details()
    assert "oops" in context.details()

    bin_path.write_binary(b'#!/bin/sh\n\n echo "tokei not-a-version"\n')
    with pytest.raises(FakeContextAbort):
        language_stats(bin_path, tmpdir / 'tree', context)
    assert context.code() == StatusCode.INTERNAL
    assert "Tokei version" in context.details()
    assert "'tokei not-a-version'" in context.details()
