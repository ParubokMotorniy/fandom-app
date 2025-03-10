FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
    glusterfs-server glusterfs-client apache2 apache2-utils bash util-linux coreutils iputils-ping && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /data /mnt/glusterfs && rm -rf /var/cache/apk/*

COPY entrypoint.sh entrypoint.sh
COPY setup.sh setup.sh

COPY fandomapp.uwu.conf /etc/apache2/sites-available/fandomapp.uwu.conf

RUN chmod +x entrypoint.sh setup.sh

# Expose GlusterFS and Apache ports
EXPOSE 24007 24008 49152 80 443

VOLUME ["/data"]

CMD ["entrypoint.sh && setup.sh"]
