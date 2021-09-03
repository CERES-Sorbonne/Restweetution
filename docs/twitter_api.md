# 1. Fonctionnement
## 1.1 API Rest

La twitter API est une API rest classique, (donc requêtable avec des schémas http )
## 1.2 Compte

Il faut avoir un compte développeur sur twitter, ce qui implique d'avoir un compte twitter et d'activer l'option développeur, puis de créer une app pour optenir les credentials de connexion. 

Il y a également possible de remplir un formulaire afin de bénéficier de l'offre de recherche qui permet d'obtenir plus de tweets chaque mois et en plus d'accéder à l'archive totale de tweeter.

## 1.3 Quotas

Pour un compte de recherche
10 000 000 tweets / mois
Accès à l'archive totale de tweeter (mais 1 requête seulement par seconde)

Il y a aussi des quotas par types de requêtes, 450 requêtes max en 15minutes pour la search api, 300 pour la full search, 300 pour les tweets counts, 300 pour les tweets, 300 pour les users

# 2. Que peut on récupérer ? 

Par défaut, très peu de données dispos, mais possibilités de préciser les champs avec tweet.fields et de récupérer aussi les images, les endroits, les users avec expansions et aussi les sondages

POUR UN TWEET NORMAL https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/tweet


Notes en vrac:
- les thread id sont dans le tweet (en fait c'est juste l'id du premier tweet ensuite il faut reconstruire le thread à partir des id de réponse)
- on a le type du tweet (reply, quote, tweet simple)
- on a les urls dépliées
- toutes les stats publiques
- les stats implicites (est ce que les gens sont allés voir le profil de l'auteur ? est ce qu'ils ont cliqué sur le lien dans le tweet ? )
- depuis quelle plateforme a été publié le tweet (mobile, web, autre ? )
- savoir si le tweet a été suspendu dans certains pays
- savoir le scope de réponse autorisé pour le tweet (qui peut répondre, tout lde monde ? les followers ? les gens cités ? )
- savoir si un tweet avec une url contient du contenu potentiellement sensible ? 
- la langue
- l'id de la personne à qui le tweet répond le cas échéant
- reconnaissance automatique d'entité et de topics avec scores de confiance
- l'id du tweet
- date de création
- les medias associés
- les lieux associés 

POUR UN UTILISATEUR (apparemment récupréable directement dans la même requête que le tweet en passant le bon query string): https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/user

- le pseudo
- le  @
- date de création
- description
- les hashtags
- les cashtags
- les lieux associés
- le tweet épinglé
- user privé ou non ? 
- l'url vers la pp
- les stats (followers, followés, nb tweets, listed_count (nb de listes dans lequels est le user))
- user vérifié ou non
- user suspendu ou non

OBJECT MEDIA https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/media

- uuid
- type: video, photo, gif
- durée (quand vidéo)
- hauteur de l'image
- largeur de l'image
- pour une vidéo: combien de users ont regardé 0%, 25%, 50%, 75%, 100% ?
- url vers l'image de placeholder
- description de l'image si c'en est une et qu'il y en a une

SEARCH API
https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-recent

- chercher avec texte exact
- combiner les termes avec des OR ou AND
- préciser si le tweet doit avoir des images ou non
- préciser les auteurs potentiels
- préciser les langues
- faire une recherche par named entity dans twitter


TWEET COUNT https://developer.twitter.com/en/docs/twitter-api/tweets/counts/introduction

- une api qui permet de savoir à l'avance les stats sur la collecte que l'on va lancer (pour une collecte non-stream ofc), cela permet d'appréhender le volume de tweets par jour / heure / minute que l'on va avoir en lançant la recherche. 
typiquement pour notre outil: permet de prévisualiser le volume de tweets de façon dyanmique juste avant de commencer à fetch

STREAM API https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/introduction

Avec un compte académique: possibilité de se connecter deux fois à la collecte (alors faut regarder en détail ce que ça veut dire, globalement ça permet j'imagine de connecter deux services en parallèle qui vont tous deux recevoir les données du stream pour pouvoir les écrire en base (il faudra juste gérer pour ne pas écrire de doublons systématiquement)) et ça permet de réduire les risques de pertes de données en cas de bug. Et si il y a effectivement un probleme de données, il existe un outil pour récupérer jusqu'à 5min de données perdues lors d'une déconnexion.

3. Roadmap

- Décider des infos exactes à récupérer
- Décider de si on fait du streaming ou si on va chercher dans les tweets récents
- Réfléchir au problème du stockage
- Récupérer un compte de recherche
- Regarder comment lancer plusieurs collectes en même temps
- Déclencher la collecte par API
- Rajouter petite interface ?
