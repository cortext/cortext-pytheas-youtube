# Base image.
FROM python:3.5

# Set the DEBIAN_FRONTEND environment variable only during the build
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update
RUN apt-get install nano -y



# copy scripts
RUN mkdir /opt/pytheas
COPY . /opt/pytheas

WORKDIR /opt/pytheas

RUN pip install -r requirements.txt



EXPOSE 5000

# Define working volumes
VOLUME ["/opt/pytheas/data", "/opt/pytheas/conf"]

CMD python main.py
