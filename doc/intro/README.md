# Intro

* [What is with Pytheas for youtube ?](#What-is-Pytheas-for-Youtube-?) 
* [How to do with Pytheas for youtube ?](#How-to-do-with-Pytheas-for-youtube-?)
* [Methodology](#Methodology)
* [Get by Google the api Youtube Data V3 Key](#Get-by-Google-the-api-Youtube-Data-V3-Key)


## What is Pytheas for Youtube ?

Pytheas is an online interface designed to simplify and enhance the downloading of data related to youtube. 

Pytheas is linked to ** the youtube Data V3 ** API, provided by Google, which gives access to the following data: videos, authors' channels, playlist, comments, subtitles, etc.

## How to do with Pytheas for youtube ?

With the use of a [**free key provided by Google**](http://pytheas.cortext.net/manage) you will be **able to explore, gather and exporting data responded by Youtube**. 

Like **videos/channel/playlist** ; Possibly **horodated by a search query**. Including **comments and subtitles** if exists. Dowbloading them as **Json**.

## Methodology

The general methodology is as follows:
1.We download a set of videos according to some parameters (channel, search, playlist or list custom)
"Download list of videos"
2. Once the set of downloaded videos can be aggreger selected data chosen (comments, subtitles)
"Aggregate data"
3. We download our datasets in JSON
"Manage data"

## Get by Google the api Youtube Data V3 Key 

https://console.developers.google.com/apis

![Image of Yaktocat](../img/console_dev.png)

A complete set of APIs, provided by Google services

Possible to activate via its google account, access to Youtube APIs: there are 3 APIs for Youtube, the one we are interested in: 
**Youtube DATA API v3** 

https://console.developers.google.com/apis/library/youtube.googleapis.com?q=youtube%20data&id=125bab65-cfb6-4f25-9826-4dcc309bc508&project=api-project-154609&folder&organizationId

![Image of Yaktocat](../img/select_api.png)

Once activated, we need to recover, a ***key api***. This will allow us to authenticate with Google, to access data via Pytheas.

![Image of Yaktocat](../img/config.png)