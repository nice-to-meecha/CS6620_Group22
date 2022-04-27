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
from glob import glob


s3 = boto3.client('s3')


def upload_func(file, bucket, object_name=None):
    #print(1)
    if object_name is None:
        object_name = os.path.basename(file)
        #s3 = boto3.client('s3')
    try:
        response = s3.upload_file(file, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True
def main(): 
    s3.create_bucket(Bucket='config-home-assistant')
    for file_name in glob('ha_config_files/*.yaml'):
        upload_func(file_name, 'config-home-assistant', file_name)



if __name__ == "__main__":
    main()
