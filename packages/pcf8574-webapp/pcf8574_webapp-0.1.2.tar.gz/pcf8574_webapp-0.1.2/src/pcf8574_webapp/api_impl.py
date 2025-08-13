from typing import List, Optional
from fastapi import WebSocket
from pcf8574_interface import PCF8574InterfaceApi
import asyncio

class WebAppNotifier(PCF8574InterfaceApi):
    """
    An implementation of the PCF8574InterfaceApi that notifies all registered WebSocket clients
    about new available values of the PCF8574 ports.
    """
    def __init__(
            self,
            asyncio_loop: Optional[asyncio.AbstractEventLoop]
    ):
        self.__asyncio_loop = asyncio_loop
        self._clients: List[WebSocket] = []

    def register(self, websocket: WebSocket):
        """
        Register a WebSocket client to receive notifications.
        Should be called when a client connects to the WebSocket endpoint.
        """
        self._clients.append(websocket)

    def unregister(self, websocket: WebSocket):
        """
        Unregister a WebSocket client to stop receiving notifications.
        Should be called when a client disconnects from the WebSocket endpoint.
        """
        if websocket in self._clients:
            self._clients.remove(websocket)

    async def notify_all(self, payload: dict):
        """
        Helper method to send JSON data to all registered WebSocket clients.
        """
        for ws in self._clients.copy():
            try:
                await ws.send_json(payload)
            except RuntimeError:
                self._clients.remove(ws)

    def notify_clients(
        self,
        unspoiled_values: List[bool],
        override_values: List[Optional[bool]],
        i2c_bus: int,
        i2c_address: int
    ) -> None:
        """
        Implementation of the notify_clients method from the PCF8574InterfaceApi.
        This method is called when the values of a PCF8574 port change.
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            if self.__asyncio_loop is None:
                return
            loop = self.__asyncio_loop

        asyncio.run_coroutine_threadsafe(
            self.notify_all({
                "i2c_bus": i2c_bus,
                "i2c_address": i2c_address,
                "values": {
                    "unspoiled": unspoiled_values,
                    "override": override_values,
                }
            }),
            loop
        )
