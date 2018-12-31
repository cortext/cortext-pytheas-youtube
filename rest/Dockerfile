# Base image.
FROM python:3.5

# Set the DEBIAN_FRONTEND environment variable only during the build
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update
RUN apt-get install nano -y

# copy scripts
RUN mkdir /opt/pytheas_rest
COPY . /opt/pytheas_rest

#prepare work directory
WORKDIR /opt/pytheas_rest

# install flask & co
RUN pip install -r requirements.txt

# prepare port
EXPOSE 5002

# Define working volumes
VOLUME ["/opt/pytheas_rest", "/opt/pytheas_rest/conf"]

#lauch app
CMD python rest.py
