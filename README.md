# pocketcasts-store
Python service that caches user playback and starred data from the Pocketcasts podcast player.

# TODO

~~Incrementally save listen records as new data is retrieved.~~

Create a function that looks for records with Size equal to 0, pulls podcast files to get their size in bytes, and stores the value in the episode's size field.

Dockerize script for deployment.

Create unit testing suite.