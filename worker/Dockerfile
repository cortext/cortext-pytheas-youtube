# Base image.
FROM python:3.5

# Set the DEBIAN_FRONTEND environment variable only during the build
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update
RUN apt-get install nano -y

# copy scripts
RUN mkdir /opt/pytheas_worker
COPY . /opt/pytheas_worker

#prepare work directory
WORKDIR /opt/pytheas_worker

# install flask & co
RUN pip install -r requirements.txt

# # prepare port
# EXPOSE 5003

# Define working volumes
VOLUME ["/opt/pytheas_worker", "/opt/pytheas_worker/conf", "/opt/pytheas_worker/logs"]

#lauch app
CMD python worker.py
