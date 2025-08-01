# AI Desktop File Organizer

A powerful, intelligent desktop file organization tool that uses AI agents to analyze, categorize, and rank files based on their content and importance. This application leverages multimodal LLMs to read and understand various file types, providing smart recommendations for file organization, cleanup, and management.

## 🚀 Features

### Intelligent Analysis
- **Multimodal AI Analysis**: Uses OpenAI GPT-4 and GPT-4 Vision to analyze text, images, PDFs, documents, code, and more
- **Content Understanding**: Reads and understands file content, not just metadata
- **Smart Categorization**: Automatically categorizes files based on content and purpose
- **Priority Ranking**: Assigns priority scores based on importance, recency, and relevance

### File Type Support
- **Documents**: PDF, Word (docx), text files, markdown
- **Images**: JPEG, PNG, GIF, BMP, TIFF, WebP (with visual analysis)
- **Code Files**: Python, JavaScript, HTML, CSS, C++, Java, and more
- **Data Files**: Excel, CSV, JSON, XML
- **Media Files**: Video and audio files (metadata analysis)
- **Archives**: ZIP, RAR, 7z files

### Organization Features
- **Automated Categorization**: Sorts files into logical folder structures
- **Duplicate Detection**: Identifies and flags duplicate files
- **Batch Operations**: Select and process multiple files at once
- **Safe Deletion**: Multiple confirmation layers and dry-run mode
- **Backup Creation**: Optional backup before any destructive operations

### Safety & Control
- **Dry Run Mode**: Test operations without making changes
- **Confirmation Dialogs**: Require explicit confirmation for deletions
- **Deletion Limits**: Configurable maximum percentage of files to delete
- **Backup Options**: Create backups before organizing
- **Detailed Reporting**: Comprehensive analysis reports and statistics

### User Interface
- **Modern GUI**: Clean, intuitive tkinter-based interface
- **Real-time Progress**: Progress bars and status updates
- **Filtering & Search**: Find files by category, action, or name
- **Detailed Views**: In-depth file analysis and metadata
- **Export Results**: Save analysis results for later review

## 📋 Requirements

- **Python**: 3.8 or higher
- **OpenAI API Key**: Required for AI analysis
- **Operating System**: Windows, macOS, or Linux
- **Memory**: 2GB RAM minimum (4GB+ recommended for large directories)
- **Storage**: 100MB for installation

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/desktop-organizer.git
   cd desktop-organizer
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

## ⚙️ Configuration

### Initial Setup
1. **Launch the application**: Run `python main.py`
2. **Configure API Key**: Go to Tools → Configuration
3. **Enter OpenAI API Key**: Your OpenAI API key (starts with 'sk-')
4. **Adjust Settings**: Configure analysis preferences and safety settings

### Configuration Options

#### API Settings
- **OpenAI API Key**: Your OpenAI API key for AI analysis
- **Text Model**: Choose between GPT-4, GPT-3.5-turbo, or GPT-4-turbo
- **Vision Model**: Select GPT-4-vision-preview or GPT-4-turbo for image analysis

#### Analysis Settings
- **Max File Size**: Maximum file size to analyze (default: 20MB)
- **Max Files**: Maximum number of files to process (default: 1000)
- **File Types**: Choose which file types to analyze
- **Recursive Scan**: Whether to scan subdirectories

#### Safety Settings
- **Dry Run Mode**: Test without making actual changes
- **Confirm Deletions**: Require confirmation before deleting files
- **Create Backup**: Backup files before organizing
- **Max Deletion %**: Maximum percentage of files that can be deleted

## 🚀 Usage

### Basic Workflow

1. **Select Directory**:
   - Click "Browse" to select the folder you want to organize
   - The application will recursively scan all subdirectories

2. **Start Analysis**:
   - Click "Start Analysis" to begin AI-powered file analysis
   - Progress will be shown in real-time
   - Analysis may take several minutes depending on file count and size

3. **Review Results**:
   - Switch to the "File List" tab to see all analyzed files
   - Use filters to find specific files or categories
   - Review AI recommendations and priority scores

4. **Take Action**:
   - Select files for deletion, archiving, or moving
   - Use batch operations for multiple files
   - Export results for later review

### Understanding Results

#### Priority Scores (0-10)
- **8-10**: High priority - Keep these files
- **5-7**: Medium priority - Review and decide
- **0-4**: Low priority - Consider deletion or archiving

#### Actions
- **Keep**: Important files that should be preserved
- **Archive**: Move to archive folder for long-term storage
- **Delete**: Files recommended for deletion (duplicates, low quality, old)
- **Move**: Organize into appropriate category folders

#### Categories
- **Documents**: Personal, work, financial, reference documents
- **Images**: Photos, screenshots, graphics, diagrams
- **Code**: Projects, scripts, libraries, configuration files
- **Data**: Spreadsheets, databases, analytics files
- **Media**: Videos, audio files
- **Archive**: Old files, duplicates, temporary files

## 📊 File Analysis Examples

### Document Analysis
- Identifies document types (resume, invoice, report, etc.)
- Detects sensitive information (personal data, financial info)
- Assesses content quality and relevance
- Recommends appropriate organization

### Image Analysis
- Describes image content using computer vision
- Identifies screenshots vs. photos vs. graphics
- Detects text within images
- Assesses image quality and uniqueness

### Code Analysis
- Identifies programming languages and frameworks
- Detects potential security issues (hardcoded secrets)
- Assesses code complexity and quality
- Categorizes by purpose (script, library, config, etc.)

## 🔒 Security & Privacy

### Data Privacy
- **Local Processing**: All file scanning happens locally on your machine
- **API Calls**: Only file content (not paths) sent to OpenAI for analysis
- **No Storage**: OpenAI doesn't store your data when using the API
- **Secure Config**: API keys stored securely with restricted file permissions

### Safety Features
- **Dry Run Mode**: Test all operations without making changes
- **Multiple Confirmations**: Several layers of confirmation for destructive operations
- **Backup Options**: Create backups before any file operations
- **Deletion Limits**: Configurable limits on how many files can be deleted
- **Detailed Logging**: Full audit trail of all operations

## 🛡️ Troubleshooting

### Common Issues

**API Key Errors**:
- Ensure your OpenAI API key is valid and has sufficient credits
- Check that the key starts with 'sk-' and is properly formatted

**Import Errors**:
- Run `pip install -r requirements.txt` to install all dependencies
- Use `python main.py --check-deps` to verify all modules are available

**Analysis Failures**:
- Check your internet connection for API calls
- Ensure files aren't corrupted or in use by other applications
- Try reducing the max file size limit in settings

**Performance Issues**:
- Reduce the number of files analyzed in one batch
- Disable analysis for large media files if not needed
- Close other applications to free up system resources

### Getting Help

1. **Built-in Help**: Use Help → User Guide in the application
2. **Error Messages**: Check the status bar and progress messages for details
3. **Logs**: Use Tools → View Logs to see detailed operation logs
4. **Configuration**: Verify all settings in Tools → Configuration

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines for more information.

### Development Setup
1. Fork the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the environment: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
4. Install development dependencies: `pip install -r requirements.txt`
5. Make your changes and test thoroughly
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool is designed to help organize files safely, but users should:
- Always backup important data before running any organization operations
- Review AI recommendations carefully before taking action
- Test with dry-run mode first on important directories
- Understand that AI analysis may not be perfect for all file types

The developers are not responsible for any data loss that may occur from using this tool.

## 🙏 Acknowledgments

- **OpenAI**: For providing the GPT-4 and GPT-4 Vision APIs
- **Python Community**: For the excellent libraries that make this project possible
- **Contributors**: Thank you to all who have contributed to this project

---

**Made with ❤️ for better file organization**
