import os
from pathlib import Path

from ids_validator.ids_validator import validate_ids_using_tdp_artifact
from ids_validator.tdp_api import APIConfig as IDSValidatorAPIConfig
from ts_protocol_virtual_machine import compiler
from ts_protocol_virtual_machine.messages import Message

from ts_cli.config.api_config import ApiConfig
from ts_cli.config.util import (
    load_from_json_file_if_present,
    load_from_yaml_file_if_present,
)
from ts_cli.errors.critical_error import CriticalError
from ts_cli.util.emit import emit_error, emit_warning

from .validator import Validator


def validate_source(
    *, path: str, validator_type: str, exiting: bool, api_config: ApiConfig
) -> None:
    """
    Does what it says on the tin
    :param path:
    :param validator_type:
    :param exiting:
    :param api_config:
    :return:
    """
    get_source_validator(
        path=path, validator_type=validator_type, exiting=exiting, api_config=api_config
    ).validate()


def get_source_validator(
    *, path: str, validator_type: str, exiting: bool, api_config: ApiConfig
) -> "SourceValidator":
    """
    :param path:
    :param validator_type:
    :param exiting:
    :param api_config:
    :return:
    """
    if validator_type == "connector":
        return ConnectorValidator(path=path, exiting=exiting)
    if validator_type == "ids":
        return IdsValidator(path=path, exiting=exiting, api_config=api_config)
    if validator_type == "task-script":
        return TaskScriptValidator(path=path, exiting=exiting)
    if validator_type == "protocol":
        return ProtocolValidator(path=path, exiting=exiting)
    if validator_type == "tetraflow":
        return TetraflowValidator(path=path, exiting=exiting)
    raise CriticalError(f"Invalid type provided: {validator_type}")


class SourceValidator(Validator):
    """
    Abstract class
    """

    def __init__(self, *, path: str, exiting: bool):
        self._path = Path(path)
        super().__init__(exiting=exiting)


class ConnectorValidator(SourceValidator):
    """
    Validates a Connector artifact's source files
    """

    def validate(self):
        package_content = os.listdir(self._path)
        if "image.tar" not in package_content:
            raise CriticalError(
                "Connector package must contain 'image.tar' containing the Connector's Docker image."
            )


class IdsValidator(SourceValidator):
    """
    Validates an IDS artifact's source files
    """

    def __init__(self, *, path: str, exiting: bool, api_config: ApiConfig):
        super().__init__(path=path, exiting=exiting)
        self._api_config = api_config

    def validate(self):
        """Run ts-ids-validator on the IDS artifact, raise an exception if it is invalid."""
        api_config = IDSValidatorAPIConfig.from_json_or_env(
            json_config=self._api_config.to_dict(),
            json_config_source="ts-cli config",
        )
        # Validate IDS artifact.
        # API config is used to download the previous IDS for breaking change validation.
        try:
            ids_artifact_is_valid = validate_ids_using_tdp_artifact(
                self._path, api_config=api_config
            )
        except Exception as error:
            print(error)
            ids_artifact_is_valid = False
        if not ids_artifact_is_valid:
            emit_error(
                "IDS artifact validation with ts-ids-validator failed, see the output "
                "of the command for details."
            )
            if self._exiting:
                raise CriticalError("Exiting")


class TaskScriptValidator(SourceValidator):
    """
    Validates a Task Script artifact's source files
    """

    def validate(self):
        # DE-3436: task-script folder must contain requirements.txt
        package_content = os.listdir(self._path)
        if "requirements.txt" not in package_content:
            raise CriticalError("Task-Script package must contain 'requirements.txt'.")


class ProtocolValidator(SourceValidator):
    """
    Validates a Protocol artifact's source files
    """

    @staticmethod
    def format_message(filename: str, message: Message):
        path = f"[{message.source_path}] " if message.source_path else ""
        expression = f"$( {message.expression} ) " if message.expression else ""
        return f"{filename} >> {path}{expression}{message.content}"

    @staticmethod
    def load_protocol(path: Path):
        if path.suffix == ".json":
            return load_from_json_file_if_present(path)
        return load_from_yaml_file_if_present(path)

    @staticmethod
    def validate_v3_protocol(filename: str, protocol: dict):
        def emit_warnings(_, warnings):
            for warning in warnings:
                emit_warning(ProtocolValidator.format_message(filename, warning))

        def emit_warnings_and_errors_and_exit(errors, warnings):
            emit_warnings(None, warnings)
            for error in errors:
                emit_error(ProtocolValidator.format_message(filename, error))
            raise CriticalError("Exiting")

        compiler.protocol_lang.to.pvm(protocol).match(
            emit_warnings,
            emit_warnings_and_errors_and_exit,
        )

    @staticmethod
    def validate_protocol(filename: str, protocol: dict, manifest: dict):
        if protocol.get("protocolSchema", None) == "v3":
            ProtocolValidator.validate_v3_protocol(filename, protocol)
        ProtocolValidator._emit_manifest_warnings(
            protocol=protocol, manifest=manifest, filename=filename
        )

    @staticmethod
    def _emit_manifest_warnings(*, protocol: dict, manifest: dict, filename: str):
        for key, manifest_value in manifest.items():
            if key in protocol:
                protocol_value = protocol[key]
                if protocol_value != manifest_value:
                    emit_warning(
                        f"Values for key '{key}' do not match between {filename} and manifest.json. "
                        + f"{filename} value '{protocol_value}' does not match "
                        + f"manifest.json value '{manifest_value}'"
                    )

    def validate(self):
        manifest = load_from_json_file_if_present(Path(self._path, "manifest.json"))
        for filename in ["protocol.yml", "protocol.yaml", "protocol.json"]:
            path = Path(self._path, filename)
            if path.exists():
                ProtocolValidator.validate_protocol(
                    filename, ProtocolValidator.load_protocol(path), manifest
                )


class TetraflowValidator(SourceValidator):
    """
    Validates a tetraflow artifact's source files
    """

    def validate(self):
        pass
