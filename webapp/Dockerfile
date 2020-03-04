# Base image.
FROM python:3.5

# Set the DEBIAN_FRONTEND environment variable only during the build
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update
RUN apt-get install nano -y

# copy scripts
RUN mkdir /opt/pytheas_webapp
COPY . /opt/pytheas_webapp

#prepare work directory
WORKDIR /opt/pytheas_webapp

# install flask & co
RUN pip install -r requirements.txt

# # prepare port
EXPOSE $PORT

# Define working volumes
VOLUME ["/opt/pytheas_webapp", "/opt/pytheas_webapp/data", "/opt/pytheas_webapp/conf","/opt/pytheas_webapp/logs" ]

#lauch app
CMD python main.py
