"""Marquee Lighted Sign Project - apiserver"""

import asyncio
import logging
import threading
import time

from fastapi import FastAPI
import uvicorn


log = logging.getLogger('marquee.' + __name__)


class APIServer:
    """"""

    # Originally generated from Google AI

    def __init__(self, app: FastAPI, host: str, port: int):
        self.config = uvicorn.Config(app=app, host=host, port=port)
        self.server = uvicorn.Server(self.config)
        self.thread = None
        self.loop = None

    def _run_server(self):
        # 1. Create a dedicated async loop for this specific background thread
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        # 2. Run Uvicorn's async start routine inside this thread's loop
        self.loop.run_until_complete(self.server.serve())

    def start(self):
        # Launch the background thread
        self.thread = threading.Thread(target=self._run_server, daemon=True)
        self.thread.start()

        # Wait a moment for the server to spin up completely
        while not self.server.started:
            time.sleep(0.01)

    def stop(self):
        if self.server.started and self.loop:
            # Safely signal the async server to shutdown from outside its thread
            self.loop.call_soon_threadsafe(self.loop.stop)
            assert self.thread is not None
            self.thread.join()

