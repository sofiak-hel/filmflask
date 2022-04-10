function onload() {
    new FileUploadChecker(
        document.getElementById('video'),
        document.getElementById('video-name'),
        document.getElementById('video-description'),
        document.getElementById('upload'),
        1024 * 1024 * 5
    )
}