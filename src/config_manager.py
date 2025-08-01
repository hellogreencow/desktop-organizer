import os
import json
import configparser
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

@dataclass
class AppConfig:
    """Application configuration settings."""
    # OpenAI API settings
    openai_api_key: str = ""
    openai_model_text: str = "gpt-4"
    openai_model_vision: str = "gpt-4-vision-preview"
    
    # Analysis settings
    max_file_size_mb: int = 20
    max_files_to_analyze: int = 1000
    skip_hidden_files: bool = True
    recursive_scan: bool = True
    
    # Organization settings
    auto_organize: bool = False
    create_backup: bool = True
    confirm_deletions: bool = True
    archive_folder: str = "Archive"
    
    # GUI settings
    window_width: int = 1200
    window_height: int = 800
    theme: str = "light"
    show_progress: bool = True
    
    # File type preferences
    analyze_images: bool = True
    analyze_documents: bool = True
    analyze_code: bool = True
    analyze_media: bool = False
    analyze_archives: bool = False
    
    # Priority thresholds
    high_priority_threshold: float = 8.0
    low_priority_threshold: float = 4.0
    
    # Safety settings
    require_confirmation: bool = True
    dry_run_mode: bool = False
    max_deletion_percentage: float = 0.5  # Don't delete more than 50% of files
    
class ConfigManager:
    """Manages application configuration and settings."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize configuration manager."""
        if config_dir is None:
            # Default to user's home directory
            self.config_dir = Path.home() / ".desktop_organizer"
        else:
            self.config_dir = Path(config_dir)
        
        self.config_dir.mkdir(exist_ok=True)
        self.config_file = self.config_dir / "config.ini"
        self.settings_file = self.config_dir / "settings.json"
        
        self.config = AppConfig()
        self.load_config()
    
    def load_config(self):
        """Load configuration from files."""
        # Load from INI file (for sensitive data like API keys)
        if self.config_file.exists():
            self._load_from_ini()
        
        # Load from JSON file (for general settings)
        if self.settings_file.exists():
            self._load_from_json()
        
        # Check for environment variables
        self._load_from_env()
    
    def _load_from_ini(self):
        """Load configuration from INI file."""
        try:
            config_parser = configparser.ConfigParser()
            config_parser.read(self.config_file)
            
            if 'API' in config_parser:
                api_section = config_parser['API']
                self.config.openai_api_key = api_section.get('openai_api_key', self.config.openai_api_key)
                self.config.openai_model_text = api_section.get('openai_model_text', self.config.openai_model_text)
                self.config.openai_model_vision = api_section.get('openai_model_vision', self.config.openai_model_vision)
            
            if 'Safety' in config_parser:
                safety_section = config_parser['Safety']
                self.config.require_confirmation = safety_section.getboolean('require_confirmation', self.config.require_confirmation)
                self.config.dry_run_mode = safety_section.getboolean('dry_run_mode', self.config.dry_run_mode)
                self.config.max_deletion_percentage = safety_section.getfloat('max_deletion_percentage', self.config.max_deletion_percentage)
                
        except Exception as e:
            print(f"Error loading INI config: {e}")
    
    def _load_from_json(self):
        """Load settings from JSON file."""
        try:
            with open(self.settings_file, 'r') as f:
                settings = json.load(f)
            
            # Update config with loaded settings
            for key, value in settings.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
                    
        except Exception as e:
            print(f"Error loading JSON settings: {e}")
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        env_mappings = {
            'OPENAI_API_KEY': 'openai_api_key',
            'DESKTOP_ORGANIZER_MODEL': 'openai_model_text',
            'DESKTOP_ORGANIZER_VISION_MODEL': 'openai_model_vision',
            'DESKTOP_ORGANIZER_DRY_RUN': 'dry_run_mode'
        }
        
        for env_var, config_attr in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                if config_attr in ['dry_run_mode', 'require_confirmation']:
                    setattr(self.config, config_attr, env_value.lower() in ['true', '1', 'yes'])
                else:
                    setattr(self.config, config_attr, env_value)
    
    def save_config(self):
        """Save configuration to files."""
        self._save_to_ini()
        self._save_to_json()
    
    def _save_to_ini(self):
        """Save sensitive configuration to INI file."""
        try:
            config_parser = configparser.ConfigParser()
            
            config_parser['API'] = {
                'openai_api_key': self.config.openai_api_key,
                'openai_model_text': self.config.openai_model_text,
                'openai_model_vision': self.config.openai_model_vision
            }
            
            config_parser['Safety'] = {
                'require_confirmation': str(self.config.require_confirmation),
                'dry_run_mode': str(self.config.dry_run_mode),
                'max_deletion_percentage': str(self.config.max_deletion_percentage)
            }
            
            with open(self.config_file, 'w') as f:
                config_parser.write(f)
                
            # Set restrictive permissions on config file (Unix-like systems)
            if os.name == 'posix':
                os.chmod(self.config_file, 0o600)
                
        except Exception as e:
            print(f"Error saving INI config: {e}")
    
    def _save_to_json(self):
        """Save general settings to JSON file."""
        try:
            # Create settings dict excluding sensitive data
            settings = asdict(self.config)
            
            # Remove sensitive keys
            sensitive_keys = ['openai_api_key']
            for key in sensitive_keys:
                settings.pop(key, None)
            
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
                
        except Exception as e:
            print(f"Error saving JSON settings: {e}")
    
    def is_valid_config(self) -> bool:
        """Check if configuration is valid for running the application."""
        if not self.config.openai_api_key:
            return False
        
        # Check if API key format looks valid (starts with sk-)
        if not self.config.openai_api_key.startswith('sk-'):
            return False
        
        return True
    
    def get_missing_config(self) -> List[str]:
        """Get list of missing required configuration items."""
        missing = []
        
        if not self.config.openai_api_key:
            missing.append("OpenAI API Key")
        
        return missing
    
    def reset_to_defaults(self):
        """Reset configuration to default values."""
        api_key = self.config.openai_api_key  # Preserve API key
        self.config = AppConfig()
        self.config.openai_api_key = api_key
    
    def export_config(self, export_path: str):
        """Export configuration to a file (excluding sensitive data)."""
        export_data = asdict(self.config)
        export_data['openai_api_key'] = '[REDACTED]'  # Don't export API key
        
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2)
    
    def import_config(self, import_path: str, preserve_api_key: bool = True):
        """Import configuration from a file."""
        try:
            with open(import_path, 'r') as f:
                imported_data = json.load(f)
            
            # Preserve API key if requested
            current_api_key = self.config.openai_api_key if preserve_api_key else ""
            
            # Update config with imported data
            for key, value in imported_data.items():
                if hasattr(self.config, key) and key != 'openai_api_key':
                    setattr(self.config, key, value)
            
            # Restore API key if preserved
            if preserve_api_key:
                self.config.openai_api_key = current_api_key
                
            return True
            
        except Exception as e:
            print(f"Error importing config: {e}")
            return False
    
    def get_organization_settings(self) -> Dict[str, Any]:
        """Get settings specific to file organization."""
        return {
            'auto_organize': self.config.auto_organize,
            'create_backup': self.config.create_backup,
            'confirm_deletions': self.config.confirm_deletions,
            'archive_folder': self.config.archive_folder,
            'high_priority_threshold': self.config.high_priority_threshold,
            'low_priority_threshold': self.config.low_priority_threshold,
            'max_deletion_percentage': self.config.max_deletion_percentage
        }
    
    def get_analysis_settings(self) -> Dict[str, Any]:
        """Get settings specific to file analysis."""
        return {
            'max_file_size_mb': self.config.max_file_size_mb,
            'max_files_to_analyze': self.config.max_files_to_analyze,
            'skip_hidden_files': self.config.skip_hidden_files,
            'recursive_scan': self.config.recursive_scan,
            'analyze_images': self.config.analyze_images,
            'analyze_documents': self.config.analyze_documents,
            'analyze_code': self.config.analyze_code,
            'analyze_media': self.config.analyze_media,
            'analyze_archives': self.config.analyze_archives
        }
    
    def validate_api_key(self) -> bool:
        """Validate the OpenAI API key format."""
        if not self.config.openai_api_key:
            return False
        
        # Basic format validation
        if not self.config.openai_api_key.startswith('sk-'):
            return False
        
        if len(self.config.openai_api_key) < 50:
            return False
        
        return True

# Global configuration instance
_config_manager = None

def get_config_manager() -> ConfigManager:
    """Get the global configuration manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager

def main():
    """Example usage of ConfigManager."""
    config_mgr = ConfigManager()
    
    print("Current configuration:")
    print(f"API Key set: {'Yes' if config_mgr.config.openai_api_key else 'No'}")
    print(f"Text Model: {config_mgr.config.openai_model_text}")
    print(f"Vision Model: {config_mgr.config.openai_model_vision}")
    print(f"Max file size: {config_mgr.config.max_file_size_mb}MB")
    print(f"Dry run mode: {config_mgr.config.dry_run_mode}")
    
    print(f"\nValid config: {config_mgr.is_valid_config()}")
    
    missing = config_mgr.get_missing_config()
    if missing:
        print(f"Missing configuration: {', '.join(missing)}")

if __name__ == "__main__":
    main()