import os
import time
import fnmatch
import re
from typing import Any, Dict, List
from logging_metrics import configure_basic_logging
import logging
from contextlib import contextmanager
from typing import Dict, List, Optional
from datetime import datetime
import stat

__all__ = [
    "list_dir_contents",
    "get_files_matching_prefix",
    "search_file_content",
    "get_file_modified_since"
]

def get_logger() -> logging.Logger:
    """Inicializa e retorna um logger com print no console.

    Returns:
        logging.Logger: Logger basico.
    """
    return configure_basic_logging()

@contextmanager
def error_handler(operation: str, logger: Optional[logging.Logger] = None, reraise: bool = True):
    """
    Context manager for handling errors in file operations.

    Args:
        operation: Description of the operation being performed
        logger: Logger for recording errors
        reraise: Whether to raise exceptions again after logging
    """
    try:
        yield
    except FileNotFoundError as e:
        logger.error(f"{operation} failed: File not found - {str(e)}")
        if reraise:
            raise
    except PermissionError as e:
        logger.error(f"{operation} failed: Permission denied - {str(e)}")
        if reraise:
            raise
    except Exception as e:
        logger.error(f"{operation} failed: {str(e)}")
        if reraise:
            raise

def _format_size(size_bytes: int) -> str:
        """
        Convert bytes to human-readable format.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Human-readable size string
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024 or unit == 'TB':
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024

def _get_file_info(file_path: str, is_dir: bool = False) -> Dict[str, Any]:
        """
        Helper method to get detailed information about a file.
        
        Args:
            file_path: Path to the file
            is_dir: Whether the path is a directory
            
        Returns:
            Dictionary with file details
        """
        stats = os.stat(file_path)
        file_type = "directory" if is_dir else "file"
        
        # Get file extension
        _, extension = os.path.splitext(file_path)
        extension = extension[1:] if extension else ""  # Remove leading dot
        
        return {
            'name': os.path.basename(file_path),
            'path': file_path,
            'type': file_type,
            'size': stats.st_size,
            'size_human': _format_size(stats.st_size),
            'created': datetime.fromtimestamp(stats.st_ctime).isoformat(),
            'modified': datetime.fromtimestamp(stats.st_mtime).isoformat(),
            'accessed': datetime.fromtimestamp(stats.st_atime).isoformat(),
            'extension': extension,
            'permissions': stat.filemode(stats.st_mode)
        }
    
def _is_binary_file(file_path: str, sample_size: int = 8192) -> bool:
        """
        Determines if a file is binary by checking for null bytes.
        
        Args:
            file_path: Path to the file
            sample_size: Number of bytes to check
            
        Returns:
            True if file appears to be binary, False otherwise
        """
        try:
            with open(file_path, 'rb') as f:
                sample = f.read(sample_size)
                if b'\0' in sample:
                    return True
                    
                # Try to decode as text
                try:
                    sample.decode('utf-8')
                    return False
                except UnicodeDecodeError:
                    return True
        except Exception:
            return True

def list_dir_contents(directory_path: str, include_dirs: bool = False,
                    recursive: bool = False, log: Optional[logging.Logger] = None) -> List[Dict[str, Any]]:
    """Lists files and directories in a path.

    Args:
        directory_path (str): Directory path.
        include_dirs (bool): Include directories in the result.
        recursive (bool): Performs a recursive search.
        log (logging.Logger, optional): Logger for auditing. If None, uses get_logger().

    Returns:
        List[Dict[str, Any]]: List of file/directory information.

    Raises:
        ValueError: If the directory does not exist.
    """
    logger = log or get_logger()

    with error_handler(f"Listing files in {directory_path}", logger):
        if not os.path.isdir(directory_path):
            raise ValueError(f"Directory {directory_path} does not exist.")

        result = []

        if recursive:
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    result.append(_get_file_info(file_path))

                if include_dirs:
                    for dir_name in dirs:
                        dir_path = os.path.join(root, dir_name)
                        result.append(_get_file_info(dir_path, is_dir=True))
        else:
            with os.scandir(directory_path) as entries:
                for entry in entries:
                    if entry.is_file() or (include_dirs and entry.is_dir()):
                        result.append(_get_file_info(entry.path, is_dir=entry.is_dir()))

        logger.info(f"Found {len(result)} {'items' if include_dirs else 'files'} in {directory_path}")
        return result

def get_files_matching_prefix(directory: str, prefix: str = "",
                               recursive: bool = False, log: Optional[logging.Logger] = None
) -> List[Dict[str, Any]]:
    """Returns files with a specific prefix.

    Args:
        directory (str): Search directory.
        prefix (str): File prefix.
        recursive (bool): Recursive search.
        log (logging.Logger, optional): Logger for auditing. If None, uses get_logger().

    Returns:
        List[Dict[str, Any]]: List of files found.

    Raises:
        NotADirectoryError: If the directory does not exist.
    """
    logger = log or get_logger()

    with error_handler(f"Finding files with prefix '{prefix}' in {directory}", logger):
        if not os.path.isdir(directory):
            raise NotADirectoryError(f"Directory {directory} does not exist.")

        results = []

        if recursive:
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.startswith(prefix):
                        file_path = os.path.join(root, file)
                        results.append(_get_file_info(file_path))
        else:
            with os.scandir(directory) as entries:
                for entry in entries:
                    if entry.is_file() and entry.name.startswith(prefix):
                        results.append(_get_file_info(entry.path))

        logger.info(f"Found {len(results)} files matching prefix '{prefix}' in {directory}")
        return results

def search_file_content(directory: str, search_text: str,
                        file_pattern: str = "*", recursive: bool = True,
                        case_sensitive: bool = False, log: Optional[logging.Logger] = None) -> List[Dict[str, Any]]:
    """Searches for text within files.

    Args:
        directory (str): Search directory.
        search_text (str): Text to search for.
        file_pattern (str): Filename pattern.
        recursive (bool): Recursive search.
        case_sensitive (bool): Consider case.
        log (logging.Logger, optional): Logger for auditing. If None, uses get_logger().

    Returns:
        List[Dict[str, Any]]: List of matches found.
    """
    logger = log or get_logger()

    with error_handler(f"Searching for '{search_text}' in {directory}", logger):
        if not os.path.isdir(directory):
            raise ValueError(f"Directory {directory} does not exist.")

        results = []
        flags = 0 if case_sensitive else re.IGNORECASE
        pattern = re.compile(re.escape(search_text), flags)

        def search_in_file(file_path):
            try:
                if _is_binary_file(file_path):
                    return

                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for i, line in enumerate(f, 1):
                        matches = list(pattern.finditer(line))
                        if matches:
                            for match in matches:
                                results.append({
                                    'file': file_path,
                                    'line_number': i,
                                    'line': line.strip(),
                                    'start': match.start(),
                                    'end': match.end(),
                                    'match': match.group(0)
                                })
            except Exception as e:
                logger.debug(f"Error searching in {file_path}: {str(e)}")

        if recursive:
            for root, _, files in os.walk(directory):
                for file in fnmatch.filter(files, file_pattern):
                    search_in_file(os.path.join(root, file))
        else:
            with os.scandir(directory) as entries:
                for entry in entries:
                    if entry.is_file() and fnmatch.fnmatch(entry.name, file_pattern):
                        search_in_file(entry.path)

        logger.info(f"Found {len(results)} matches for '{search_text}' in {directory}")
        return results

def get_file_modified_since(directory: str, days: float,
                             recursive: bool = True, log: Optional[logging.Logger] = None) -> List[Dict[str, Any]]:
    """Searches for files modified in the last N days.

    Args:
        directory (str): Search directory.
        days (float): Number of days.
        recursive (bool): Recursive search.
        log (logging.Logger, optional): Logger for auditing. If None, uses get_logger().

    Returns:
        List[Dict[str, Any]]: List of files found.
    """
    logger = log or get_logger()
    with error_handler(f"Finding files modified in last {days} days in {directory}", logger):
        if not os.path.isdir(directory):
            raise ValueError(f"Directory {directory} does not exist.")

        results = []
        cutoff_time = time.time() - (days * 86400)

        if recursive:
            for root, _, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    mod_time = os.path.getmtime(file_path)
                    if mod_time >= cutoff_time:
                        results.append(_get_file_info(file_path))
        else:
            with os.scandir(directory) as entries:
                for entry in entries:
                    if entry.is_file() and entry.stat().st_mtime >= cutoff_time:
                        results.append(_get_file_info(entry.path))

        logger.info(f"Found {len(results)} files modified in the last {days} days")
        return results
