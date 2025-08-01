import os
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd

from file_scanner import FileInfo, FileScanner
from multimodal_analyzer import MultimodalAnalyzer

@dataclass
class OrganizationAction:
    """Represents an action to take on a file."""
    action_type: str  # 'keep', 'archive', 'delete', 'move'
    target_folder: Optional[str] = None
    reason: str = ""
    confidence: float = 0.0

@dataclass
class FileAnalysis:
    """Combined file information and analysis results."""
    file_info: FileInfo
    analysis_result: Dict[str, Any]
    priority_score: float
    organization_action: OrganizationAction
    category: str
    subcategory: str = ""

class FileRankingSystem:
    """System to rank and categorize files based on analysis results."""
    
    def __init__(self):
        self.category_weights = {
            'documents': 0.8,
            'images': 0.6,
            'code': 0.9,
            'data': 0.7,
            'media': 0.5,
            'archives': 0.4,
            'logs': 0.3,
            'config': 0.8,
            'temporary': 0.1,
            'system': 0.2,
            'unknown': 0.5
        }
        
        # Define organization folders
        self.organization_structure = {
            'Documents': {
                'Personal': ['resume', 'cv', 'letter', 'personal'],
                'Work': ['report', 'presentation', 'business', 'work'],
                'Financial': ['invoice', 'receipt', 'tax', 'financial'],
                'Reference': ['manual', 'guide', 'reference', 'documentation'],
                'Archive': ['old', 'backup', 'archive']
            },
            'Images': {
                'Photos': ['photo', 'picture', 'family', 'vacation'],
                'Screenshots': ['screenshot', 'capture', 'screen'],
                'Graphics': ['logo', 'design', 'artwork', 'graphic'],
                'Diagrams': ['diagram', 'chart', 'flowchart', 'schematic']
            },
            'Code': {
                'Projects': ['project', 'application', 'app'],
                'Scripts': ['script', 'automation', 'utility'],
                'Libraries': ['library', 'module', 'package'],
                'Config': ['config', 'configuration', 'settings']
            },
            'Data': {
                'Spreadsheets': ['financial', 'inventory', 'contacts'],
                'Databases': ['database', 'backup', 'export'],
                'Analytics': ['analysis', 'report', 'statistics']
            },
            'Media': {
                'Videos': ['video', 'movie', 'recording'],
                'Audio': ['music', 'podcast', 'audio', 'sound']
            },
            'Archive': {
                'Old_Files': ['old', 'backup', 'archive'],
                'Duplicates': ['duplicate', 'copy'],
                'Temp': ['temporary', 'temp', 'cache']
            }
        }
    
    def calculate_priority_score(self, file_info: FileInfo, analysis: Dict[str, Any]) -> float:
        """Calculate a comprehensive priority score for a file."""
        score = 0.0
        
        # Base importance from AI analysis
        importance = analysis.get('importance', 5)
        score += importance * 0.3
        
        # Quality score from analysis
        quality = analysis.get('quality', 5)
        score += quality * 0.2
        
        # File age factor (newer files generally more important)
        age_days = (datetime.now() - file_info.modified_time).days
        if age_days < 30:
            age_factor = 1.0
        elif age_days < 90:
            age_factor = 0.8
        elif age_days < 365:
            age_factor = 0.6
        elif age_days < 730:
            age_factor = 0.4
        else:
            age_factor = 0.2
        
        score += age_factor * 2.0
        
        # Size factor (very small or very large files may be less important)
        size_mb = file_info.size / (1024 * 1024)
        if size_mb < 0.001:  # Very small files
            size_factor = 0.3
        elif size_mb < 10:  # Normal files
            size_factor = 1.0
        elif size_mb < 100:  # Large files
            size_factor = 0.8
        else:  # Very large files
            size_factor = 0.6
        
        score += size_factor * 1.0
        
        # Sensitive data bonus
        if analysis.get('contains_sensitive', False):
            score += 2.0
        
        # Duplicate penalty
        if file_info.is_duplicate:
            score *= 0.3
        
        # Category-specific adjustments
        category = analysis.get('category', 'unknown').lower()
        category_weight = self.category_weights.get(category, 0.5)
        score *= category_weight
        
        # Specific content bonuses
        if analysis.get('contains_secrets', False):
            score += 3.0  # Code with secrets is very important
        
        if analysis.get('business_relevance', 0) > 7:
            score += 1.5
        
        if analysis.get('analysis_type') == 'fallback':
            score *= 0.5  # Reduce score for unanalyzed files
        
        # Normalize to 0-10 scale
        return min(max(score, 0), 10)
    
    def categorize_file(self, file_info: FileInfo, analysis: Dict[str, Any]) -> Tuple[str, str]:
        """Categorize file into main category and subcategory."""
        
        # Get category from analysis
        analysis_category = analysis.get('category', 'unknown').lower()
        analysis_type = analysis.get('analysis_type', 'unknown')
        
        # Map analysis results to our organization structure
        if analysis_type == 'document' or 'document' in analysis_category:
            main_category = 'Documents'
            
            # Determine subcategory based on content
            if any(keyword in analysis.get('summary', '').lower() 
                   for keyword in ['resume', 'cv', 'personal']):
                subcategory = 'Personal'
            elif any(keyword in analysis.get('summary', '').lower() 
                     for keyword in ['work', 'business', 'report']):
                subcategory = 'Work'
            elif any(keyword in analysis.get('summary', '').lower() 
                     for keyword in ['invoice', 'financial', 'tax']):
                subcategory = 'Financial'
            elif any(keyword in analysis.get('summary', '').lower() 
                     for keyword in ['manual', 'guide', 'reference']):
                subcategory = 'Reference'
            else:
                subcategory = 'Work'  # Default for documents
                
        elif analysis_type == 'image':
            main_category = 'Images'
            
            if analysis.get('category', '').lower() == 'screenshot':
                subcategory = 'Screenshots'
            elif 'diagram' in analysis.get('summary', '').lower():
                subcategory = 'Diagrams'
            elif any(keyword in analysis.get('summary', '').lower() 
                     for keyword in ['logo', 'design', 'graphic']):
                subcategory = 'Graphics'
            else:
                subcategory = 'Photos'
                
        elif analysis_type == 'code':
            main_category = 'Code'
            
            if analysis.get('category', '').lower() == 'config':
                subcategory = 'Config'
            elif analysis.get('category', '').lower() == 'script':
                subcategory = 'Scripts'
            elif analysis.get('category', '').lower() == 'library':
                subcategory = 'Libraries'
            else:
                subcategory = 'Projects'
                
        elif analysis_type in ['spreadsheet', 'json', 'xml']:
            main_category = 'Data'
            
            if 'spreadsheet' in analysis_type:
                subcategory = 'Spreadsheets'
            else:
                subcategory = 'Analytics'
                
        elif file_info.extension.lower() in ['.mp4', '.avi', '.mov', '.wmv']:
            main_category = 'Media'
            subcategory = 'Videos'
            
        elif file_info.extension.lower() in ['.mp3', '.wav', '.flac']:
            main_category = 'Media'
            subcategory = 'Audio'
            
        elif file_info.is_duplicate:
            main_category = 'Archive'
            subcategory = 'Duplicates'
            
        elif analysis.get('is_outdated', False) or analysis.get('quality', 5) < 3:
            main_category = 'Archive'
            subcategory = 'Old_Files'
            
        else:
            main_category = 'Archive'
            subcategory = 'Old_Files'
        
        return main_category, subcategory
    
    def recommend_action(self, file_info: FileInfo, analysis: Dict[str, Any], priority_score: float) -> OrganizationAction:
        """Recommend what action to take with a file."""
        
        # High priority files - always keep
        if priority_score >= 8.0:
            return OrganizationAction(
                action_type='keep',
                reason=f"High priority file (score: {priority_score:.1f})",
                confidence=0.9
            )
        
        # Files with sensitive data - keep but organize
        if analysis.get('contains_sensitive', False) or analysis.get('contains_secrets', False):
            return OrganizationAction(
                action_type='keep',
                reason="Contains sensitive/secret data",
                confidence=0.95
            )
        
        # Duplicates - mark for deletion
        if file_info.is_duplicate:
            return OrganizationAction(
                action_type='delete',
                reason="Duplicate file detected",
                confidence=0.8
            )
        
        # Very old, low quality files
        age_days = (datetime.now() - file_info.modified_time).days
        if age_days > 730 and priority_score < 4.0:
            return OrganizationAction(
                action_type='delete',
                reason=f"Old file ({age_days} days) with low priority",
                confidence=0.7
            )
        
        # Low quality files
        if analysis.get('quality', 5) < 3 and priority_score < 5.0:
            return OrganizationAction(
                action_type='delete',
                reason="Low quality content",
                confidence=0.6
            )
        
        # Temporary files
        if 'temp' in file_info.name.lower() or 'tmp' in file_info.name.lower():
            return OrganizationAction(
                action_type='delete',
                reason="Temporary file",
                confidence=0.8
            )
        
        # Medium priority - archive
        if 4.0 <= priority_score < 6.0:
            return OrganizationAction(
                action_type='archive',
                reason=f"Medium priority file (score: {priority_score:.1f})",
                confidence=0.6
            )
        
        # Default - move to organized folder
        return OrganizationAction(
            action_type='move',
            reason=f"Organize file (score: {priority_score:.1f})",
            confidence=0.7
        )

class FileOrganizer:
    """Main orchestrator for file organization system."""
    
    def __init__(self, openai_api_key: str):
        self.scanner = FileScanner()
        self.analyzer = MultimodalAnalyzer(openai_api_key)
        self.ranking_system = FileRankingSystem()
        self.analysis_results: List[FileAnalysis] = []
    
    def analyze_directory(self, directory_path: str, recursive: bool = True) -> List[FileAnalysis]:
        """Analyze all files in a directory and return organized results."""
        print(f"Scanning directory: {directory_path}")
        files_info = self.scanner.scan_directory(directory_path, recursive)
        
        print(f"Found {len(files_info)} files. Beginning analysis...")
        
        analysis_results = []
        
        for i, file_info in enumerate(files_info):
            print(f"Analyzing file {i+1}/{len(files_info)}: {file_info.name}")
            
            # Analyze file content
            analysis_result = self.analyzer.analyze_file(file_info)
            
            # Calculate priority score
            priority_score = self.ranking_system.calculate_priority_score(file_info, analysis_result)
            
            # Categorize file
            main_category, subcategory = self.ranking_system.categorize_file(file_info, analysis_result)
            
            # Recommend action
            action = self.ranking_system.recommend_action(file_info, analysis_result, priority_score)
            action.target_folder = f"{main_category}/{subcategory}"
            
            # Create combined analysis
            file_analysis = FileAnalysis(
                file_info=file_info,
                analysis_result=analysis_result,
                priority_score=priority_score,
                organization_action=action,
                category=main_category,
                subcategory=subcategory
            )
            
            analysis_results.append(file_analysis)
        
        self.analysis_results = analysis_results
        return analysis_results
    
    def get_summary_report(self) -> Dict[str, Any]:
        """Generate a comprehensive summary of the analysis."""
        if not self.analysis_results:
            return {}
        
        total_files = len(self.analysis_results)
        total_size = sum(fa.file_info.size for fa in self.analysis_results)
        
        # Action counts
        action_counts = defaultdict(int)
        for fa in self.analysis_results:
            action_counts[fa.organization_action.action_type] += 1
        
        # Category distribution
        category_dist = defaultdict(int)
        for fa in self.analysis_results:
            category_dist[fa.category] += 1
        
        # Priority distribution
        priority_ranges = {'High (8-10)': 0, 'Medium (5-7)': 0, 'Low (0-4)': 0}
        for fa in self.analysis_results:
            if fa.priority_score >= 8:
                priority_ranges['High (8-10)'] += 1
            elif fa.priority_score >= 5:
                priority_ranges['Medium (5-7)'] += 1
            else:
                priority_ranges['Low (0-4)'] += 1
        
        # Files to delete (space savings)
        delete_files = [fa for fa in self.analysis_results if fa.organization_action.action_type == 'delete']
        potential_space_savings = sum(fa.file_info.size for fa in delete_files)
        
        # Duplicate information
        duplicates = [fa for fa in self.analysis_results if fa.file_info.is_duplicate]
        
        return {
            'total_files': total_files,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'action_counts': dict(action_counts),
            'category_distribution': dict(category_dist),
            'priority_distribution': priority_ranges,
            'duplicates_found': len(duplicates),
            'potential_space_savings_mb': round(potential_space_savings / (1024 * 1024), 2),
            'files_to_delete': len(delete_files),
            'high_priority_files': len([fa for fa in self.analysis_results if fa.priority_score >= 8]),
        }
    
    def export_results(self, output_path: str = "file_analysis_results.json"):
        """Export analysis results to JSON file."""
        export_data = []
        
        for fa in self.analysis_results:
            export_item = {
                'file_path': fa.file_info.path,
                'file_name': fa.file_info.name,
                'file_size': fa.file_info.size,
                'extension': fa.file_info.extension,
                'created_time': fa.file_info.created_time.isoformat(),
                'modified_time': fa.file_info.modified_time.isoformat(),
                'is_duplicate': fa.file_info.is_duplicate,
                'priority_score': fa.priority_score,
                'category': fa.category,
                'subcategory': fa.subcategory,
                'action_type': fa.organization_action.action_type,
                'action_reason': fa.organization_action.reason,
                'action_confidence': fa.organization_action.confidence,
                'target_folder': fa.organization_action.target_folder,
                'analysis_summary': fa.analysis_result.get('summary', ''),
                'analysis_importance': fa.analysis_result.get('importance', 0),
                'analysis_recommendations': fa.analysis_result.get('recommendations', '')
            }
            export_data.append(export_item)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"Results exported to {output_path}")
    
    def get_files_by_action(self, action_type: str) -> List[FileAnalysis]:
        """Get all files with a specific recommended action."""
        return [fa for fa in self.analysis_results if fa.organization_action.action_type == action_type]
    
    def get_files_by_category(self, category: str) -> List[FileAnalysis]:
        """Get all files in a specific category."""
        return [fa for fa in self.analysis_results if fa.category == category]

def main():
    """Example usage of FileOrganizer."""
    # You would need to provide a valid OpenAI API key
    organizer = FileOrganizer("your-openai-api-key-here")
    
    # Analyze a directory
    results = organizer.analyze_directory("/path/to/your/directory")
    
    # Generate summary
    summary = organizer.get_summary_report()
    print("Organization Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # Export results
    organizer.export_results()
    
    # Show files recommended for deletion
    delete_files = organizer.get_files_by_action('delete')
    print(f"\nFiles recommended for deletion ({len(delete_files)}):")
    for fa in delete_files[:10]:  # Show first 10
        print(f"  {fa.file_info.name} - {fa.organization_action.reason}")

if __name__ == "__main__":
    main()