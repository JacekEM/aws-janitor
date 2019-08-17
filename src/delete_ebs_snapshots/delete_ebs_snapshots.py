import datetime
import logging
import os

import boto3


snapshot_max_days = int(os.environ["snapshot_max_days"])


def is_past_max_age(snapshot_creation_time):

    return (datetime.datetime.now() - snapshot_creation_time.replace(tzinfo=None)).days > snapshot_max_days


def lambda_handler(event, context):

    ec2 = boto3.client('ec2')
    snapshots = ec2.describe_snapshots(OwnerIds=['self'])['Snapshots']
    excluded_snapshots = ec2.describe_snapshots(OwnerIds=['self'],
                                                Filters=[{'Name': 'tag:Recycle', 'Values': ['False', 'false']}])['Snapshots']

    excluded_snapshot_ids = [i['SnapshotId'] for i in excluded_snapshots]
    funny_state_snapshots = []
    for s in snapshots:
        snapshot_id = s['SnapshotId']
        if s["State"] != "completed":
            funny_state_snapshots.append(snapshot_id)
            logging.info(f'skipping snapshot: {snapshot_id}')

        elif snapshot_id not in excluded_snapshot_ids and is_past_max_age(s['StartTime']):
            logging.info(f'deleting snapshot: {snapshot_id}')
            ec2.delete_snapshot(SnapshotId=snapshot_id)
