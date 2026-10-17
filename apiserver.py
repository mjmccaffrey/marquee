"""Marquee Lighted Sign Project - apiserver"""

import asyncio
import logging
import threading
import time

from fastapi import FastAPI
import uvicorn


log = logging.getLogger('marquee.' + __name__)


class APIServer:
    """Uvicorn and FastAPI running in a separate thread.
       Originally generated from Google AI."""

    def __init__(self, app: FastAPI, host: str, port: int):
        """"""
        self.config = uvicorn.Config(app=app, host=host, port=port)
        self.server = uvicorn.Server(self.config)
        self.thread = None
        self.loop = None

    def _run_server(self):
        """"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.server.serve())

    def start(self):
        """"""
        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()
        while not self.server.started:
            time.sleep(0.01)

    def stop(self):
        """"""
        if self.server.started and self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)
            assert self.thread is not None
            self.thread.join()

