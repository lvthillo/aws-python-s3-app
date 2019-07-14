# aws-python-s3-app
Python application which uses IAM role to put objects inside an S3 bucket.

Update the `config.ini` with the correct IAM role ARN and the name of the bucket to write to.
Details on how to create the role are described in [this tutorial](https://medium.com/@lvthillo/connect-on-premise-python-application-with-aws-services-using-roles-8b24ab4872e6).

### Start application
```
$ pip install virtualenv
$ virtualenv -p /usr/local/bin/python3.7 venv
$ source venv/bin/activate
$ pip3.7 install -r requirements.txt
$ python3.7 app.py
```
