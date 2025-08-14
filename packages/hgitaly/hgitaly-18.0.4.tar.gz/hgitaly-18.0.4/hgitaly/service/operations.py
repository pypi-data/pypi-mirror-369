# Copyright 2023 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
import logging
import time

from grpc import StatusCode

from heptapod import (
    obsutil,
)

from heptapod.gitlab.branch import (
    NAMED_BRANCH_PREFIX,
)

from ..branch import (
    gitlab_branch_head
)
from ..changelog import (
    ancestor,
    merge_content,
)
from ..errors import (
    operation_error_treatment,
    structured_abort,
)
from ..logging import LoggerAdapter
from ..revision import (
    changeset_by_commit_id_abort,
    gitlab_revision_changeset,
    validate_oid,
)
from ..servicer import HGitalyServicer

from ..stub.operations_pb2 import (
    OperationBranchUpdate,
    UserFFBranchError,
    UserFFBranchRequest,
    UserFFBranchResponse,
    UserSquashRequest,
    UserSquashResponse,
    UserSquashError,
)
from ..stub.errors_pb2 import (
    ReferenceUpdateError,
    ResolveRevisionError,
)
from ..stub.operations_pb2_grpc import OperationServiceServicer


base_logger = logging.getLogger(__name__)


class OperationServicer(OperationServiceServicer, HGitalyServicer):
    """OperationsServiceService implementation.
    """

    def UserSquash(self,
                   request: UserSquashRequest,
                   context) -> UserSquashResponse:
        logger = LoggerAdapter(base_logger, context)
        repo = self.load_repo(request.repository, context,
                              for_mutation_by=request.user)
        with_hg_git = not repo.ui.configbool(b'heptapod', b'no-git')
        # Gitaly's squash is merge-centric, start_sha is actually the
        # merge target, whereas end_sha is the head of the MR being accepted
        # TODO check that there are no public changesets for a nicer
        # user feedback.
        start_sha, end_sha = request.start_sha, request.end_sha
        if not start_sha:
            context.abort(StatusCode.INVALID_ARGUMENT, "empty StartSha")
        if not end_sha:
            context.abort(StatusCode.INVALID_ARGUMENT, "empty EndSha")
        start_rev, end_rev = start_sha.encode('ascii'), end_sha.encode('ascii')
        start_ctx = gitlab_revision_changeset(repo, start_rev)
        end_ctx = gitlab_revision_changeset(repo, end_rev)

        for (ctx, rev, error_label) in (
                (start_ctx, start_rev, 'start'), (end_ctx, end_rev, 'end')
        ):
            if ctx is None:
                structured_abort(
                    context,
                    StatusCode.INVALID_ARGUMENT,
                    f'resolving {error_label} revision: reference not found',
                    UserSquashError(resolve_revision=ResolveRevisionError(
                        revision=rev))
                )

        revset = (f"ancestor({start_sha}, {end_sha})::{end_sha}"
                  f"- ancestor({start_sha}, {end_sha})").encode('ascii')
        end_ctx = gitlab_revision_changeset(repo, end_sha.encode('ascii'))
        logger.info("Folding revset %s, mirroring to Git=%r",
                    revset, with_hg_git)
        # TODO add the hg_git flag or maybe let servicer do it.
        message = request.commit_message
        if not message:
            context.abort(StatusCode.INVALID_ARGUMENT, "empty CommitMessage")

        # Mercurial does not distinguish between author (actual author of
        # the work) and committer (could be just someone with commit rights
        # relaying the original work). In case an author is provided, it
        # feels right to derive the Mercurial author from it, as preserving
        # the actual work metadata (and copyright) should have priority.
        # This is what `HgGitRepository` used to do on the Rails side.
        author = request.author
        if not author.name:
            context.abort(StatusCode.INVALID_ARGUMENT, "empty Author")

        # timestamp is supposed to be for the committer, but Mercurial does
        # not have such a distinction, hence it will become the commit date.
        if not request.HasField('timestamp'):
            unix_ts = int(time.time())
        else:
            unix_ts = request.timestamp.seconds

        opts = {'from': False,  # cannot be used as regular kwarg
                'exact': True,
                'rev': [revset],
                'message': message,
                'user': b'%s <%s>' % (author.name, author.email),
                'date': b'%d 0' % unix_ts,
                }
        # Comment taken from `hg_git_repository.rb`:
        #   Note that `hg fold --exact` will fail unless the revset is
        #   "an unbroken linear chain". That fits the idea of a Merge Request
        #   neatly, and should be unsuprising to users: it's natural to expect
        #   squashes to stay simple.
        #   In particular, if there's a merge of a side topic, it will be
        #   unsquashable.
        # Not 100% sure we need a workdir, but I don't see
        #   an explicit "inmemory" option as there is for `hg rebase`. What
        #   I do see is user (status) messages as in updates, so…
        # If we update the workdir to "end" changeset, then the fold will
        #   look like an extra head and be rejected (probably because it is
        #   kept active by being the workdir parent).
        #   On the other hand, the "start" changeset is by design of the
        #   method not to be folded and is probably close enough that we
        #   get a reasonable average efficiency.
        with self.working_dir(gl_repo=request.repository,
                              repo=repo,
                              changeset=start_ctx,
                              context=context) as wd:
            # `allowunstable=no` protects us against all instabilities,
            # in particular against orphaning dependent topics.
            # TODO this setting should probably be set in all mutations
            wd.repo.ui.setconfig(b'experimental.evolution', b'allowunstable',
                                 False)
            with operation_error_treatment(context, UserSquashError,
                                           logger=logger):
                retcode = self.repo_command(wd.repo, context, 'fold', **opts)
                if retcode == 1:
                    revs = wd.repo.revs(revset)
                    if len(revs) == 1:
                        rev = next(iter(revs))
                        self.repo_command(wd.repo, context, 'update', rev)
                        self.repo_command(
                            wd.repo, context, 'amend',
                            message=message,
                            note=(b"Description changed for squash request "
                                  b"for a single changeset"),
                        )
                    else:  # pragma no cover
                        # This block is currently unreachable from tests
                        # and is here in case of unexpected behaviour change
                        # in the `fold` command.
                        context.abort(
                            StatusCode.INTERNAL,
                            "Internal return code 1, but zero or more than "
                            "one changeset for revset %r" % revset
                        )
            self.repo_command(wd.repo, context, 'update', start_ctx.hex())
            # The workdir repo does not have to be reloaded, whereas the
            # main repo would. We just need to regrab the end changeset
            # (now obsolete)
            end_ctx = wd.repo.unfiltered()[end_ctx.rev()]
            folded = obsutil.latest_unique_successor(end_ctx)

        return UserSquashResponse(squash_sha=folded.hex().decode('ascii'))

    def UserFFBranch(self,
                     request: UserFFBranchRequest,
                     context) -> UserFFBranchResponse:
        logger = LoggerAdapter(base_logger, context)
        repo = self.load_repo(request.repository, context,
                              for_mutation_by=request.user)
        with_hg_git = not repo.ui.configbool(b'heptapod', b'no-git')

        to_publish = changeset_by_commit_id_abort(
            repo, request.commit_id, context)
        if to_publish is None:
            context.abort(
                StatusCode.INTERNAL,
                f'checking for ancestry: invalid commit: "{request.commit_id}"'
            )

        old_id = request.expected_old_oid
        if old_id and not validate_oid(old_id):
            context.abort(StatusCode.INVALID_ARGUMENT,
                          f'cannot parse commit ID: "{old_id}"')

        if not request.branch:
            context.abort(StatusCode.INVALID_ARGUMENT, "empty branch name")

        if not request.branch.startswith(NAMED_BRANCH_PREFIX):
            context.abort(StatusCode.FAILED_PRECONDITION,
                          "Heptapod fast forwards are currently "
                          "for named branches only (no topics nor bookmarks)")

        current_head = gitlab_branch_head(repo, request.branch)
        if to_publish.branch() != current_head.branch():
            context.abort(StatusCode.FAILED_PRECONDITION,
                          "not a fast-forward (Mercurial branch differs)")

        fail = False
        for cs in merge_content(to_publish, current_head):
            if cs.obsolete():
                fail = True
                fail_msg = "is obsolete"
            if cs.isunstable():
                fail = True
                fail_msg = "is unstable"
        if fail:
            context.abort(StatusCode.FAILED_PRECONDITION,
                          f"not a fast-forward (changeset "
                          f"{cs.hex().decode('ascii')} {fail_msg})")

        if old_id and old_id != current_head.hex().decode('ascii'):
            # We did not need to resolve before this, but now we do because
            # Gitaly has a specific error if resolution fails
            if changeset_by_commit_id_abort(repo, old_id, context) is None:
                context.abort(StatusCode.INVALID_ARGUMENT,
                              "cannot resolve expected old object ID: "
                              "reference not found")
            # no point trying to match the Gitaly error details: we
            # have the much better structured error
            structured_abort(context,
                             StatusCode.FAILED_PRECONDITION,
                             "expected_old_oid mismatch",
                             UserFFBranchError(
                                 reference_update=ReferenceUpdateError(
                                     # Gitaly doesn't fill in `reference_name`
                                     old_oid=old_id,
                                     new_oid=to_publish.hex().decode('ascii'),
                                 )))

        if ancestor(to_publish, current_head) != current_head.rev():
            context.abort(StatusCode.FAILED_PRECONDITION,
                          "not fast forward")

        # TODO use phases.advanceboundary directly? Check cache invalidations
        # carefully. ('phases' command is a pain to call and does lots of
        # unnecessary stuff).
        logger.info("All checks passed, now publishing %r, "
                    "mirroring to Git=%r", to_publish, with_hg_git)
        self.publish(to_publish, context)
        return UserFFBranchResponse(branch_update=OperationBranchUpdate(
            commit_id=to_publish.hex().decode('ascii'),
        ))
