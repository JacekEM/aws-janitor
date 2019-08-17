import datetime
from dateutil.parser import *
import logging
import os

import boto3

ami_max_days = int(os.environ["ami_max_days"])


def is_past_max_age(ami_creation_time):

    return (datetime.datetime.now() - parse(ami_creation_time).replace(tzinfo=None)).days > ami_max_days


def lambda_handler(event, context):

    ec2 = boto3.client('ec2')
    amis = ec2.describe_images(Owners=['self'])['Images']
    excluded_amis = ec2.describe_images(Owners=['self'],
                                        Filters=[{'Name':'tag:Recycle', 'Values':['False', 'false']}])['Images']
    excluded_amis_imageids = [i['ImageId'] for i in excluded_amis]

    for ami in amis:
        image_id = ami['ImageId']
        if ami["ImageId"] not in excluded_amis_imageids and is_past_max_age(ami['CreationDate']):
            logging.info(f'deregistering ami: {image_id}')
            ec2.deregister_image(ImageId=image_id)

