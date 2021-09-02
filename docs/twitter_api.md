# 1. Fonctionnement
## 1.1 API Rest

## 1.2 Compte
## 1.3 Quotas

# 2. Que peut on récupérer ? 

Par défaut, très peu de données dispos, mais possibilités de préciser les champs avec tweet.fields et de récupérer aussi les images, les endroits, les users avec expansions

POUR UN TWEET NORMAL

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

POUR UN UTILISATEUR (apparemment récupréable directement dans la même requête que le tweet en passant le bon query string):
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

OBJECT MEDIA
- uuid
- type: video, photo, gif
- durée (quand vidéo)
- hauteur de l'image
- largeur de l'image
- pour une vidéo: combien de users ont regardé 0%, 25%, 50%, 75%, 100% ?
- url vers l'image de placeholder
- description de l'image si c'en est une et qu'il y en a une

Pour chercher des tweets on peut:
- chercher avec texte exact
- combiner les termes avec des OR ou AND
- préciser si le tweet doit avoir des images ou non
- préciser les auteurs potentiels
- préciser les langues
- faire une recherche par named entity dans twitter

3. Roadmap

Décider des infos exactes à récupérer
Décider de si on fait du streaming ou si on va chercher dans les tweets récents
Réfléchir au problème du stockage
Récupérer un compte de recherche
Regarder comment lancer plusieurs collectes en même temps
Déclencher la collecte par API
