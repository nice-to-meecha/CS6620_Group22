'''
Group 22:
    Stamesha Bello
    Bhavya Duvvuri
    Thara Messeroux
    Maharshi Pathak
    Nic Shepard

This script will generate an EKS cluster, which will later host Home Assistant.
'''

import boto3, logging
from botocore.exceptions import ClientError

EKS = boto3.client('eks', region_name = 'us-east-1')

def main():
    pass



if __name__ == "__main__":
    main()
