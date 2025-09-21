"""Git utilities for AB Code Reviewer."""

import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any

from .exceptions import ToolExecutionError


class GitManager:
    """Manages git operations for code review context."""
    
    def __init__(self, project_path: Path):
        """
        Initialize git manager.
        
        Args:
            project_path: Path to git repository
        """
        self.project_path = project_path
    
    def is_git_repository(self) -> bool:
        """Check if project is a git repository."""
        return (self.project_path / ".git").exists()
    
    def get_git_diff(self, staged_only: bool = False) -> Optional[str]:
        """
        Get git diff of recent changes.
        
        Args:
            staged_only: Only get staged changes
            
        Returns:
            Git diff output or None if no changes
        """
        if not self.is_git_repository():
            return None
        
        try:
            if staged_only:
                result = subprocess.run(
                    ["git", "diff", "--cached"],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            else:
                # Get staged changes first, then unstaged
                result = subprocess.run(
                    ["git", "diff", "--cached"],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout
                
                # If no staged changes, get unstaged changes
                result = subprocess.run(
                    ["git", "diff"],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            
            if result.returncode == 0:
                return result.stdout if result.stdout.strip() else None
            
        except subprocess.TimeoutExpired:
            raise ToolExecutionError("Git diff command timed out")
        except FileNotFoundError:
            raise ToolExecutionError("Git not found")
        except Exception as e:
            raise ToolExecutionError(f"Git diff failed: {str(e)}")
        
        return None
    
    def get_recent_commits(self, count: int = 5) -> List[Dict[str, Any]]:
        """
        Get recent commit information.
        
        Args:
            count: Number of recent commits to retrieve
            
        Returns:
            List of commit information dictionaries
        """
        if not self.is_git_repository():
            return []
        
        try:
            result = subprocess.run(
                ["git", "log", f"-{count}", "--pretty=format:%H|%s|%an|%ad", "--date=short"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return []
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split('|', 3)
                    if len(parts) >= 4:
                        commits.append({
                            "hash": parts[0],
                            "message": parts[1],
                            "author": parts[2],
                            "date": parts[3]
                        })
            
            return commits
        
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []
    
    def get_branch_info(self) -> Dict[str, str]:
        """
        Get current branch information.
        
        Returns:
            Dictionary with branch information
        """
        if not self.is_git_repository():
            return {}
        
        try:
            # Get current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            current_branch = result.stdout.strip() if result.returncode == 0 else "unknown"
            
            # Get remote tracking branch
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            tracking_branch = result.stdout.strip() if result.returncode == 0 else None
            
            return {
                "current": current_branch,
                "tracking": tracking_branch
            }
        
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return {"current": "unknown", "tracking": None}
    
    def get_file_status(self) -> Dict[str, List[str]]:
        """
        Get git status of files.
        
        Returns:
            Dictionary with file status information
        """
        if not self.is_git_repository():
            return {}
        
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return {}
            
            status = {
                "modified": [],
                "added": [],
                "deleted": [],
                "untracked": []
            }
            
            for line in result.stdout.strip().split('\n'):
                if line:
                    status_code = line[:2]
                    filename = line[3:]
                    
                    if status_code[0] == 'M' or status_code[1] == 'M':
                        status["modified"].append(filename)
                    elif status_code[0] == 'A' or status_code[1] == 'A':
                        status["added"].append(filename)
                    elif status_code[0] == 'D' or status_code[1] == 'D':
                        status["deleted"].append(filename)
                    elif status_code == '??':
                        status["untracked"].append(filename)
            
            return status
        
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return {}
