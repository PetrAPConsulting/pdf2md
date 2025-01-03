import os
import glob
import google.generativeai as genai
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import sys
from typing import Dict, Optional

# --- START: API KEY INSERTION ---
API_KEY = "INSERT YOUR API KEY HERE"  # <--- INSERT YOUR API KEY HERE
# --- END: API KEY INSERTION ---

# Gemini Model Options
MODEL_OPTIONS: Dict[int, tuple] = {
    1: ("Gemini 1.5 Flash", "gemini-1.5-flash-002", "Fastest, good for simple documents"),
    2: ("Gemini 1.5 Pro", "gemini-1.5-pro-002", "Best quality, handles complex documents"),
    3: ("Gemini 2.0 Flash", "gemini-2.0-flash-exp", "Excellent experimental model")
}

def display_models() -> None:
    """Display available models with their descriptions."""
    print("\nAvailable Models:")
    print("-" * 50)
    for num, (name, model_id, description) in MODEL_OPTIONS.items():
        print(f"{num}. {name:<10} - {description}")
    print("-" * 50)

def get_model_choice() -> Optional[str]:
    """Get and validate user's model choice."""
    while True:
        display_models()
        try:
            choice = int(input("\nEnter model number (1-3): "))
            if choice in MODEL_OPTIONS:
                return MODEL_OPTIONS[choice][1]
            print("Invalid choice. Please select a number between 1 and 3.")
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            return None

def pdf_to_markdown(pdf_path: str, model_name: str) -> Optional[str]:
    """Convert PDF to Markdown using Gemini API."""
    try:
        print(f"Processing: {pdf_path}")
        print(f"Using model: {model_name}")
        
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel(model_name)

        with open(pdf_path, "rb") as pdf_file:
            pdf_content = pdf_file.read()

        prompt = """
        Convert this PDF to Markdown format following these rules:

        1. Document Structure:
           - Preserve the original document hierarchy
           - Use appropriate Markdown headers (# for main titles, ## for subtitles, etc.)
           - Maintain original paragraph spacing
           - Keep all lists and enumerations in proper Markdown format

        2. Special Elements:
           - Tables: Convert to Markdown tables (|header|header|) with alignment
           - Code blocks: Use triple backticks with language specification
           - Mathematical formulas: Convert to LaTeX format between $$ markers
           - Links: Preserve as Markdown links [text](url)

        3. Formatting:
           - Preserve bold, italic, and other text styling
           - Maintain all diacritical marks and special characters
           - Keep original text indentation where meaningful

        4. Graphics and Figures:
           - Describe charts/graphs with key data points
           - Include captions and references
           - Note any important visual elements

        Convert everything to clean, valid Markdown without adding any explanatory text.
        Focus on accuracy and maintaining the original document's structure and meaning.
        """
        
        response = model.generate_content([
            prompt,
            {"mime_type": "application/pdf", "data": pdf_content},
        ])

        markdown_content = response.text

        if not markdown_content or not markdown_content.strip():
            print(f"Warning: No text extracted from: {pdf_path}")
            return None

        return markdown_content

    except Exception as e:
        print(f"Error processing {pdf_path}: {str(e)}")
        return None

def save_markdown(markdown_content: str, output_path: str) -> bool:
    """Save Markdown content to file."""
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        print(f"✓ Saved: {output_path}")
        return True
    except Exception as e:
        print(f"✗ Error saving {output_path}: {str(e)}")
        return False

def process_pdf(pdf_path: str, model_name: str, output_dir: str) -> bool:
    """Process a single PDF file."""
    try:
        markdown_content = pdf_to_markdown(pdf_path, model_name)
        if markdown_content:
            output_filename = Path(pdf_path).stem + ".md"
            output_path = os.path.join(output_dir, output_filename)
            return save_markdown(markdown_content, output_path)
        return False
    except Exception as e:
        print(f"Error processing {pdf_path}: {str(e)}")
        return False

def main() -> None:
    """Main function to run the PDF to Markdown converter."""
    print(f"PDF to Markdown Converter")
    print(f"Python executable: {sys.executable}")
    print("-" * 50)

    # Setup directories
    input_dir = os.getcwd()
    output_dir = os.path.join(input_dir, "output")

    # Create output directory if it doesn't exist
    try:
        os.makedirs(output_dir, exist_ok=True)
    except OSError as error:
        print(f"Error creating output directory: {error}")
        return

    # Get model choice
    model_name = get_model_choice()
    if not model_name:
        return

    # Find PDF files
    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))
    if not pdf_files:
        print("No PDF files found in the current directory.")
        return

    print(f"\nFound {len(pdf_files)} PDF files.")
    
    # Process files
    start_time = time.time()
    successful_conversions = 0
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(process_pdf, pdf_path, model_name, output_dir)
            for pdf_path in pdf_files
        ]
        
        for future in as_completed(futures):
            if future.result():
                successful_conversions += 1

    end_time = time.time()
    duration = end_time - start_time

    # Print summary
    print("\nConversion Summary:")
    print("-" * 50)
    print(f"Total files processed: {len(pdf_files)}")
    print(f"Successful conversions: {successful_conversions}")
    print(f"Failed conversions: {len(pdf_files) - successful_conversions}")
    print(f"Total time: {duration:.2f} seconds")
    print(f"Average time per file: {duration/len(pdf_files):.2f} seconds")
    print(f"\nOutput directory: {output_dir}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
