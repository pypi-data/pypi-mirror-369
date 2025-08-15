from github import Github, GithubException, Organization, Repository, UnknownObjectException

# We can keep the custom error here or move it to a shared exceptions file
class GitHubError(Exception):
    pass

class RepositoryManager:
    def __init__(self, gh: Github, org: Organization):
        self._gh = gh
        self._org = org

    def create(self, name: str, description: str, private: bool, readmefile: bool = True) -> 'Repository':
        """Creates a new repository in the configured organization."""
        try:
            repo = self._org.create_repo(
                name=name,
                description=description,
                private=private,
                auto_init=readmefile,
            )
            return repo
        except GithubException as e:
            if e.status == 422:
                raise GitHubError(f"Repository '{name}' likely already exists.\nfull text error:\n{e})")
            else:
                raise GitHubError(f"An API error occurred: {e.data.get('message', 'Unknown error')}")
            
    def get(self, name: str) -> Repository.Repository:
        """
        Retrieves a single repository by its name.

        Args:
            name (str): The name of the repository to retrieve.

        Returns:
            The Repository object from PyGithub.

        Raises:
            GitHubError: If the repository is not found.
        """
        try:
            return self._org.get_repo(name)
        except GithubException as e:
            if e.status == 404:
                raise GitHubError(f"Repository '{name}' not found in organization '{self._org.login}'.")
            else:
                raise GitHubError(f"Failed to get repository '{name}'. Details: {e.data.get('message', 'Unknown error')}")
            
    def edit(self, repo: Repository.Repository, default_branch: str):
        """
        Edits repository settings.

        Args:
            repo (Repository.Repository): The repository object to edit.
            default_branch (str): The name to set as the default branch.
        """
        try:
            repo.edit(default_branch=default_branch)
        except GithubException as e:
            raise GitHubError(f"Failed to edit repository settings. Details: {e.data.get('message', 'Unknown error')}")

    def create_release(self, repo: Repository.Repository, tag_name: str, name: str, message: str):
        """Creates a new GitHub Release."""
        try:
            return repo.create_git_release(tag=tag_name, name=name, message=message, prerelease=False)
        except GithubException as e:
            raise GitHubError(f"Failed to create release. Details: {e.data.get('message', 'Unknown error')}")
        
    def compare_commits(self, repo: Repository.Repository, base: str, head: str) -> list[str]:
        """Compares two commits/tags and returns a formatted list of commit messages."""
        try:
            comparison = repo.compare(base, head)
            return [f"- {commit.commit.message.splitlines()[0]} by @{commit.author.login}" for commit in comparison.commits]
        except GithubException as e:
            raise GitHubError(f"Failed to compare commits. Details: {e.data.get('message', 'Unknown error')}")
        
    def get_or_create_label(self, repo: Repository.Repository, name: str, color: str, description: str = "") -> 'Label':
        """Gets a label by name, creating it if it doesn't exist."""
        try:
            return repo.get_label(name)
        except UnknownObjectException:
            try:
                return repo.create_label(name=name, color=color, description=description)
            except GithubException as e:
                raise GitHubError(f"Failed to create label '{name}'. Details: {e.data.get('message', 'Unknown error')}")
            