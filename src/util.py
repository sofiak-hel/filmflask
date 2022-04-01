from flask import render_template
import ffmpeg


def error(error: str):
    return render_template("error.html", error=error)


def process_image(blob: bytes):
    process = (
        ffmpeg
        .input('pipe:')
        .filter_('scale', 250, -1)
        .output('pipe:', format="image2pipe", vcodec="png", pix_fmt="rgba")
        .run_async(pipe_stdout=True, pipe_stdin=True)
    )
    process.stdin.write(blob)
    process.stdin.close()
    res = process.stdout.read()
    process.wait()
    return res
