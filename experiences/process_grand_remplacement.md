# Workflow

1. Create a stream with the REST API
2. Connect to the stream with a client (spawn in new process)
3. Write the tweets to disk

# Data to collect

- Tweet ID
- Tweet Message
- Tweet Images if any
- Author ID 
- More Author info if not already in base
- Nb of likes + retweets + reactions
- Reply to: to study clusters ? 
- Avoid Retweets ? 

# Infra

- One Client API to fetch tweets
- Images are stored in @Root_dir/images/image_id (detect duplicates with SHA-1) ? (store later in an Object Storage)
  - there will be a metadata.json for each image with the stored SHA-1 (later stored in document DB suchas mongo)
  - when storing an image check if medata.SHA-1 already exist, if yes then just increment the duplicate count of the image metadata
  - Le problème c'est de pouvoir retrouver facilement une image avec son id, et facilement avec son sha1
  - How to do for videos ? there is a thumbnail image: can we be sure that's it's unique for every video => turns out they can be changed manually => we'll use that anyway for now
- Videos are stored in @Root_dir/images
- Tweets are stored separated in @Root_dir/stream_tag/tweets/tweet_id and it's then easy to agregate them if needed
- maybe store images and videos in subprocess to handle tweets faster
- For now everything stored with fs (see later how to make it storage agnostic)
- Start Collect with storage size limit to avoid overflowing the disk, use: https://stackoverflow.com/a/1392549/4541360 to check directory size from time to time


Pour le moment petit hack pour les images:
- on stocke l'image à images/image_id et on stocke un fichier vide à images/sha1/image_id   du coup si un sha1 existe déjà, à la place de persister l'image dans images/image_id on stocke juste dans images/image_id l'id de "redirection"
- on verra avec une base documentaire comment rendre ça plus propre 