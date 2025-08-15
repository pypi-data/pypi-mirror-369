# gfr/utils/github/issues.py
from github import Github, GithubException, Repository, AuthenticatedUser
from .exceptions import GitHubError

class IssueManager:
    """Handles all actions related to GitHub issues."""
    def __init__(self, gh: Github, user: AuthenticatedUser):
        self._gh = gh
        self._user = user

    def create(self, repo: Repository.Repository, title: str, body: str, labels: list[str]) -> 'Issue':
        """
        Creates a new issue in a specified repository.

        Args:
            repo (Repository.Repository): The repository to create the issue in.
            title (str): The title of the issue.
            body (str): The description/body of the issue.
            labels (list[str]): A list of labels to apply to the issue.

        Returns:
            The created Issue object from PyGithub.
        """
        try:
            issue = repo.create_issue(
                title=title,
                body=body,
                assignee=self._user,
                labels=labels
            )
            return issue
        except GithubException as e:
            raise GitHubError(f"Failed to create issue. Details: {e.data.get('message', 'Unknown error')}")
