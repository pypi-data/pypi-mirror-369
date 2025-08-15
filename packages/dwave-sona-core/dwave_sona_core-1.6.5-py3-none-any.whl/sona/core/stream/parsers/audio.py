import av
from sona.core.stream.messages import AVAudioStreamData


class AudioStreamParser:
    def __init__(self, samples=3200, sample_rate=16000, layout="mono", format="s16"):
        self.samples = samples
        self.sample_rate = sample_rate
        self.layout = layout
        self.format = format
        self.fifo = av.AudioFifo()
        self.resampler = av.AudioResampler(self.format, self.layout, self.sample_rate)

    def parse_raw(self, codec, raw):
        codec_ctx = av.CodecContext.create(codec, "r")
        codec_ctx.parse(raw)
        for packet in codec_ctx.parse():
            for frame in codec_ctx.decode(packet):
                for resample_frame in self.parse_frame(frame):
                    yield resample_frame

    def parse_frame(self, frame):
        for frame in self.resampler.resample(frame):
            frame.pts = None
            self.fifo.write(frame)
            for resample_frame in self.fifo.read_many(self.samples):
                yield AVAudioStreamData(data=resample_frame)
