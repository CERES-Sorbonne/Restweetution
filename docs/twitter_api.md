# 1. Fonctionnement
## 1.1 API Rest

La twitter API est une API rest classique, (donc requêtable avec des schémas d'uri ). 

Par souci de clarté on parlera des sous parties de l'API en tant qu'API à part entière. 
>Par exemple, toutes les routes d'API commençant par `/users` pourront être appelées User API, alors qu'elles ne font toute partie que d'un même tout.
## 1.2 Compte

Il faut avoir un compte développeur sur twitter, ce qui implique d'avoir un compte twitter puis d'activer l'option développeur, et enfin de créer une app pour optenir les identifiants de connexion à l'API.

Il y est également possible de remplir un formulaire afin de bénéficier de l'offre de recherche qui permet d'obtenir plus de tweets chaque mois et en plus d'accéder à l'archive totale de tweeter.

## 1.3 Quotas

L'API est soumise à des quotas de requêtes, ainsi qu'a des quotas de nombre de tweets. C'est à dire que l'on pourra collecter au maximum un certain nombre de tweets par mois en fonction du type de compte, et effectuer au maximum un certains nombre de requêtes toutes les 15 min.

Pour un compte normal la limite est de 500 000 tweets collectés par mois, (que cela soit par API Rest ou par Stream API). Pour un compte de recherche on peut aller jusqu'à 10 000 000 tweets par mois.

Pour les quotas par types de requêtes, ils sont sensiblement les mêmes quel que soit le type de compte: 450 requêtes max en 15minutes pour la search api, 300 pour la full search, 300 pour les tweets counts, 300 pour les tweets, 300 pour les users. Ces différentes API seront détaillées plus loin. 

# 2. Comment récupérer des tweets ? 

Il existe un certain nombre de manières de collecter des tweets et leurs données associées.

On peut toutefois les diviser en deux grandes catégories: 
- Les requêtes individuelles à l'API Rest.
- La création d'un flux continu de collecte avec la Stream API.

## 2.1 L'API REST

L'API Rest offre différentes façons d'effectuer une collecte. Comme vu précédemment, l'usage en est assez simple et consiste à interroger twitter à l'aide d'une requête http dans du code ou dans un logiciel dédié. 

### 2.1.1 La Search API [🔗](https://developer.twitter.com/en/docs/twitter-api/tweets/search/api-reference/get-tweets-search-recent)

La search API est la manière la plus classique de récupérer des tweets, elle permet d'aller chercher tous les résultats correspondant à certains critères mais uniquement dans les 15 derniers jours. 

#### Lesdits critères sont les suivants: 
- chercher tous les tweets contenant un ou plusieurs mots clés
- préciser si le tweet doit avoir des media attachés ou non et si oui spécifier le type de media
- filtrer en fonction d'un ou plusieurs auteurs
- filtrer en fonction de la langue des tweets (celle ci est détectée automatiquement par twitter)
- faire une recherche par named entity
- filtrer par hashtag
- prendre en compte ou non le retweets
- tous ces filtres sont combinables avec des opérateurs logiques

> NB: Si la search API est de base limitée à un historique de 15 jours, avoir un compte de recherche permet d'accéder à l'historique total depuis les débuts de twitter.

### 2.1.2 La User Timeline API [🔗](https://developer.twitter.com/en/docs/twitter-api/tweets/timelines/quick-start)

Cette API permet de récupérer tous les contenus tweeter liés à la timeline d'un utilisateur, ses tweets, retweets, ainsi que les tweets où il peut être mentionné. Cela revient à utiliser la Search API avec un filtre sur l'utilisateur, mais de façon plus simple et en incluant les mentions. 

### 2.1.3 La Tweet API [🔗](https://developer.twitter.com/en/docs/twitter-api/tweets/lookup/quick-start)

Cette API est plus spécifique au sens où elle ne permet de récupérer que les tweets dont on a déjà l'id. 
L'id d'un tweet peut être obtenu dans l'url du tweet. L'appel à cette API en spécifiant un ou plusieurs id de tweets permet ensuite de récupérer de nombreuses informations complémentaires et de les stocker.

## 2.2 La Stream API

Là ou l'API REST nous permet de récupérer des données de façon momentané (une requête = un ensemble de résultats), la Stream API permet elle de se connecter à un flux de résultats de tweets et de les récupérer au fur et à mesure de leur publication. C'est le moyen le plus fiable de récupérer toutes les données possibles (alors que certains tweets ne seront plus accessibles à l'aide de la search api si ils ont été supprimés entre le moment de leur publication et le moment où l'on fait la requête). 
Cela dit cette techniquement est un peu plus complexe à mettre en plus puisqu'elle implique de créer le stream, puis de s'y connecter et ensuite de stocker les données lors de leur réception.

### 2.2.1 Configuration du stream

On peut appliquer à un stream exactement les mêmes filtres que ceux décrits [ici](#lesdits-criteres-sont-les-suivants).

> N.B Il est également possible de modifier les filtres du stream **pendant** la collecte. 

> N.B L'un des risques de la méthode du Stream est l'interruption, par exemple une coupure réseau peut interrompre la réception des données ou encore un bug quelconque de la machine ou du processus qui est connecté au stream... Pour pallier à cela, Twitter propose aux comptes de recherche de lancer deux processus en parallèle pour que l'un tourne toujours si l'autre plante, et également de récupérer jusqu'à 5 minutes de données manquantes en cas d'interruption.

# 3. Que peut on récupérer exactement ? 

Viennent d'être présentées les différentes manières de collecter des tweets, on s'intéressera ici à ce que contiennent ou peuvent contenir les tweets récupérés.

## 3.1 Données de tweet [🔗](https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/tweet)

Les données retournées par défaut lorsque l'on collecte un tweet sont minimes; seuls l'id du tweet et le contenu textuel sont retournés.

On peut cependant sélectionner un certain nombre d'informations supplémentaires à l'aide de paramètres lors de la requête appelés tweet.fields. (et spécifiés sous forme de query string). 

Les informations additionnelles sont les suivantes: 
- **le type du tweet:** le tweet est il une réponse ? une citation ? un tweet simple ? un retweet ?     
- **la langue:** détectée automatiquement par twitter.
- **les urls dépliées:** les urls des tweets sont automatiquement raccourcies, ce champ permet d'obtenir la version complète.
- **l'id de l'auteur:** l'id identifiant l'utilisateur qui a tweeté.
- **les stats publiques:** le nombre de likes, de retweets, de commentaires, de citations.
- **les stats implicites:** le nombre de vues du tweet, le nombre de personnes qui sont allés voir le profil de l'auteur après lecture du tweet et le nombre de personnes ayant cliqué sur un lien du tweet si il y en avait un.
- **les entités nommées:** les entités (personnalités, marques, pays, entreprises...) reconnus automatiquement par twitter, ainsi que les catégories associées.
- **l'id du premier tweet du thread:** si jamais le tweet provient d'un thread, cela permet de retrouver le tweet originel et de récupérer le thread entier à partir de là.
- **la plateforme depuis laquelle le tweet a été publié:** Twitter web, mobile, app externe...
- **la date de publication du tweet**: .
- **les id des pièces jointes:** si il y a des pièces jointes, leurs ids. A noter que les pièces jointes peuvent être des media (vidéo, photo, gif) ou des sondages.
- **scope de réponse:** savoir qui a le droit de répondre au tweet, personne, tout le monde, followers, les users cités dans le tweet ? 
- **suspension:** le tweet a-t-il été suspendu dans certains pays ? 
- **lieu:** twitter permet de préciser un lieu au moment de tweeter, le cas échéant cette information est également disponible.

Toutes ces informations peuvent encore être complétées en utilisant d'autres paramètres additionnels appelé tweet.extensions. Elles permettent notamment d'enrichier avec les données utilisateur ainsi que les données des media. 

## 3.2 Données d'utilisateur [🔗](https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/user)

En plus de l'id de l'auteur du tweet on peut également récupérer les données suivantes:

- **le pseudo:** le nom affiché sur le tweet, il peut être changé et il est non unique.
- **le  @:** il est unique et ne peut être changé.
- **la date de création**
- **la bio:** la description écrite par l'utilisateur pour se présenter. Il est également possible de récupérer à part les urls, hashtags, et entitées nommées présentes dans la description de l'utilisateur. 
- **le tweet épinglé:** le tweet qui s'affiche en haut du profil d'un utilisateur.
- **l'url de la photo de profil**
- **utilisateur vérifié ou non?:** un utilisateur vérifié est un utilisateur reconnu par twitter comme étant le compté vérifié d'une personnalité.
- **utilisateur privé ou non?:** le profil de l'utilisateur est il public ? 
- **les stats:** le nombre de followers, le nombre de personnes qu'il follow, le nombre de tweets.
- **utilisateur suspendu?**

## 3.3 Données de Media [🔗](https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/media)

En plus des id des media on peut également récupérer les données suivantes:

- **type:** video, photo, gif.
- **durée:** si le media est une vidéo.
- **hauteur du media en pixels**
- **largeur du media en pixels**
- **pourcentage de visionnage:** pour une vidéo, combien de users ont regardé 0%, 25%, 50%, 75%, 100% ?
- **url vers la ressource:** permet de récupérer le fichier. 
- **description de l'image:**  si le media est une image des utilisateurs peuvent ajouter parfois une légende à cette image.

# 4. Bonne pratiques lors d'une collecte

## 4.1 Utiliser la tweet count API [🔗](https://developer.twitter.com/en/docs/twitter-api/tweets/counts/introduction)

Cette API permet de savoir à l'avance les stats sur la collecte que l'on va lancer (pour une collecte en utilisant l'API Rest et non le Stream), cela permet d'appréhender le volume de tweets par jour / heure / minute que l'on va avoir en lançant la recherche. 

Utiliser cette API avant de lancer la collecte est ainsi une bonne pratique pour estimer le stockage nécessaire à l'effectuer ou encore pour savoir si le volume récolté va pouvoir être traité à la main ou non.

## 4.2 Autres bonnes pratiques

- Enregistrer lors d'une collecte la requête qui a permis d'obtenir les résultats.
- Lancer la collecte sur un serveur pour éviter les redémarrages de l'ordinateur, ou les coupures internet (les serveurs ou sont souvent hébergés dans des environnements avec de meilleurs réseaux). 
- En cas de modification des filtres d'une collecte par stream: noter et dater les modifications.
- Travail préalable afin de déterminer les informations à récolter (gain de place et de temps si l'on a pas besoin de tout).
- Choisir en fonction du cas d'usage le mode de collecte.
- Utiliser un compte de recherche si possible.
- Bien réfléchir au préalable aux problématiques de stockage de la collecte.

