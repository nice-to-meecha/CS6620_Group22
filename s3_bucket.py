'''
Group 22:
    Stamesha Bello
    Bhavya Duvvuri
    Thara Messeroux
    Maharshi Pathak
    Nic Shepard

This script will generate an S3 bucket, retaining necessary config files
for the Home Assistant container.
'''

import boto3, logging
from botocore.exceptions import ClientError

S3 = boto3.client('s3', region_name = 'us-east-1')

def main():
    pass



if __name__ == "__main__":
    main()
