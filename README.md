# Task 1:

The following environment variables must be configured in AWS Lambda:

BUCKET_NAME: Name of the S3 bucket containing the Excel file.
FILE_KEY: Key (path) of the Excel file in the S3 bucket.

Additional Dependencies which needed to be installed
boto3(only for local enviroment): For S3 interactions.
pandas: For processing Excel data.
openpyxl: For reading Excel files.
logging: For error and info logging.

In my case of I had these dependencies in my aws layer

When invoked, the Lambda function will process the file, validate data, and return the formatted response as JSON. 

URL:https://ul7sbiyd47.execute-api.us-east-1.amazonaws.com/dev/ProcessS3excelfile2
