FROM python:3.8-slim-buster

COPY requirements.txt topicconsumer.py messagepoller.py message.py /

RUN pip3 install -r requirements.txt

CMD ["python3", "-u", "topicconsumer.py"]