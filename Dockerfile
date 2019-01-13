FROM python:3.6

RUN mkdir -p /usr/src/frf
WORKDIR /usr/src/frf

COPY requirements.txt .
RUN pip install -U -r requirements.txt

EXPOSE 8000