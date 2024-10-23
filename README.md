# Task 1:

The following environment variables must be configured in AWS Lambda:

BUCKET_NAME: Name of the S3 bucket containing the Excel file.
FILE_KEY: Key (path) of the Excel file in the S3 bucket.

Additional Dependencies which needed to be installed
boto3(only for local enviroment): For S3 interactions.
pandas: For processing Excel data.
openpyxl: For reading Excel files.

To manage external dependencies like pandas and openpyxl in AWS Lambda, a Lambda Layer was created.
When invoked, the Lambda function will process the file, validate data, and return the formatted response as JSON. 

URL:https://ul7sbiyd47.execute-api.us-east-1.amazonaws.com/dev/ProcessS3excelfile2

# Task 2:

Extracts text from the PDF using PyPDF2.
Sends the text to Claude AI for specific data extraction.
Returns the result in valid JSON format.
The script downloads the specified PDF file from S3 to the Lambda's /tmp directory.

The following environment variables must be set in the Lambda function:

CLAUDE_API_KEY: API key for Anthropic Claude API.
BUCKET_NAME: Name of the S3 bucket where the PDF is stored.
FILE_NAME: The key (path) of the PDF file in the S3 bucket.

External Dependencies used:

PyPDF2: For extracting text from PDF files.
anthropic: For communicating with Claude API.

