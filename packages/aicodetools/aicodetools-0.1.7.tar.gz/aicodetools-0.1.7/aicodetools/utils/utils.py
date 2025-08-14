"""
Utility functions for aicodetools package.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional


def validate_file_path(path: str) -> str:
    """
    Validate and normalize file path.
    
    Args:
        path: File path to validate
        
    Returns:
        Normalized absolute path
        
    Raises:
        ValueError: If path is invalid
    """
    if not path or not isinstance(path, str):
        raise ValueError("Path must be a non-empty string")
    
    # Convert to Path object for normalization
    path_obj = Path(path)
    
    # Convert to absolute path
    abs_path = path_obj.resolve()
    
    return str(abs_path)


def create_success_response(data: Any, metadata: Optional[Dict] = None) -> Dict:
    """
    Create standardized success response.
    
    Args:
        data: The successful operation result
        metadata: Optional metadata about the operation
        
    Returns:
        Standardized success response dictionary
    """
    response = {
        "success": True,
        "data": data
    }
    
    if metadata:
        response["metadata"] = metadata
        
    return response


def create_error_response(error: str, suggestions: Optional[List[str]] = None, details: Optional[str] = None) -> Dict:
    """
    Create standardized error response.
    
    Args:
        error: Human-readable error message
        suggestions: Optional list of suggested solutions
        details: Optional technical details
        
    Returns:
        Standardized error response dictionary
    """
    response = {
        "success": False,
        "error": error
    }
    
    if suggestions:
        response["suggestions"] = suggestions
        
    if details:
        response["details"] = details
        
    return response


def parse_grep_output(output: str) -> List[Dict]:
    """
    Parse grep output into structured results.
    
    Args:
        output: Raw grep output
        
    Returns:
        List of match dictionaries with file, line, and content
    """
    results = []
    
    if not output or not output.strip():
        return results
    
    for line in output.strip().split('\n'):
        if ':' in line:
            # Split on first two colons to handle file:line:content format
            parts = line.split(':', 2)
            if len(parts) >= 3:
                file_path = parts[0].strip()
                line_num = parts[1].strip()
                content = parts[2].strip()
                
                # Try to convert line number to int
                try:
                    line_num = int(line_num)
                except ValueError:
                    line_num = 0
                
                results.append({
                    "file": file_path,
                    "line": line_num,
                    "content": content
                })
    
    return results


def safe_filename(filename: str) -> str:
    """
    Convert filename to safe version by removing/replacing problematic characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Safe filename
    """
    # Replace problematic characters with underscores
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing whitespace and dots
    safe_name = safe_name.strip('. ')
    
    # Ensure it's not empty
    if not safe_name:
        safe_name = "unnamed_file"
    
    return safe_name


def get_file_extension(file_path: str) -> str:
    """
    Get file extension from path.
    
    Args:
        file_path: Path to file
        
    Returns:
        File extension (including the dot) or empty string
    """
    return Path(file_path).suffix.lower()


def is_text_file(file_path: str) -> bool:
    """
    Check if file is likely a text file based on extension.
    
    Args:
        file_path: Path to file
        
    Returns:
        True if likely text file, False otherwise
    """
    text_extensions = {
        '.txt', '.md', '.py', '.js', '.ts', '.html', '.css', '.json', '.xml',
        '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.sh', '.bat',
        '.c', '.cpp', '.h', '.hpp', '.java', '.cs', '.php', '.rb', '.go',
        '.rs', '.swift', '.kt', '.scala', '.clj', '.hs', '.ml', '.fs',
        '.sql', '.r', '.m', '.pl', '.ps1', '.dockerfile', '.makefile'
    }
    
    ext = get_file_extension(file_path)
    return ext in text_extensions or Path(file_path).name.lower() in {'makefile', 'dockerfile', 'readme'}


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def expand_glob_pattern(pattern: str, root_path: str = ".") -> List[str]:
    """
    Expand glob pattern to list of matching files.
    
    Args:
        pattern: Glob pattern (e.g., "*.py", "**/*.js")
        root_path: Root directory to search from
        
    Returns:
        List of matching file paths
    """
    import glob
    
    root = Path(root_path).resolve()
    
    # Handle both relative and absolute patterns
    if os.path.isabs(pattern):
        search_pattern = pattern
    else:
        search_pattern = str(root / pattern)
    
    # Use glob with recursive support
    matches = glob.glob(search_pattern, recursive=True)
    
    # Convert to absolute paths and filter for files only
    result = []
    for match in matches:
        abs_match = Path(match).resolve()
        if abs_match.is_file():
            result.append(str(abs_match))
    
    return sorted(result)