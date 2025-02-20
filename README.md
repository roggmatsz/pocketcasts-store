# pocketcasts-store
Python service that caches user playback and starred data from the Pocketcasts podcast player.

# TODO

~~Incrementally save listen records as new data is retrieved.~~

Use GitHub Actions to track version number.
- Update revision number only when making merges from a feature branch to staging.
- ~~Update minor number when completing PRs to main~~.
- ~~Update major at will.~~

Publish to Docker Hub on successful PR merge to main.

Create a function that looks for records with Size equal to 0, pulls podcast files to get their size in bytes, and stores the value in the episode's size field.

~~Dockerize script for deployment.~~
- Accept user-designated PIDs and GIDs.
- User Docker secrets to safely load Pocketcasts credentials into container.

Add performance unit tests.

Add logging logic that will cache all errors or stdout messages to separate SQLite file for monitoring.

~~Create unit testing suite.~~