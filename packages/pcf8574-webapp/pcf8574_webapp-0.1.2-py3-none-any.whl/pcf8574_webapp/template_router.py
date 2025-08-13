from typing import Callable, Union

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path

from jinja2 import ChoiceLoader, FileSystemLoader, BaseLoader

from .jinja_filters import to_hex


class TemplateRouter:
    """
    A class to manage FastAPI routes that serve Jinja2 templates.
    """
    def __init__(self, base_template_dir: Path):
        self.__router = APIRouter()
        self.__templates = Jinja2Templates(directory=base_template_dir)
        self.__templates.env.filters["to_hex"] = to_hex

    def get_router(self) -> APIRouter:
        return self.__router

    def add_template_route(self, path: str, template_name: str, context: Union[dict, Callable[[], dict]] = None):
        context = context or {}

        @self.__router.get(path, response_class=HTMLResponse)
        async def route(request: Request):
            evaluated_context = context() if callable(context) else (context or {})
            evaluated_context["request"] = request
            return self.__templates.TemplateResponse(template_name, evaluated_context)

    def _add_loader_support(self, additional_loader: BaseLoader):
        base_loader = self.__templates.env.loader
        if not isinstance(base_loader, ChoiceLoader):
            self.__templates.env.loader = ChoiceLoader([base_loader, additional_loader])
        else:
            self.__templates.env.loader = ChoiceLoader(base_loader.loaders + [additional_loader])

    def add_template_directory(self, template_dir: Path):
        self._add_loader_support(FileSystemLoader(str(template_dir)))
