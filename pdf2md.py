import os
import glob
from google import genai
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import sys
from typing import Optional

# --- START: API KEY INSERTION ---
API_KEY = "YOUR_API_KEY_HERE"  # <--- INSERT YOUR API KEY HERE
# --- END: API KEY INSERTION ---

# Gemini Model Options
MODEL_OPTIONS: dict[int, tuple[str, str, str]] = {
    1: ("Gemini 3 Flash", "gemini-3-flash-preview", "Fast and efficient"),
    2: ("Gemini 3 Pro", "gemini-3-pro-preview", "Most powerful model"),
}

# Generation Settings
TEMPERATURE = 1.0  # 1.0 is default and recommended for Gemini 3 models
THINKING_LEVEL = "HIGH"  # Options (FLASH): "MINIMAL", "LOW", "MEDIUM", "HIGH" Options (PRO): "LOW", "HIGH"

def display_models() -> None:
    """Display available models with their descriptions."""
    print("\nAvailable Models:")
    print("-" * 50)
    for num, (name, model_id, description) in MODEL_OPTIONS.items():
        print(f"{num}. {name:<15} - {description}")
    print("-" * 50)


def get_model_choice() -> Optional[str]:
    """Get and validate user's model choice."""
    while True:
        display_models()
        try:
            choice = int(input("\nEnter model number (1-2): "))
            if choice in MODEL_OPTIONS:
                return MODEL_OPTIONS[choice][1]
            print("Invalid choice. Please select 1 or 2.")
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            return None


def pdf_to_markdown(pdf_path: str, model_name: str, client: genai.Client) -> Optional[str]:
    """Convert PDF to Markdown using Gemini API."""
    try:
        print(f"Processing: {pdf_path}")
        print(f"Using model: {model_name}")

        # Read PDF content
        with open(pdf_path, "rb") as pdf_file:
            pdf_content = pdf_file.read()

        prompt = """
        Convert this PDF to Markdown format following these rules:

        1. Document Structure:
           - Preserve the original document hierarchy
           - Use appropriate Markdown headers (# for main titles, ## for subtitles, etc.)
           - Maintain original paragraph spacing
           - Keep all lists and enumerations in proper Markdown format
           - Maintain numerical precision exactly as shown

        2. Special Elements:
           - Tables: Convert to proper Markdown tables with headers and data rows with alignment. For example:
           | Column1 | Column2 |
           |---------|---------|
           | Data1   | Data2   |
           - Code blocks: Use triple backticks with language specification
           - Mathematical formulas: Convert to LaTeX format between $$ markers. For example: $$ y = mx + b $$
           - Links: Preserve as Markdown links [text](url)
           - Process Flows: Create a numbered list with clear step progression and any branching conditions.
           - Charts and Graphs: Extract the actual data points and represent them in a markdown table. Include axis labels, units, and scale information. Describe the relationship pattern (linear, exponential, etc.) as a markdown header.

        3. Formatting:
           - Preserve bold, italic, and other text styling
           - Please convert the multi-column text to a single column format with these specific requirements:
                - Process the text column by column, from left to right
                - Complete each column from top to bottom before moving to the next column
                - Ensure paragraphs that continue across pages are kept together and completed before moving to the next paragraph
                - Look for context clues like incomplete sentences at the bottom of a page and their continuation at the top of the next page in the same column
                - Do not jump between columns mid-text
                - Keep paragraphs in their original sequence as they appear in the source document
                - Use the full available page width
                - Remove hyphenation that was used for line breaks in the original narrow columns
                - Rejoin hyphenated words that were split across lines
                - Reflow all text to fill the entire width of the page
                - Remove any artificial line breaks from the original column formatting
           - Maintain all diacritical marks and special characters
           - Keep original text indentation where meaningful
           - Preserve all labels and annotations as markdown text
           - Structure the output to prioritize machine readability

        4. Graphics and Figures:
           - Include captions and references
           - Note any important visual elements
           - Preserve any measurements or specifications in tables
           - Convert flowcharts and diagrams to mermaid markdown syntax when possible:
            ```mermaid
            graph LR
                A-->B
                B-->C
            ```

        Convert everything to clean, valid Markdown without adding any explanatory text.
        Focus on accuracy and maintaining the original document's structure and meaning.
        """

        # Use the new google-genai SDK API
        response = client.models.generate_content(
            model=model_name,
            contents=[
                prompt,
                genai.types.Part.from_bytes(data=pdf_content, mime_type="application/pdf"),
            ],
        )

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


def process_pdf(pdf_path: str, model_name: str, output_dir: str, client: genai.Client) -> bool:
    """Process a single PDF file."""
    try:
        markdown_content = pdf_to_markdown(pdf_path, model_name, client)
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
    print("PDF to Markdown Converter")
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

    # Initialize the client with new google-genai SDK
    client = genai.Client(api_key=API_KEY)

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
            executor.submit(process_pdf, pdf_path, model_name, output_dir, client)
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
    print(f"Average time per file: {duration / len(pdf_files):.2f} seconds")
    print(f"\nOutput directory: {output_dir}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
