from flask import render_template
import ffmpeg
import tempfile


def error(error: str):
    return render_template("error.html", error=error)


def process_image(blob: bytes):
    process = (
        ffmpeg
        .input('pipe:')
        .filter_("crop", "min(iw,ih)", "min(iw,ih)")
        .filter_('scale', 250, 250)
        .output('pipe:', format="image2pipe", vcodec="png", pix_fmt="rgba")
        .run_async(pipe_stdout=True, pipe_stdin=True)
    )
    process.stdin.write(blob)
    process.stdin.close()
    res = process.stdout.read()
    process.wait()
    return res


def process_video(blob: bytes):
    inf = tempfile.NamedTemporaryFile()
    ouf = tempfile.NamedTemporaryFile()
    inf.write(blob)

    process = (
        ffmpeg
        .input(inf.name)
        .output(ouf.name, format="mp4")
        .overwrite_output()
        .run_async(pipe_stdout=True)
    )
    process.wait()
    inf.close()

    res = ouf.read()
    ouf.close()
    return res


def create_thumbnail(blob: bytes):
    inf = tempfile.NamedTemporaryFile()
    inf.write(blob)

    process = (
        ffmpeg
        .input(inf.name)
        .filter("select", "eq(n,34)")
        .output('pipe:', format="image2pipe", vcodec="mjpeg", vframes=1)
        .run_async(pipe_stdout=True)
    )
    res = process.stdout.read()
    inf.close()
    process.wait()
    return res
