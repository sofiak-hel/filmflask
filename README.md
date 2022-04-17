
## FilmFlask
FilmFlask is a video service made with Python and Flask for the Helsinki
University course [Tietokantasovellus](https://hy-tsoha.github.io/materiaali/).

FilmFlask aims to be quite similar to [YouTube](https://www.youtube.com/) and is
licensed under the [GPLv3 license](./LICENSE).

A demo is hosted on [Heroku](https://dashboard.heroku.com/) at
[https://filmflask.herokuapp.com/](https://filmflask.herokuapp.com/). It seems
that Heroku is limiting bandwidth to a degree that _might_ cause issues with
uploading and downloading videos

## Notes for the reviewer:

This project is structured in the following way:
- `src`-folder contains all of the code related the the project.
- `src/db` contains a abstraction layers to working with the postgres-database.
  Each file has one or more abstraction classes that are used, necessary
  postgres-calls are then defined below these classes.
- `src/pages` contains the actual routing code related to Flask
- `src/sql` contains the necessary sql to run this project. `init.sql` is an
  idempotent sql script that initializes the database and is ran every time the
  program launches. `shorts.json` is a dictionary mapping for all of the sql
  commands used in this project.
- `src/templates` contains all of the `html`-templates used in the project.

Further documentation _may_ be found within the files themselves.

### Image / Video storage
In this project videos and images are saved as `bytea` into the database. This
is usually an incredibly bad idea to do, but for the purposes of hosting this
project in Heroku, it must be done this way. Another solution would possibly be
to host the files on an external platform, but that would require relying on
external platforms and their expenses.

As the Heroku database is limited in capacity, the default video size limit is
5MB, which is more than enough for a lot of videos and is small enough to fit
around 200 videos of max size into the database.

## Progress, features and what is to come:

## Todo's since Välipalautus 2:
- [X] Currently the frontend is very clunky to use and very ugly. I would like to
  add more CSS and use more JavaScript to make the experience more smooth.
    - CSS has been slightly improved, and the user-experience as a whole has
      been improved by quite a bit with a little bit of javascript
- [X] Default avatars for users. Unsure if this should be done client-side or
  serverside.
- [ ] It would be useful, if the user could delete their videos after they have been
  uploaded.
- [ ] I want to add a role-system. Currently it already exists in the database, but
  is not used at all. This would allow some administrative actions without
  needing to do so through `psql` manually.
  - [ ] There is also a flag in the database for a deleted user, but it is not
    currently used. The idea is that a user could be "soft-deleted" through the
    admin-interface, so that they, their videos, comments or ratings are no
    longer visible. The user could still be re-instated if so desired.
- [X] I would like to add the possibility of editing video titles and descriptions
  even after they have been uploaded.
- [ ] Playlists and rating comments from the wanted features are also still missing,
  I would like to see those.
- [ ] If I have the time, email notifications would be a nice addition as well.

### Välipalautus 2
By Välipalautus 2 the project is looking pretty good already. 

**The following functionality exists right now**:
- User can login, logout and register. Logging in will use Flask's
  `session`-module to upkeep a session_id.
- CSRF-tokens are implemented, for each pageload a new CSRF token is generated
  and placed in appropriate forms. The CSRF-token is then checked in each
  `POST`-endpoint with annotations that are defined in `util.py`
- Users have user details defined in the MVP.
  - Users have a nickname, handle, bio and an avatar.
  - Nickname and bio are set when the user registers
  - Bio and avatar may be changed after registration at `/user/edit`.
- Videos exist according to the MVP.
  - They have a title, description and an upload time. No details can be changed
    after the video is uploaded.
  - Videos can be uploaded and their title, description and the video itself is
    set at this point. User must be logged in to upload a video.
  - Videos have a convenient page to view them at `/watch/<video_id>`, but the
    raw video itself can be found at `/video/<video_id>`
  - Videos are listed at the front page from newest to oldest.
  - Commenting videos is possible:
    - User must be logged in to do so
    - Comments can be deleted afterwards
    - Comments are displayed under the video in the `/watch`-page
  - Rating videos is possible:
    - User must be logged in to do so
    - User can either give a video a "thumbs up" or a "thumbs down".
    - If the user has already rated a video, they can delete their rating completely.
    - User may not rate a video multiple times, instead if they re-rate a video,
      their previous rating is replaced.
- Subscribing to users is possible
  - Users must be logged in to do so
  - Subscriber counts are visible on the user-page and on the `watch`-page
  - Users can Unsubscribe to delete their subscription
  - Users can see a list of the videos of the users they have subscribed to
    under the `/subbox`-page
- Users are able to search videos from the front page, they do not need to be
  logged in to do so.

**What I would still like add or modify:**
- This section has been replaced with the Todos since Välipalautus 2. It
  contains mostly the same things, but it's formatted in a list-format and has more details.

## Minimum Viable Product:
Minimum viable product for this use case means basically a simple and ugly
version of YouTube. The optimal version would be quite similar to YouTube itself
and might use JavaScript, but the minimal viable product it is not necessary.

This list is viewed as a checklist so that it may be checked along the
development of the product.

- [X] Login, logout
- [X] User details
    - [X] Nickname and handle separately (see twitter in comparison)
    - [X] Bio or description
    - [X] Profile picture
- [X] Uploading and viewing videos
    - [X] Must have a title, description and an upload time
    - [X] Commenting to said videos while logged in
    - [X] Rating said videos
- [X] Subscribing to other users
- [X] Browsing videos in the front page
  - [X] Including a subbox
- [X] User profiles showing their videos and details

### Wanted features, but not neceassarily included in the MVP:
- [X] Editing video titles and descriptions after upload
- [X] View counters (how to measure a view?)
- [ ] Rating comments
    - Even though this seems like a simple feature, it can actually take up
      quite a lot of time to implement correctly and efficiently.
- [X] Searching for videos
    - This seems like an easy feature, but contains some tricky questions, such
      as which things are considered in the search
- [ ] Playlists
    - This has some interesting things that need to be thought out before it can
      be done:
        - How are videos stored in the database? By index? As linked list?
    - [ ] This also would mean that playlists should probably be listed on the user
      details page.
- [ ] Suggested videos next to videos
    - This also seems like an easy feature, but what makes a video "relevant" to
      another?
- [ ] Email and notifications via email

### Later added wanted features:
- [ ] Delete videos
- [ ] Role-system
  - [ ] Add administrative actions for users with said roles
  - [ ] Add possibility to soft-delete a user