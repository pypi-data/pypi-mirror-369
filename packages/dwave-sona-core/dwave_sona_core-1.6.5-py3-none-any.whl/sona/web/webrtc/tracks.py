import asyncio
from collections import deque

import av
from aiortc import MediaStreamTrack


class VideoInferencerTrack(MediaStreamTrack):
    kind = "video"


class AudioInferencerTrack(MediaStreamTrack):
    kind = "audio"

    def __init__(self):
        super().__init__()
        self.queue = asyncio.Queue()
        self.resampler = av.AudioResampler("s16", "mono", 16000)
        self.fifo = av.AudioFifo()
        self.timestamp = 0
        self.rtcframes = deque()

    async def recv(self):
        while not self.rtcframes:
            await self.recv_queue()
        return self.rtcframes.pop()

    async def recv_queue(self):
        frame = await self.queue.get()
        for rtcframe in self.resampler.resample(frame):
            rtcframe.pts = self.timestamp
            self.timestamp += rtcframe.samples
            self.fifo.write(rtcframe)
            self.rtcframes.extendleft(self.fifo.read_many(960))

    def reply(self, frame):
        self.queue.put_nowait(frame)
