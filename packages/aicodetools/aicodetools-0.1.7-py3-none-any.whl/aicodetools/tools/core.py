"""
Core CodeToolsInstance class providing all tool methods for AI agents.

Simple session management using SWE Rex native capabilities:
- Multiple named bash sessions with persistent environments
- Direct integration with SWE Rex runtime session tracking
- No active session tracking - agents specify session names explicitly

Example usage:
    # Create sessions and run commands (session names always required)
    await instance.create_bash_session("build")
    await instance.run_bash_session("export BUILD_MODE=production", "build")
    await instance.run_bash_session("make", "build")
    
    await instance.create_bash_session("test")
    await instance.run_bash_session("pytest", "test")
    
    # List and close sessions
    sessions = await instance.list_bash_sessions()  # Returns ['build', 'test']
    await instance.close_bash_session("build")
"""

import asyncio
import json
import os
import re
import subprocess
import tempfile
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any, Union


# === UNIFIED OUTPUT STRUCTURES ===

@dataclass
class ToolResponse:
    """Base response class for all tool operations."""
    success: bool
    message: str = ""
    details: Optional[str] = None
    suggestions: List[str] = field(default_factory=list)


@dataclass
class FileReadResponse(ToolResponse):
    """Response for read file operations."""
    content: Optional[str] = None
    lines_shown: Optional[int] = None
    total_lines: Optional[int] = None
    is_truncated: bool = False


@dataclass
class FileWriteResponse(ToolResponse):
    """Response for write file operations."""
    bytes_written: Optional[int] = None


@dataclass
class FileEditResponse(ToolResponse):
    """Response for edit file operations."""
    replacements_made: int = 0
    preview: Optional[str] = None


@dataclass
class CommandResponse(ToolResponse):
    """Response for command execution."""
    stdout: str = ""
    stderr: str = ""
    exit_code: Optional[int] = None
    command: str = ""
    session_name: Optional[str] = None
    is_interactive: bool = False
    interrupted: bool = False
    expect_string: Optional[str] = None


@dataclass
class SearchMatch:
    """Single search result match."""
    file: str
    line: int
    content: str


@dataclass
class SearchResponse(ToolResponse):
    """Response for search operations."""
    matches: List[SearchMatch] = field(default_factory=list)
    total_matches: int = 0
    files_searched: int = 0

from swerex.deployment.docker import DockerDeployment
from swerex.runtime.abstract import (
    BashAction, Command, CreateBashSessionRequest, CreateSessionRequest,
    ReadFileRequest, WriteFileRequest, CloseSessionRequest, BashInterruptAction
)

from ..utils.utils import (
    validate_file_path, create_success_response, create_error_response,
    parse_grep_output, safe_filename, get_file_extension, is_text_file,
    format_file_size, expand_glob_pattern
)


@dataclass
class BashConfig:
    """Simple configuration for unified bash session commands."""
    timeout: float = 60.0  # generous default for agents
    expect_strings: List[str] = field(default_factory=lambda: [">>> ", "$ ", "> ", "# ", "sqlite> ", "(Pdb) ", "ipdb> "])  # common interactive prompts
    interactive: bool = True  # always interactive by default
    interrupt_timeout: float = 2.0
    interrupt_retries: int = 3


@dataclass
class CodeToolsConfig:
    """Configuration for CodeTools instance."""
    default_read_offset: int = 1
    default_read_limit: Optional[int] = None  # None means read entire file
    default_bash_session: str = "main"
    max_exception_lines: int = 10
    track_read_files: bool = True


class CodeToolsInstance:
    """
    Core instance providing tool methods for AI agent integration.
    
    All operations go through SWE-REX runtime for consistency and reliability.
    Methods follow patterns from both Aider and Gemini CLI for best practices.
    """
    
    def __init__(self, deployment: DockerDeployment, config: Optional[CodeToolsConfig] = None):
        """
        Initialize CodeToolsInstance with SWE-REX deployment.
        
        Args:
            deployment: SWE-REX DockerDeployment instance
            config: Optional configuration for tool behavior
        """
        self.runtime = deployment.runtime
        self.config = config or CodeToolsConfig()
        self._session_files = set()  # Track files in current session
        self.sessions = {}
        self.read_files = []  # Track files that have been read for validation 
        # Pre-configured expect strings for various interactive environments
        self.interactive_expects = [
            # Shell prompts
            "$ ", "# ", "> ", ">>> ", 
            # Python environments
            ">>> ", "... ", r"In \[", r"Out\[", "ipdb> ", r"\(Pdb\) ",
            # Database prompts  
            "sqlite> ", "mysql> ", "postgres=# ", "redis> ",
            # Languages/REPLs
            r"irb\(main\):", r"iex\(", "ghci> ", "scala> ", "node> ",
            # Development tools
            "git> ", r"\(venv\) ", "poetry> ", "npm > ",
            # System tools
            "root@", "user@", "admin@", ": ~", ": /",
            # Interactive applications
            "Press any key", "Continue? ", "y/n", "Y/N", r"\[Y/n\]", r"\[y/N\]",
            # vim/editor
            ":", "--INSERT--", "-- VISUAL --",
            # Other common
            r"More\? ", r"Next\? ", "Continue", "Enter", "Password:",
        ]
        
        # Default configuration for agent usage
        self.default_config = BashConfig(
            timeout=60.0,
            expect_strings=self.interactive_expects,
            interactive=True,
            interrupt_timeout=2.0,
            interrupt_retries=3
        )

  
    def _format_exception(self, exception_text: str) -> str:
        """Format long exceptions to show first and last few lines."""
        lines = exception_text.split('\n')
        max_lines = self.config.max_exception_lines
        
        if len(lines) <= max_lines:
            return exception_text
            
        half = max_lines // 2
        first_lines = lines[:half]
        last_lines = lines[-half:]
        
        return '\n'.join(first_lines) + '\n... [truncated] ...\n' + '\n'.join(last_lines)
    
    def _create_success_response(self, response_class, message: str = "Success", **kwargs) -> Any:
        """Create a successful response of the specified type."""
        return response_class(success=True, message=message, **kwargs)
    
    def _create_error_response(self, response_class, error_message: str, 
                              details: Optional[str] = None, 
                              suggestions: List[str] = None) -> Any:
        """Create an error response of the specified type."""
        formatted_details = self._format_exception(details) if details and len(details) > 500 else details
        return response_class(
            success=False, 
            message=error_message,
            details=formatted_details,
            suggestions=suggestions or []
        )
    
    async def _file_exists(self, path: str) -> bool:
        """
        #TODO for other env OS who knows whihc env it will be
        Check if a file exists using bash command to avoid ReadFileRequest exceptions.
        
        Args:
            path: File path to check
            
        Returns:
            True if file exists, False otherwise
        """
        try:
            # Use test command to check file existence
            result = await self.run_command(f'test -f "{path}"')
            return result.exit_code == 0
        except Exception:
            # If command fails for any reason, assume file doesn't exist
            return False

    
    async def _try_system_grep(self, pattern: str, path: str, include: str = None) -> Dict:
        """Try system grep strategy."""
        try:
            cmd = f"grep -r -n -E '{pattern}' ."
            
            # Add common exclusions
            exclusions = [".git", "node_modules", "__pycache__", ".venv", ".env"]
            for exc in exclusions:
                cmd += f" --exclude-dir='{exc}'"
            
            if include:
                cmd += f" --include='{include}'"
            
            result = await self.run_command(cmd, directory=path)
            if result.exit_code <= 1:  # grep returns 1 for no matches, which is OK
                matches = parse_grep_output(result.stdout) if result.stdout else []
                return {"success": True, "matches": matches}
            else:
                return {"success": False, "error": result.stderr}
        except:
            return {"success": False, "error": "System grep failed"}
    
    async def _try_python_grep(self, pattern: str, path: str, include: str = None) -> List[Dict]:
        """Python fallback search strategy."""
        try:
            import re
            import glob
            
            regex = re.compile(pattern, re.IGNORECASE)
            matches = []
            
            # Determine search pattern
            if include:
                search_pattern = os.path.join(path, "**", include)
            else:
                search_pattern = os.path.join(path, "**", "*")
            
            # Find files using glob
            for file_path in glob.glob(search_pattern, recursive=True):
                if not os.path.isfile(file_path):
                    continue
                
                # Skip binary files and common ignore patterns
                if not is_text_file(file_path):
                    continue
                
                if any(ignore in file_path for ignore in ['.git/', 'node_modules/', '__pycache__/']):
                    continue
                
                try:
                    # Read and search file
                    content = await self.read_file(file_path)
                    if isinstance(content, dict):  # Error response
                        continue
                    
                    lines = content.splitlines()
                    for line_num, line in enumerate(lines, 1):
                        if regex.search(line):
                            matches.append({
                                "file": file_path,
                                "line": line_num,
                                "content": line.strip()
                            })
                except:
                    continue  # Skip files we can't read
            
            return matches
            
        except Exception as e:
            return create_error_response(
                f"Python search failed: {str(e)}",
                details=str(e)
            )
    
    def _parse_test_output(self, output: str, command: str) -> Dict:
        """Parse test output to extract statistics."""
        stats = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0
        }
        
        try:
            if "pytest" in command:
                # Parse pytest output
                if "failed" in output.lower():
                    failed_match = re.search(r'(\d+) failed', output)
                    if failed_match:
                        stats["failed"] = int(failed_match.group(1))
                
                if "passed" in output.lower():
                    passed_match = re.search(r'(\d+) passed', output)
                    if passed_match:
                        stats["passed"] = int(passed_match.group(1))
                
                if "skipped" in output.lower():
                    skipped_match = re.search(r'(\d+) skipped', output)
                    if skipped_match:
                        stats["skipped"] = int(skipped_match.group(1))
            
            elif "npm test" in command:
                # Parse npm test output
                if "failing" in output.lower():
                    failed_match = re.search(r'(\d+) failing', output)
                    if failed_match:
                        stats["failed"] = int(failed_match.group(1))
                
                if "passing" in output.lower():
                    passed_match = re.search(r'(\d+) passing', output)
                    if passed_match:
                        stats["passed"] = int(passed_match.group(1))
            
            stats["total"] = stats["passed"] + stats["failed"] + stats["skipped"]
            
        except:
            # If parsing fails, just return empty stats
            pass
        
        return stats
    
    async def _try_git_grep(self, pattern: str, path: str, include: str = None) -> Dict:
        """Try git grep strategy."""
        try:
            cmd = f"git grep -n -E '{pattern}'"
            if include:
                cmd += f" -- '{include}'"
            
            result = await self.run_command(cmd, directory=path)
            if result["success"] and result["stdout"]:
                matches = parse_grep_output(result["stdout"])
                return {"success": True, "matches": matches}
            else:
                return {"success": False, "error": result.get("stderr", "")}
        except:
            return {"success": False, "error": "Git grep failed"}
    
    # === FILE OPERATIONS ===

    async def read_file(self, path: str, offset: Optional[int] = None, 
                        limit: Optional[int] = None, encoding: Optional[str] = None) -> FileReadResponse:
        """***ISTOOL***
        Reads content from a file with optional line-based pagination.

This tool is intended for reading text files only. It tracks read operations
for later validation in write/edit commands. If the file is binary or unreadable
due to permissions or encoding, it returns a structured error.

Usage:
    await read_file("README.md", offset=1, limit=50)

Args:
    path (str): File path to read.
    offset (Optional[int]): Starting line number (1-based). Defaults to config default.
    limit (Optional[int]): Number of lines to read. Defaults to config default.
    encoding (Optional[str]): Encoding to use. Defaults to system default.

Returns:
    FileReadResponse:
        - content (str): File content (possibly truncated).
        - lines_shown (int), total_lines (int), is_truncated (bool)

Possible Failures:
    - File not found
    - Invalid encoding
    - Binary file (unsupported)
    - Permission issues

Suggestions:
    - Use `list_directory()` or `glob_files()` to find valid file paths.
    - Ensure encoding matches file format.
        """
        try:
            # Use configuration defaults if not specified
            effective_offset = offset if offset is not None else self.config.default_read_offset
            effective_limit = limit if limit is not None else self.config.default_read_limit
            
            # For container operations, use path as-is
            abs_path = path
            
            # print((await self._file_exists(abs_path)))
            # Check if file exists using our safe method
            if not await self._file_exists(abs_path):
                return self._create_error_response(
                    FileReadResponse,
                    f"File not found: {path}",
                    suggestions=[
                        "Check if the file path is correct",
                        "Use list_directory() to explore available files",
                        "Use glob_files() to find files matching a pattern"
                    ]
                )
            
            # Read the file content
            try:
                request = ReadFileRequest(path=abs_path, encoding=encoding)
                response = await self.runtime.read_file(request)
                content = response.content
            except Exception as read_error:
                return self._create_error_response(
                    FileReadResponse,
                    f"Failed to read file: {path}",
                    details=str(read_error),
                    suggestions=[
                        "Check file permissions",
                        "Verify the file is not locked by another process",
                        "Try a different encoding if the file contains special characters"
                    ]
                )
            
            # Track successfully read files
            if self.config.track_read_files and abs_path not in self.read_files:
                self.read_files.append(abs_path)
            
            lines = content.splitlines()
            total_lines = len(lines)
            
            # Apply pagination if specified
            is_truncated = False
            lines_shown = total_lines
            
            if effective_offset > 1 or effective_limit is not None:
                start_idx = max(0, effective_offset - 1)
                
                if effective_limit is not None:
                    end_idx = start_idx + effective_limit
                    paginated_lines = lines[start_idx:end_idx]
                    is_truncated = end_idx < total_lines or start_idx > 0
                else:
                    paginated_lines = lines[start_idx:]
                    is_truncated = start_idx > 0
                
                lines_shown = len(paginated_lines)
                content = '\n'.join(paginated_lines)
                
                # Add truncation notice if content was truncated
                if is_truncated:
                    truncation_msg = f"[File content truncated: showing lines {effective_offset}-{effective_offset + lines_shown - 1} of {total_lines} total lines]\n"
                    content = truncation_msg + content
            
            return self._create_success_response(
                FileReadResponse,
                "File read successfully",
                content=content,
                lines_shown=lines_shown,
                total_lines=total_lines,
                is_truncated=is_truncated
            )
            
        except Exception as e:
            return self._create_error_response(
                FileReadResponse,
                f"Failed to read file: {str(e)}",
                details=str(e),
                suggestions=[
                    "Verify the file path is accessible",
                    "Check file permissions",
                    "Ensure the file is not locked by another process"
                ]
            )
    
    async def write_file(self, path: str, content: str, 
                         force: bool = False, encoding: Optional[str] = None) -> FileWriteResponse:
        """***ISTOOL***
        Writes text content to a file, with overwrite protection.

To avoid accidental modification of unknown files, writing to an existing file
requires it to have been read first — unless `force=True`.

Usage:
    await write_file("example.txt", "new content", force=True)

Args:
    path (str): Path to file to write.
    content (str): Text content to write.
    force (bool): Set to True to bypass read-before-write check.
    encoding (Optional[str]): Text encoding (default: system default).

Returns:
    FileWriteResponse:
        - bytes_written (int)

Possible Failures:
    - Path invalid or unwritable
    - File not read beforehand (if force=False)
    - Permission or disk issues

Suggestions:
    - Use `read_file()` before editing.
    - Set `force=True` if you're sure you want to overwrite.
        """
        try:
            abs_path = path
            
            # Check if file exists using our safe method
            file_exists = await self._file_exists(abs_path)
            
            # print(file_exists)
            # Validate read-before-write for existing files
            if file_exists and self.config.track_read_files and not force:
                if abs_path not in self.read_files:
                    return self._create_error_response(
                        FileWriteResponse,
                        f"Cannot write to existing file without reading it first: {path}",
                        suggestions=[
                            "Use read_file() to examine the file before modifying",
                            "Use force=True to bypass this safety check",
                            "Use edit_file() for targeted changes instead"
                        ]
                    )
            
            # Write the file
            # print("XX").
            request = WriteFileRequest(path=abs_path, content=content)
            response = await self.runtime.write_file(request)
            
            # Calculate bytes written
            bytes_written = len(content.encode('utf-8'))
            
            # Track the file as read since we just wrote to it
            if self.config.track_read_files and abs_path not in self.read_files:
                self.read_files.append(abs_path)
            
            action = "created" if not file_exists else "updated"
            return self._create_success_response(
                FileWriteResponse,
                f"File {action} successfully",
                bytes_written=bytes_written
            )
            
        except Exception as e:
            return self._create_error_response(
                FileWriteResponse,
                f"Failed to write file: {str(e)}",
                details=str(e),
                suggestions=[
                    "Check if the directory exists and is writable",
                    "Verify file permissions",
                    "Ensure disk space is available"
                ]
            )
    
    async def edit_file(self, path: str, old_string: str, new_string: str, 
                        replace_all: bool = False) -> FileEditResponse:
        """***ISTOOL***
        Performs text replacement in a file.

Supports both single and full replacement modes. The file must be read first
before edits are allowed for safety.

Usage:
    await edit_file("code.py", "old_function()", "new_function()", replace_all=True)

Args:
    path (str): Path to the file to edit.
    old_string (str): Text to search for.
    new_string (str): Replacement text.
    replace_all (bool): If True, replace all instances. Default is first match only.

Returns:
    FileEditResponse:
        - replacements_made (int)
        - preview (str): Change preview (first line diff)

Possible Failures:
    - File unread or not previously read
    - Match string not found
    - Write failure after edit

Suggestions:
    - Use `read_file()` before edit.
    - Ensure exact match in whitespace and formatting.
        """
        try:
            abs_path = path
            
            # Check if file exists and validate read requirement
            if self.config.track_read_files and abs_path not in self.read_files:
                return self._create_error_response(
                    FileEditResponse,
                    f"Cannot edit file without reading it first: {path}",
                    suggestions=[
                        "Use read_file() to examine the file before editing",
                        "Use write_file() with force=True for new files"
                    ]
                )
            
            # Read current content
            read_response = await self.read_file(path)
            if not read_response.success:
                # File doesn't exist - suggest creating it
                return self._create_error_response(
                    FileEditResponse,
                    f"Cannot edit non-existent file: {path}",
                    suggestions=[
                        "Use write_file() to create the file first",
                        "Check if the file path is correct"
                    ]
                )
            
            current_content = read_response.content
            
            # Check if old_string exists
            if old_string not in current_content:
                return self._create_error_response(
                    FileEditResponse,
                    f"Text to replace not found in file: {path}",
                    suggestions=[
                        "Check if the text to replace is exactly correct",
                        "Ensure proper whitespace and line endings",
                        "Use glob_files() or list_directory() to explore the file"
                    ]
                )
            
            # Count potential replacements for reporting
            replacement_count = current_content.count(old_string)
            
            # Perform replacement
            if replace_all:
                new_content = current_content.replace(old_string, new_string)
                replacements_made = replacement_count
            else:
                new_content = current_content.replace(old_string, new_string, 1)
                replacements_made = 1
            
            # Generate preview of changes
            preview_lines = []
            old_lines = current_content.split('\n')
            new_lines = new_content.split('\n')
            
            # Find first difference for preview
            for i, (old_line, new_line) in enumerate(zip(old_lines, new_lines)):
                if old_line != new_line:
                    preview_lines.append(f"Line {i+1}:")
                    preview_lines.append(f"- {old_line}")
                    preview_lines.append(f"+ {new_line}")
                    break
            
            preview = '\n'.join(preview_lines) if preview_lines else "No preview available"
            
            # Write back to file using force=True since we validated read
            write_response = await self.write_file(path, new_content, force=True)
            if not write_response.success:
                return self._create_error_response(
                    FileEditResponse,
                    f"Failed to write edited content: {write_response.message}",
                    details=write_response.details
                )
            
            return self._create_success_response(
                FileEditResponse,
                f"File edited successfully ({replacements_made} replacement{'s' if replacements_made != 1 else ''} made)",
                replacements_made=replacements_made,
                preview=preview
            )
            
        except Exception as e:
            return self._create_error_response(
                FileEditResponse,
                f"Failed to edit file: {str(e)}",
                details=str(e),
                suggestions=[
                    "Verify the file exists and is readable",
                    "Check if the search text is correct",
                    "Ensure proper file permissions"
                ]
            )
    
    async def list_directory(self, path: str = ".", ignore: List[str] = None) -> Union[List[Dict], ToolResponse]:
        """***ISTOOL***
        List files and directories with metadata.
        
        Args:
            path: Directory path to list
            ignore: List of regex patterns to ignore (case-insensitive matching)
                   Common patterns: r'\.git', r'__pycache__', r'node_modules', r'\..*'
            
        Returns:
            List of file/directory info dicts, or ToolResponse if error
        """
        try:
            # For container operations, use path as-is (don't resolve to host paths)
            abs_path = path  # Keep container path as-is
            
            # Let SWE-REX handle directory validation within the container
            
            # Set up ignore patterns (convert to regex if not already)
            import re
            ignore_patterns = ignore or []
            
            # Add default ignore patterns as regex
            default_ignores = [r'\.git$', r'__pycache__$', r'\.DS_Store$', r'node_modules$']
            ignore_patterns.extend(default_ignores)
            
            # Compile regex patterns for efficient matching
            compiled_patterns = []
            for pattern in ignore_patterns:
                try:
                    compiled_patterns.append(re.compile(pattern, re.IGNORECASE))
                except re.error:
                    # If regex compilation fails, treat as literal string
                    escaped_pattern = re.escape(pattern)
                    compiled_patterns.append(re.compile(escaped_pattern, re.IGNORECASE))
            
            # Use ls -la command to get detailed directory listing in container
            ls_command = f"ls -la '{abs_path}' 2>/dev/null || echo 'Directory not found'"
            cmd_list = ["bash", "-c", ls_command]
            cmd_obj = Command(command=cmd_list)
            response = await self.runtime.execute(cmd_obj)
            
            if response.exit_code != 0 or "Directory not found" in response.stdout:
                return self._create_error_response(
                    ToolResponse,
                    f"Directory not found: {path}",
                    suggestions=["Check if the directory path is correct"]
                )
            
            items = []
            lines = response.stdout.strip().split('\n')
            
            # Skip first line (total) and parse each file/directory line
            for line in lines[1:] if len(lines) > 1 else []:
                if not line.strip():
                    continue
                    
                try:
                    # Parse ls output: permissions, links, user, group, size, date, time, name
                    parts = line.split()
                    if len(parts) < 8:
                        continue
                        
                    permissions = parts[0]
                    size = int(parts[4]) if parts[4].isdigit() else 0
                    name = ' '.join(parts[8:])  # Handle filenames with spaces
                    
                    # Skip . and .. entries
                    if name in ['.', '..']:
                        continue
                        
                    # Skip ignored patterns using regex matching
                    if any(pattern.search(name) for pattern in compiled_patterns):
                        continue
                    
                    is_directory = permissions.startswith('d')
                    full_path = f"{abs_path.rstrip('/')}/{name}"
                    
                    items.append({
                        "name": name,
                        "path": full_path,
                        "type": "directory" if is_directory else "file",
                        "size": size if not is_directory else 0,
                        "size_formatted": format_file_size(size) if not is_directory else "",
                        "modified": 0,  # Would need stat to get accurate timestamp
                        "is_text": is_text_file(name) if not is_directory else False
                    })
                    
                except (ValueError, IndexError):
                    # Skip malformed lines
                    continue
            
            # Sort: directories first, then files, both alphabetically
            items.sort(key=lambda x: (x["type"] != "directory", x["name"].lower()))
            
            return items
            
        except Exception as e:
            return self._create_error_response(
                ToolResponse,
                f"Failed to list directory: {str(e)}",
                details=str(e),
                suggestions=[
                    "Verify the directory path exists",
                    "Check directory permissions",
                    "Ensure the path is accessible within the container"
                ]
            )
    
    # === SESSION MANAGEMENT ===
    
    async def create_bash_session(self, session_name: Optional[str] = None) -> ToolResponse:
        """***ISTOOL***
        Create a new named bash session using SWE Rex native functionality.
        
        Creates an interactive, persistent shell session that maintains environment
        variables, working directory, and command history across multiple commands.
        
        If you encounter errors or unwanted output from a session, close it and
        create a new one for a clean state.
        
        Args:
            session_name: Name for the session (defaults to config default)
            
        Returns:
            ToolResponse indicating success or failure
        """
        try:
            effective_session_name = session_name or self.config.default_bash_session
            
            if session_name in self.sessions.keys() : 
                return self._create_error_response(
                    ToolResponse,
                    f"Session '{effective_session_name}' already exists",
                    suggestions=[
                        "Use a different session name", 
                        "Close the existing session first",
                        "Use get_bash_sessions() to see active sessions"
                    ]
                )

            request = CreateBashSessionRequest(session=effective_session_name)
            await self.runtime.create_session(request)
            self.sessions[effective_session_name] = True
            
            return self._create_success_response(
                ToolResponse,
                f"Bash session '{effective_session_name}' created successfully"
            )
            
        except Exception as e:
            if "already exists" in str(e):
                return self._create_error_response(
                    ToolResponse,
                    f"Session '{effective_session_name}' already exists",
                    suggestions=[
                        "Use a different session name", 
                        "Close the existing session first",
                        "Use get_bash_sessions() to see active sessions"
                    ]
                )
            return self._create_error_response(
                ToolResponse,
                f"Failed to create bash session: {str(e)}",
                details=str(e)
            )
    
    async def get_bash_sessions(self) -> Dict:
        """
        List all active bash sessions using SWE Rex native functionality.
        
        Returns:
            List of session names
        """
        return self.sessions
    
    async def close_bash_session(self, session_name: str) -> Union[bool, Dict]:
        """
        Close a specific bash session using SWE Rex native functionality.

        Args:
            session_name: Name of session to close
            
        Returns:
            True if successful, error dict if failed
        """
        try:
            if session_name not in self.sessions.keys():
                return create_error_response(
                    f"Session '{session_name}' not found",
                    suggestions=["Use get_bash_sessions() to see available sessions"]
                )
            if self.sessions[session_name]: 
                request = CloseSessionRequest(session=session_name)
                await self.runtime.close_session(request)
                self.sessions[session_name] = False  # Mark as closed
                return True
            else: 
                return create_error_response(
                    f"Session '{session_name}' was already closed",
                    suggestions=["Use get_bash_sessions() to see available sessions"]
                )
            
        except Exception as e:
            return create_error_response(
                f"Failed to close session: {str(e)}",
                details=str(e)
            )
    
    # === SHELL OPERATIONS ===
    
    async def run_command(
        self,
        command: str,
        directory: Optional[str] = None,
        timeout: Optional[float] = None
    ) -> CommandResponse:
        """***ISTOOL***
        Executes a single shell command in non-interactive, stateless mode.

    Intended for straightforward, short-lived commands. This function does *not* maintain shell state, support interactive input (like prompts or REPLs), or handle long-running builds gracefully. If your workflow needs any of that, this is probably not the tool you want — unless, of course, it's the only one you have.

    Args:
        command (str): Shell command to run.
        directory (Optional[str]): Directory in which to execute the command.
        timeout (Optional[float]): Max time (in seconds) to wait before forcefully terminating the command. Defaults to 60 seconds.

    Returns:
        CommandResponse:
            - stdout: Standard output of the command.
            - stderr: Standard error of the command.
            - exit_code: Integer exit code.
            - command: The original command string.

    Behavior Notes:
        - Commands that prompt for input will hang or fail silently.
        - Processes exceeding the timeout will exit silently and return current output.
        - Silent operation - no exceptions thrown for timeouts or non-zero exit codes.

    Suggestions:
        • If you're stuck with just this function: favor simple, deterministic commands. For anything resembling a build, CI setup, or anything with a progress bar, use `nohup`, backgrounding (`&`), and log redirection (`> file.log 2>&1`) to work around limitations.
        • If you happen to have access to more capable tools (persistent sessions, file readers, interactive shells, etc.), you might want to use those instead for multi-step workflows or anything stateful.

    Use wisely. Or at least pragmatically.
        """
        try:
            if timeout is None : 
                timeout = self.default_config.timeout
            cmd_obj = Command(
                command=command,
                shell=True,
                cwd=directory,
                timeout=timeout,
                check=False,  # Don't raise exceptions on non-zero exit codes
            )

            response = await self.runtime.execute(cmd_obj)

            return self._create_success_response(
                CommandResponse,
                "Command executed successfully.",
                stdout=response.stdout,
                stderr=response.stderr,
                exit_code=response.exit_code,
                command=command
            )

        except Exception as e:
            # Handle timeout and other exceptions silently
            # Try to extract any partial output from the exception
            stdout_output = ''
            stderr_output = ''
            exit_code = -1
            
            # Extract output from different types of exceptions
            if hasattr(e, 'stdout'):
                stdout_output = str(e.stdout) if e.stdout else ''
            if hasattr(e, 'stderr'):
                stderr_output = str(e.stderr) if e.stderr else ''
            if hasattr(e, 'exit_code') or hasattr(e, 'returncode'):
                exit_code = getattr(e, 'exit_code', getattr(e, 'returncode', -1))
            
            # If no specific error output, put the exception message in stderr
            if not stderr_output and not stdout_output:
                stderr_output = str(e)
            
            # Always return success=True to avoid throwing further errors
            return self._create_success_response(
                CommandResponse,
                "Command execution completed.",
                stdout=stdout_output,
                stderr=stderr_output,
                exit_code=exit_code,
                command=command
            )
    
    async def run_bash_session(self, command: str, session_name: Optional[str] = None,
                               timeout: Optional[float] = None,
                               interrupt: bool = False,
                               interactive: Optional[bool] = None) -> CommandResponse:
        """***ISTOOL***
        Execute command in a persistent bash session.
        
        This method maintains state between commands including:
        - Environment variables
        - Working directory
        - Command history
        - Interactive program states
        
        Args:
            command: Command to run in session
            session_name: Name of session to use (defaults to config default)
            timeout: Optional timeout override (uses 60s default if None)
            interrupt: If True, interrupts the session instead of running command
            interactive: If True, treat as interactive command. If None, auto-detect based on command
            
        Returns:
            CommandResponse with execution results
        """
        try:
            effective_session_name = session_name or self.config.default_bash_session
            
            # Use instance default config with optional timeout override
            config = self.default_config
            if timeout is not None:
                config = BashConfig(
                    timeout=timeout,
                    expect_strings=self.interactive_expects,
                    interactive=True,
                    interrupt_timeout=2.0,
                    interrupt_retries=3
                )
            
            # Auto-create session if it doesn't exist or was closed
            if effective_session_name not in self.sessions.keys() or not self.sessions[effective_session_name]:
                create_result = await self.create_bash_session(effective_session_name)
                if not create_result.success:
                    return CommandResponse(
                        success=False,
                        message=f"Failed to create session: {create_result.message}",
                        details=create_result.details,
                        command=command,
                        session_name=effective_session_name
                    )
            
            # Branch to interrupt if requested
            if interrupt:
                interrupt_action = BashInterruptAction(
                    session=effective_session_name,
                    timeout=config.interrupt_timeout,
                    n_retry=config.interrupt_retries,
                    expect=self.interactive_expects
                )
                response = await self.runtime.run_in_session(interrupt_action)
                
                return self._create_success_response(
                    CommandResponse,
                    "Session interrupted successfully",
                    stdout=response.output,
                    exit_code=0,
                    command="INTERRUPT",
                    session_name=effective_session_name,
                    is_interactive=True,
                    interrupted=True,
                    expect_string=getattr(response, 'expect_string', None)
                )
            
            # Detect if command should be interactive
            if interactive is None:
                # Auto-detect interactive commands
                interactive_indicators = [
                    'python', 'python3', 'node', 'irb', 'ghci', 'sqlite3', 'mysql',
                    'redis-cli', 'mongo', 'psql', 'vim', 'nano', 'emacs', 'top', 'htop',
                    'less', 'more', 'tail -f', 'watch', 'ssh', 'telnet', 'ftp'
                ]
                is_interactive = any(indicator in command.lower() for indicator in interactive_indicators)
                # Also check if command doesn't end with expected output (no pipes, redirects, etc)
                has_output_redirect = any(op in command for op in ['>', '>>', '|', '&&', '||', ';'])
                # Simple commands should not be interactive unless explicitly specified
                if not has_output_redirect and not is_interactive:
                    is_interactive = False
                else:
                    is_interactive = True
            else:
                is_interactive = interactive
            
            # Execute command using SWE Rex's native session parameter
            if is_interactive:
                action = BashAction(
                    command=command,
                    session=effective_session_name,
                    timeout=config.timeout,
                    is_interactive_command=True,
                    is_interactive_quit=False,
                    expect=self.interactive_expects,
                    check="silent"
                )
            else:
                # For non-interactive commands, use simpler execution
                action = BashAction(
                    command=command,
                    session=effective_session_name,
                    timeout=config.timeout,
                    is_interactive_command=False,
                    is_interactive_quit=False,
                    expect=[],  # No expect strings for simple commands
                    check="silent"
                )
            response = await self.runtime.run_in_session(action)
            
            success = response.exit_code == 0 if response.exit_code is not None else True
            message = "Command executed successfully" if success else "Command completed with errors"
            
            return self._create_success_response(
                CommandResponse,
                message,
                stdout=response.output,
                stderr=getattr(response, 'stderr', ''),
                exit_code=response.exit_code,
                command=command,
                session_name=effective_session_name,
                is_interactive=is_interactive,
                expect_string=getattr(response, 'expect_string', None)
            )
            
        except Exception as e:
            return CommandResponse(
                success=False,
                message=f"Failed to execute bash command: {str(e)}",
                details=str(e),
                command=command,
                session_name=effective_session_name or "unknown"
            )
    
    async def run_in_jupyter_ipython(
        self,
        command: str,
        timeout: Optional[float] = None
    ) -> CommandResponse:
        """***ISTOOL***
        Executes or continues output streaming from code in a persistent Jupyter kernel.

        Parameters:
            code (str): 
                - Normal: Python, shell (!), or bash (%%bash) code.
                - " " (space): Special signal to continue retrieving output from a prior command.
                - "C-c": Interrupts the currently running command in the kernel.
                - If is_input=True: text to send to Python's `input()` prompt (see below).

            timeout (int):
                - How long to wait for output, default is 30 sec.
                - If execution is not complete in time, output can be resumed later with `" "`.
                - command isn't killed

            is_input (bool):
                - True when sending response to a Python `input()` call.
                - Input support only works for Python code using `input()` — not bash or shell commands.

        Returns:
            str: Combined stdout and stderr, or status message.

        Notes:
            - Only one command can execute at a time.
            - Use `" "` to resume incomplete execution and stream remaining output.
            - Send `"C-c"` to interrupt long-running or stalled code.
        """

        try:
            if timeout is None:
                timeout = self.default_config.timeout

            jupy_command = f"jupyter-remote-runner run {command} --timeout {timeout}"

            command_timeout = timeout * 2
            
            cmd_obj = Command(
                command=jupy_command,
                shell=True,
                timeout=command_timeout
            )

            response = await self.runtime.execute(cmd_obj)

            return self._create_success_response(
                CommandResponse,
                "Command executed successfully in Jupyter IPython.",
                stdout=response.stdout,
                stderr=response.stderr,
                exit_code=response.exit_code,
                command=command
            )

        except Exception as e:
            return CommandResponse(
                success=False,
                message=f"Failed to execute command in Jupyter IPython: {str(e)}",
                details=str(e),
                command=command
            )
    # === SEARCH & DISCOVERY ===
    
    async def grep_files(self, pattern: str, path: str = ".", include: str = None) -> Union[List[Dict], Dict]:
        """***ISTOOL***
        Multi-strategy search 

        Args:
            pattern: Regex pattern to search for
            path: Directory to search in
            include: File pattern to include (e.g., "*.py")
            
        Returns:
            List of match dicts with file, line, content, or error dict
        """
        try:
            # For container operations, use path as-is (don't resolve to host paths)
            abs_path = path
            
            # For container operations, use simple grep command with find
            if include:
                # Use find to filter by file pattern, then grep the results
                cmd = f"find '{abs_path}' -name '{include}' -type f -exec grep -Hn '{pattern}' {{}} \\; 2>/dev/null || true"
            else:
                # Search all files
                cmd = f"find '{abs_path}' -type f -exec grep -Hn '{pattern}' {{}} \\; 2>/dev/null || true"
            
            result = await self.run_command(cmd)
            
            if result.success:
                matches = []
                for line in result.stdout.splitlines():
                    if ':' in line:
                        # Parse grep output: filename:line_number:content
                        parts = line.split(':', 2)
                        if len(parts) >= 3:
                            matches.append({
                                "file": parts[0],
                                "line": int(parts[1]) if parts[1].isdigit() else 0,
                                "content": parts[2]
                            })
                return matches
            else:
                return []
            
        except Exception as e:
            return create_error_response(
                f"Search failed: {str(e)}",
                details=str(e)
            )
    
    async def glob_files(self, pattern: str, path: str = ".", case_sensitive: bool = True) -> Union[List[str], Dict]:
        """***ISTOOL***
        File pattern matching with glob syntax.

        TODO
        kindly veiw the doc of gemeni cli apporach and implenent in similar manner 
        glob finds files matching specific glob patterns (e.g., src/**/*.ts, *.md), returning absolute paths sorted by modification time (newest first).

        Tool name: glob
        Display name: FindFiles
        File: glob.ts
        Parameters:
        pattern (string, required): The glob pattern to match against (e.g., "*.py", "src/**/*.js").
        path (string, optional): The absolute path to the directory to search within. If omitted, searches the tool's root directory.
        case_sensitive (boolean, optional): Whether the search should be case-sensitive. Defaults to false.
        respect_git_ignore (boolean, optional): Whether to respect .gitignore patterns when finding files. Defaults to true.
        Behavior:
        Searches for files matching the glob pattern within the specified directory.
        Returns a list of absolute paths, sorted with the most recently modified files first.
        Ignores common nuisance directories like node_modules and .git by default.
        Output (llmContent): A message like: Found 5 file(s) matching "*.ts" within src, sorted by modification time (newest first):\nsrc/file1.ts\nsrc/subdir/file2.ts...
        Confirmation: No.
        
        Args:
            pattern: Glob pattern (e.g., "*.py", "**/*.js")
            path: Directory to search in
            case_sensitive: Whether matching should be case sensitive
            
        Returns:
            List of matching file paths, or error dict
        """
        try:
            # For container operations, use path as-is (don't resolve to host paths)
            abs_path = path
            
            # For container operations, use shell find command with globbing
            if case_sensitive:
                cmd = f"find '{abs_path}' -name '{pattern}' -type f 2>/dev/null || true"
            else:
                cmd = f"find '{abs_path}' -iname '{pattern}' -type f 2>/dev/null || true"
            
            result = await self.run_command(cmd)
            
            if result.success:
                files = [line.strip() for line in result.stdout.splitlines() if line.strip()]
                return files
            else:
                return []
            
        except Exception as e:
            return create_error_response(
                f"Glob search failed: {str(e)}",
                details=str(e)
            )
    
    # === WEB OPERATIONS ===
    
    # TODO FILES FROM Additionals
    # === DEVELOPMENT TOOLS ===

    async def format_code(self, file_path: str, formatter: str = None) -> Union[bool, Dict]:
        """***ISTOOL***
        Format code file using appropriate formatter.
        
        Args:
            file_path: Path to file to format
            formatter: Specific formatter to use (optional)
            
        Returns:
            True if successful, error dict if failed
        """
        try:
            abs_path = file_path
            
            if not await self._file_exists(abs_path):
                return self._create_error_response(
                    FileReadResponse,
                    f"File not found: {abs_path}",
                    suggestions=[
                        "Check if the file path is correct",
                        "Use list_directory() to explore available files",
                        "Use glob_files() to find files matching a pattern"
                    ]
                )
            
            # Determine formatter based on file extension or explicit choice
            ext = get_file_extension(abs_path)
            
            if formatter:
                cmd = f"{formatter} '{abs_path}'"
            elif ext == '.py':
                cmd = f"black '{abs_path}'"
            elif ext in ['.js', '.ts', '.jsx', '.tsx']:
                cmd = f"prettier --write '{abs_path}'"
            elif ext in ['.go']:
                cmd = f"gofmt -w '{abs_path}'"
            elif ext in ['.rs']:
                cmd = f"rustfmt '{abs_path}'"
            elif ext in ['.c', '.cpp', '.h', '.hpp']:
                cmd = f"clang-format -i '{abs_path}'"
            elif ext in ['.java']:
                cmd = f"google-java-format --replace '{abs_path}'"
            else:
                return create_error_response(
                    f"No formatter available for file type: {ext}",
                    suggestions=[
                        "Specify a formatter explicitly",
                        "Install appropriate formatter for the language",
                        f"Supported types: .py, .js, .ts, .go, .rs, .c, .cpp, .java"
                    ]
                )
            
            result = await self.run_command(cmd)
            
            if result.success:
                return True
            else:
                return create_error_response(
                    f"Code formatting failed: {result.stdout}",
                    suggestions=[
                        f"Ensure {cmd.split()[0]} is installed",
                        "Check if the file has syntax errors",
                        "Try with a different formatter"
                    ]
                )
                
        except Exception as e:
            return create_error_response(
                f"Code formatting failed: {str(e)}",
                details=str(e)
            )

    # === PROJECT ANALYSIS ===
    
    async def analyze_project_structure(self, path: str = ".") -> Union[Dict, Dict]:
        """***ISTOOL***
        Analyze project structure and provide summary.

        TDOO kindly recheck the implemenattion
        
        Args:
            path: Project root directory
            
        Returns:
            Dict with project analysis, or error dict
        """
        try:
            abs_path = validate_file_path(path) if path != "." else os.getcwd()
            
            if not Path(abs_path).is_dir():
                return create_error_response(
                    f"Path is not a directory: {path}",
                    suggestions=["Provide a valid directory path"]
                )
            
            analysis = {
                "root_path": abs_path,
                "files_by_type": {},
                "total_files": 0,
                "total_size": 0,
                "languages": {},
                "project_type": "unknown",
                "config_files": [],
                "main_directories": []
            }
            
            # Language extensions mapping
            lang_extensions = {
                'Python': ['.py', '.pyw', '.pyi'],
                'JavaScript': ['.js', '.jsx', '.mjs'],
                'TypeScript': ['.ts', '.tsx'],
                'Go': ['.go'],
                'Rust': ['.rs'],
                'Java': ['.java'],
                'C': ['.c', '.h'],
                'C++': ['.cpp', '.cxx', '.cc', '.hpp', '.hxx'],
                'C#': ['.cs'],
                'PHP': ['.php'],
                'Ruby': ['.rb'],
                'Swift': ['.swift'],
                'Kotlin': ['.kt'],
                'HTML': ['.html', '.htm'],
                'CSS': ['.css', '.scss', '.sass', '.less'],
                'Shell': ['.sh', '.bash', '.zsh'],
                'SQL': ['.sql'],
                'JSON': ['.json'],
                'YAML': ['.yml', '.yaml'],
                'XML': ['.xml'],
                'Markdown': ['.md', '.markdown']
            }
            
            # Analyze files
            for root, dirs, files in os.walk(abs_path):
                # Skip hidden directories and common ignore patterns
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'build', 'dist', 'target']]
                
                for file in files:
                    if file.startswith('.'):
                        continue
                    
                    file_path = os.path.join(root, file)
                    try:
                        stat = Path(file_path).stat()
                        ext = get_file_extension(file).lower()
                        
                        # Count by extension
                        if ext not in analysis["files_by_type"]:
                            analysis["files_by_type"][ext] = 0
                        analysis["files_by_type"][ext] += 1
                        
                        # Count by language
                        for lang, extensions in lang_extensions.items():
                            if ext in extensions:
                                if lang not in analysis["languages"]:
                                    analysis["languages"][lang] = 0
                                analysis["languages"][lang] += 1
                                break
                        
                        analysis["total_files"] += 1
                        analysis["total_size"] += stat.st_size
                        
                    except (OSError, PermissionError):
                        continue
            
            # Detect project type
            config_patterns = {
                'Python': ['requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile', 'poetry.lock'],
                'Node.js': ['package.json', 'yarn.lock', 'package-lock.json'],
                'Go': ['go.mod', 'go.sum'],
                'Rust': ['Cargo.toml', 'Cargo.lock'],
                'Java': ['pom.xml', 'build.gradle', 'gradle.properties'],
                'C#': ['*.csproj', '*.sln'],
                'PHP': ['composer.json', 'composer.lock'],
                'Ruby': ['Gemfile', 'Gemfile.lock'],
                'Docker': ['Dockerfile', 'docker-compose.yml']
            }
            
            for project_type, patterns in config_patterns.items():
                for pattern in patterns:
                    if list(Path(abs_path).glob(pattern)):
                        analysis["project_type"] = project_type
                        analysis["config_files"].extend([str(f) for f in Path(abs_path).glob(pattern)])
                        break
                if analysis["project_type"] != "unknown":
                    break
            
            # Common directories
            common_dirs = ['src', 'lib', 'tests', 'test', 'docs', 'examples', 'scripts', 'bin', 'config']
            for dir_name in common_dirs:
                dir_path = Path(abs_path) / dir_name
                if dir_path.is_dir():
                    analysis["main_directories"].append(dir_name)
            
            # Format total size
            analysis["total_size_formatted"] = format_file_size(analysis["total_size"])
            
            return analysis
            
        except Exception as e:
            return create_error_response(
                f"Project analysis failed: {str(e)}",
                details=str(e)
            )
    
    async def get_file_dependencies(self, file_path: str) -> Union[List[str], Dict]:
        """***ISTOOL***
        Get dependencies/imports for a file.

        TODO Kindly recheck the implemenattions 
        
        Args:
            file_path: Path to file to analyze
            
        Returns:
            List of dependency/import statements, or error dict
        """
        try:
            abs_path = validate_file_path(file_path)
            
            if not Path(abs_path).exists():
                return create_error_response(
                    f"File not found: {file_path}",
                    suggestions=["Check if the file exists"]
                )
            
            content = await self.read_file(abs_path)
            if isinstance(content, dict):  # Error response
                return content
            
            ext = get_file_extension(abs_path)
            dependencies = []
            
            lines = content.splitlines()
            
            if ext == '.py':
                # Python imports
                for line in lines:
                    line = line.strip()
                    if line.startswith('import ') or line.startswith('from '):
                        dependencies.append(line)
            
            elif ext in ['.js', '.ts', '.jsx', '.tsx']:
                # JavaScript/TypeScript imports
                for line in lines:
                    line = line.strip()
                    if line.startswith('import ') or line.startswith('const ') and 'require(' in line:
                        dependencies.append(line)
            
            elif ext == '.go':
                # Go imports
                in_import_block = False
                for line in lines:
                    line = line.strip()
                    if line.startswith('import ('):
                        in_import_block = True
                        dependencies.append(line)
                    elif in_import_block:
                        if line == ')':
                            dependencies.append(line)
                            in_import_block = False
                        else:
                            dependencies.append(line)
                    elif line.startswith('import '):
                        dependencies.append(line)
            
            elif ext == '.rs':
                # Rust uses
                for line in lines:
                    line = line.strip()
                    if line.startswith('use ') or line.startswith('extern crate '):
                        dependencies.append(line)
            
            elif ext == '.java':
                # Java imports
                for line in lines:
                    line = line.strip()
                    if line.startswith('import '):
                        dependencies.append(line)
            
            return dependencies
            
        except Exception as e:
            return create_error_response(
                f"Dependency analysis failed: {str(e)}",
                details=str(e)
            )
    
    async def find_references(self, symbol: str, file_types: List[str] = None) -> Union[List[Dict], Dict]:
        """***ISTOOL***
        Find symbol references in project.

        TODO : KINDLY RECHECK THE IMPLEMENTATION AS I HAVE REMOVED THE GREP METHOD 
        
        Args:
            symbol: Symbol name to find references for
            file_types: File extensions to search in (e.g., ['.py', '.js'])
            
        Returns:
            List of reference locations, or error dict
        """
        try:
            if not symbol or not symbol.strip():
                return create_error_response(
                    "Symbol name cannot be empty",
                    suggestions=["Provide a symbol name to search for"]
                )
            
            # Simple word boundary search for references
            pattern = f"\\b{symbol}\\b"
            
            include_pattern = None
            if file_types:
                if len(file_types) == 1:
                    include_pattern = f"*{file_types[0]}"
                # For multiple types, search all and filter later
            
            matches = await self.grep_files(pattern, include=include_pattern)
            if isinstance(matches, dict):  # Error response
                return matches
            
            results = []
            for match in matches:
                # Filter by file type if specified
                if file_types:
                    file_ext = get_file_extension(match["file"])
                    if file_ext not in file_types:
                        continue
                
                results.append({
                    "symbol": symbol,
                    "file": match["file"],
                    "line": match["line"],
                    "content": match["content"]
                })
            
            return sorted(results, key=lambda x: (x["file"], x["line"]))
            
        except Exception as e:
            return create_error_response(
                f"Reference search failed: {str(e)}",
                details=str(e)
            )
        
