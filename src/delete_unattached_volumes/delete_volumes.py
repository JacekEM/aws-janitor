import logging

import boto3


def lambda_handler(event, context):

    ec2 = boto3.client('ec2')
    ebs_volumes = ec2.describe_volumes(Filters=[{'Name': 'status', 'Values': ['available']}])['Volumes']
    excluded_ebs_volumes = ec2.describe_volumes(
        Filters=[{'Name': 'status', 'Values': ['available']},
                 {'Name': 'tag:Recycle', 'Values': ['False', 'false']}]
    )['Volumes']

    excluded_volumes_ids = [i['VolumeId'] for i in excluded_ebs_volumes]

    for vol in ebs_volumes:
        volume_id = vol['VolumeId']
        if volume_id not in excluded_volumes_ids:
            logging.info(f'deleting volume: {volume_id}')
            ec2.delete_volume(VolumeId=volume_id)
