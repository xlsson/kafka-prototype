FROM debian:bullseye-slim

RUN apt-get update && apt-get -y install curl

COPY register.sh /

RUN chmod +x register.sh

CMD ["./register.sh"]