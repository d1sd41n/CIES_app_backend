FROM python:3.6.3

ENV PYTHONUNBUFFERED 1
RUN mkdir /qr
ADD requirements.txt /qr/
WORKDIR /qr
RUN pip install -r /qr/requirements.txt
