import boto3
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, COMMASPACE

def create_message(send_from, send_to, subject, plain_text_body, html_body):
    message = MIMEMultipart('alternative')
    message['From'] = send_from
    message['To'] = COMMASPACE.join(send_to)
    message['Date'] = formatdate(localtime=True)
    message['Subject'] = subject
    message.attach(MIMEText(plain_text_body, 'plain'))
    message.attach(MIMEText(html_body, 'html'))
    return message

def add_attachment_from_s3(message, bucket, key):
    client = boto3.client("s3")
    attachment = client.get_object(Bucket=bucket, Key=key)
    part = MIMEApplication(attachment["Body"].read(), Name=basename(key))
    part['Content-Disposition'] = 'attachment; filename="%s"' % basename(key)
    message.attach(part)


def add_attachment_from_local_disk(message, path):
    with open(path, "rb") as file:
        part = MIMEApplication(file.read(),Name=basename(path))
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(path)
        message.attach(part)


def send_message(message):
    client = boto3.client("ses")
    response = client.send_raw_email(RawMessage = {'Data': message.as_string()})


message = create_message(
    "sender@domain.com",
    ["recipient1@domain.com", "recipient2@domain.com"],
    "Testing",
    "Testing 123\nTesting 123\nTesting 123",
    "<html><head></head><body><h1>Testing 123</h1><p>testing 123</p></body></html>")
add_attachment_from_local_disk(message, 'C:\\path\\to\\local\\file.pdf')
add_attachment_from_s3(message, 'bucket_name', 'prefix/file.pdf')
send_message(message)
