
import ffmpeg
from typing import Any, Callable, Optional

import tempfile


def process_image(blob: bytes, flags="bilinear", **kwargs):
    process = (
        ffmpeg
        .input('pipe:', **kwargs)
        .filter_("crop", "min(iw,ih)", "min(iw,ih)")
        .filter_('scale', 250, 250, flags=flags)
        .output('pipe:', format="image2pipe", vcodec="mjpeg", pix_fmt="rgba")
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

    data = ffmpeg.probe(inf.name)
    available_streams = [False, False]
    if 'streams' in data:
        for stream in data['streams']:
            if 'codec_type' in stream:
                if stream['codec_type'] == 'audio':
                    available_streams[0] = True
                if stream['codec_type'] == 'video':
                    available_streams[1] = True

    input = ffmpeg.input(inf.name)
    streams = []
    if available_streams[0]:
        streams.append(input.audio)
    if available_streams[1]:
        streams.append(
            input.video
            # Scales down the video so it is 480p or smaller
            .filter_('scale', w="if(gt(ih,iw),-1,min(iw,854))", h="if(gt(ih,iw),min(ih,480),-1)", force_original_aspect_ratio='decrease')
            # Pads the video with black bars, so every video will end up as 16:9 aspect ratio
            .filter_('pad', "max(iw,ceil(ih*(16/9)/2)*2)", "max(ceil(iw*(9/16)/2)*2,ih)", "-1", "-1")
        )
    process = (
        ffmpeg.output(*streams,
                      ouf.name,
                      format="mp4")
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
