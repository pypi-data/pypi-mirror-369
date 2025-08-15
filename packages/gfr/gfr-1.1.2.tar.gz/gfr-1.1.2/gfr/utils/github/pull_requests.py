from github import Github, GithubException, Repository, AuthenticatedUser
from .exceptions import GitHubError

class PullRequestManager:
    """Handles all actions related to GitHub Pull Requests."""
    def __init__(self, gh: Github, user: AuthenticatedUser):
        self._gh = gh
        self._user = user

    def create(self, repo: Repository.Repository, title: str, body: str, head: str, base: str, labels: list[str]) -> 'PullRequest':
        """
        Creates a new pull request.

        Args:
            repo: The repository to create the PR in.
            title: The title of the PR.
            body: The description/body of the PR.
            head: The name of the source branch.
            base: The name of the target branch.
            labels: A list of labels to apply.

        Returns:
            The created PullRequest object.
        """
        try:
            pr = repo.create_pull(
                title=title,
                body=body,
                head=head,
                base=base
            )
            pr.set_labels(*labels)
            pr.add_to_assignees(self._user)
            return pr
        except GithubException as e:
            raise GitHubError(f"Failed to create pull request. Details: {e.data.get('message', 'Unknown error')}")

    def merge(self, pr: 'PullRequest'):
        """Merges a pull request."""
        try:
            pr.merge()
        except GithubException as e:
            raise GitHubError(f"Failed to merge pull request. Details: {e.data.get('message', 'Unknown error')}")
