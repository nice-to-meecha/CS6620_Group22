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

import boto3, logging, sys, os
from botocore.exceptions import ClientError
from glob import glob


s3 = boto3.client('s3')



def create_bucket(name: str, tag: str):
    '''
    Creates an S3 bucket, with the provided name and tag

    :param name: The name of the S3 bucket
    :param tag: The tag for the S3 bucket

    :return: None
    '''

    try:
        s3.create_bucket(Bucket = name)
        s3.put_bucket_tagging(
                Bucket = name,
                Tagging = {
                    'TagSet': [
                        {
                            'Key': 'Name',
                            'Value': tag
                            }
                        ]
                    }
                )

    except ClientError as e:
        logging.error(e)



def upload_file(file: str, bucket: str, object_tag: str, object_name: str = None):
    '''
    Uploads the provided file within the indicated S3 bucket

    :param file: The name of the file to be uploaded into an S3 bucket
    :param bucket: The name of the S3 bucket, in which the provided file
                   will be uploaded
    :param object_tag: The tag of the newly uploaded file/object
    :param object_name: The name that the file/object will utilize, after being
                        uploaded in the provided bucket
    '''

    if object_name is None:
        object_name = os.path.basename(file)
    
    try:
        s3.upload_file(file, bucket, object_name)
        s3.put_object_tagging(
                Bucket = bucket,
                Key = object_name,
                Tagging = {
                    'TagSet': [
                        {
                            'Key': 'Name',
                            'Value': object_tag
                            }
                        ]
                    }
                )

    except ClientError as e:
        logging.error(e)
        return False

    return True



def main():
    '''
    Creates an S3 bucket and uploads the config files for Home Assistant,
    using the following command line arguments:

    s3_bucket.py <bucket_name> <bucket_tag>

    :CLI arg bucket_name: The name of the S3 bucket to be generated
    :CLI arg bucket_tag: The tag for the S3 bucket
    :CLI arg config_file_dir: The relative directory for Home Assistant's
                              config files
    '''

    bucket_name = sys.argv[1]
    bucket_tag = sys.argv[2]
    create_bucket(bucket_name, bucket_tag)

    config_file_dir = sys.argv[3]
    if (config_file_dir[-1] != "/"):
        config_file_dir = config_file_dir + "/"
        
    config_file_yaml = config_file_dir + "*.yaml"
    object_tag = bucket_tag + "-object"

    for file_name in glob(config_file_yaml):
        upload_file(file_name, bucket_name, object_tag, file_name)

    config_file_storage = config_file_dir + ".storage/*"
    for file_name in glob(config_file_storage):
        upload_file(file_name, bucket_name, object_tag, file_name)




if __name__ == "__main__":
    main()

