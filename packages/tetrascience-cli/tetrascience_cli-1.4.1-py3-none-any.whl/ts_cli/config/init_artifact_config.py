import inquirer

from ts_cli.config.artifact_config import ArtifactConfig
from ts_cli.config.interactive_config import InteractiveConfig
from ts_cli.config.provider import Provider
from ts_cli.config.util import assert_is_any_namespace


def map_args_prefix(args: dict, prefix: str) -> dict:
    return {
        "namespace": args.get(f"{prefix}_namespace"),
        "slug": args.get(f"{prefix}_slug"),
        "version": args.get(f"{prefix}_version"),
    }


class InitTemplateConfig(InteractiveConfig):
    def __init__(
        self,
        args,
        *,
        interactive: bool,
    ):
        super().__init__(args, interactive=interactive)
        self._type: str = "Template"
        values = self._resolve(
            Provider.pipe(lambda: args.__dict__), ["template"], skip_confirmation=True
        )
        self._provider = Provider(lambda: values)
        self.template: str = self._provider.get("template")
        self._print_config_keys(self, ["template"], self._type)
        self.validate(["template"])

    def _get_inquiry(self, existing_values: dict):
        """
        Returns a list of inquirer questions, using existing values as defaults
        :param existing_values:
        :return:
        """

        return [
            inquirer.List(
                "template",
                message="Template",
                choices=[
                    "ids",
                    "protocol",
                    "task-script",
                    "tetraflow",
                ],  # TODO "all-in-one"
                default=existing_values.get("template"),
            ),
        ]


class InitArtifactConfig(ArtifactConfig):
    def __init__(
        self,
        args,
        *,
        interactive: bool,
        artifact_type: str,
        type_pretty: str,
        has_function: bool,
        defaults: dict,
    ):
        super().__init__(args, interactive=interactive, has_function=has_function)
        self._type: str = type_pretty
        self.type = artifact_type
        self.prefix: str = artifact_type.replace("-", "_")
        args = args.__dict__
        non_interactive_provider = Provider.pipe(
            lambda: {"type": artifact_type},
            lambda: map_args_prefix(args, self.prefix),
            lambda: args,
            lambda: {
                "namespace": self._cli_config.get("org")
                and f"private-{self._cli_config.get('org')}"
            },
        )
        self.keys = ["type", "namespace", "slug", "version"]
        if has_function:
            self.keys.append("function")
        values = self._resolve(non_interactive_provider, self.keys)
        self._provider = Provider.pipe(lambda: values, lambda: defaults)

    def _get_correct_message(self, answers: dict) -> str:
        """
        :param answers:
        :return:
        """
        return f"Correct? [{self.format({'type': self.type,**answers}, add_function=self.has_function)}]"

    def _get_inquiry(self, existing_values: dict):
        """
        Returns a list of inquirer questions, using existing values as defaults
        :param existing_values:
        :return:
        """

        inquiry = [
            inquirer.Text(
                "namespace",
                message=f"{self._type} Namespace",
                default=existing_values.get("namespace"),
                validate=assert_is_any_namespace,
            ),
            inquirer.Text(
                "slug",
                message=f"{self._type} Slug",
                default=existing_values.get("slug"),
            ),
            inquirer.Text(
                "version",
                message=f"{self._type} Version",
                default=existing_values.get("version"),
            ),
        ]
        if self.has_function:
            inquiry.append(
                inquirer.Text(
                    "function",
                    message=f"{self._type} Function",
                    default=existing_values.get("function"),
                ),
            )
        return inquiry

    def _parse(self, values: dict) -> dict:
        return super()._parse({**values, "type": self.type})
