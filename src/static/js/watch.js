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
        console.log((await res.json()).message);
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
        console.log((await res.json()).message);
    } else {
        update_ratings(video_id);
    }
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

async function request(url, data) {
    const csrf_token = document.getElementsByName('csrf')[0].content;
    data = { csrf_token, ...data };

    const formData = new FormData();
    for (const key of Object.keys(data)) {
        formData.append(key, data[key]);
    }
    return fetch(url, {
        method: 'POST',
        body: formData,
    });
}