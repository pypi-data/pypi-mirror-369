# Copyright 2023 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from google.protobuf.timestamp_pb2 import Timestamp
from grpc import (
    RpcError,
    StatusCode,
)
import pytest

from mercurial import (
    phases,
)

from hgext3rd.heptapod.branch import (
    gitlab_branches,
)

from hgitaly.stub.operations_pb2 import (
    OperationBranchUpdate,
    UserFFBranchRequest,
    UserSquashRequest,
)
from hgitaly.stub.operations_pb2_grpc import (
    OperationServiceStub,
)
from hgitaly.stub.shared_pb2 import (
    User,
)
from hgitaly.tests.common import make_empty_repo_with_gitlab_state_maintainer

from .fixture import MutationServiceFixture

parametrize = pytest.mark.parametrize


class OperationsFixture(MutationServiceFixture):

    stub_cls = OperationServiceStub

    def user_squash(self, **kw):
        kw.setdefault('repository', self.grpc_repo)
        kw.setdefault('user', self.user)
        return self.stub.UserSquash(UserSquashRequest(**kw),
                                    metadata=self.grpc_metadata())

    def user_ff_branch(self, **kw):
        kw.setdefault('repository', self.grpc_repo)
        kw.setdefault('user', self.user)
        return self.stub.UserFFBranch(UserFFBranchRequest(**kw),
                                      metadata=self.grpc_metadata())


@pytest.fixture
def operations_fixture(grpc_channel, server_repos_root):
    with OperationsFixture(
            grpc_channel, server_repos_root,
            repo_factory=make_empty_repo_with_gitlab_state_maintainer
    ) as fixture:
        yield fixture


@parametrize('timestamp', ('timestamp', 'now'))
@parametrize('project_mode', ('hg-git-project', 'native-project'))
def test_user_squash(operations_fixture, project_mode, timestamp):
    fixture = operations_fixture
    wrapper = fixture.repo_wrapper
    hg_repo = wrapper.repo

    # because of the config set by fixture, this leads in all cases to
    # creation of a Git repo and its `branch/default` Git branch
    sha1 = wrapper.commit_file('foo').hex().decode('ascii')
    sha2 = wrapper.commit_file('foo', message='foo2').hex().decode('ascii')
    sha3 = wrapper.commit_file('foo', message='foo3').hex().decode('ascii')
    wrapper.update(sha1)  # avoid keeping changeset 3 visible
    # let's confirm it
    git_repo = fixture.git_repo()
    before_squash_git_branches = git_repo.branches()
    assert before_squash_git_branches[b'branch/default']['title'] == b'foo3'

    squash = fixture.user_squash

    fixture.hg_native = project_mode != 'hg-git-project'

    if timestamp == 'now':
        ts = None
    else:
        ts = Timestamp()
        ts.FromSeconds(1702472217)
    author = User(name=b"John Doe",
                  gl_id='user-987',
                  email=b"jd@heptapod.test",
                  )
    resp = squash(start_sha=sha1,
                  end_sha=sha3,
                  author=author,
                  timestamp=ts,
                  commit_message=b'squashed!')

    # we will need more that list_refs, namely that the state file does exist,
    # without any fallback.
    # TODO check obslog on the result
    wrapper.reload()
    hg_repo = wrapper.repo
    gl_branches = gitlab_branches(hg_repo)
    folded_sha = gl_branches[b'branch/default']
    assert folded_sha == resp.squash_sha.encode('ascii')
    assert folded_sha != sha2.encode('ascii')
    folded_ctx = hg_repo[folded_sha]
    assert folded_ctx.description() == b'squashed!'
    unfi = hg_repo.unfiltered()
    for sha in (sha2, sha3):
        assert unfi[sha].obsolete()
    assert fixture.list_refs() == {
        b'refs/heads/branch/default': folded_sha.decode('ascii')
    }

    if fixture.hg_native:
        # expect Git branches not to have moved
        assert git_repo.branches() == before_squash_git_branches
    else:
        # expect Git branch to point on new commit (also Git repo may have
        # moved, let's also reload it)
        git_repo = fixture.git_repo()
        assert git_repo.branches()[b'branch/default']['title'] == b'squashed!'

    for kw in (
            dict(user=None, start_sha=sha1, end_sha=sha2),
            dict(commit_message=None, start_sha=sha1, end_sha=sha2),
            # missing author
            dict(commit_message=b'squashed', start_sha=sha1, end_sha=sha2),
            # missing start_sha or end_sha
            dict(commit_message=b'squashed', author=author, end_sha=sha2),
            dict(commit_message=b'squashed', author=author, start_sha=sha1),
            dict(commit_message=b'squashed', author=author,
                 start_sha='unknown', end_sha=sha2),
            dict(commit_message=b'squashed', author=author, end_sha=sha2),
            dict(commit_message=b'squashed', author=author,
                 start_sha=sha1, end_sha='unknown'),
    ):
        with pytest.raises(RpcError) as exc_info:
            squash(**kw)
        assert exc_info.value.code() == StatusCode.INVALID_ARGUMENT

    amend_msg = b'squash becomes an amend!'
    resp = squash(start_sha=sha1,
                  end_sha=folded_sha,
                  author=author,
                  commit_message=amend_msg)
    amended_sha = resp.squash_sha.encode('ascii')
    wrapper.reload()
    amended_ctx = wrapper.repo[amended_sha]
    assert amended_ctx.description() == amend_msg


@parametrize('project_mode', ('hg-git-project', 'native-project'))
def test_user_ff_branch(operations_fixture, project_mode):
    fixture = operations_fixture
    ff_branch = fixture.user_ff_branch

    fixture.hg_native = project_mode != 'hg-git-project'
    wrapper = fixture.repo_wrapper

    gl_topic = b'topic/default/zetop'
    gl_branch = b'branch/default'

    # because of the config set by fixture, this leads in all cases to
    # creation of a Git repo and its `branch/default` Git branch
    ctx0 = wrapper.commit_file('foo')
    sha0 = ctx0.hex().decode()
    default_head = wrapper.commit_file('foo')
    ctx2 = wrapper.commit_file('foo', topic='zetop', message='foo2')
    sha2 = ctx2.hex().decode('ascii')
    wrapper.commit_file('bar', branch='other', parent=ctx0)
    needs_rebase = wrapper.commit_file('old', parent=ctx0,
                                       topic='needs-rebase'
                                       ).hex().decode('ascii')
    bogus1 = wrapper.commit_file('bogus', topic='bogus',
                                 parent=default_head)
    bogus1_sha = bogus1.hex().decode()
    # changing topic so that amending bogus1 is not a multiple heads condition
    bogus2 = wrapper.commit_file('bogus', topic='bogus2')
    bogus2_sha = bogus2.hex().decode()

    # let's confirm the mirroring to Git
    git_repo = fixture.git_repo()
    before_ff_git_branches = git_repo.branches()
    assert before_ff_git_branches[gl_topic]['title'] == b'foo2'

    # making bogus_top1 obsolete
    wrapper.update_bin(bogus1.node())
    wrapper.amend_file('foo')

    before_refs = fixture.list_refs()

    with pytest.raises(RpcError) as exc_info:
        ff_branch(branch=b'branch/other', commit_id=sha2)
    assert exc_info.value.code() == StatusCode.FAILED_PRECONDITION
    assert 'branch differ' in exc_info.value.details()

    with pytest.raises(RpcError) as exc_info:
        ff_branch(branch=gl_branch, commit_id=bogus2_sha)
    assert exc_info.value.code() == StatusCode.FAILED_PRECONDITION
    assert 'unstable' in exc_info.value.details()

    with pytest.raises(RpcError) as exc_info:
        ff_branch(branch=gl_branch, commit_id=bogus1_sha)
    assert exc_info.value.code() == StatusCode.FAILED_PRECONDITION
    assert 'obsolete' in exc_info.value.details()

    with pytest.raises(RpcError) as exc_info:
        ff_branch(branch=gl_topic, commit_id=sha2)
    assert exc_info.value.code() == StatusCode.FAILED_PRECONDITION
    assert 'named branches only' in exc_info.value.details()

    # case where nothing is pathological, but is not a fast-forward
    with pytest.raises(RpcError) as exc_info:
        ff_branch(branch=gl_branch, commit_id=needs_rebase)
    assert exc_info.value.code() == StatusCode.FAILED_PRECONDITION
    assert 'not fast forward' in exc_info.value.details()

    # basic errors, missing and unresolvable arguments
    with pytest.raises(RpcError) as exc_info:
        ff_branch(commit_id=sha2)
    assert exc_info.value.code() == StatusCode.INVALID_ARGUMENT
    assert 'empty branch' in exc_info.value.details()

    with pytest.raises(RpcError) as exc_info:
        ff_branch(branch=gl_branch, commit_id='not-a-hash')
    assert exc_info.value.code() == StatusCode.INVALID_ARGUMENT
    assert 'parse commit ID' in exc_info.value.details()

    unknown_oid = '01beef23' * 5
    with pytest.raises(RpcError) as exc_info:
        ff_branch(branch=gl_branch, commit_id=unknown_oid)
    assert exc_info.value.code() == StatusCode.INTERNAL
    assert 'invalid commit' in exc_info.value.details()

    with pytest.raises(RpcError) as exc_info:
        ff_branch(branch=gl_branch, commit_id=sha2,
                  expected_old_oid=unknown_oid)
    assert exc_info.value.code() == StatusCode.INVALID_ARGUMENT
    assert 'old object' in exc_info.value.details()

    with pytest.raises(RpcError) as exc_info:
        ff_branch(branch=gl_branch, commit_id=sha2,
                  expected_old_oid='12deadbeef')  # short hash
    assert exc_info.value.code() == StatusCode.INVALID_ARGUMENT
    assert 'parse commit ID' in exc_info.value.details()

    # old oid mismatch
    with pytest.raises(RpcError) as exc_info:
        ff_branch(branch=gl_branch, commit_id=sha2, expected_old_oid=sha0)
    assert exc_info.value.code() == StatusCode.FAILED_PRECONDITION
    assert exc_info.value.details() == "expected_old_oid mismatch"

    assert fixture.list_refs() == before_refs

    # Actual call expected to succeed
    resp = ff_branch(branch=gl_branch, commit_id=sha2)

    # checking change on default branch ref, and only this ref.
    expected_refs = before_refs.copy()
    expected_refs[b'refs/heads/' + gl_branch] = sha2
    del expected_refs[b'refs/heads/' + gl_topic]

    assert fixture.list_refs() == expected_refs
    assert resp.branch_update == OperationBranchUpdate(commit_id=sha2,
                                                       repo_created=False,
                                                       branch_created=False)
    wrapper.reload()
    assert wrapper.repo[ctx2.rev()].phase() == phases.public
