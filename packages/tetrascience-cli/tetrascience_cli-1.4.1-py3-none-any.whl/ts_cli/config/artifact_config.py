from typing import Optional

from ts_cli.config.cli_config import CliConfig
from ts_cli.config.interactive_config import InteractiveConfig
from ts_cli.config.util import to_version
from ts_cli.util.colour import blue, green


def _colour_string(string: Optional[str]):
    if string:
        return green(string)
    else:
        return blue("<unset>")


def _ensure_string(string: Optional[str]) -> str:
    if string:
        return string
    else:
        return "<unset>"


class ArtifactConfig(InteractiveConfig):
    """
    Artifact Configuration Abstract Class
    """

    def __init__(self, args, *, interactive: bool, has_function=False):
        super().__init__(args, interactive=interactive)
        self._cli_config = CliConfig(args)
        self._interactive = interactive
        self.type = None
        self.namespace = None
        self.slug = None
        self.version = None
        self.has_function = has_function

    def _parse(self, values: dict) -> dict:
        return {
            "type": values.get("type") or None,
            "namespace": values.get("namespace") or None,
            "slug": str.lower(values.get("slug") or "") or None,
            "version": (
                to_version(values.get("version"))
                if (values.get("version") or None) is not None
                else None
            ),
            "function": values.get("function") or None,
        }

    def print(self):
        print(self.to_string(formatter=_colour_string, add_function=self.has_function))

    def to_string(self, *, formatter=_ensure_string, add_function: bool = False):
        return self.format(
            {
                "type": self.get("type"),
                "namespace": self.get("namespace"),
                "slug": self.get("slug"),
                "version": self.get("version"),
                "function": self.get("function"),
            },
            add_function=add_function,
            formatter=formatter,
        )

    def format(self, values: dict, add_function: bool, formatter=_colour_string):
        values = self._parse(values)
        artifact_type = formatter(values.get("type"))
        namespace = formatter(values.get("namespace"))
        slug = formatter(values.get("slug"))
        version = formatter(values.get("version"))
        function_name = formatter(values.get("function"))
        function_suffix = f"@{function_name}" if add_function else ""
        return f"{artifact_type}: {namespace}/{slug}:{version}{function_suffix}"
