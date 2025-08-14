tool_dict = {
"read_file" : """
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
""",

"write_file" : """
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
""",

"edit_file" : """
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
""",

"list_directory" : """
Lists files and directories in a path with metadata.

Supports ignore patterns (regex) for filtering out noisy entries such as `.git`
or `node_modules`.

Usage:
    await list_directory(".", ignore=["__pycache__"])

Args:
    path (str): Path to the directory to list.
    ignore (List[str]): Regex patterns to ignore (e.g., r"\\.git", r"__pycache__").

Returns:
    List[Dict]:
        - name, path, type ("file"/"directory"), size, is_text, etc.

Possible Failures:
    - Invalid or inaccessible directory path
    - Permission issues

Suggestions:
    - Use `glob_files()` to match specific file types.
    - Double-check directory path if result is empty.
""",

"create_bash_session" : """
Creates a named persistent bash session.

Sessions preserve environment, working directory, and state across commands.
Use when chaining multiple operations or running interactive shells.

Usage:
    await create_bash_session("dev-shell")

Args:
    session_name (Optional[str]): Name for the session. Defaults to config.

Returns:
    ToolResponse with session creation status.

Possible Failures:
    - Session already exists

Suggestions:
    - Use `get_bash_sessions()` to list existing ones.
    - Use `close_bash_session()` to close stale sessions.
""",

"run_command" : """
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
        - Processes exceeding the timeout will be killed.
        - A non-zero exit code will be treated as a failure — as it should be.

    Suggestions:
        • If you're stuck with just this function: favor simple, deterministic commands. For anything resembling a build, CI setup, or anything with a progress bar, use `nohup`, backgrounding (`&`), and log redirection (`> file.log 2>&1`) to work around limitations.
        • If you happen to have access to more capable tools (persistent sessions, file readers, interactive shells, etc.), you might want to use those instead for multi-step workflows or anything stateful.

    Use wisely. Or at least pragmatically.
""",

"run_bash_session" : """
Runs a command in a persistent interactive bash session.

Use this for programs that require input/output interactivity,
environment continuity, or multi-step workflows.

Suggestion : 
Interactive commands (use interactiev=False more often): Avoid commands that require interactive user input, as this can cause the tool to hang. Use non-interactive flags if available (e.g., npm init -y).

Usage:
    await run_bash_session("python3", session_name="py-dev", interactive=True)

Args:
    command (str): Command to run.
    session_name (Optional[str]): Session name. Defaults to config.
    timeout (Optional[float]): Max run time in seconds.
    interrupt (bool): Interrupt session instead of running command.
    interactive (Optional[bool]): Force interactive mode. checks using possible interactive expects using pyexpect.

Returns:
    CommandResponse:
        - stdout, stderr, session_name, is_interactive, expect_string

Possible Failures:
    - Session creation failed
    - Unexpected command behavior in interactive mode

Suggestions:
    - Avoid long-running sessions without timeout.
    - Use `interrupt=True` to stop hanging sessions.
""",


"glob_files" : """
Finds files matching a glob pattern, sorted by modification time.

This tool scans recursively and filters out common noise like `.git`, `node_modules`.
Results are sorted with the newest files first.

Usage:
    await glob_files("*.ts", path="src", case_sensitive=False)

Args:
    pattern (str): Glob pattern (e.g., "*.py", "**/*.md").
    path (str): Base directory to search.
    case_sensitive (bool): If True, pattern match is case-sensitive.

Returns:
    List[str]: List of matching file paths.

Possible Failures:
    - No matches
    - Invalid path
    - Permission denied

Suggestions:
    - Validate pattern correctness.
    - Use `list_directory()` to confirm path contents.
""",

"glob_files" : """
Search for a regex pattern across multiple files.

Supports directory-wide search using `grep` combined with `find`. Useful for
tracing usage of functions, variables, or keywords. Allows file filtering via extension.

Usage:
    await grep_files(pattern="def ", path="src", include="*.py")

Args:
    pattern (str): Regex pattern to search for (e.g., "import .*").
    path (str): Base directory to search in.
    include (str): File glob to restrict search scope (e.g., "*.js").

Returns:
    List[Dict]:
        - file (str): File path
        - line (int): Line number
        - content (str): Line text

Possible Failures:
    - No matches
    - Invalid regex
    - Permission errors on files

Suggestions:
    - Use `glob_files()` first to preview candidate files.
    - Keep patterns simple for performance.
""",

"format_code" : """
Format a source code file using the appropriate formatter.

Auto-selects formatter based on file extension. Supports Python, JS/TS, Go,
Rust, C/C++, Java, and more. You can override the formatter explicitly.

Usage:
    await format_code("app.py")
    await format_code("style.scss", formatter="prettier")

Args:
    file_path (str): Path to the file to format.
    formatter (Optional[str]): Formatter name (e.g., "black", "prettier").

Returns:
    bool: True if formatting succeeded, or error dict on failure.

Possible Failures:
    - Unsupported file type
    - Missing formatter binary
    - Invalid syntax in file

Suggestions:
    - Use `read_file()` to inspect file content first.
    - Ensure formatter is installed in runtime environment.
""",

"analyze_project_structure" : """
Scans a project directory and summarizes its structure.

Detects language distribution, file type breakdown, project type (e.g., Python, Node),
main directories (e.g., src/, tests/), config files, and overall stats.

Usage:
    await analyze_project_structure(".")

Args:
    path (str): Root directory to analyze.

Returns:
    Dict:
        - root_path (str)
        - total_files (int), total_size (bytes)
        - files_by_type (Dict[str, int])
        - languages (Dict[str, int])
        - project_type (str)
        - config_files (List[str])
        - main_directories (List[str])

Possible Failures:
    - Invalid or non-directory path
    - Permission denied while traversing

Suggestions:
    - Use `list_directory()` to verify path first.
    - Clean up large or unused directories before analyzing.
""",

"get_file_dependencies" : """
Extracts import or dependency statements from a source file.

Supports multiple languages (Python, JS/TS, Go, Rust, Java). Returns only
static imports; dynamic or runtime-loading statements are not detected.

Usage:
    await get_file_dependencies("main.py")

Args:
    file_path (str): Path to the file to scan.

Returns:
    List[str]: Lines representing dependency statements.

Possible Failures:
    - File not found or unreadable
    - Unsupported file type
    - Binary or non-text file

Suggestions:
    - Use `read_file()` to confirm text content.
    - Manually inspect complex import styles.
""",

"find_references" : """
Find references to a symbol in the codebase.

Searches for exact word-boundary matches across code files using `grep`. Can
be filtered by file type (e.g., only `.py` or `.js` files).

Usage:
    await find_references("my_function", file_types=[".py", ".pyi"])

Args:
    symbol (str): Symbol name to search for.
    file_types (List[str]): List of file extensions to restrict search.

Returns:
    List[Dict]:
        - symbol (str), file (str), line (int), content (str)

Possible Failures:
    - Symbol not found
    - Grep execution error

Suggestions:
    - Ensure symbol is a full identifier (e.g., function, class name).
    - Use `grep_files()` for more flexible pattern search.
""",

"run_in_jupyter_ipython" : """
Executes or continues output streaming from code in a persistent Jupyter kernel.

Requires jupyter-remote-runner to be installed in the deployment environment.
This tool provides interactive Python execution with persistent state.

Usage:
    await run_in_jupyter_ipython("print('Hello World')", timeout=30)

Args:
    command (str): 
        - Normal: Python, shell (!), or bash (%%bash) code.
        - " " (space): Special signal to continue retrieving output from a prior command.
        - "C-c": Interrupts the currently running command in the kernel.
        - If is_input=True: text to send to Python's input() prompt.
    timeout (Optional[float]): How long to wait for output, default is 30 sec.
        If execution is not complete in time, output can be resumed later with " ".

Returns:
    CommandResponse:
        - stdout: Combined stdout and stderr, or status message.
        - stderr: Error output if any.
        - exit_code: Command exit code.

Behavior Notes:
    - Only one command can execute at a time.
    - Use " " to resume incomplete execution and stream remaining output.
    - Send "C-c" to interrupt long-running or stalled code.
    - Input support only works for Python code using input() — not bash or shell commands.

Possible Failures:
    - jupyter-remote-runner not installed
    - Kernel startup failure
    - Command timeout

Suggestions:
    - Ensure jupyter-remote-runner is installed: pipx install jupyter-remote-runner
    - Use shorter timeouts for exploratory commands
    - Use "C-c" to interrupt hanging commands
"""
}