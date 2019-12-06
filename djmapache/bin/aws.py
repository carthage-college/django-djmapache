# -*- coding: utf-8 -*-

import os, sys
import boto3

# env
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djmapache.settings.shell")

from django.conf import settings

from botocore.exceptions import ClientError


def main():
    """
    """

    s3_client = boto3.client('s3')
    s3_resource = boto3.resource('s3')

    #session = boto3.Session(
        #aws_access_key_id="id",
        #aws_secret_access_key="secret",
        #region_name="us-east-1"
    #)
    #s3_resource = session.resource("s3")

    bucket_name='pg-carthage-prod-593'
    #s3.create_bucket(Bucket=bucket_name)
    liza = s3_resource.Bucket(bucket_name)

    try:
        # Upload a new file
        data = open('student.z.csv', 'rb')
        liza.put_object(Key='student.z.csv', Body=data)
    except Exception as e:
        print("put_object() method failed")
        print("Exception: {}".format(str(e)))

    print('list objects in bucket liza')
    for obj in liza.objects.all():
        print(obj.key, obj.last_modified)

    """
    obj = s3_resource.Object(bucket_name, "test.csv")
    obj.delete()

    print('list objects in bucket liza after delete')
    for obj in liza.objects.all():
        print(obj.key, obj.last_modified)
    """

    """
    # Print out bucket names
    try:
        for bucket in s3.buckets.all():
            print(bucket.name)
    except Exception as e:
        print("buckets.all() method failed")
        print("Exception: {}".format(str(e)))

    try:
        s3.list_buckets()
    except Exception as e:
        print("list_buckets() method failed")
        print("Exception: {}".format(str(e)))
    """


######################
# shell command line
######################

if __name__ == "__main__":

    sys.exit(main())
