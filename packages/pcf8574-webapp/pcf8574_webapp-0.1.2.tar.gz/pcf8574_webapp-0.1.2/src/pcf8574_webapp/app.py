import asyncio
import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from pcf8574_interface import IoPortType, PCF8574Pool

from .api_impl import WebAppNotifier
from .template_router import TemplateRouter


class PCF8574WebApp:
    """
    Gives you a simple web interface to control your PCF8574 ports.

    Creating an instance of this class will automatically set up a FastAPI application with one default route.
    The default route serves an index page that lists all input and output ports available in the provided `hardware_pool`.
    You can add more routes (with custom templates) using the `add_route` method.

    Args:
        hardware_pool (PCF8574Pool): The pool of PCF8574 ports to be managed by the web application.
        asyncio_loop (Optional[asyncio.AbstractEventLoop]): An optional asyncio event loop to run the application on.
    """
    def __init__(
            self,
            hardware_pool: PCF8574Pool,
            asyncio_loop: Optional[asyncio.AbstractEventLoop] = None
    ):
        self.hardware_pool = hardware_pool
        self.__BASE_DIR = Path(__file__).resolve().parent
        self.__app = FastAPI()
        self.__notifier = WebAppNotifier(asyncio_loop)
        self.__template_router = TemplateRouter(self.__BASE_DIR / "templates")
        self.__setup_static()
        self.__setup_routes()
        self.__app.include_router(self.__template_router.get_router())

    def __setup_static(self):
        static_dir = self.__BASE_DIR / "static"
        self.__app.mount("/static", StaticFiles(directory=static_dir), name="static")

    def __setup_routes(self):
        # set up the default route to serve the index page
        self.__template_router.add_template_route(
            path = "/",
            template_name = "index.html",
            context = lambda: {
                "inputs": self.hardware_pool.get_ports_by_type(IoPortType.IN),
                "outputs": self.hardware_pool.get_ports_by_type(IoPortType.OUT)
            }
        )

        # set up the WebSocket endpoint for real-time communication
        @self.__app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.__notifier.register(websocket)
            try:
                while True:
                    message = await websocket.receive_text()
                    if message == "init":
                        # Trigger repr to send initial inputs/outputs
                        _ = [repr(port.port) for port in self.hardware_pool.get_all_ports()]
                    else:
                        data = json.loads(message)
                        port = self.hardware_pool.get_port(data["i2c_bus"], data["i2c_address"])
                        if port is None:
                            continue
                        port.set_override(data["values"]["override"])

            except WebSocketDisconnect:
                self.__notifier.unregister(websocket)

        @self.__app.get("/health")
        async def health():
            return {"status": "ok"}

    def get_app(self) -> FastAPI:
        return self.__app

    def get_notifier(self) -> WebAppNotifier:
        return self.__notifier

    def add_route(self, path: str, template_name: str, context: dict = None):
        """
        Adds a new route to the web application with a specified template and context.

        Args:
            path (str): The URL path for the new route.
            template_name (str): The name of the template to be rendered for this route. Custom templates must be registered with the 'add_template_directory' method.
            context (dict, optional): A dictionary containing context variables to be passed to the template.
        """
        self.__template_router.add_template_route(path=path, template_name=template_name, context=context)
        self.__app.include_router(self.__template_router.get_router())

    def add_template_directory(self, directory: Path):
        """
        Add a directory containing custom templates used for custom routes.
        """
        self.__template_router.add_template_directory(directory)
