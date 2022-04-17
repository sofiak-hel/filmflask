
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
- `src/static` contains all of the `css` and `javascript` of this project in
  their respective folders.
- `src/templates` contains all of the `html`-templates used in the project.
- `src/templates/components` contains all smaller "components" used by the larger sites.

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

### Migration and large processing
For some reason heroku seems to have problems with large requests and long
migrations. For this reason they are run always on my local machine using the
remote heroku database. For my personal projects I would use docker-compose and
a cloud server instead of Heroku, but as I am forced to use this, this is how
I'm forced to deal with this problem.

## Progress, features and what is to come:

### Välipalautus 3
Since Välipalautus 2, a lot has happened:

**In addition to Välipalautus 2 the following functionality exists:**
- Added proper meta tags to everything, including previews for discord/twitter,
  and meta-information about the used charset and viewport for mobile users.
- A lot more CSS and JavaScript has been added to make the user experience
  smoother. 
  - Most requests no longer redirect the users and many of them give the user an
  informative pop-up if something goes wrong. The error pages have also been
  vastly improved.
  - Javascript has also been added to "remember" the volume level you had on
    your last video.
  - The mobile interface has been vastly improved, but it is still quite
    work-in-progress, as this project is first and foremost intended for desktop
    audiences.
  - New styling also makes use of forkawesome icons, which look good.
  - Footer has also been added, that links to the repository of this project.
- Users have default avatars that are generated for them when they first create
  their user. This is done by manually generating an array of bytes and then
  passing it to ffmpeg to process it to a jpeg image.
- Some sort of migration system has also been created where the program
  automatically checks for the current version of the schema and then runs said
  upgrade scripts automatically so that it can continue functionality as normal.
    - For example, this functionality adds default avatars to users with no avatars
- Videos can be edited and deleted after they have been uploaded
  - Doing so can be achieved via the video's own `/watch`-page by anyone who has
    the proper access to editing or deleting it.
  - Currently only the title and the description of the video can be edited.
  - Editing and deleting require the same role, or for you to be the uploader.
- There is now a proper authorization system that checks weather a user is
  authorized to do something.
  - Currently this only supports deleting comments and editing/deleting videos.
  - There are two roles by default, admin which can do anything and user that
    can do nothing.
  - Roles can not be edited via the front-end and must be done via `psql` for
    the time being.
  - This feature can be hard to demonstrate because of the security risks on
    heroku. If you feel the need to do so, please clone and run the project for
    yourself using the provided docker compose file.

**What I still would like to see implemented:**
- [ ] Making the `/subbox` more prevalent and at least having a link to it would
  certainly be a nice addition.
- [ ] I would like to see playlists exist before the final turn-in.
- [ ] Rating comments would be really good to see as well. I feel like they are somewhat important
- [ ] It would probably be good, if the uploader of the video could delete
  comments from it, if desired.
- [ ] The mobile interface still requires a lot of work. It would be great to see that as well.
- [ ] It would be very useful if assigning roles and editing them would be
  possible from the frontend as well.
- [ ] Soft-deleting users from the front-end could be useful.

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
- [X] Delete videos
- [X] Role-system
  - [X] Add administrative actions for users with said roles
  - [ ] Add possibility to soft-delete a user