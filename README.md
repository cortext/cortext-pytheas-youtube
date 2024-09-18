***ARCHIVED***
moved to https://gitlab.com/cortext/pytheas-youtube

# Pytheas from CorTexT

Pytheas is a webtool used to download youtube data from the latest api version
(v3) 

>  **[pytheas.cortext.net](https://pytheas.cortext.net)**

YouTube documentation : [developers.google.com/youtube/v3/docs](https://developers.google.com/youtube/v3/docs)

1.  [Installation](#installation)
2.  [Workflow](#workflow)
3.  [User guides and documentation](#user-guides-and-documentation)

### Objectives
- Explore YouTube from a "data point of view"
- Export requested data
- Make data analyzable by [CorTexT platform](https://managerv2.cortext.net/)

### Features
- Get videos, playlists, channels and search methods as queries
- Get Comments, captions, metrics and related videos from those queries
- Explore, manage and download it as JSON files

## Requirements
- **python3** as main language
- **mongodb** for database
- **docker/docker-compose** : container-app

#### File organisation
``` bash
Pytheas/
├── doc/
├── data/
├── logs/
    └── **activity_log.json**
├── scripts/
├── config/
    └── **config.json**
├── restapp/
├── webapp/
├── worker/
└── **docker-compose.yml**
```

## Installation
It is higly recommanded to instal and use it via Docker but it is still possible to install it as separated python processes (see [**python environment**](#python-environment) ) .

### Configuration file
You can here manage your paths, db name, machines names and port, fixe api_key, modify statue for debug and oauth.

- **DATA_DIR** and **LOG_DIR** need each a separated directory (fixed by default but can be moved)
- **PORT**, **MONGO**, **REST** and **WORKER** need each an assignated port number
- **api_key** : if you want to overide all query with an api key
- **api_key_test**: api key only for trying form on homepage
- **oauth_status** : True or False (deactive it for being on your own)
- **debug_level** : True or False

A normally **conf/conf-default.json** exist and can be copied as **conf/conf.json**. It should looked like this :

#### conf/conf.json
``` json
{
  "DATA_DIR": "data/",
  "LOG_DIR": "logs/",
  
  "PORT": 5050,
  "REDIRECT_URI": "http://localhost:5050/auth",
  "GRANT_HOST_URL": "https://my.own.oauth.server.com",

  "MONGO_HOST": "mongo",
  "MONGO_DBNAME": "youtube",
  "MONGO_PORT": 27017,
  
  "REST_HOST": "restapp",
  "REST_PORT": 5053,

  "WORKER_HOST": "worker",
  "WORKER_PORT": 5003,
  
  "api_key": "",
  "api_key_test": "",
  "oauth_status" : "True",
  "debug_level": "False"
}
```

### Dockers
On production server docker-compose file will follow this:

- **webapp**: front interface. Give orders that can be threaded to restapp
- **restapp**: make interface between webapp and restapp. Will be also used for an external opening
- **worker**: used to register all queries to database incoming from restapp
- **mongodb**: main database
- **mongodbclient**: client used to access db from http

#### docker-compose.yaml
``` yaml    
version: '3'
services:
  ## Back
  # mongo server
  mongo:
    container_name: py_mongoserver
    hostname: mongo
    image: "mongo:3.4"
    restart: always
    command: mongod
    ports:
     - "27017:27017"
    volumes: 
     - './data/mongo:/data/db'
    network_mode: bridge
  # restapp
  restapp:
    container_name: py_restapp
    hostname: restapp
    build: ./restapp/
    network_mode: bridge
    restart: always
    depends_on:
      - mongo
    links:
      - mongo
      - worker
    ports:
     - "5002:5002"
    volumes:
     - './restapp:/opt/pytheas_rest'
     - './conf:/opt/pytheas_rest/conf'
     - './logs:/opt/pytheas_rest/logs'
  # worker:
  worker:
    container_name: py_worker
    hostname: worker
    build: ./worker/
    network_mode: bridge
    restart: always
    ports:
     - "5003:5003"
    depends_on:
      - mongo
    links:
      - mongo
    volumes:
     - './worker:/opt/pytheas_worker'
     - './conf:/opt/pytheas_worker/conf'
     - './logs:/opt/pytheas_worker/logs'
  ## Front
  # mongo client
  mongoclient:
    container_name: py_mongoclient
    image: "mongoclient/mongoclient"
    restart: always
    ports:
     - "3000:3000"
    depends_on:
      - mongo
    links:
      - mongo
  # wepapp
  webapp:
    container_name: py_webapp
    hostname: webapp
    build: ./webapp/
    network_mode: bridge
    restart: always
    ports:
     - "5000:5000"
    depends_on:
     - restapp
    links:
      - restapp
      - mongo
    volumes:
     - './webapp/:/opt/pytheas_webapp'
     - './data:/opt/pytheas_webapp/data'
     - './logs:/opt/pytheas_webapp/logs'
     - './conf:/opt/pytheas_webapp/conf'
```

#### Python environment
For this variant please be sure 
``` bash
cd pytheas-youtube
virtualenv env3 -p python3
source ./env3/bin/activate
```
Then from two terminal and for each docker machine in separated terminal(webapp, restapp and worker) :
``` bash
pip install -R requirements.txt
python main.py
```

## First deployment 
From cloned repository (/pytheas-youtube) :
``` bash
docker-compose build
docker-compose start
```

You can also watch logs mannually first before:
``` bash
docker-compose up
```

## Workflow
### Update
In repository just git pull (machine have normally auto-reload):
``` bash
git pull
```

### Mandatory update
If configuration file, networks or dockers settings modified you have to rebuild:
``` bash
git pull
docker-compose stop
docker-compose build
docker-compose start
```

## User guides and documentation
Other helping ressources can be found on :
- [user guide](https://pytheas.cortext.net/documentation)
- [medium tutorial](https://medium.com/@bertacaro1996/pytheas-as-a-tool-to-get-youtubedata-3b238d698418) from @BerthaBrenes
- [developer documentation](https://gitlab.com/cortext/pytheas-youtube/wikis/home)

## To do
* [ ] threading management
* [ ] continue refactoring : verify each class from each machine (see youtube.py on webapp and worker)
* [ ] integrate external scripts from /script
* [ ] integrate doc in markdown from /doc
* [ ] better errorhandling (distinguish http error than each machine errors) and management
* [ ] integrate api openSpec and swagger file (see rest.py path)
* [ ] continue to integrate methods : channel as list (for description field) 
* [ ] new page to associate metrics, stats and other methods to analyze query (or set of queries?)
* [ ] script to manage conf file and docker port/location/name...
* [ ] combined to swagger file -> REST methods
* [ ] work UX
