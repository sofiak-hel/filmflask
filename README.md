
## FilmFlask
FilmFlask is a video service made with Python and Flask for the Helsinki
University course [Tietokantasovellus](https://hy-tsoha.github.io/materiaali/).

FilmFlask aims to be quite similar to [YouTube](https://www.youtube.com/) and is
licensed under the [GPLv3 license](./LICENSE).

## Minimum Viable Product:
Minimum viable product for this use case means basically a simple and ugly
version of YouTube. The optimal version would be quite similar to YouTube itself
and might use JavaScript, but the minimal viable product it is not necessary.

This list is viewed as a checklist so that it may be checked along the
development of the product.

- [ ] Login, logout
- [ ] User details
    - [ ] Nickname and handle separately (see twitter in comparison)
    - [ ] Bio or description
    - [ ] Profile picture
- [ ] Uploading videos
    - [ ] Must have a title, description and an upload time
    - [ ] Commenting to said videos while logged in
    - [ ] Rating said videos and comments
- [ ] Subscribing to other users
- [ ] Browsing videos in the front page, including a subbox
- [ ] User profiles showing their videos and details

### Wanted features, but not neceassarily included in the MVP:
- [ ] View counters (how to measure a view?)
- [ ] Searching for videos
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