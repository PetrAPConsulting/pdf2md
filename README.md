# PDF to Markdown Converter

This tool helps you convert complex PDF files (columns, tables, formulas) into clear Markdown format using Google's Gemini vision models. You even do not need OCR. It's designed to be simple to use, even if you're not familiar with programming.

## What Does It Do?

- Converts PDF files to Markdown format
- Keeps the original document structure
- Handles tables, formulas using LaTeX, and special characters
- Processes multiple PDF files at once
- Creates clean, readable Markdown files

## Before You Start

1. You'll need:
   - Python installed on your computer (version 3.7 or newer)
   - A Google Gemini API key (you can get one from [Google AI Studio](https://makersuite.google.com/app/apikey))

2. Required Python packages:
   ```bash
   pip install google-generativeai pathlib
   ```

## Setup Instructions

1. Download the `pdf2md.py` script to your computer

2. Open the script in a text editor and add your Google API key:
   - Find this section at the top of the file:
     ```python
     API_KEY = "INSERT YOUR API KEY HERE"
     ```
   - Replace "INSERT YOUR API KEY HERE" with your actual API key
   - Save the file

## How to Use

1. Put the script (`pdf2md.py`) in the same folder as your PDF files

2. Open a command prompt or terminal in that folder

3. Run the script:
   ```bash
   python pdf2md.py
   ```
  or
  for Mac users
  ```bash
   python3 pdf2md.py
   ```

4. Choose a model when prompted:
   - Press 1 for the fastest and cheapest conversion (good for simple documents)
   - Press 2 for the highest quality (best for complex documents)
   - Press 3 for the excellent experimental model (check out for name on Google API site and modify appropriately) 

5. Wait for the conversion to finish
   - The script will create an "output" folder
   - Your converted Markdown files will be saved there
   - Each file will have the same name as the original PDF but with `.md` extension

## Features

- Easy model selection with numbered options
- Processes multiple PDFs at the same time
- Creates an organized output folder
- Shows progress as it works
- Provides a summary when finished

## Troubleshooting

If you run into problems:

- Make sure your API key is correctly entered in the script
- Check names of Google models and correct them if differ
- Check that your PDF files are in the same folder as the script
- Ensure you have internet connection (needed for the Google API)
- Make sure you've installed all required Python packages

## Notes

- The conversion quality depends on the PDF's structure and content
- Some complex layouts might not convert perfectly
- The script needs internet connection to work
- Each PDF conversion uses your Google API quota, choose model wisely 

## Need Help?

If you have questions or run into problems:
1. Check the troubleshooting section above
2. Make sure you followed all setup steps
3. Create an issue on GitHub if you need more help
