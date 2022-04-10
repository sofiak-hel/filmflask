function onload() {
    new FileUploadChecker(
        document.getElementById('avatar'),
        document.getElementById('image-name'),
        document.getElementById('image-description'),
        document.getElementById('update-avatar'),
        1024 * 200
    )
}