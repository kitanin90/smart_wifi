FROM ubuntu:16.04

RUN apt-get -y update && apt-get -y install flow-tools && mkdir /var/log/flow
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

CMD /entrypoint.sh