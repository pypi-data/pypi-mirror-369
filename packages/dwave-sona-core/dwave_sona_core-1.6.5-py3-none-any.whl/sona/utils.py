import hashlib
import os
import sys
import traceback
from pathlib import Path

import av
from loguru import logger


def import_class(import_str):
    mod_str, _sep, class_str = import_str.rpartition(".")
    __import__(mod_str)
    try:
        return getattr(sys.modules[mod_str], class_str)
    except AttributeError:
        raise ImportError(
            f"Class {class_str} cannot be found ({traceback.format_exception(*sys.exc_info())})"
        )


def convert_audio(filepath, ext, format=None, sample_rate=None):
    filepath = Path(filepath)
    in_path = str(filepath)
    out_path = str(filepath.parent / f"{filepath.stem}.{ext}")

    codec = "pcm_s16le" if ext == "wav" else ext
    with av.open(in_path, "r", metadata_errors="ignore") as in_av:
        with av.open(out_path, "w") as out_av:
            in_stream = in_av.streams.audio[0]
            format = format or in_stream.format
            sample_rate = sample_rate or in_stream.sample_rate

            out_stream = out_av.add_stream(codec)
            out_stream.format = format
            out_stream.sample_rate = sample_rate
            for packet in in_av.demux(in_stream):
                try:
                    for frame in packet.decode():
                        for packet in out_stream.encode(frame):
                            out_av.mux(packet)
                except Exception as e:
                    logger.warning(
                        f"Converting incomplete cause: {e}, inferencer may not process all of the audio data"
                    )
            for packet in out_stream.encode(None):
                out_av.mux(packet)
    return out_path


def get_audio_metadata(filepath):
    with av.open(filepath, "r") as container:
        audio = container.streams.audio[0]
        return {
            "format": audio.format.name,
            "layout": audio.layout.name,
            "samplerate": audio.rate,
            "duration": float(audio.duration * audio.time_base),
        }


def zero_copy(in_fd, out_fd):
    ret = 0
    offset = 0
    while True:
        ret = os.sendfile(in_fd, out_fd, offset, 65536)
        offset += ret
        if ret == 0:
            break


def md5_hex(obj):
    md5 = hashlib.md5()
    md5.update(str(obj).encode())
    return md5.hexdigest()


def md5_content_hex(path):
    md5 = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)
    return md5.hexdigest()
