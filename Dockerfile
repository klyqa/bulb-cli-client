FROM python:3.9-slim

ADD bulb_cli.py /
ADD requirements.txt /

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["/bulb_cli.py"]
