# PDF to Markdown Converter with Image Analysis

A Python tool that converts PDF files to Markdown format with intelligent image analysis using OpenAI's GPT-4o model. The tool extracts images from PDFs, processes them with AI to generate descriptions, and creates a comprehensive Markdown output.

## Features

- **PDF to Markdown Conversion**: Converts PDF documents to clean Markdown format
- **Image Extraction**: Automatically extracts images from PDF files
- **AI-Powered Image Analysis**: Uses OpenAI GPT-4o to analyze and describe images
- **Local Storage**: Saves processed files locally with organized directory structure
- **Flask API**: Provides a web API interface for processing files
- **Batch Processing**: Handles multiple images efficiently

## Prerequisites

Before installing, ensure you have:
- Python 3.7 or higher
- Windows 10/11 (for marker_single installation)
- OpenAI API key (optional, for image analysis)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/pdf-to-markdown-converter.git
cd pdf-to-markdown-converter
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```
### 3. Install marker_single on Windows

`marker_single` is the core tool for PDF processing. Here's how to install it on Windows:

#### Method 2: From Source
If pip installation fails, install from source:

```bash
# Install Git if not already installed
# Download from: https://git-scm.com/download/win

# Clone the marker repository
git clone https://github.com/VikParuchuri/marker.git
cd marker

# Install dependencies
pip install -e .
```

### 4. Verify marker_single Installation

Test if marker_single is properly installed:
```bash
marker_single --help
```

If you see help output, the installation was successful.

### 5. Set Up Environment Variables

Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

## Usage

### Command Line Usage

```python
python app.py
```

Replace `"input_pdf_file.pdf"` in the script with your PDF file path.

### API Usage

Start the Flask server:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

### Custom Prompt

Modify the `prompt` variable in the script to customize image analysis:

```python
prompt = "Your custom analysis prompt here"
```

## How It Works

### Step-by-Step Process

1. **PDF Input Processing**
   - The script accepts a PDF file path as input
   - Creates a temporary directory for processing
   - Copies the PDF to the temporary location

2. **PDF to Markdown Conversion**
   - Uses `marker_single` command to convert PDF to Markdown
   - Extracts text content and identifies image locations
   - Creates a folder structure with the converted content

3. **Image Extraction and Processing**
   - Scans the output directory for image files (JPG, PNG, JPEG)
   - Filters images by size (processes only images > 20KB)
   - Creates a local directory structure for organized storage

4. **AI-Powered Image Analysis**
   - Converts images to base64 format for API transmission
   - Sends images to OpenAI GPT-4o with custom prompts
   - Generates detailed descriptions for each image
   - Handles API errors gracefully

5. **Markdown Enhancement**
   - Replaces image references in the Markdown file
   - Adds AI-generated descriptions using custom tags
   - Creates relative paths for local image storage

6. **Output Generation**
   - Saves the enhanced Markdown file
   - Copies images to organized directories
   - Creates metadata files (JSON) for tracking
   - Returns processed content (truncated if over 2000 characters)

### Directory Structure

After processing, your files will be organized as:

```
pdf_to_text/
├── [pdf_filename]/
│   ├── [pdf_filename].md          # Enhanced Markdown file
│   ├── [pdf_filename].pdf         # Original PDF copy
│   ├── images/                    # Extracted images
│   │   ├── image1.jpg
│   │   ├── image2.png
│   │   └── ...
│   └── image_dict.json           # Image descriptions metadata
└── files_dict.json               # File tracking metadata
```

## Code Structure

### Main Functions

- `process_local_file()`: Main processing function that orchestrates the entire workflow
- PDF validation and temporary file management
- Subprocess execution for marker_single
- Image processing and AI analysis loop
- File organization and output generation

### Key Components

- **Environment Setup**: Uses `python-dotenv` for configuration management
- **Image Processing**: PIL for image handling and size validation
- **AI Integration**: OpenAI client for image analysis
- **File Management**: Automated directory creation and file copying
- **Error Handling**: Comprehensive error catching and logging

## Configuration

### Character Limit
Modify the `char_limit` variable to change output truncation:
```python
char_limit = 2000  # Adjust as needed
```

### Image Size Threshold
Change the minimum image size for processing:
```python
if image_size_dict[file_name] > 20000:  # 20KB threshold
```

## Troubleshooting

### Common Issues

1. **marker_single not found**
   - Ensure marker_single is installed and in your PATH
   - Try reinstalling using different methods above

2. **OpenAI API errors**
   - Verify your API key is correct
   - Check your OpenAI account has sufficient credits
   - Ensure stable internet connection

3. **Permission errors**
   - Run command prompt as administrator
   - Check file permissions on input PDF

4. **Large file processing**
   - Increase timeout values for large PDFs
   - Consider processing in smaller batches

### Debug Mode

Enable debug output by adding:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [marker-pdf](https://github.com/VikParuchuri/marker) for PDF processing
- OpenAI for image analysis capabilities
- Flask for web framework support
