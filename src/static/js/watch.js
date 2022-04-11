
function onload() {
    const video = document.getElementsByTagName('video')[0];
    const volume = localStorage.getItem('volume');
    if (volume != null)
        video.volume = volume;

    video.addEventListener('volumechange', (e) => {
        localStorage.setItem('volume', e.target.volume);
    });
}

async function thumbsup(video_id) {
    let res;
    if (curr_rating === 1) {
        res = await request('/rate/delete', {
            video_id,
        });
        curr_rating = 0;
    } else {
        res = await request('/rate/thumbsup', {
            video_id,
        });
        curr_rating = 1;
    }
    if (res.status === 500) {
        alert((await res.json()).message)
        return
    } else {
        update_ratings(video_id);
    }
}

async function thumbsdown(video_id) {
    if (curr_rating === -1) {
        res = await request('/rate/delete', {
            video_id,
        });
        curr_rating = 0;
    } else {
        res = await request('/rate/thumbsdown', {
            video_id,
        });
        curr_rating = -1;
    }
    if (res.status === 500) {
        alert((await res.json()).message)
        return
    } else {
        update_ratings(video_id);
    }
}

async function add_comment(video_id) {
    const content = document.getElementById('comment-content');
    res = await request('/comment', {
        comment_video_id: video_id,
        content: content.value,
    }, 'POST')
    if (res.status === 500) {
        alert((await res.json()).message)
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