Pytheas guide utilisateur
======

***Guide utilisateur de l'application en ligne Pytheas***

**http://pytheas.cortext.net**

Pytheas est une interface simplifiée de téléchargement de données youtube via l'API youtube Data V3 fournis par les services Google.

------------------------------------------

[TOC]

------------------------------------------


## Lexique et mots-clés
* Concepts API :
	* API 
	* clé api
	* parts
* Ressources :
	* requêtes
	* liste de vidéos
		* vidéo
		* channel
		* playlist 
		* vidéos arbitraire
	* commentaires
	* sous-titres
* Methodes de recoltes
	* recherche par ressources (voir section 'ressources')
	* moteur de recherche Youtube
	* recherche horodaté
* Données produites :
	* liste de vidéos
	* liste de commentaires
	* liste de sous-titre






## Presentation pytheas

Pytheas simplifie téléchargement de données liés a youtube. Entres autres : 

- données liés aux vidéos
- données des commentaires
- données des sous-titres
- données liés aux auteurs (en cours)


La méthodologie générale est la suivante :
1. On télécharge un ensemble de vidéos selon certains paramètre (chaine, search, playlist ou list custom) 
"Download list of videos"
2. Une fois l'ensemble de vidéos téléchargés on peut aggreger certaines données complentaires choisis (commentaires, sous-titres)
"Aggregate data"
3. On télécharge nos sets de données en JSON
"Manage data"








## Google api

https://console.developers.google.com/apis

![Image of Yaktocat](./img/console_dev.png)

Un set complet d'API, fournis par les services de Google

Possible d'activer via son compte google, l'acces aux API Youtube : il existe 3 API pour Youtube, celle qui nous interesse :  
**Youtube DATA API v3** 

https://console.developers.google.com/apis/library/youtube.googleapis.com?q=youtube%20data&id=125bab65-cfb6-4f25-9826-4dcc309bc508&project=api-project-154609&folder&organizationId

![Image of Yaktocat](./img/select_api.png)

Une fois activée, il nous faut recuperer, une ***clé api***. Celle-ci va nous permettre de nous authentifier aupres de Google, pour pouvoir acceder aux données via Pytheas.


![Image of Yaktocat](./img/config.png)




## Exploration 

https://pytheas.cortext.net/explore

Permettre simplement la vue en données que nous  montre Google, pour : 

- une vidéo
- un chaine
- une playlist








## Méthode et requetes de récoltes

Une **requête** dans pytheas correspond à un ensemble de vidéos delimités selon critères.

### par moteur de recherche youtube
https://pytheas.cortext.net/search

Utilisation du moteur de recherche de youtube.

Par defaut entre 500 et 1000 videos (dont une pertinence forte pour les 500 première seulement). Correspond à la copie du moteur de recherche youtube.

Necessite une langue.

* recherche horodaté
La recherche horodaté permet de repeter une requete du moteur de recherche de youtube en le calibrant sur une journée. Cela permet ainsi d'etendre considerablement les sets recoltés au pris de la baisse en pertinence.

### par chaines
https://pytheas.cortext.net/channel

Recherche de vidéos par chaine youtube.

### par playlist
https://pytheas.cortext.net/playlist

Recherche de vidéos par chaine playlist.

### par liste de vidéos arbitraires
https://pytheas.cortext.net/videos-list

Egalement possible de récolté en fonction de listes de vidéos données arbitrairement.








## Recoltes de données

#### liste de vidéos

1 vidéos appartient à une requête

(peut être = 1)


#### liste de commentaires associés à un set de liste de vidéos

1 commentaires est toujours liée à une vidéo.


#### liste de sous-titres associés à un set de liste de vidéos







## Exportation des données

http://pytheas.cortext.net/manage
JSON 





