FROM python:3.13-slim
COPY . .

RUN pip install -r requirements.txt

CMD python3 main.py