const KB = 1000;
const MB = KB * KB;

class FileUploadChecker {
    constructor(fileElem, nameElem, descriptionElem, submitElem, maxFileSize) {
        this.nameElem = nameElem;
        this.descriptionElem = descriptionElem;
        this.fileElem = fileElem;
        this.fileElem.addEventListener('change', this.onChange.bind(this));
        submitElem.addEventListener('click', this.onUpload.bind(this));

        this.maxFileSize = maxFileSize;
    }

    onChange(event) {
        const file = event.target.files[0];
        this.descriptionElem.classList.remove("error-message");
        this.nameElem.innerHTML = file.name;
        if (file.size > this.maxFileSize) {
            this.descriptionElem.innerHTML = `File over ${convertSize(this.maxFileSize)}`;
            this.descriptionElem.classList.add("error-message");
        } else {
            this.descriptionElem.innerHTML = convertSize(file.size);
        }
    }

    onUpload(event) {
        const file = this.fileElem.files[0];
        if (file == null) {
            event.preventDefault();
            alert('No file selected!')
        }
        else if (file.size > this.maxFileSize) {
            event.preventDefault();
            alert(`File over ${convertSize(this.maxFileSize)}`)
        }
    }
}


function convertSize(size) {
    return (size > MB) ?
        (`${(size / MB).toFixed(2)} MB`) :
        (size > KB) ?
            (`${(size / KB).toFixed(2)} KB`) :
            size
}