
    # === GIT OPERATIONS ===
    
    # async def git_status(self) -> Union[str, Dict]:
    #     """
    #     Get git status.
        
    #     Returns:
    #         Git status output as string, or error dict
    #     """
    #     try:
    #         result = await self.run_command("git status --porcelain")
            
    #         if result["success"]:
    #             return result["stdout"]
    #         else:
    #             return create_error_response(
    #                 f"Git status failed: {result.get('stderr', 'Unknown error')}",
    #                 suggestions=["Ensure you're in a git repository", "Check if git is installed"]
    #             )
                
    #     except Exception as e:
    #         return create_error_response(
    #             f"Git status failed: {str(e)}",
    #             details=str(e)
    #         )
    
    # async def git_add(self, files: List[str]) -> Union[bool, Dict]:
    #     """
    #     Add files to git staging area.
        
    #     Args:
    #         files: List of file paths to add
            
    #     Returns:
    #         True if successful, error dict if failed
    #     """
    #     try:
    #         if not files:
    #             return create_error_response(
    #                 "No files specified to add",
    #                 suggestions=["Provide a list of files to add to git"]
    #             )
            
    #         # Quote filenames to handle spaces and special characters
    #         quoted_files = [f"'{f}'" for f in files]
    #         file_list = " ".join(quoted_files)
            
    #         result = await self.run_command(f"git add {file_list}")
            
    #         if result["success"]:
    #             return True
    #         else:
    #             return create_error_response(
    #                 f"Git add failed: {result.get('stderr', 'Unknown error')}",
    #                 suggestions=["Check if files exist", "Ensure you're in a git repository"]
    #             )
                
    #     except Exception as e:
    #         return create_error_response(
    #             f"Git add failed: {str(e)}",
    #             details=str(e)
    #         )
    
    # async def git_commit(self, message: str) -> Union[bool, Dict]:
    #     """
    #     Commit staged changes with message.
        
    #     Args:
    #         message: Commit message
            
    #     Returns:
    #         True if successful, error dict if failed
    #     """
    #     try:
    #         if not message or not message.strip():
    #             return create_error_response(
    #                 "Commit message cannot be empty",
    #                 suggestions=["Provide a descriptive commit message"]
    #             )
            
    #         # Escape the commit message properly
    #         escaped_message = message.replace("'", "'\"'\"'")
    #         result = await self.run_command(f"git commit -m '{escaped_message}'")
            
    #         if result["success"]:
    #             return True
    #         else:
    #             # Check for common issues
    #             if "nothing to commit" in result["stdout"].lower():
    #                 return create_error_response(
    #                     "Nothing to commit - no staged changes",
    #                     suggestions=["Use git_add() to stage files first", "Check git_status() for changes"]
    #                 )
    #             else:
    #                 return create_error_response(
    #                     f"Git commit failed: {result.get('stderr', 'Unknown error')}",
    #                     suggestions=["Ensure files are staged with git_add()", "Check git status"]
    #                 )
                
    #     except Exception as e:
    #         return create_error_response(
    #             f"Git commit failed: {str(e)}",
    #             details=str(e)
    #         )
    
    # async def git_diff(self, files: List[str] = None) -> Union[str, Dict]:
    #     """
    #     Show git diff for specified files or all changes.
        
    #     Args:
    #         files: Optional list of files to show diff for
            
    #     Returns:
    #         Diff output as string, or error dict
    #     """
    #     try:
    #         if files:
    #             quoted_files = [f"'{f}'" for f in files]
    #             file_list = " ".join(quoted_files)
    #             cmd = f"git diff {file_list}"
    #         else:
    #             cmd = "git diff"
            
    #         result = await self.run_command(cmd)
            
    #         if result["success"]:
    #             return result["stdout"]
    #         else:
    #             return create_error_response(
    #                 f"Git diff failed: {result.get('stderr', 'Unknown error')}",
    #                 suggestions=["Ensure you're in a git repository", "Check if files exist"]
    #             )
                
    #     except Exception as e:
    #         return create_error_response(
    #             f"Git diff failed: {str(e)}",
    #             details=str(e)
    #         )
    
    # async def git_log(self, limit: int = 10) -> Union[str, Dict]:
    #     """
    #     Show git commit history.
        
    #     Args:
    #         limit: Maximum number of commits to show
            
    #     Returns:
    #         Log output as string, or error dict
    #     """
    #     try:
    #         result = await self.run_command(f"git log --oneline -{limit}")
            
    #         if result["success"]:
    #             return result["stdout"]
    #         else:
    #             return create_error_response(
    #                 f"Git log failed: {result.get('stderr', 'Unknown error')}",
    #                 suggestions=["Ensure you're in a git repository with commits"]
    #             )
                
    #     except Exception as e:
    #         return create_error_response(
    #             f"Git log failed: {str(e)}",
    #             details=str(e)
    #         )
    
    # async def git_branch(self) -> Union[str, Dict]:
    #     """
    #     Show current branch and list all branches.
        
    #     Returns:
    #         Branch output as string, or error dict
    #     """
    #     try:
    #         result = await self.run_command("git branch")
            
    #         if result["success"]:
    #             return result["stdout"]
    #         else:
    #             return create_error_response(
    #                 f"Git branch failed: {result.get('stderr', 'Unknown error')}",
    #                 suggestions=["Ensure you're in a git repository"]
    #             )
                
    #     except Exception as e:
    #         return create_error_response(
    #             f"Git branch failed: {str(e)}",
    #             details=str(e)
    #         )
    
    # async def git_checkout(self, branch: str) -> Union[bool, Dict]:
    #     """
    #     Checkout a git branch.
        
    #     Args:
    #         branch: Branch name to checkout
            
    #     Returns:
    #         True if successful, error dict if failed
    #     """
    #     try:
    #         if not branch or not branch.strip():
    #             return create_error_response(
    #                 "Branch name cannot be empty",
    #                 suggestions=["Provide a valid branch name"]
    #             )
            
    #         result = await self.run_command(f"git checkout '{branch}'")
            
    #         if result["success"]:
    #             return True
    #         else:
    #             return create_error_response(
    #                 f"Git checkout failed: {result.get('stderr', 'Unknown error')}",
    #                 suggestions=[
    #                     "Check if branch exists with git_branch()",
    #                     "Ensure working directory is clean",
    #                     "Use 'git checkout -b <branch>' to create new branch"
    #                 ]
    #             )
                
    #     except Exception as e:
    #         return create_error_response(
    #             f"Git checkout failed: {str(e)}",
    #             details=str(e)
    #         )
    

    # todo , make generlist ,too explicit
    # async def run_tests(self, test_pattern: str = None, directory: str = None) -> Dict:
    #     """
    #     Run tests with pattern matching (Aider pattern).
        
    #     Args:
    #         test_pattern: Test file/directory pattern (e.g., "tests/", "test_*.py")
    #         directory: Directory to run tests from
            
    #     Returns:
    #         Dict with test results, success status, and output
    #     """
    #     try:
    #         # Determine test command based on project structure
    #         test_commands = [
    #             "python -m pytest",  # pytest
    #             "python -m unittest discover",  # unittest
    #             "npm test",  # Node.js
    #             "go test ./...",  # Go
    #             "cargo test",  # Rust
    #             "mvn test",  # Maven
    #             "gradle test",  # Gradle
    #         ]
            
    #         # If pattern specified, use pytest with pattern
    #         if test_pattern:
    #             cmd = f"python -m pytest {test_pattern} -v"
    #         else:
    #             # Try to detect which test runner to use
    #             current_dir = directory or os.getcwd()
                
    #             if Path(current_dir).glob("**/pytest.ini") or Path(current_dir).glob("**/test_*.py"):
    #                 cmd = "python -m pytest -v"
    #             elif Path(current_dir).glob("**/package.json"):
    #                 cmd = "npm test"
    #             elif Path(current_dir).glob("**/go.mod"):
    #                 cmd = "go test ./..."
    #             elif Path(current_dir).glob("**/Cargo.toml"):
    #                 cmd = "cargo test"
    #             elif Path(current_dir).glob("**/pom.xml"):
    #                 cmd = "mvn test"
    #             elif Path(current_dir).glob("**/build.gradle"):
    #                 cmd = "gradle test"
    #             else:
    #                 cmd = "python -m pytest -v"  # Default to pytest
            
    #         result = await self.run_command(cmd, directory=directory)
            
    #         # Parse test results
    #         success = result["success"]
    #         output = result["stdout"] + "\n" + result["stderr"]
            
    #         # Try to extract test statistics
    #         test_stats = self._parse_test_output(output, cmd)
            
    #         return {
    #             "success": success,
    #             "passed": success,
    #             "output": output,
    #             "command": cmd,
    #             "stats": test_stats,
    #             "exit_code": result["exit_code"]
    #         }           
    #     except Exception as e:
    #         return create_error_response(
    #             f"Test execution failed: {str(e)}",
    #             details=str(e)
    #         )



    # todo extract files
    # async def compress_files(self, files: List[str], output_path: str) -> Union[bool, Dict]:
    #     """
    #     Compress files into archive.
        
    #     Args:
    #         files: List of file paths to compress
    #         output_path: Output archive path
            
    #     Returns:
    #         True if successful, error dict if failed
    #     """
    #     try:
    #         if not files:
    #             return create_error_response(
    #                 "No files specified to compress",
    #                 suggestions=["Provide a list of files to compress"]
    #             )
            
    #         if not output_path:
    #             return create_error_response(
    #                 "Output path cannot be empty",
    #                 suggestions=["Provide an output archive path"]
    #             )
            
    #         # Determine compression method based on output extension
    #         ext = get_file_extension(output_path).lower()
            
    #         # Validate files exist
    #         quoted_files = []
    #         for file_path in files:
    #             abs_path = validate_file_path(file_path)
    #             if not Path(abs_path).exists():
    #                 return create_error_response(
    #                     f"File not found: {file_path}",
    #                     suggestions=["Check if all files exist before compressing"]
    #                 )
    #             quoted_files.append(f"'{abs_path}'")
            
    #         file_list = " ".join(quoted_files)
            
    #         if ext in ['.zip']:
    #             cmd = f"zip -r '{output_path}' {file_list}"
    #         elif ext in ['.tar.gz', '.tgz']:
    #             cmd = f"tar -czf '{output_path}' {file_list}"
    #         elif ext in ['.tar']:
    #             cmd = f"tar -cf '{output_path}' {file_list}"
    #         elif ext in ['.tar.bz2', '.tbz2']:
    #             cmd = f"tar -cjf '{output_path}' {file_list}"
    #         else:
    #             return create_error_response(
    #                 f"Unsupported archive format: {ext}",
    #                 suggestions=["Use .zip, .tar.gz, .tar, or .tar.bz2 format"]
    #             )
            
    #         result = await self.run_command(cmd)
            
    #         if result["success"]:
    #             return True
    #         else:
    #             return create_error_response(
    #                 f"Compression failed: {result.get('stderr', 'Unknown error')}",
    #                 suggestions=[
    #                     "Check if compression tool is installed",
    #                     "Ensure sufficient disk space",
    #                     "Verify file permissions"
    #                 ]
    #             )
                
    #     except Exception as e:
    #         return create_error_response(
    #             f"Compression failed: {str(e)}",
    #             details=str(e)
    #         )
    
    # async def extract_archive(self, archive_path: str, destination: str = ".") -> Union[bool, Dict]:
    #     """
    #     Extract archive to destination directory.
        
    #     Args:
    #         archive_path: Path to archive file
    #         destination: Destination directory (default: current directory)
            
    #     Returns:
    #         True if successful, error dict if failed
    #     """
    #     try:
    #         abs_archive = validate_file_path(archive_path)
    #         abs_dest = validate_file_path(destination)
            
    #         if not Path(abs_archive).exists():
    #             return create_error_response(
    #                 f"Archive not found: {archive_path}",
    #                 suggestions=["Check if the archive file exists"]
    #             )
            
    #         if not Path(abs_dest).is_dir():
    #             # Create destination directory
    #             Path(abs_dest).mkdir(parents=True, exist_ok=True)
            
    #         # Determine extraction method based on archive extension
    #         ext = get_file_extension(abs_archive).lower()
            
    #         if ext in ['.zip']:
    #             cmd = f"unzip '{abs_archive}' -d '{abs_dest}'"
    #         elif ext in ['.tar.gz', '.tgz']:
    #             cmd = f"tar -xzf '{abs_archive}' -C '{abs_dest}'"
    #         elif ext in ['.tar']:
    #             cmd = f"tar -xf '{abs_archive}' -C '{abs_dest}'"
    #         elif ext in ['.tar.bz2', '.tbz2']:
    #             cmd = f"tar -xjf '{abs_archive}' -C '{abs_dest}'"
    #         else:
    #             return create_error_response(
    #                 f"Unsupported archive format: {ext}",
    #                 suggestions=["Supported formats: .zip, .tar.gz, .tar, .tar.bz2"]
    #             )
            
    #         result = await self.run_command(cmd)
            
    #         if result["success"]:
    #             return True
    #         else:
    #             return create_error_response(
    #                 f"Extraction failed: {result.get('stderr', 'Unknown error')}",
    #                 suggestions=[
    #                     "Check if extraction tool is installed",
    #                     "Ensure sufficient disk space",
    #                     "Verify archive is not corrupted"
    #                 ]
    #             )
                
    #     except Exception as e:
    #         return create_error_response(
    #             f"Extraction failed: {str(e)}",
    #             details=str(e)
    #         )
    
    # === SESSION MANAGEMENT ===
    # todo add adding files to env and tesing etc
    # async def add_files_to_session(self, file_patterns: List[str]) -> Union[List[str], Dict]:
    #     """
    #     Add files to current session (Aider pattern).
        
    #     Args:
    #         file_patterns: List of file paths or glob patterns
            
    #     Returns:
    #         List of added file paths, or error dict
    #     """
    #     try:
    #         if not file_patterns:
    #             return create_error_response(
    #                 "No file patterns specified",
    #                 suggestions=["Provide file paths or glob patterns to add"]
    #             )
            
    #         added_files = []
            
    #         for pattern in file_patterns:
    #             if '*' in pattern or '?' in pattern or '[' in pattern:
    #                 # Handle glob pattern
    #                 matches = await self.glob_files(pattern)
    #                 if isinstance(matches, dict):  # Error response
    #                     return matches
    #                 added_files.extend(matches)
    #             else:
    #                 # Handle regular file path
    #                 try:
    #                     abs_path = validate_file_path(pattern)
    #                     if Path(abs_path).exists() and Path(abs_path).is_file():
    #                         added_files.append(abs_path)
    #                     else:
    #                         return create_error_response(
    #                             f"File not found: {pattern}",
    #                             suggestions=["Check if the file exists", "Use glob patterns for multiple files"]
    #                         )
    #                 except ValueError as e:
    #                     return create_error_response(
    #                         f"Invalid file path: {pattern}",
    #                         details=str(e)
    #                     )
            
    #         # Add to session files set
    #         self._session_files.update(added_files)
            
    #         return sorted(list(added_files))
            
    #     except Exception as e:
    #         return create_error_response(
    #             f"Failed to add files to session: {str(e)}",
    #             details=str(e)
    #         )
    
    # async def remove_files_from_session(self, file_patterns: List[str]) -> Union[List[str], Dict]:
    #     """
    #     Remove files from current session.
        
    #     Args:
    #         file_patterns: List of file paths or patterns to remove
            
    #     Returns:
    #         List of removed file paths, or error dict
    #     """
    #     try:
    #         if not file_patterns:
    #             return create_error_response(
    #                 "No file patterns specified",
    #                 suggestions=["Provide file paths or patterns to remove"]
    #             )
            
    #         removed_files = []
            
    #         for pattern in file_patterns:
    #             if '*' in pattern or '?' in pattern or '[' in pattern:
    #                 # Handle glob pattern - find matching files in session
    #                 import fnmatch
    #                 matching_files = [f for f in self._session_files if fnmatch.fnmatch(f, pattern)]
    #                 removed_files.extend(matching_files)
    #             else:
    #                 # Handle regular file path
    #                 try:
    #                     abs_path = validate_file_path(pattern)
    #                     if abs_path in self._session_files:
    #                         removed_files.append(abs_path)
    #                 except ValueError:
    #                     # Invalid path, ignore
    #                     pass
            
    #         # Remove from session files set
    #         for file_path in removed_files:
    #             self._session_files.discard(file_path)
            
    #         return sorted(list(removed_files))
            
    #     except Exception as e:
    #         return create_error_response(
    #             f"Failed to remove files from session: {str(e)}",
    #             details=str(e)
    #         )
    
    # async def list_session_files(self) -> List[str]:
    #     """
    #     List all files in current session.
        
    #     Returns:
    #         List of file paths in session
    #     """
    #     return sorted(list(self._session_files))
    
    # async def clear_all_sessions(self) -> bool:
    #     """
    #     Clear all files from session and close all bash sessions using SWE Rex native functionality.
        
    #     Returns:
    #         True if successful
    #     """
    #     try:
    #         # Clear session files
    #         self._session_files.clear()
            
    #         # Close all active bash sessions
    #         for session_name in list(self.sessions.keys()):
    #             if self.sessions[session_name]:  # Only close active sessions
    #                 await self.close_bash_session(session_name)
            
    #         return True
            
    #     except Exception:
    #         # Even if something fails, we can still clear our internal state
    #         self._session_files.clear()
    #         self.sessions.clear()
    #         return True


# === DEPRECATED METHODS (Removed from core.py) ===

"""
The following methods were removed from CodeToolsInstance as they were marked 
as unnecessary in the TODO comments:

1. grep_files() - Line 690: "REMOVE THIS AND APPEND THIS METHOD TO additional_todo.py file and mark it as unnecessary"
2. find_files() - Line 795: "REMOVE THIS AND APPEND THIS METHOD TO additional_todo.py file and mark it as unnecessary"
3. copy_to_clipboard() - Line 1011: "REMOVE THIS AND APPEND THIS METHOD TO additional_todo.py file and mark it as unnecessary"
4. paste_from_clipboard() - Line 1062: "REMOVE THIS AND APPEND THIS METHOD TO additional_todo.py file and mark it as unnecessary"
5. find_definitions() - Line 1315: "REMOVE THIS AND APPEND THIS METHOD TO additional_todo.py file"

These methods have been preserved here for reference but are not part of the main
tool interface anymore. Alternative approaches:

- For searching: Use proper search tools or bash commands in sessions
- For clipboard operations: Use bash commands like xclip, pbcopy, etc.
- For code analysis: Use language-specific tools through bash sessions
"""

# async def grep_files_deprecated(self, pattern: str, path: str = ".", include: str = None):
#     """Multi-strategy search - DEPRECATED"""
#     # Implementation removed - use bash grep commands instead
#     pass

# async def find_files_deprecated(self, name_pattern: str = None, path: str = "."):
#     """Find files by name pattern - DEPRECATED"""
#     # Implementation removed - use bash find command instead
#     pass

# async def copy_to_clipboard_deprecated(self, content: str):
#     """Copy content to system clipboard - DEPRECATED"""
#     # Implementation removed - use bash clipboard commands instead
#     pass

# async def paste_from_clipboard_deprecated(self):
#     """Paste content from system clipboard - DEPRECATED"""
#     # Implementation removed - use bash clipboard commands instead
#     pass

# async def find_definitions_deprecated(self, symbol: str, file_types = None):
#     """Find symbol definitions in project - DEPRECATED"""
#     # Implementation removed - use language-specific tools instead
#     pass

# async def find_definitions(self, symbol: str, file_types: List[str] = None) -> Union[List[Dict], Dict]:
#         """
#         Find symbol definitions in project.

        
#         TODO REMOVE THIS AND APPEND THIS METHOD TO additional_todo.py  file 
        
#         Args:
#             symbol: Symbol name to find definitions for
#             file_types: File extensions to search in (e.g., ['.py', '.js'])
            
#         Returns:
#             List of definition locations, or error dict
#         """
#         try:
#             if not symbol or not symbol.strip():
#                 return create_error_response(
#                     "Symbol name cannot be empty",
#                     suggestions=["Provide a symbol name to search for"]
#                 )
            
#             # Build search patterns for different languages
#             patterns = []
            
#             if not file_types or '.py' in file_types:
#                 patterns.extend([
#                     f"def {symbol}\\(",  # Python function
#                     f"class {symbol}\\(",  # Python class
#                     f"class {symbol}:",   # Python class without params
#                     f"{symbol} = "        # Python variable assignment
#                 ])
            
#             if not file_types or any(ext in file_types for ext in ['.js', '.ts', '.jsx', '.tsx']):
#                 patterns.extend([
#                     f"function {symbol}\\(",  # JavaScript function
#                     f"const {symbol} = ",     # JavaScript const
#                     f"let {symbol} = ",       # JavaScript let
#                     f"var {symbol} = ",       # JavaScript var
#                     f"class {symbol} ",       # JavaScript class
#                 ])
            
#             if not file_types or '.go' in file_types:
#                 patterns.extend([
#                     f"func {symbol}\\(",      # Go function
#                     f"type {symbol} ",        # Go type
#                     f"var {symbol} ",         # Go variable
#                     f"const {symbol} ",       # Go constant
#                 ])
            
#             if not file_types or '.rs' in file_types:
#                 patterns.extend([
#                     f"fn {symbol}\\(",        # Rust function
#                     f"struct {symbol} ",      # Rust struct
#                     f"enum {symbol} ",        # Rust enum
#                     f"let {symbol} = ",       # Rust variable
#                 ])
            
#             results = []
            
#             # Search for each pattern
#             for pattern in patterns:
#                 include_pattern = None
#                 if file_types:
#                     # Convert extensions to glob pattern
#                     if len(file_types) == 1:
#                         include_pattern = f"*{file_types[0]}"
#                     else:
#                         # For multiple types, we'll search all and filter later
#                         pass
                
#                 matches = await self.grep_files(pattern, include=include_pattern)
#                 if isinstance(matches, dict):  # Error response
#                     continue
                
#                 for match in matches:
#                     # Filter by file type if specified
#                     if file_types:
#                         file_ext = get_file_extension(match["file"])
#                         if file_ext not in file_types:
#                             continue
                    
#                     results.append({
#                         "symbol": symbol,
#                         "file": match["file"],
#                         "line": match["line"],
#                         "content": match["content"],
#                         "pattern": pattern
#                     })
            
#             # Remove duplicates and sort
#             unique_results = []
#             seen = set()
#             for result in results:
#                 key = (result["file"], result["line"])
#                 if key not in seen:
#                     seen.add(key)
#                     unique_results.append(result)
            
#             return sorted(unique_results, key=lambda x: (x["file"], x["line"]))
            
#         except Exception as e:
#             return create_error_response(
#                 f"Definition search failed: {str(e)}",
#                 details=str(e)
#             )
    

    # === UTILITY OPERATIONS ===
    
    # async def copy_to_clipboard(self, content: str) -> Union[bool, Dict]:
    #     """
    #     Copy content to system clipboard.

        
    #     TODO REMOVE THIS AND APPEND THIS METHOD TO additional_todo.py  file and mark it as unnecessary 
        
    #     Args:
    #         content: Content to copy to clipboard
            
    #     Returns:
    #         True if successful, error dict if failed
    #     """
    #     try:
    #         if not content:
    #             return create_error_response(
    #                 "Content to copy cannot be empty",
    #                 suggestions=["Provide content to copy to clipboard"]
    #             )
            
    #         # Try different clipboard commands based on platform
    #         commands = [
    #             "pbcopy",  # macOS
    #             "xclip -selection clipboard",  # Linux
    #             "clip",  # Windows
    #         ]
            
    #         for cmd in commands:
    #             # Test if command exists
    #             test_result = await self.run_command(f"which {cmd.split()[0]} 2>/dev/null || command -v {cmd.split()[0]}")
    #             if test_result["success"]:
    #                 # Use echo to pipe content to clipboard command
    #                 result = await self.run_command(f"echo '{content}' | {cmd}")
    #                 if result["success"]:
    #                     return True
            
    #         return create_error_response(
    #             "No clipboard command available",
    #             suggestions=[
    #                 "Install xclip on Linux",
    #                 "Ensure pbcopy is available on macOS",
    #                 "Ensure clip is available on Windows"
    #             ]
    #         )
            
    #     except Exception as e:
    #         return create_error_response(
    #             f"Clipboard copy failed: {str(e)}",
    #             details=str(e)
    #         )
    
    # async def paste_from_clipboard(self) -> Union[str, Dict]:
    #     """
    #     Paste content from system clipboard.

        
    #     TODO REMOVE THIS AND APPEND THIS METHOD TO additional_todo.py  file and mark it as unnecessary 
        
    #     Returns:
    #         Clipboard content as string, or error dict
    #     """
    #     try:
    #         # Try different clipboard commands based on platform
    #         commands = [
    #             "pbpaste",  # macOS
    #             "xclip -selection clipboard -o",  # Linux
    #             # Windows doesn't have a direct equivalent, would need PowerShell
    #         ]
            
    #         for cmd in commands:
    #             result = await self.run_command(cmd)
    #             if result["success"]:
    #                 return result["stdout"]
            
    #         return create_error_response(
    #             "No clipboard paste command available",
    #             suggestions=[
    #                 "Install xclip on Linux",
    #                 "Ensure pbpaste is available on macOS"
    #             ]
    #         )
            
    #     except Exception as e:
    #         return create_error_response(
    #             f"Clipboard paste failed: {str(e)}",
    #             details=str(e)
    #         )

    #     async def web_fetch(self, url: str) -> Union[str, Dict]:
    #     """
    #     Fetch content from URL (similar to Gemini CLI).
        
    #     Args:
    #         url: URL to fetch content from
            
    #     Returns:
    #         Web content as string, or error dict
    #     """
    #     try:
    #         if not url or not url.strip():
    #             return create_error_response(
    #                 "URL cannot be empty",
    #                 suggestions=["Provide a valid URL to fetch"]
    #             )
            
    #         # Use curl to fetch content (available on most systems)
    #         result = await self.run_command(f"curl -s '{url}'")
            
    #         if result["success"]:
    #             return result["stdout"]
    #         else:
    #             return create_error_response(
    #                 f"Failed to fetch URL: {result.get('stderr', 'Unknown error')}",
    #                 suggestions=[
    #                     "Check if the URL is correct and accessible",
    #                     "Ensure internet connection is available",
    #                     "Try with a different URL"
    #                 ]
    #             )
                
    #     except Exception as e:
    #         return create_error_response(
    #             f"Web fetch failed: {str(e)}",
    #             details=str(e)
    #         )
    
    # async def web_search(self, query: str, num_results: int = 5) -> Union[List[Dict], Dict]:
    #     """
    #     Perform web search (basic implementation using DuckDuckGo).
        
    #     Args:
    #         query: Search query
    #         num_results: Number of results to return
            
    #     Returns:
    #         List of search result dicts, or error dict
    #     """
    #     try:
    #         if not query or not query.strip():
    #             return create_error_response(
    #                 "Search query cannot be empty",
    #                 suggestions=["Provide a valid search query"]
    #             )
            
    #         # Simple web search using DuckDuckGo instant answers API
    #         encoded_query = urllib.parse.quote(query)
    #         api_url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json&no_html=1&skip_disambig=1"
            
    #         content = await self.web_fetch(api_url)
    #         if isinstance(content, dict):  # Error response
    #             return content
            
    #         try:
    #             import json
    #             data = json.loads(content)
                
    #             results = []
                
    #             # Add instant answer if available
    #             if data.get("Abstract"):
    #                 results.append({
    #                     "title": data.get("Heading", "Instant Answer"),
    #                     "snippet": data.get("Abstract"),
    #                     "url": data.get("AbstractURL", ""),
    #                     "type": "instant_answer"
    #                 })
                
    #             # Add related topics
    #             for topic in data.get("RelatedTopics", [])[:num_results-len(results)]:
    #                 if isinstance(topic, dict) and topic.get("Text"):
    #                     results.append({
    #                         "title": topic.get("FirstURL", "").split("/")[-1].replace("_", " "),
    #                         "snippet": topic.get("Text"),
    #                         "url": topic.get("FirstURL", ""),
    #                         "type": "related_topic"
    #                     })
                
    #             return results[:num_results]
                
    #         except json.JSONDecodeError:
    #             return create_error_response(
    #                 "Failed to parse search results",
    #                 suggestions=["Try a different search query", "Check internet connection"]
    #             )
                
    #     except Exception as e:
    #         return create_error_response(
    #             f"Web search failed: {str(e)}",
    #             details=str(e)
    #         )
    

        # async def find_files(self, name_pattern: str = None, path: str = ".") -> Union[List[str], Dict]:
        # """
        # Find files by name pattern.

        # TODO Unnecessary as GLOB is already present

        # Args:
        #     name_pattern: File name pattern (e.g., "test_*.py")
        #     path: Directory to search in
            
        # Returns:
        #     List of matching file paths, or error dict
        # """
        # try:
        #     # For container operations, use path as-is (don't resolve to host paths)
        #     abs_path = path
            
        #     if name_pattern:
        #         cmd = f"find '{abs_path}' -name '{name_pattern}' -type f"
        #     else:
        #         cmd = f"find '{abs_path}' -type f"
            
        #     result = await self.run_command(cmd)
            
        #     if result.success:
        #         files = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        #         return sorted(files)
        #     else:
        #         return create_error_response(
        #             f"Find command failed: {result.stderr}",
        #             details=result.stderr
        #         )
                
        # except Exception as e:
        #     return create_error_response(
        #         f"Find files failed: {str(e)}",
        #         details=str(e)
        #     )
    





# ====================================================
# DOC

# =====================================================
    
# find_files="""
# [Deprecated] Find files by filename pattern.

# Use `glob_files()` instead. This is a basic wrapper around `find -name`.

# Usage:
#     await find_files(name_pattern="test_*.py", path="src")

# Args:
#     name_pattern (str): Pattern to match filenames (e.g., "*.json").
#     path (str): Directory to search from.

# Returns:
#     List[str]: List of matching file paths.

# Limitations:
#     - No filtering by modification time
#     - No `.gitignore` or directory filtering

# Suggestions:
#     - Prefer `glob_files()` for modern workflows.
# """
