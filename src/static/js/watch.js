
let currentlyEditing = false;

function onload() {
    const video = document.getElementsByTagName('video')[0];
    const volume = localStorage.getItem('volume');
    if (volume != null)
        video.volume = volume;

    video.addEventListener('volumechange', (e) => {
        localStorage.setItem('volume', e.target.volume);
    });

    const deleteDialog = document.getElementById('delete-dialog');
    if (typeof deleteDialog.showModal !== 'function') {
        favDialog.hidden = true;
        document.getElementById('error-dialog').hidden = true;
        /* a fallback script to allow this dialog/form to function
           for legacy browsers that do not support <dialog>
           could be provided here.
        */
    }

    const deleteModalBtm = document.getElementById('delete-video-modal');
    const deleteVideoBtn = document.getElementById('delete-video');
    const cancelChangesBtn = document.getElementById('cancel-changes');
    const editVideoBtn = document.getElementById('edit-video');

    document.getElementById('thumbsup-button').addEventListener('click', thumbs_button);
    document.getElementById('thumbsdown-button').addEventListener('click', thumbs_button);

    deleteModalBtm.addEventListener('click', (e) => {
        if (typeof deleteDialog.showModal === "function") {
            deleteDialog.showModal();
        } else {
            outputBox.value = "Sorry, the <dialog> API is not supported by this browser.";
        }
        e.preventDefault()
    });
    deleteVideoBtn.addEventListener('click', deleteVideo)
    editVideoBtn.addEventListener('click', toggleEditing)
    cancelChangesBtn.addEventListener('click', toggleEditing)
}

function deleteVideo(e) {
    new Promise(async (resolve) => {
        const res = await request(`/video/${e.target.dataset.videoid}`, {}, 'DELETE');
        if (res.status >= 300) {
            text = await res.text();
            try {
                showError(JSON.parse(text).message)
            } catch (_) {
                showError(text);
            }
        }
        else {
            location.replace('/')
        }
        e.preventDefault();
        resolve()
    })
}

function toggleEditing(e) {
    currentlyEditing = !currentlyEditing;
    const title = document.getElementById('title');
    const titleInput = document.querySelector('input[name="title"]')
    const description = document.getElementById('description');
    const descriptionInput = document.querySelector('textarea[name="description"]')

    const editingButtons = document.getElementById('editing-buttons')
    const notEditingButtons = document.getElementById('not-editing-buttons')

    titleInput.value = title.innerHTML;
    descriptionInput.value = description.innerHTML;

    title.hidden = currentlyEditing;
    description.hidden = currentlyEditing;
    notEditingButtons.hidden = currentlyEditing;
    titleInput.hidden = !currentlyEditing;
    descriptionInput.hidden = !currentlyEditing;
    editingButtons.hidden = !currentlyEditing;
    e.preventDefault();
}

function showError(error) {
    const errorDialog = document.getElementById('error-dialog');
    errorDialog.getElementsByClassName('error-message')[0].innerHTML = error;
    errorDialog.showModal();
}

async function thumbs_button(e) {
    const elem = e.target.parentElement;
    const video_id = elem.dataset.videoid;
    let rating = -1; // Defaults to thumbs down
    if (elem.id == 'thumbsup-button') {
        rating = 1 // Was a thumbs up!
    }
    let res;
    if (curr_rating === rating) {
        res = await request('/rate', {
            video_id,
        }, 'DELETE');
        curr_rating = 0;
    } else if (rating === 1) {
        res = await request('/rate/thumbsup', {
            video_id,
        });
        curr_rating = 1;
    } else {
        res = await request('/rate/thumbsdown', {
            video_id,
        });
        curr_rating = -1;
    }
    if (res.status === 500) {
        showError((await res.json()).message)
        return
    } else {
        update_ratings(video_id);
    }
    e.preventDefault();
}

async function add_comment(video_id) {
    const content = document.getElementById('comment-content');
    res = await request('/comment', {
        comment_video_id: video_id,
        content: content.value,
    }, 'POST')
    if (res.status === 500) {
        showError((await res.json()).message)
        return
    }

    content.value = "";

    comments = await (await fetch(`/comments/${video_id}`)).text()
    document.getElementById(`comments`).innerHTML = comments;
}

async function delete_comment(comment_id) {
    res = await request('/comment', {
        comment_id,
    }, 'DELETE');
    document.getElementById(`comment-${comment_id}`).remove();
}

async function update_ratings(video_id) {
    const res = await fetch(`/rate/get/${video_id}`);
    const ratings = await res.json();
    document.getElementById('thumbsups').innerHTML = ratings[0];
    document.getElementById('thumbsdowns').innerHTML = ratings[1];

    const thumbsup = document.getElementById('thumbsup-icon');
    const thumbsdown = document.getElementById('thumbsdown-icon');
    thumbsup.classList.remove('fa-thumbs-up', 'fa-thumbs-o-up');
    thumbsdown.classList.remove('fa-thumbs-down', 'fa-thumbs-o-down');
    thumbsup.classList.add((curr_rating === 1) ? 'fa-thumbs-up' : 'fa-thumbs-o-up');
    thumbsdown.classList.add((curr_rating === -1) ? 'fa-thumbs-down' : 'fa-thumbs-o-down');
}

async function request(url, data, method = 'POST') {
    const csrf_token = document.getElementsByName('csrf')[0].content;
    data = { csrf_token, ...data };

    const formData = new FormData();
    for (const key of Object.keys(data)) {
        formData.append(key, data[key]);
    }
    return fetch(url, {
        method,
        body: formData,
        headers: {
            accept: "application/json"
        }
    });
}