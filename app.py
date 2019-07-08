import boto3
import configparser
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
app = Flask(__name__)

config = configparser.ConfigParser()
config.read('./config.ini')
ALLOWED_EXTENSIONS = set(['txt', 'png', 'jpg'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            put_in_s3(filename, file)


    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


def put_in_s3(filename, data):

    # determine the "AWS Profile", there are three options:
    # 1. the value is taken from ['AWS']['Profile'] or
    # 2. ...from ['DEFAULT']['Profile'] or
    # 3. ...from an ~/.aws/credentials [default]

    if True == config.has_option('AWS', 'Profile'):
      profile = config['AWS']['Profile']
    elif False == config.has_option('DEFAULT', 'Profile'):
      profile = 'default'

    # create an STS client object that represents a live connection to the
    # STS service

    sts_session = boto3.Session(profile_name=profile)
    sts_client = sts_session.client('sts')

    # Call the assume_role method of the STSConnection object and pass the role
    # ARN and a role session name.
    role_arn = config['AWS']['RoleArn']
    assumed_role_object = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName="AssumeRoleSession1"
    )

    # From the response that contains the assumed role, get the temporary
    # credentials that can be used to make subsequent API calls
    credentials = assumed_role_object['Credentials']

    # Use the temporary credentials that AssumeRole returns to make a
    # connection to Amazon S3
    s3_resource = boto3.resource(
        's3',
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'],
    )

    # Use the Amazon S3 resource object that is now configured with the
    # credentials to access your S3 buckets.
    s3_bucket = config['AWS']['BucketName']
    s3_resource.Bucket(s3_bucket).put_object(Key=filename, Body=data)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
