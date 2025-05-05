FROM python:3.13-slim

WORKDIR /hhru

COPY . .

RUN pip install -r requirements.txt

CMD python3 cli.py