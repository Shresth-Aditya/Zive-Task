import os
import json
import anthropic
import PyPDF2
import re
import boto3

MODEL = "claude-3-5-sonnet-20240620"
MAX_TOKENS = 1024
S3 = boto3.client('s3')

def download_pdf_from_s3(s3_bucket, s3_key, local_path):
    """Downloads a PDF from S3 to a local path."""
    try:
        S3.download_file(s3_bucket, s3_key, local_path)
        print(f"Downloaded {s3_key} from {s3_bucket} to {local_path}")
    except Exception as e:
        print(f"Error downloading PDF from S3: {str(e)}")

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        print(f"Error extracting text from PDF: {str(e)}")
        raise

def lambda_handler(event, context):
    # Fetch API Key and PDF path from environment variables
    API_KEY = os.getenv('CLAUDE_API_KEY')
    FILE_NAME = os.getenv('FILE_NAME')
    BUCKET_NAME = os.getenv('BUCKET_NAME')
    
    if not API_KEY or not BUCKET_NAME or not FILE_NAME :
        raise ValueError("Environment variables BUCKET_NAME or FILE_NAME or PDF_FILE_PATH are not set.")
    
    local_pdf_path = "/tmp/temp.pdf"
    
    download_pdf_from_s3(BUCKET_NAME, FILE_NAME, local_pdf_path)
    
    # Initialize the client with the API key
    client = anthropic.Anthropic(api_key=API_KEY)

    # Extract text from the PDF file
    pdf_text = extract_text_from_pdf(local_pdf_path)
    print(f"Extracted text length: {len(pdf_text.split())} words")

    # Define the prompt for Claude
    prompt = """
    Provide the information for the following parameters for July 2024:
    - Year
    - Quarter
    - NetIncome
    - TotalAssets
    - Total Liabilities
    - Operational Cash Generated

    Provide the response **only** in valid JSON format. No additional text or explanation, no introduction, no comments, and no surrounding text. Do not include any other information except the raw JSON data.
    """

    try:
        # Create message request to Claude API
        message = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[
                {"role": "user", "content": prompt},
                {"role": "user", "content": pdf_text}
            ]
        )

        # Extract the content from the API response
        response_text = message.content[0].text

        # Use regex to extract the JSON part of the response
        json_match = re.search(r'{.*}', response_text, re.DOTALL)

        if json_match:
            json_str = json_match.group(0)
            json_output_data = json.loads(json_str)

            # Log the output JSON to CloudWatch logs
            print("Extracted JSON Output:", json.dumps(json_output_data, indent=2))

            # Return the JSON data as Lambda's response
            return {
                "statusCode": 200,
                "body": json_output_data
            }
        else:
            raise ValueError("No valid JSON found in the response.")

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return {
            "statusCode": 500,
            "body": {"error": str(e)}
        }
