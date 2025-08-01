#!/usr/bin/env python3
"""
AI Desktop File Organizer - Main Entry Point

A powerful desktop file organization tool that uses AI agents to analyze,
categorize, and rank files based on their content and importance.

Features:
- Multimodal AI analysis of various file types (text, images, PDFs, etc.)
- Smart categorization and priority ranking
- Batch file operations with safety controls
- Comprehensive reporting and analytics
- User-friendly GUI interface

Author: AI Assistant
Version: 1.0.0
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    """Main entry point for the application."""
    try:
        # Import and run the GUI application
        from gui_application import DesktopOrganizerGUI
        
        print("Starting AI Desktop File Organizer...")
        print("Loading GUI interface...")
        
        app = DesktopOrganizerGUI()
        app.run()
        
    except ImportError as e:
        print(f"Error importing required modules: {e}")
        print("Please ensure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        print("Please check the configuration and try again.")
        sys.exit(1)

def check_dependencies():
    """Check if all required dependencies are available."""
    required_modules = [
        'openai',
        'pillow',
        'magic',
        'PyPDF2',
        'docx',
        'pandas',
        'openpyxl'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("Missing required dependencies:")
        for module in missing_modules:
            print(f"  - {module}")
        print("\nPlease install missing dependencies:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def print_help():
    """Print help information."""
    help_text = """
AI Desktop File Organizer

USAGE:
    python main.py                 # Start GUI application
    python main.py --help          # Show this help message
    python main.py --check-deps    # Check dependencies

FEATURES:
    - AI-powered file analysis using OpenAI GPT-4
    - Support for multiple file types (documents, images, code, etc.)
    - Smart categorization and priority ranking
    - Safe batch operations with confirmations
    - Comprehensive reporting and statistics
    - User-friendly graphical interface

REQUIREMENTS:
    - Python 3.8 or higher
    - OpenAI API key
    - Required Python packages (see requirements.txt)

SETUP:
    1. Install dependencies: pip install -r requirements.txt
    2. Run the application: python main.py
    3. Configure your OpenAI API key in the settings
    4. Select a directory to analyze
    5. Review recommendations and take action

For more information, see the README.md file.
"""
    print(help_text)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print_help()
            sys.exit(0)
        elif sys.argv[1] == "--check-deps":
            if check_dependencies():
                print("All dependencies are available.")
                sys.exit(0)
            else:
                sys.exit(1)
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print("Use --help for usage information.")
            sys.exit(1)
    
    # Check dependencies before starting
    if not check_dependencies():
        sys.exit(1)
    
    # Run the main application
    main()