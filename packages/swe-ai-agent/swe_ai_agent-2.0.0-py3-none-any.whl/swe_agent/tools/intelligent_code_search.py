#!/usr/bin/env python3
"""
Interactive Fast Code Search - Optimized for speed with multiprocessing, memory mapping, and smart filtering
Based on the provided implementation with memory mapping and efficient file processing.
"""

import os
import re
import sys
import time
import mmap
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count
from typing import List, Tuple, Generator, Optional, Dict, Any
import fnmatch
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

# Common code file extensions
CODE_EXTENSIONS = {
    '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.c', '.cpp', '.cc', '.cxx', 
    '.h', '.hpp', '.cs', '.php', '.rb', '.go', '.rs', '.kt', '.scala', '.swift',
    '.m', '.mm', '.sh', '.bash', '.zsh', '.sql', '.r', '.pl', '.lua', '.dart',
    '.vue', '.svelte', '.html', '.htm', '.css', '.scss', '.sass', '.less',
    '.xml', '.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.md',
    '.txt', '.log'
}

# Directories to skip for faster search
SKIP_DIRS = {
    '.git', '.svn', '.hg', '__pycache__', 'node_modules', '.venv', 'venv',
    'env', '.env', 'build', 'dist', '.tox', '.mypy_cache', '.pytest_cache',
    'coverage', '.coverage', 'htmlcov', '.idea', '.vscode', 'target',
    'bin', 'obj', '.gradle', '.nuget', 'packages', 'logs'
}

@dataclass 
class SearchResult:
    """Represents a code search result."""
    file_path: str
    line_number: int
    line_content: str
    context_before: List[str] = None
    context_after: List[str] = None
    match_type: str = 'text_match'
    score: float = 1.0
    language: str = 'unknown'
    highlighted_content: str = ""

class LanguageDetector:
    """Simple language detection from file extensions."""
    
    EXTENSION_MAP = {
        '.py': 'python', '.js': 'javascript', '.jsx': 'javascript',
        '.ts': 'typescript', '.tsx': 'typescript', '.html': 'html',
        '.css': 'css', '.php': 'php', '.c': 'c', '.h': 'c',
        '.cpp': 'cpp', '.cc': 'cpp', '.hpp': 'cpp', '.cs': 'csharp',
        '.java': 'java', '.go': 'go', '.rs': 'rust', '.rb': 'ruby',
        '.sh': 'shell', '.bash': 'shell', '.md': 'markdown'
    }
    
    @staticmethod
    def detect_language(file_path: Path) -> str:
        """Detect language from file extension."""
        suffix = file_path.suffix.lower()
        return LanguageDetector.EXTENSION_MAP.get(suffix, 'unknown')

class FastCodeSearcher:
    def __init__(self, max_workers: Optional[int] = None):
        self.max_workers = max_workers or min(cpu_count(), 32)
        self.stats = {
            'files_found': 0,
            'files_searched': 0,
            'matches_found': 0,
            'search_time': 0,
            'file_scan_time': 0
        }

    def find_code_files(self, root_path: str, include_patterns: List[str] = None, 
                       exclude_patterns: List[str] = None) -> Generator[Path, None, None]:
        """Fast file discovery with smart filtering"""
        start_time = time.time()
        root = Path(root_path)
        
        include_patterns = include_patterns or ['*']
        exclude_patterns = exclude_patterns or []
        
        for dirpath, dirnames, filenames in os.walk(root):
            # Skip unwanted directories in-place (modifies dirnames)
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            
            # Apply directory exclude patterns
            if exclude_patterns:
                dirnames[:] = [d for d in dirnames 
                              if not any(fnmatch.fnmatch(d, pattern) for pattern in exclude_patterns)]
            
            current_dir = Path(dirpath)
            
            for filename in filenames:
                filepath = current_dir / filename
                
                # Fast extension check
                if filepath.suffix.lower() not in CODE_EXTENSIONS:
                    continue
                
                # Apply include patterns
                if not any(fnmatch.fnmatch(filename, pattern) for pattern in include_patterns):
                    continue
                
                # Apply exclude patterns
                if any(fnmatch.fnmatch(filename, pattern) for pattern in exclude_patterns):
                    continue
                
                self.stats['files_found'] += 1
                yield filepath
        
        self.stats['file_scan_time'] = time.time() - start_time

    def search_file(self, args: Tuple[Path, str, bool, bool, bool]) -> List[Tuple[str, int, str]]:
        """Search a single file using memory mapping for speed"""
        filepath, pattern, case_sensitive, regex_mode, exact_match = args
        results = []
        
        try:
            # Skip binary files and very large files (>100KB)
            stat = filepath.stat()
            if stat.st_size > 100 * 1024:  # 100KB limit
                return results
            
            with open(filepath, 'rb') as f:
                # Use memory mapping for large files
                if stat.st_size > 8192:  # 8KB threshold
                    try:
                        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                            content = mm.read().decode('utf-8', errors='ignore')
                    except (OSError, ValueError):
                        content = f.read().decode('utf-8', errors='ignore')
                else:
                    content = f.read().decode('utf-8', errors='ignore')
            
            # Compile regex once per file
            if regex_mode:
                flags = 0 if case_sensitive else re.IGNORECASE
                try:
                    regex = re.compile(pattern, flags)
                except re.error:
                    return results  # Skip invalid regex
            
            lines = content.splitlines()
            for line_num, line in enumerate(lines, 1):
                if regex_mode:
                    if regex.search(line):
                        results.append((str(filepath), line_num, line.strip()))
                else:
                    # Text match search
                    search_line = line if case_sensitive else line.lower()
                    search_pattern = pattern if case_sensitive else pattern.lower()
                    
                    if exact_match:
                        # Split line into words and check for exact matches
                        words = re.split(r'\W+', search_line)
                        if search_pattern in words:
                            results.append((str(filepath), line_num, line.strip()))
                    else:
                        # Simple substring search
                        if search_pattern in search_line:
                            results.append((str(filepath), line_num, line.strip()))
            
        except (IOError, OSError, UnicodeDecodeError, MemoryError):
            pass  # Skip problematic files
        
        return results

    def search(self, root_path: str, pattern: str, case_sensitive: bool = False,
               regex_mode: bool = False, exact_match: bool = True, include_patterns: List[str] = None,
               exclude_patterns: List[str] = None, max_results: int = 1000) -> List[Tuple[str, int, str]]:
        """Main search function with multiprocessing"""
        
        logger.info(f"Scanning files in {root_path}...")
        files = list(self.find_code_files(root_path, include_patterns, exclude_patterns))
        
        logger.info(f"Found {len(files)} code files in {self.stats['file_scan_time']:.2f}s")
        logger.info(f"Searching for: {'regex' if regex_mode else 'text'} pattern '{pattern}'")
        logger.info(f"Using {self.max_workers} worker processes...")
        
        start_time = time.time()
        all_results = []
        
        # Prepare arguments for worker processes
        search_args = [(f, pattern, case_sensitive, regex_mode, exact_match) for f in files]
        
        # Use process pool for parallel searching
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_file = {executor.submit(self.search_file, args): args[0] 
                             for args in search_args}
            
            # Collect results as they complete
            for future in as_completed(future_to_file):
                try:
                    results = future.result()
                    all_results.extend(results)
                    self.stats['files_searched'] += 1
                    
                    # Show progress every 1000 files
                    if self.stats['files_searched'] % 1000 == 0:
                        logger.debug(f"Searched {self.stats['files_searched']}/{len(files)} files... "
                                    f"({len(all_results)} matches so far)")
                    
                    # Limit results to prevent memory issues
                    if len(all_results) >= max_results:
                        logger.info(f"Hit result limit ({max_results}), stopping search...")
                        break
                        
                except Exception as e:
                    pass  # Skip files with errors
        
        self.stats['search_time'] = time.time() - start_time
        self.stats['matches_found'] = len(all_results)
        
        return all_results

    def print_results(self, results: List[Tuple[str, int, str]], max_display: int = 50):
        """Print search results in a readable format"""
        if not results:
            logger.info("No matches found.")
            return
        
        logger.info(f"\n{'='*60}")
        logger.info(f"SEARCH RESULTS ({len(results)} matches found)")
        logger.info(f"{'='*60}")
        
        displayed = 0
        current_file = None
        
        # Sort results by file path for better organization
        results.sort(key=lambda x: (x[0], x[1]))
        
        for filepath, line_num, line_content in results:
            if displayed >= max_display:
                remaining = len(results) - displayed
                logger.info(f"\n... and {remaining} more matches (use max_display parameter to show more)")
                break
            
            # Print file header when switching files
            if filepath != current_file:
                if current_file is not None:
                    logger.info("")  # Add spacing between files
                logger.info(f"\n📁 {filepath}")
                logger.info("-" * min(len(filepath) + 4, 80))
                current_file = filepath
            
            # Print line with line number
            logger.info(f"{line_num:>6}: {line_content}")
            displayed += 1
        
        # Print statistics
        logger.info(f"\n{'='*60}")
        logger.info(f"SEARCH STATISTICS")
        logger.info(f"{'='*60}")
        logger.info(f"Files scanned:    {self.stats['files_found']:,}")
        logger.info(f"Files searched:   {self.stats['files_searched']:,}")
        logger.info(f"Matches found:    {self.stats['matches_found']:,}")
        logger.info(f"Scan time:        {self.stats['file_scan_time']:.2f}s")
        logger.info(f"Search time:      {self.stats['search_time']:.2f}s")
        logger.info(f"Total time:       {self.stats['file_scan_time'] + self.stats['search_time']:.2f}s")
        if self.stats['search_time'] > 0:
            rate = self.stats['files_searched'] / self.stats['search_time']
            logger.info(f"Search rate:      {rate:.0f} files/second")

# Compatibility class for SWE Agent integration
class FastCodeSearch:
    """SWE Agent compatible interface for the memory-mapped search system."""
    
    def __init__(self, workspace_dir: str = None, max_workers: int = None):
        """Initialize search system.
        
        Args:
            workspace_dir: Root directory to search (default: current working directory)
            max_workers: Number of worker processes (default: CPU count)
        """
        self.workspace_dir = Path(workspace_dir or os.getcwd())
        self.searcher = FastCodeSearcher(max_workers)
        logger.info(f"📁 Fast Code Search initialized - workspace: {self.workspace_dir}")

    def search(self, pattern: str, case_sensitive: bool = False, 
               context_lines: int = 2, max_results: int = 1000) -> List[SearchResult]:
        """Search for pattern across all files in workspace using memory mapping."""
        
        if not pattern or not pattern.strip():
            logger.warning("Empty search pattern provided")
            return []
        
        logger.info(f"[?] Searching for text: '{pattern}' (case_sensitive={case_sensitive})")
        
        # Use the optimized searcher
        raw_results = self.searcher.search(
            root_path=str(self.workspace_dir),
            pattern=pattern,
            case_sensitive=case_sensitive,
            regex_mode=False,
            exact_match=False,  # Allow substring matching for better results
            max_results=max_results
        )
        
        # Convert to SearchResult objects
        results = []
        for file_path, line_number, line_content in raw_results:
            try:
                path = Path(file_path)
                language = LanguageDetector.detect_language(path)
                
                result = SearchResult(
                    file_path=file_path,
                    line_number=line_number,
                    line_content=line_content,
                    context_before=[],  # Context can be added if needed
                    context_after=[],
                    match_type='text_match',
                    score=1.0,
                    language=language
                )
                results.append(result)
            except Exception as e:
                logger.debug(f"Error converting result: {e}")
        
        logger.info(f"[OK] Search completed: {len(results)} matches")
        return results

    def search_functions(self, function_name: str, case_sensitive: bool = False) -> List[SearchResult]:
        """Search for function definitions and calls using memory mapping."""
        patterns = [
            f"def {function_name}",
            f"function {function_name}",
            f"func {function_name}",
            f"{function_name}("
        ]
        
        all_results = []
        for pattern in patterns:
            results = self.search(pattern, case_sensitive=case_sensitive, max_results=250)
            all_results.extend(results)
        
        # Remove duplicates
        seen = set()
        unique_results = []
        for result in all_results:
            key = (result.file_path, result.line_number)
            if key not in seen:
                seen.add(key)
                unique_results.append(result)
        
        unique_results.sort(key=lambda x: (x.file_path, x.line_number))
        return unique_results

    def search_classes(self, class_name: str, case_sensitive: bool = False) -> List[SearchResult]:
        """Search for class definitions and usage using memory mapping."""
        patterns = [
            f"class {class_name}",
            f"struct {class_name}",
            f"interface {class_name}",
            f"{class_name}("
        ]
        
        all_results = []
        for pattern in patterns:
            results = self.search(pattern, case_sensitive=case_sensitive, max_results=250)
            all_results.extend(results)
        
        # Remove duplicates
        seen = set()
        unique_results = []
        for result in all_results:
            key = (result.file_path, result.line_number)
            if key not in seen:
                seen.add(key)
                unique_results.append(result)
        
        unique_results.sort(key=lambda x: (x.file_path, x.line_number))
        return unique_results

    def search_imports(self, import_name: str, case_sensitive: bool = False) -> List[SearchResult]:
        """Search for import statements using memory mapping."""
        patterns = [
            f"import {import_name}",
            f"from {import_name}",
            f"#include {import_name}",
            f"require('{import_name}')",
            f'require("{import_name}")'
        ]
        
        all_results = []
        for pattern in patterns:
            results = self.search(pattern, case_sensitive=case_sensitive, max_results=250)
            all_results.extend(results)
        
        # Remove duplicates
        seen = set()
        unique_results = []
        for result in all_results:
            key = (result.file_path, result.line_number)
            if key not in seen:
                seen.add(key)
                unique_results.append(result)
        
        unique_results.sort(key=lambda x: (x.file_path, x.line_number))
        return unique_results

# Tool functions for SWE Agent integration
def search_code_patterns(pattern: str, workspace_path: str = None, 
                        case_sensitive: bool = False, max_results: int = 100) -> List[Dict[str, Any]]:
    """Search for code patterns using memory-mapped text matching."""
    try:
        searcher = FastCodeSearch(workspace_path)
        results = searcher.search(
            pattern=pattern,
            case_sensitive=case_sensitive,
            max_results=max_results
        )
        
        return [
            {
                'file_path': r.file_path,
                'line_number': r.line_number,
                'line_content': r.line_content,
                'language': r.language,
                'context_before': r.context_before[-2:] if r.context_before else [],
                'context_after': r.context_after[:2] if r.context_after else []
            }
            for r in results
        ]
        
    except Exception as e:
        logger.error(f"Error in search_code_patterns: {e}")
        return []

def find_function_definitions(function_name: str, workspace_path: str = None) -> List[Dict[str, Any]]:
    """Find function definitions using memory-mapped search."""
    try:
        searcher = FastCodeSearch(workspace_path)
        results = searcher.search_functions(function_name)
        
        return [
            {
                'file_path': r.file_path,
                'line_number': r.line_number,
                'line_content': r.line_content,
                'language': r.language
            }
            for r in results
        ]
        
    except Exception as e:
        logger.error(f"Error in find_function_definitions: {e}")
        return []

def find_class_definitions(class_name: str, workspace_path: str = None) -> List[Dict[str, Any]]:
    """Find class definitions using memory-mapped search."""
    try:
        searcher = FastCodeSearch(workspace_path)
        results = searcher.search_classes(class_name)
        
        return [
            {
                'file_path': r.file_path,
                'line_number': r.line_number,
                'line_content': r.line_content,
                'language': r.language
            }
            for r in results
        ]
        
    except Exception as e:
        logger.error(f"Error in find_class_definitions: {e}")
        return []

def find_import_statements(import_name: str, workspace_path: str = None) -> List[Dict[str, Any]]:
    """Find import statements using memory-mapped search."""
    try:
        searcher = FastCodeSearch(workspace_path)
        results = searcher.search_imports(import_name)
        
        return [
            {
                'file_path': r.file_path,
                'line_number': r.line_number,
                'line_content': r.line_content,
                'language': r.language
            }
            for r in results
        ]
        
    except Exception as e:
        logger.error(f"Error in find_import_statements: {e}")
        return []

def get_function_definition_and_usages(function_name: str, workspace_path: str = None) -> Dict[str, Any]:
    """Legacy compatibility function."""
    return {
        'definitions': find_function_definitions(function_name, workspace_path),
        'usages': search_code_patterns(f"{function_name}(", workspace_path)
    }

def analyze_code_structure(file_path: str) -> Dict[str, Any]:
    """Simple code structure analysis using text patterns."""
    try:
        path = Path(file_path)
        if not path.exists():
            return {'error': f'File not found: {file_path}'}
        
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        lines = content.splitlines()
        language = LanguageDetector.detect_language(path)
        
        # Simple pattern matching for code elements
        functions = []
        classes = []
        imports = []
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Find functions (simple patterns)
            if ('def ' in line_stripped or 'function ' in line_stripped or 
                'func ' in line_stripped):
                functions.append({'line': i, 'content': line_stripped})
            
            # Find classes
            if ('class ' in line_stripped or 'struct ' in line_stripped):
                classes.append({'line': i, 'content': line_stripped})
            
            # Find imports
            if (line_stripped.startswith('import ') or line_stripped.startswith('from ') or
                line_stripped.startswith('#include') or 'require(' in line_stripped):
                imports.append({'line': i, 'content': line_stripped})
        
        return {
            'file_path': file_path,
            'language': language,
            'total_lines': len(lines),
            'functions': functions,
            'classes': classes,
            'imports': imports
        }
        
    except Exception as e:
        logger.error(f"Error analyzing code structure: {e}")
        return {'error': str(e)}