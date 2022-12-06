FROM ubuntu:22.04

RUN apt list --upgradable \
    && apt update \
    && apt upgrade -y \
    && apt autoremove -y \
    && apt install -y vim git curl iproute2 vim

# Make .aws directory
RUN mkdir /root/.aws /root/work

# Install the Python
RUN apt install -y python3 python3-pip

# Install the nodejs
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt update \
    && apt install -y nodejs

# Install the aws-cdk
RUN npm install -g aws-cdk aws-cdk-lib

# Copy AWS Config
ADD credentials /root/.aws/credentials
ADD config /root/.aws/config

WORKDIR /root/work

