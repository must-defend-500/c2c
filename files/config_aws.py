#Upload settings
AWS_UPLOAD_BUCKET = 'c2c-success'

AWS_UPLOAD_USERNAME = 'c2c_final'

AWS_UPLOAD_GROUP = 'c2c-success-group'

AWS_UPLOAD_REGION = 'us-west-2'

AWS_UPLOAD_ACCESS_KEY_ID = 'AKIAJVX2VDRFFOT6SUIA'

AWS_UPLOAD_SECRET_KEY = 'j1nzTsf1OvyHprmYbBIUb95iZgRceLyojHlYqose'

#Download settings
AWS_STORAGE_BUCKET_NAME = 'c2c-success'

S3DIRECT_REGION =  'us-west-2'

PROTECTED_DIR_NAME = '<your-in-bucket-dir-name>'
PROTECTED_MEDIA_URL = '//%s.s3.amazonaws.com/%s/' %( AWS_STORAGE_BUCKET_NAME, PROTECTED_DIR_NAME)

AWS_DOWNLOAD_EXPIRE = 5000 #(0ptional, in milliseconds)
