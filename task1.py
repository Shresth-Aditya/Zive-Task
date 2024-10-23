import boto3
import pandas as pd
import io
import random
import string
import json
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def generate_user_id():
    """Generates a userID in the format 'k9m009-05b84f9'."""
    part1 = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    part2 = ''.join(random.choices(string.ascii_lowercase + string.digits, k=7))
    return f"{part1}-{part2}"
    
def lambda_handler(event, context):
    # Configuration
    BUCKET_NAME = os.environ['BUCKET_NAME']
    FILE_KEY = os.environ['FILE_KEY']

    # Initialize S3 client
    s3 = boto3.client('s3')
    
    try:
        # Get the Excel file from S3
        logger.info(f'Retrieving object from Bucket: {BUCKET_NAME}, Key: {FILE_KEY}')
        obj = s3.get_object(Bucket=BUCKET_NAME, Key=FILE_KEY)
        data = obj['Body'].read()
        logger.info(f'Retrieved {len(data)} bytes from {FILE_KEY}')
        
        # Read Excel into DataFrame
        df = pd.read_excel(io.BytesIO(data),sheet_name='Users')
        
        # Split 'Name' into 'First Name' and 'Last Name'
        df[['First Name', 'Last Name']] = df['Name'].str.split(pat=' ',n=1,expand=True)
        # Generate 'userID' for each row
        df['userID'] = df.apply(lambda row: generate_user_id(), axis=1)
        
        # Ensure 'Role' contains only 'associate' or 'manager'
        invalid_roles = df[~df['Role'].str.lower().isin(['associate', 'manager'])]
        
        if not invalid_roles.empty:
            raise InvalidRoleError(f"Invalid role found: {invalid_roles['Role'].unique()}")
        
        # Validate 'Access'
        invalid_access = df[~df['Access'].str.lower().isin(['general', 'admin'])]
        
        if not invalid_access.empty:
            raise InvalidAccessError(f"Invalid access found: {invalid_access['Access'].unique()}")

        # Reset index after filtering
        df.reset_index(drop=True, inplace=True)
        df=df.drop('Name',axis=1)
        
        # Convert DataFrame to JSON
        data_json = df.to_dict(orient='records')
    
        # Create the response
        response = {
            "data": data_json,
        }
        return {
            'statusCode': 200,
            'body': json.dumps(response)
            }
    
    except s3.exceptions.NoSuchKey:
        logger.error(f'Object with key {FILE_KEY} does not exist in bucket {BUCKET_NAME}.')
        return {
            'statusCode': 404,
            'body': f'Object with key {FILE_KEY} does not exist in bucket {BUCKET_NAME}.'
        }
    except s3.exceptions.NoSuchBucket:
        logger.error(f'The bucket {BUCKET_NAME} does not exist.')
        return {
            'statusCode': 404,
            'body': f'The bucket {BUCKET_NAME} does not exist.'
        }
    except Exception as e:
        logger.error(f'An unexpected error occurred: {str(e)}')
        return {
            'statusCode': 500,
            'body': f'An unexpected error occurred: {str(e)}'
        }
