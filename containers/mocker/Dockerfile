FROM python:3.8-slim-buster

COPY requirements.txt mocker.py job.py errors.py /

RUN pip3 install -r requirements.txt

ENV PYTHONUNBUFFERED=1

CMD ["python3", "-u", "mocker.py"]