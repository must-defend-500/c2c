import base64
import hashlib
import hmac
import os
import re
import time
import boto3
import boto #this is for ViewFile

from django.shortcuts import render
from rest_framework import permissions, status, authentication
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views import View
from django.contrib import messages
from .config_aws import (
    AWS_UPLOAD_BUCKET,
    AWS_UPLOAD_REGION,
    AWS_UPLOAD_ACCESS_KEY_ID,
    AWS_UPLOAD_SECRET_KEY,

)
from boto.s3.connection import OrdinaryCallingFormat

from .models import FileItem

class AWSDownload(object):
    access_key = None
    secret_key = None
    bucket = None
    region = None
    # expires = getattr(settings, 'AWS_DOWNLOAD_EXPIRE', 5000)
    expires = 5000

    def __init__(self,  access_key, secret_key, bucket, region, *args, **kwargs):
        self.bucket = bucket
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        super(AWSDownload, self).__init__(*args, **kwargs)

    def s3connect(self):
        conn = boto.s3.connect_to_region(
                self.region,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                is_secure=True,
                calling_format=OrdinaryCallingFormat()
            )
        return conn

    def get_bucket(self):
        conn = self.s3connect()
        bucket_name = self.bucket
        bucket = conn.get_bucket(bucket_name)
        return bucket

    def get_key(self, path):
        bucket = self.get_bucket()
        key = bucket.get_key(path)
        return key

    def get_filename(self, path, new_filename=None):
        current_filename =  os.path.basename(path)
        if new_filename is not None:
            filename, file_extension = os.path.splitext(current_filename)
            escaped_new_filename_base = re.sub(
                                            '[^A-Za-z0-9\#]+',
                                            '-',
                                            new_filename)
            escaped_filename = escaped_new_filename_base + file_extension
            return escaped_filename
        return current_filename

    def generate_url(self, path, download=False, new_filename=None):
        file_url = None
        aws_obj_key = self.get_key(path)
        if aws_obj_key:
            headers = None
            if download:
                filename = self.get_filename(path, new_filename=new_filename)
                headers = {
                    'response-content-type': 'application/force-download',
                    'response-content-disposition':'attachment;filename="%s"'%filename
                }
            file_url = aws_obj_key.generate_url(
                                response_headers=headers,
                                 expires_in=self.expires,
                                method='GET')
        return file_url

class ViewFile(View):
    #path = "https://s3-us-west-2.amazonaws.com/c2c-success/c2c.ai/164/164.pdf"
    # path = "c2c.ai/164/164.pdf"

    def get(self, request, *args, **kwargs):
        path = "c2c.ai/164/164.pdf"
        aws_dl_object =  AWSDownload(AWS_UPLOAD_ACCESS_KEY_ID, AWS_UPLOAD_SECRET_KEY, AWS_UPLOAD_BUCKET, AWS_UPLOAD_REGION)
        file_url = aws_dl_object.generate_url(path)
        print(file_url)
        return render(request, "profile.html", {"html_var": True, "source_url": file_url})

class FileUploadCompleteHandler(APIView):
 permission_classes = [permissions.IsAuthenticated]
 authentication_classes = [authentication.SessionAuthentication]

 def post(self, request, *args, **kwargs):
     file_id = request.POST.get('file')
     size = request.POST.get('fileSize')
     course_obj = None
     data = {}
     type_ = request.POST.get('fileType')
     if file_id:
         obj = FileItem.objects.get(id=int(file_id))
         obj.size = int(size)
         obj.uploaded = True
         obj.type = type_
         obj.save()
         data['id'] = obj.id
         data['saved'] = True
     return Response(data, status=status.HTTP_200_OK)

class FilePolicyAPI(APIView):
    """
    This view is to get the AWS Upload Policy for our s3 bucket.
    What we do here is first create a FileItem object instance in our
    Django backend. This is to include the FileItem instance in the path
    we will use within our bucket as you'll see below.
    """
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.SessionAuthentication]

    def post(self, request, *args, **kwargs):
        """
        The initial post request includes the filename
        and auth credientails. In our case, we'll use
        Session Authentication but any auth should work.
        """
        filename_req = request.data.get('filename')
        if not filename_req:
                return Response({"message": "A filename is required"}, status=status.HTTP_400_BAD_REQUEST)
        policy_expires = int(time.time()+5000)
        user = request.user
        username_str = str(request.user.username)
        """
        Below we create the Django object. We'll use this
        in our upload path to AWS.

        Example:
        To-be-uploaded file's name: Some Random File.mp4
        Eventual Path on S3: <bucket>/username/2312/2312.mp4
        """
        file_obj = FileItem.objects.create(user=user, name=filename_req)
        file_obj_id = file_obj.id
        upload_start_path = "{username}/{file_obj_id}/".format(
                    username = username_str,
                    file_obj_id=file_obj_id
            )
        _, file_extension = os.path.splitext(filename_req)
        filename_final = "{file_obj_id}{file_extension}".format(
                    file_obj_id= file_obj_id,
                    file_extension=file_extension

                )
        print("upload start "+upload_start_path)
        print("filename_final "+filename_final)
        """
        Eventual file_upload_path includes the renamed file to the
        Django-stored FileItem instance ID. Renaming the file is
        done to prevent issues with user generated formatted names.
        """
        final_upload_path = "{upload_start_path}{filename_final}".format(
                                 upload_start_path=upload_start_path,
                                 filename_final=filename_final,
                            )
        print("final upload path "+final_upload_path)

        if filename_req and file_extension:
            """
            Save the eventual path to the Django-stored FileItem instance
            """
            file_obj.path = final_upload_path
            file_obj.save()

        policy_document_context = {
            "expire": policy_expires,
            "bucket_name": AWS_UPLOAD_BUCKET,
            "key_name": "",
            "acl_name": "private",
            "content_name": "",
            "content_length": 524288000,
            "upload_start_path": upload_start_path,

            }
        policy_document = """
        {"expiration": "2019-01-01T00:00:00Z",
          "conditions": [
            {"bucket": "%(bucket_name)s"},
            ["starts-with", "$key", "%(upload_start_path)s"],
            {"acl": "%(acl_name)s"},

            ["starts-with", "$Content-Type", "%(content_name)s"],
            ["starts-with", "$filename", ""],
            ["content-length-range", 0, %(content_length)d]
          ]
        }
        """ % policy_document_context
        aws_secret = str.encode(AWS_UPLOAD_SECRET_KEY)
        algorithm = 'AWS4-HMAC-SHA256'
        policy_document_str_encoded = str.encode(policy_document.replace(" ", ""))
        url = 'https://{bucket}.s3-{region}.amazonaws.com/'.format(
                        bucket=AWS_UPLOAD_BUCKET,
                        region=AWS_UPLOAD_REGION
                        )

        policy = base64.b64encode(policy_document_str_encoded)
        signature = base64.b64encode(hmac.new(aws_secret, policy, hashlib.sha1).digest())
        data = {
            "policy": policy,
            "signature": signature,
            "key": AWS_UPLOAD_ACCESS_KEY_ID,
            "file_bucket_path": upload_start_path,
            "file_id": file_obj_id,
            "filename": filename_final,
            "url": url,
            "username": username_str,
            "final_upload_path": final_upload_path
        }
        return Response(data, status=status.HTTP_200_OK)
