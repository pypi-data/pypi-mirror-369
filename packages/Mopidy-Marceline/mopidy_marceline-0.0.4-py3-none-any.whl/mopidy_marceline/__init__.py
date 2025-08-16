import logging
import pathlib
from importlib.metadata import version

import mopidy.config
import mopidy.core
import mopidy.ext
import tornado.web

__version__ = version("Mopidy-Marceline")
__folder__ = pathlib.Path(__file__).parent

logger = logging.getLogger(__name__)


class SPARouterHandler(tornado.web.StaticFileHandler):
    async def get(
        self,
        path: str,  # noqa: ARG002
        include_body: bool = True,  # noqa: FBT001, FBT002
    ) -> None:
        return await super().get(self.root, include_body)


def marceline_factory(
    _: mopidy.config.ConfigValue, __: mopidy.core.actor.Core
) -> tornado.web._RuleList:
    path = __folder__ / "static"

    paths = (
        str(p.relative_to(path)) if p.is_file() else f"{p.relative_to(path)}/.*"
        for p in path.iterdir()
    )

    return [
        (
            f"/({'|'.join(paths)})",
            tornado.web.StaticFileHandler,
            {"path": path},
        ),
        (r"/(.*)", SPARouterHandler, {"path": path, "default_filename": "index.html"}),
    ]


class Extension(mopidy.ext.Extension):
    dist_name = "Mopidy-Marceline"
    ext_name = "marceline"
    version = __version__

    def get_default_config(self) -> str:
        return mopidy.config.read(__folder__ / "ext.conf")

    def setup(self, registry: mopidy.ext.Registry) -> None:
        registry.add(
            "http:app",
            {
                "name": self.ext_name,
                "factory": marceline_factory,
            },  # pyright: ignore[reportArgumentType]
        )
