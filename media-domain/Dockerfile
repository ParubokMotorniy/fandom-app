FROM debian:latest

RUN apt-get update && apt-get install -y glusterfs-server bash util-linux coreutils glusterfs-client iputils-ping && \
    apt-get clean && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /data /mnt/glusterfs && rm -rf /var/cache/apk/*

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

VOLUME ["/data"]

EXPOSE 24007 24008 49152

CMD ["/entrypoint.sh"]
