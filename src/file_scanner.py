import os
import mimetypes
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import magic

@dataclass
class FileInfo:
    """Data class to store file information and metadata."""
    path: str
    name: str
    extension: str
    size: int
    mime_type: str
    created_time: datetime
    modified_time: datetime
    accessed_time: datetime
    hash_md5: str
    is_duplicate: bool = False
    analysis_result: Optional[Dict[str, Any]] = None
    priority_score: float = 0.0
    category: str = "Unknown"
    
class FileScanner:
    """Scans directories and extracts file metadata for analysis."""
    
    def __init__(self):
        self.supported_extensions = {
            '.txt', '.md', '.doc', '.docx', '.pdf', '.rtf',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp',
            '.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv',
            '.mp3', '.wav', '.flac', '.aac', '.ogg',
            '.zip', '.rar', '.7z', '.tar', '.gz',
            '.py', '.js', '.html', '.css', '.cpp', '.java', '.c',
            '.xls', '.xlsx', '.csv', '.json', '.xml', '.yaml',
            '.ppt', '.pptx', '.log', '.ini', '.cfg'
        }
        self.ignore_patterns = {
            '.DS_Store', 'Thumbs.db', '.gitignore', '.git',
            '__pycache__', '.pytest_cache', 'node_modules',
            '.vscode', '.idea', '.tmp', '.temp'
        }
        
    def get_file_hash(self, file_path: str) -> str:
        """Generate MD5 hash for file content."""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except (IOError, OSError):
            return ""
    
    def get_mime_type(self, file_path: str) -> str:
        """Determine file MIME type using python-magic."""
        try:
            mime_type = magic.from_file(file_path, mime=True)
            return mime_type or "application/octet-stream"
        except:
            # Fallback to mimetypes module
            mime_type, _ = mimetypes.guess_type(file_path)
            return mime_type or "application/octet-stream"
    
    def should_analyze_file(self, file_path: str) -> bool:
        """Determine if a file should be analyzed based on extension and patterns."""
        file_name = os.path.basename(file_path)
        file_ext = Path(file_path).suffix.lower()
        
        # Skip ignored patterns
        if any(pattern in file_name for pattern in self.ignore_patterns):
            return False
            
        # Only analyze supported file types
        return file_ext in self.supported_extensions or file_ext == ''
    
    def extract_file_info(self, file_path: str) -> Optional[FileInfo]:
        """Extract comprehensive metadata from a single file."""
        try:
            path_obj = Path(file_path)
            stat_info = path_obj.stat()
            
            file_info = FileInfo(
                path=str(path_obj.absolute()),
                name=path_obj.name,
                extension=path_obj.suffix.lower(),
                size=stat_info.st_size,
                mime_type=self.get_mime_type(file_path),
                created_time=datetime.fromtimestamp(stat_info.st_ctime),
                modified_time=datetime.fromtimestamp(stat_info.st_mtime),
                accessed_time=datetime.fromtimestamp(stat_info.st_atime),
                hash_md5=self.get_file_hash(file_path)
            )
            
            return file_info
            
        except (OSError, IOError) as e:
            print(f"Error processing file {file_path}: {e}")
            return None
    
    def scan_directory(self, directory_path: str, recursive: bool = True) -> List[FileInfo]:
        """Scan directory and return list of FileInfo objects."""
        files_info = []
        hash_map = {}  # Track duplicates by hash
        
        try:
            path_obj = Path(directory_path)
            if not path_obj.exists() or not path_obj.is_dir():
                raise ValueError(f"Directory does not exist: {directory_path}")
            
            # Walk through directory
            if recursive:
                file_paths = path_obj.rglob('*')
            else:
                file_paths = path_obj.iterdir()
                
            for file_path in file_paths:
                if file_path.is_file() and self.should_analyze_file(str(file_path)):
                    file_info = self.extract_file_info(str(file_path))
                    
                    if file_info:
                        # Check for duplicates
                        if file_info.hash_md5 in hash_map:
                            file_info.is_duplicate = True
                            hash_map[file_info.hash_md5]['duplicates'].append(file_info)
                        else:
                            hash_map[file_info.hash_md5] = {
                                'original': file_info,
                                'duplicates': []
                            }
                        
                        files_info.append(file_info)
            
            print(f"Scanned {len(files_info)} files in {directory_path}")
            return files_info
            
        except Exception as e:
            print(f"Error scanning directory {directory_path}: {e}")
            return []
    
    def get_scan_summary(self, files_info: List[FileInfo]) -> Dict[str, Any]:
        """Generate summary statistics from scanned files."""
        if not files_info:
            return {}
            
        total_size = sum(f.size for f in files_info)
        duplicates = [f for f in files_info if f.is_duplicate]
        
        # Group by extension
        extensions = {}
        for file_info in files_info:
            ext = file_info.extension or 'no_extension'
            extensions[ext] = extensions.get(ext, 0) + 1
        
        # Group by size ranges
        size_ranges = {
            'tiny': 0,      # < 1KB
            'small': 0,     # 1KB - 1MB
            'medium': 0,    # 1MB - 100MB
            'large': 0,     # 100MB - 1GB
            'huge': 0       # > 1GB
        }
        
        for file_info in files_info:
            size = file_info.size
            if size < 1024:
                size_ranges['tiny'] += 1
            elif size < 1024 * 1024:
                size_ranges['small'] += 1
            elif size < 100 * 1024 * 1024:
                size_ranges['medium'] += 1
            elif size < 1024 * 1024 * 1024:
                size_ranges['large'] += 1
            else:
                size_ranges['huge'] += 1
        
        return {
            'total_files': len(files_info),
            'total_size': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'duplicates_count': len(duplicates),
            'extensions': extensions,
            'size_distribution': size_ranges,
            'oldest_file': min(files_info, key=lambda f: f.created_time).created_time,
            'newest_file': max(files_info, key=lambda f: f.created_time).created_time
        }

def main():
    """Example usage of FileScanner."""
    scanner = FileScanner()
    files = scanner.scan_directory("/path/to/directory")
    summary = scanner.get_scan_summary(files)
    
    print("Scan Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    main()