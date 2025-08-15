from dataclasses import dataclass, field
from typing import List

@dataclass
class RepoStatus:
    """A simple data class to hold the detailed status of a repository."""
    branch: str
    staged: List[str] = field(default_factory=list)
    unstaged: List[str] = field(default_factory=list)
    untracked: List[str] = field(default_factory=list)