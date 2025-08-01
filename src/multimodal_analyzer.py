import os
import base64
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
import openai
from PIL import Image
import PyPDF2
from docx import Document
import pandas as pd
import xml.etree.ElementTree as ET

from file_scanner import FileInfo

class MultimodalAnalyzer:
    """Analyzes various file types using OpenAI's multimodal capabilities."""
    
    def __init__(self, api_key: str, model_text: str = "gpt-4", model_vision: str = "gpt-4-vision-preview"):
        """Initialize the analyzer with OpenAI API key and models."""
        self.client = openai.OpenAI(api_key=api_key)
        self.model_text = model_text
        self.model_vision = model_vision
        
        # File type handlers
        self.handlers = {
            '.txt': self._analyze_text_file,
            '.md': self._analyze_text_file,
            '.py': self._analyze_code_file,
            '.js': self._analyze_code_file,
            '.html': self._analyze_code_file,
            '.css': self._analyze_code_file,
            '.cpp': self._analyze_code_file,
            '.java': self._analyze_code_file,
            '.c': self._analyze_code_file,
            '.pdf': self._analyze_pdf_file,
            '.docx': self._analyze_docx_file,
            '.doc': self._analyze_doc_file,
            '.jpg': self._analyze_image_file,
            '.jpeg': self._analyze_image_file,
            '.png': self._analyze_image_file,
            '.gif': self._analyze_image_file,
            '.bmp': self._analyze_image_file,
            '.tiff': self._analyze_image_file,
            '.webp': self._analyze_image_file,
            '.xlsx': self._analyze_excel_file,
            '.xls': self._analyze_excel_file,
            '.csv': self._analyze_csv_file,
            '.json': self._analyze_json_file,
            '.xml': self._analyze_xml_file,
            '.log': self._analyze_log_file,
        }
    
    def encode_image(self, image_path: str) -> str:
        """Encode image to base64 for OpenAI API."""
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            raise Exception(f"Failed to encode image {image_path}: {e}")
    
    def safe_read_text_file(self, file_path: str, max_chars: int = 10000) -> str:
        """Safely read text files with encoding detection and size limits."""
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read(max_chars)
                        return content
                except UnicodeDecodeError:
                    continue
            
            # If all encodings fail, read as binary and decode with errors='ignore'
            with open(file_path, 'rb') as f:
                content = f.read(max_chars)
                return content.decode('utf-8', errors='ignore')
                
        except Exception as e:
            return f"Error reading file: {e}"
    
    def _analyze_text_file(self, file_info: FileInfo) -> Dict[str, Any]:
        """Analyze plain text or markdown files."""
        content = self.safe_read_text_file(file_info.path)
        
        prompt = f"""Analyze this text file and provide insights:

File: {file_info.name}
Size: {file_info.size} bytes
Content (first 10000 chars):
{content}

Please provide a JSON response with:
1. "summary": Brief description of the content
2. "importance": Score 1-10 for how important this file seems
3. "category": Main category (document, note, reference, etc.)
4. "contains_sensitive": Boolean if it contains personal/sensitive data
5. "language": Primary language detected
6. "topics": List of main topics/themes
7. "quality": Score 1-10 for content quality/usefulness
8. "recommendations": Suggestions for keeping, archiving, or deleting

Respond only with valid JSON."""

        try:
            response = self.client.chat.completions.create(
                model=self.model_text,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            result['analysis_type'] = 'text'
            return result
            
        except Exception as e:
            return self._fallback_analysis(file_info, f"Text analysis failed: {e}")
    
    def _analyze_code_file(self, file_info: FileInfo) -> Dict[str, Any]:
        """Analyze source code files."""
        content = self.safe_read_text_file(file_info.path)
        
        prompt = f"""Analyze this source code file:

File: {file_info.name}
Extension: {file_info.extension}
Size: {file_info.size} bytes
Code:
{content}

Please provide a JSON response with:
1. "summary": Brief description of what the code does
2. "importance": Score 1-10 for code importance/complexity
3. "category": Type (script, library, config, test, etc.)
4. "language": Programming language
5. "complexity": Score 1-10 for code complexity
6. "contains_secrets": Boolean if it might contain API keys/passwords
7. "dependencies": List of main dependencies/imports
8. "purpose": Main purpose/functionality
9. "quality": Score 1-10 for code quality
10. "recommendations": Keep, archive, or delete suggestions

Respond only with valid JSON."""

        try:
            response = self.client.chat.completions.create(
                model=self.model_text,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            result['analysis_type'] = 'code'
            return result
            
        except Exception as e:
            return self._fallback_analysis(file_info, f"Code analysis failed: {e}")
    
    def _analyze_image_file(self, file_info: FileInfo) -> Dict[str, Any]:
        """Analyze image files using GPT-4 Vision."""
        try:
            # Check if image is too large
            if file_info.size > 20 * 1024 * 1024:  # 20MB limit
                return self._fallback_analysis(file_info, "Image too large for analysis")
            
            base64_image = self.encode_image(file_info.path)
            
            prompt = f"""Analyze this image file:

File: {file_info.name}
Size: {file_info.size} bytes

Please provide a JSON response with:
1. "summary": Description of what's in the image
2. "importance": Score 1-10 for importance/usefulness
3. "category": Type (photo, screenshot, diagram, artwork, etc.)
4. "contains_people": Boolean if people are visible
5. "contains_text": Boolean if text is readable in image
6. "quality": Score 1-10 for image quality
7. "subjects": List of main subjects/objects
8. "setting": Where/what setting the image shows
9. "is_duplicate_likely": Boolean if it looks like a common/generic image
10. "recommendations": Keep, archive, or delete suggestions

Respond only with valid JSON."""

            response = self.client.chat.completions.create(
                model=self.model_vision,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            result['analysis_type'] = 'image'
            return result
            
        except Exception as e:
            return self._fallback_analysis(file_info, f"Image analysis failed: {e}")
    
    def _analyze_pdf_file(self, file_info: FileInfo) -> Dict[str, Any]:
        """Analyze PDF files by extracting text content."""
        try:
            text_content = ""
            with open(file_info.path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract text from first few pages
                max_pages = min(5, len(pdf_reader.pages))
                for page_num in range(max_pages):
                    page = pdf_reader.pages[page_num]
                    text_content += page.extract_text() + "\n"
            
            if not text_content.strip():
                return self._fallback_analysis(file_info, "PDF contains no extractable text")
            
            prompt = f"""Analyze this PDF document:

File: {file_info.name}
Size: {file_info.size} bytes
Pages: {len(pdf_reader.pages)}
Content (first 5 pages):
{text_content[:5000]}

Please provide a JSON response with:
1. "summary": Brief description of the document content
2. "importance": Score 1-10 for document importance
3. "category": Type (report, manual, invoice, article, etc.)
4. "contains_sensitive": Boolean if it contains personal/financial data
5. "language": Primary language
6. "document_type": Formal classification
7. "topics": List of main topics
8. "quality": Score 1-10 for content quality
9. "is_outdated": Boolean if content seems outdated
10. "recommendations": Keep, archive, or delete suggestions

Respond only with valid JSON."""

            response = self.client.chat.completions.create(
                model=self.model_text,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            result['analysis_type'] = 'pdf'
            result['page_count'] = len(pdf_reader.pages)
            return result
            
        except Exception as e:
            return self._fallback_analysis(file_info, f"PDF analysis failed: {e}")
    
    def _analyze_docx_file(self, file_info: FileInfo) -> Dict[str, Any]:
        """Analyze Word documents."""
        try:
            doc = Document(file_info.path)
            text_content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            
            if not text_content.strip():
                return self._fallback_analysis(file_info, "Document contains no text")
            
            prompt = f"""Analyze this Word document:

File: {file_info.name}
Size: {file_info.size} bytes
Content:
{text_content[:5000]}

Please provide a JSON response with:
1. "summary": Brief description of the document
2. "importance": Score 1-10 for importance
3. "category": Type (letter, report, resume, etc.)
4. "contains_sensitive": Boolean if contains personal data
5. "language": Primary language
6. "document_type": Formal classification
7. "topics": List of main topics
8. "quality": Score 1-10 for content quality
9. "is_template": Boolean if it appears to be a template
10. "recommendations": Keep, archive, or delete suggestions

Respond only with valid JSON."""

            response = self.client.chat.completions.create(
                model=self.model_text,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            result['analysis_type'] = 'document'
            return result
            
        except Exception as e:
            return self._fallback_analysis(file_info, f"Document analysis failed: {e}")
    
    def _analyze_excel_file(self, file_info: FileInfo) -> Dict[str, Any]:
        """Analyze Excel/spreadsheet files."""
        try:
            # Read first sheet with limited rows
            df = pd.read_excel(file_info.path, nrows=100)
            
            prompt = f"""Analyze this spreadsheet file:

File: {file_info.name}
Size: {file_info.size} bytes
Columns: {list(df.columns)}
Row count (sample): {len(df)}
Sample data:
{df.head(10).to_string()}

Please provide a JSON response with:
1. "summary": Description of the data/purpose
2. "importance": Score 1-10 for data importance
3. "category": Type (financial, inventory, contacts, etc.)
4. "contains_sensitive": Boolean if contains personal/financial data
5. "data_quality": Score 1-10 for data completeness
6. "column_count": Number of columns
7. "main_purpose": Primary use of the spreadsheet
8. "is_template": Boolean if it's an empty template
9. "business_relevance": Score 1-10 for business value
10. "recommendations": Keep, archive, or delete suggestions

Respond only with valid JSON."""

            response = self.client.chat.completions.create(
                model=self.model_text,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            result['analysis_type'] = 'spreadsheet'
            result['actual_columns'] = len(df.columns)
            return result
            
        except Exception as e:
            return self._fallback_analysis(file_info, f"Spreadsheet analysis failed: {e}")
    
    def _analyze_csv_file(self, file_info: FileInfo) -> Dict[str, Any]:
        """Analyze CSV files."""
        try:
            df = pd.read_csv(file_info.path, nrows=100)
            return self._analyze_excel_file(file_info)  # Reuse Excel analysis logic
        except Exception as e:
            return self._fallback_analysis(file_info, f"CSV analysis failed: {e}")
    
    def _analyze_json_file(self, file_info: FileInfo) -> Dict[str, Any]:
        """Analyze JSON files."""
        try:
            with open(file_info.path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert to string for analysis, but limit size
            json_str = json.dumps(data, indent=2)[:5000]
            
            prompt = f"""Analyze this JSON file:

File: {file_info.name}
Size: {file_info.size} bytes
Content structure:
{json_str}

Please provide a JSON response with:
1. "summary": Description of the data structure/purpose
2. "importance": Score 1-10 for data importance
3. "category": Type (config, data, api_response, etc.)
4. "contains_sensitive": Boolean if contains credentials/secrets
5. "data_type": Classification of data type
6. "structure_complexity": Score 1-10 for structure complexity
7. "is_config": Boolean if it's a configuration file
8. "potential_secrets": Boolean if might contain sensitive info
9. "business_relevance": Score 1-10 for business value
10. "recommendations": Keep, archive, or delete suggestions

Respond only with valid JSON."""

            response = self.client.chat.completions.create(
                model=self.model_text,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            result['analysis_type'] = 'json'
            return result
            
        except Exception as e:
            return self._fallback_analysis(file_info, f"JSON analysis failed: {e}")
    
    def _analyze_xml_file(self, file_info: FileInfo) -> Dict[str, Any]:
        """Analyze XML files."""
        try:
            tree = ET.parse(file_info.path)
            root = tree.getroot()
            
            # Get a sample of the XML structure
            xml_str = ET.tostring(root, encoding='unicode')[:3000]
            
            prompt = f"""Analyze this XML file:

File: {file_info.name}
Size: {file_info.size} bytes
Root element: {root.tag}
XML structure sample:
{xml_str}

Please provide a JSON response with:
1. "summary": Description of the XML content/purpose
2. "importance": Score 1-10 for data importance
3. "category": Type (config, data, feed, etc.)
4. "contains_sensitive": Boolean if contains sensitive data
5. "xml_type": Classification of XML type
6. "root_element": Name of root element
7. "is_config": Boolean if it's a configuration file
8. "data_complexity": Score 1-10 for data complexity
9. "business_relevance": Score 1-10 for business value
10. "recommendations": Keep, archive, or delete suggestions

Respond only with valid JSON."""

            response = self.client.chat.completions.create(
                model=self.model_text,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            result['analysis_type'] = 'xml'
            return result
            
        except Exception as e:
            return self._fallback_analysis(file_info, f"XML analysis failed: {e}")
    
    def _analyze_log_file(self, file_info: FileInfo) -> Dict[str, Any]:
        """Analyze log files."""
        content = self.safe_read_text_file(file_info.path, max_chars=5000)
        
        prompt = f"""Analyze this log file:

File: {file_info.name}
Size: {file_info.size} bytes
Content sample:
{content}

Please provide a JSON response with:
1. "summary": Description of what system/application this log is from
2. "importance": Score 1-10 for log importance
3. "category": Type (application, system, error, access, etc.)
4. "contains_errors": Boolean if contains error messages
5. "log_type": Classification of log type
6. "system_source": What system/app generated this
7. "contains_sensitive": Boolean if contains sensitive info
8. "is_current": Boolean if logs seem recent/relevant
9. "value_for_debugging": Score 1-10 for debugging value
10. "recommendations": Keep, archive, or delete suggestions

Respond only with valid JSON."""

        try:
            response = self.client.chat.completions.create(
                model=self.model_text,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            result['analysis_type'] = 'log'
            return result
            
        except Exception as e:
            return self._fallback_analysis(file_info, f"Log analysis failed: {e}")
    
    def _analyze_doc_file(self, file_info: FileInfo) -> Dict[str, Any]:
        """Analyze legacy .doc files (fallback analysis)."""
        return self._fallback_analysis(file_info, "Legacy .doc format not fully supported")
    
    def _fallback_analysis(self, file_info: FileInfo, error_msg: str = "") -> Dict[str, Any]:
        """Provide fallback analysis when specific handlers fail."""
        return {
            'summary': f"File analysis failed or not supported: {error_msg}",
            'importance': 5,
            'category': 'unknown',
            'contains_sensitive': False,
            'quality': 5,
            'analysis_type': 'fallback',
            'error': error_msg,
            'recommendations': 'Manual review required'
        }
    
    def analyze_file(self, file_info: FileInfo) -> Dict[str, Any]:
        """Main method to analyze a file based on its extension."""
        try:
            handler = self.handlers.get(file_info.extension.lower())
            if handler:
                result = handler(file_info)
            else:
                result = self._fallback_analysis(file_info, f"No handler for {file_info.extension} files")
            
            # Add common metadata
            result.update({
                'file_path': file_info.path,
                'file_name': file_info.name,
                'file_size': file_info.size,
                'file_extension': file_info.extension,
                'analysis_timestamp': str(file_info.modified_time)
            })
            
            return result
            
        except Exception as e:
            return self._fallback_analysis(file_info, f"Analysis error: {e}")

def main():
    """Example usage of MultimodalAnalyzer."""
    # This would require a valid OpenAI API key
    analyzer = MultimodalAnalyzer("your-openai-api-key-here")
    
    # Example analysis (would need actual file)
    from file_scanner import FileInfo
    from datetime import datetime
    
    # This is just an example - you'd get this from FileScanner
    sample_file = FileInfo(
        path="/path/to/file.txt",
        name="example.txt",
        extension=".txt",
        size=1024,
        mime_type="text/plain",
        created_time=datetime.now(),
        modified_time=datetime.now(),
        accessed_time=datetime.now(),
        hash_md5="example_hash"
    )
    
    result = analyzer.analyze_file(sample_file)
    print("Analysis Result:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()