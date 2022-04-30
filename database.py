'''
Group 22:
    Stamesha Bello
    Bhavya Duvvuri
    Thara Messeroux
    Maharshi Pathak
    Nic Shepard

This script will generate a database, with an associated security group,
for usage in conjunction with an EKS cluster.
'''

import boto3, logging, sys, cloudstack
from botocore.exceptions import ClientError


EC2 = boto3.client('ec2', region_name = 'us-east-1')
RDS = boto3.client('rds', region_name = 'us-east-1')



def create_security_group(vpc_id: str, name: str, tag: str, description: str):
    '''
    Creates a security group, with the provided name, to be added to the supplied VPC group. 

    :param vpc_id: The ID of the VPC, to which the security group will be added
    :param name: The name of the security group
    :param tag: The tag of the security group
    :param description: A description of the purpose of the security group

    :return: The ID of the newly created security group
    '''

    try:
        return EC2.create_security_group(
                Description = description,
                GroupName = name,
                VpcId = vpc_id,
                TagSpecifications = [
                    {
                        'ResourceType': 'security-group',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': name
                                }
                            ]
                        }
                    ]
                )['GroupId']

    except ClientError as client_error:
        logging.error(client_error)



def add_inbound_rule(security_group_id: str, protocol: str, port: int, ip_range: str, tag: str):
    '''
    Creates an inbound rule for the provided security group, allowing traffic from the provided IP range

    :param security_group_id: The ID of the security group, to which an inbound rule will be created
    :param protocol: The IP protocol name
    :param port: The port for which the inbound rule will be created
    :param ip_range: The range of IP addresses, which will be able to access the specified port
    :param tag: The tag for the new security group rule

    :return: None
    '''

    try:
        EC2.authorize_security_group_ingress(
                GroupId = security_group_id,
                IpPermissions = [
                    {
                        'IpProtocol': protocol,
                        'FromPort': port,
                        'ToPort': port,
                        'IpRanges': [
                            {
                                'CidrIp': ip_range
                                }
                            ]
                        }
                    ],
                TagSpecifications = [
                    {
                        'ResourceType': 'security-group-rule',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': tag
                                }
                            ]
                        }
                    ]
                )

    except ClientError as client_error:
        logging.error(client_error)



def create_database_subnet_group(group_name: str, group_tag: str, group_description: str, subnet_ids: list):
    '''
    Creates a database subnet group, using the provided subnet IDs

    :param group_name: The name of the database subnet group to be created
    :param group_description: A description of the purpose of the database subnet group
    :param subnet_ids: A list of subnet IDs which will be used to create a database subnet group

    :return: None
    '''

    try:
        RDS.create_db_subnet_group(
                DBSubnetGroupName = group_name,
                DBSubnetGroupDescription = group_description,
                SubnetIds = subnet_ids,
                Tags = [
                    {
                        'Key': 'Name',
                        'Value': group_tag
                        }
                    ]
                )

    except ClientError as client_error:
        logging.error(client_error)



def create_database(database_name: str, database_instance_identifier: str, storage_capacity: int,
        db_instance_class: str, db_engine: str, username: str, password: str, security_group_id: str,
        db_subnet_group_name: str, name_tag: str):
    '''
    Create a database instance, within Amazon RDS, using the provided parameters.

    :param database_name: The name of the database to be created
    :param database_instance_identifier: The name used to identify the database instance created
    :param storage_capacity: The storage capacity allocated to the database, prior to autoscaling
    :param db_instance_class: The instance class of the database to be generated
    :param db_engine: The database engine to be utilized
    :param username: The username of the Master user
    :param password: The password of the Master user
    :param security_group_id: The ID of the VPC security group, handling inbound and outbound access rules
                              for the database
    :param db_subnet_group_name: The group of subnets, within which the database will reside
    :param name_tag: The name tag for the database instance

    :return: None
    '''

    try:
        RDS.create_db_instance(
                DBName = database_name,
                DBInstanceIdentifier = database_instance_identifier,
                AllocatedStorage = storage_capacity,
                DBInstanceClass = db_instance_class,
                Engine = db_engine,
                MasterUsername = username,
                MasterUserPassword = password,
                VpcSecurityGroupIds = [
                    security_group_id
                    ],
                DBSubnetGroupName = db_subnet_group_name,
                MultiAZ = True,
                AutoMinorVersionUpgrade = False,
                PubliclyAccessible = True,
                Tags = [
                    {
                        'Key': 'Name',
                        'Value': name_tag
                        }
                    ],
                StorageType = "standard",
                StorageEncrypted = False
                )

    except ClientError as client_error:
        logging.error(client_error)



def get_database_endpoint(database_instance_identifier: str):
    '''
    Waits until the provided database is finished being created.
    Then, returns the endpoint for the database.

    :param database_instance_identifier: A user-defined identifier, to locate a specific
                                         database instance

    :return: The endpoint for the created database
    '''

    try:
        db_waiter = RDS.get_waiter('db_instance_available')
        print("\nWaiting for active status of the database...")
        db_waiter.wait(DBInstanceIdentifier = database_instance_identifier)
        print("\n{} is active".format(database_instance_identifier))

        return RDS.describe_db_instances(
                DBInstanceIdentifier = database_instance_identifier
                )['DBInstances'][0]['Endpoint']['Address']

    except ClientError as client_error:
        logging.error(client_error)



def main():
    '''
    Creates a database and associated security group with the following command
    line arguments:

    database.py <stack_name> <db_instance_name> <db_name> <username> <password>

    :CLI arg stack_name: The name of the cloud stack, from which the VPC ID will
                         be garnered
    :CLI arg db_instance_name: The name of the instance of the database to be generated
    :CLI arg db_name: The name of the database to be generated
    :CLI arg username: The master username for the database
    :CLI arg password: The password for the master user of the database
    '''

    stack_name = sys.argv[1]
    vpc_id, public_subnet1_id, public_subnet2_id, private_subnet1_id, private_subnet2_id = \
            cloudstack.get_vpc_subnet_ids(stack_name)

    db_instance_name = sys.argv[2]
    db_sg_name = db_instance_name + "_security_group"
    db_sg_tag = db_sg_name.replace("_", "-")
    db_sg_description = "Security group for {}, which will be accessed by EKS".format(db_instance_name)
    db_sg_id = create_security_group(vpc_id, db_sg_name, db_sg_tag, db_sg_description)

    protocol = "tcp"
    db_port = 3306
    public_ip_range = "0.0.0.0/0"
    inbound_rule_tag = db_sg_tag + "-inbound-rule"
    add_inbound_rule(db_sg_id, protocol, db_port, public_ip_range, inbound_rule_tag)

    subnet_group_name = db_instance_name + "_subnet_group"
    subnet_group_tag = subnet_group_name.replace("_", "-")
    subnet_group_description = "Subnet group for {}".format(db_instance_name)
    create_database_subnet_group(subnet_group_name, subnet_group_tag, subnet_group_description,
            [public_subnet1_id, public_subnet2_id])

    db_name = sys.argv[3]
    storage_capacity = 20
    db_instance_class = "db.t2.micro"
    db_engine = "mariadb"
    username = sys.argv[4]
    password = sys.argv[5]
    db_tag = db_instance_name.replace("_", "-")
    create_database(db_name, db_instance_name, storage_capacity, db_instance_class, db_engine,
            username, password, db_sg_id, subnet_group_name, db_tag)



if __name__ == "__main__":
    main()
