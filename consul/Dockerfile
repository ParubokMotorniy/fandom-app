FROM ubuntu:latest

RUN apt update && apt install curl -y

WORKDIR /registration/

COPY --chmod=666 ./3rdparty_services/* /registration/3rdparty_services/
COPY --chmod=777 ./consul_subscriber.sh /registration/

CMD ["/bin/sh" ,"/registration/consul_subscriber.sh" ]

