FROM python:3.8-slim-buster

COPY requirements.txt app.py /

RUN pip3 install -r requirements.txt

ENV PYTHONUNBUFFERED=1

CMD ["python3", "-u", "app.py"]