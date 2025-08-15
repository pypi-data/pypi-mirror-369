import argparse
import os
import textwrap
from argparse import ArgumentParser
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List, Optional

from jinja2 import Template

from ts_cli.commands.utils import any_namespace_type, platform_version_type
from ts_cli.config.cli_config import CliConfig
from ts_cli.config.init_artifact_config import InitArtifactConfig, InitTemplateConfig
from ts_cli.config.util import to_version
from ts_cli.errors.critical_error import CriticalError
from ts_cli.util.emit import emit_error, emit_warning
from ts_cli.util.files import copy, delete, get_conflicts

MAX_KNOWN_PLATFORM_VERSION = 4.3


def add_init_parser(subparsers):
    """
    Adds the `init` subparser
    :param subparsers:
    :return:
    """
    init_cmd_args(
        subparsers.add_parser(
            "init",
            help="Create a new artifact from a template",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description=textwrap.dedent(
                f"""
                Create a new artifact for the Tetra Data Platform. For example:

                    ts-cli init protocol .

                where "." is the path to the new artifact source.
                The source code positional argument defaults to the current working directory.

                The template configuration field is required.

                Each template uses 1 to 3 artifact configurations,
                    protocol, task-script, or ids
                  consisting of the following fields:
                    namespace, slug, version
                  Additionally, for the task-script artifact, there is the function field.
                While artifact configuration fields are not required, the init command will
                  sequentially check each of the following locations for each configuration:
                    1. The respective command argument for the specific artifact type
                        Example: --ids-slug my-slug
                    2. The respective command argument for all artifacts used by the template
                        Example: --slug my-slug
                For the namespace field, the init command will additionally look for
                  a configured org (see below)
                If no configuration can be found, it will either be omitted, or filled in
                  with default values from [common/example:v1.0.0@main] if it is required.

                The init command will sequentially check each of the following locations
                  for an org
                    1. In the process's environment variables, at TS_ORG
                    2. The yaml or json formatted file at  "~/.config/tetrascience/config"

                The init command has support for multiple Tetra Data Platform versions.
                  The init command will sequentially check each of the following locations
                  for a configured platform version
                    1. The `--platform-version` command line argument
                    2. In the process's environment variables, at TS_PLATFORM_VERSION
                    3. The yaml or json formatted file at "~/.config/tetrascience/config"
                  If no platform versio is found, the current TDP version
                    v{MAX_KNOWN_PLATFORM_VERSION} is assumed.
                """
            ),
        )
    )


def init_cmd_args(parser: ArgumentParser):
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="interactively set up Artifact configuration",
    )
    parser.add_argument(
        "--overwrite",
        "-o",
        action="store_true",
        help="Force overwrite files and folders on conflict",
    )
    parser.add_argument(
        "--preserve-templates",
        "-p",
        action="store_true",
        help="Leave template files on disk instead of deleting them",
    )
    parser.add_argument(
        "--platform-version",
        type=platform_version_type,
        help="The version of the platform",
    )
    parser.add_argument(
        "--profile", help="The name of the configuration profile to use", type=str
    )

    artifact_group = parser.add_argument_group("General Artifact Configuration")
    artifact_group.add_argument(
        "--namespace",
        type=any_namespace_type,
        help="Artifact namespace configuration",
    )
    artifact_group.add_argument(
        "--slug",
        type=str,
        help="Artifact slug configuration",
    )
    artifact_group.add_argument(
        "--version",
        type=to_version,
        help="Artifact version configuration",
    )

    protocol_group = parser.add_argument_group("Protocol Configuration")
    protocol_group.add_argument(
        "--protocol-namespace",
        type=any_namespace_type,
        help="Protocol namespace configuration",
    )
    protocol_group.add_argument(
        "--protocol-slug", type=str, help="Protocol slug configuration"
    )
    protocol_group.add_argument(
        "--protocol-version", type=to_version, help="Protocol version configuration"
    )

    task_script_group = parser.add_argument_group("Task Script Configuration")
    task_script_group.add_argument(
        "--task-script-namespace",
        type=any_namespace_type,
        help="Task Script namespace configuration",
    )
    task_script_group.add_argument(
        "--task-script-slug",
        type=str,
        help="Task Script slug configuration",
    )
    task_script_group.add_argument(
        "--task-script-version",
        type=to_version,
        help="Task Script version configuration",
    )

    ids_group = parser.add_argument_group("IDS Configuration")
    ids_group.add_argument(
        "--ids-namespace", type=any_namespace_type, help="IDS namespace configuration"
    )
    ids_group.add_argument("--ids-slug", type=str, help="IDS slug configuration")
    ids_group.add_argument(
        "--ids-version", type=to_version, help="IDS version configuration"
    )

    parser.add_argument(
        "template",
        type=str,
        choices=["ids", "protocol", "task-script", "tetraflow"],  # TODO "all-in-one"
        nargs="?",
        help="artifact template to use",
    )
    parser.add_argument(
        "target",
        type=str,
        help="Destination folder",
        nargs="?",
        default=os.getcwd(),
    )

    parser.set_defaults(func=init)


def get_pretty_name(artifact_type: str) -> str:
    if artifact_type == "protocol":
        return "Protocol"
    elif artifact_type == "task-script":
        return "Task Script"
    elif artifact_type == "ids":
        return "IDS"
    elif artifact_type == "tetraflow":
        return "Tetraflow"
    else:
        raise NotImplementedError(f"Unrecognized type: {artifact_type}")


def init_artifact_config(
    artifact_type: str, args, defaults: dict, *, has_function=False
):
    return InitArtifactConfig(
        args,
        interactive=args.interactive,
        type_pretty=get_pretty_name(artifact_type),
        artifact_type=artifact_type,
        defaults=defaults,
        has_function=has_function,
    )


EXAMPLE_LOCATION = {
    "namespace": "common",
    "slug": "example",
    "version": "v1.0.0",
    "function": "main",
}


def task_script_template_config(args) -> List[InitArtifactConfig]:
    task_script = init_artifact_config("task-script", args, {})
    ids = init_artifact_config("ids", args, EXAMPLE_LOCATION)
    return [task_script, ids]


def protocol_template_config(args) -> List[InitArtifactConfig]:
    protocol = init_artifact_config("protocol", args, {})
    task_script = init_artifact_config(
        "task-script", args, EXAMPLE_LOCATION, has_function=True
    )
    return [protocol, task_script]


def ids_template_config(args) -> List[InitArtifactConfig]:
    ids = init_artifact_config("ids", args, EXAMPLE_LOCATION)
    return [ids]


def all_template_config(args) -> List[InitArtifactConfig]:
    protocol = init_artifact_config("protocol", args, {})
    task_script = init_artifact_config("task-script", args, EXAMPLE_LOCATION)
    ids = init_artifact_config("ids", args, EXAMPLE_LOCATION)
    return [protocol, task_script, ids]


def tetraflow_template_config(args) -> List[InitArtifactConfig]:
    tetraflow = init_artifact_config("tetraflow", args, EXAMPLE_LOCATION)
    return [tetraflow]


def create_template_config_list(args, template: str) -> List[InitArtifactConfig]:
    if template == "task-script":
        configs = task_script_template_config(args)
    elif template == "protocol":
        configs = protocol_template_config(args)
    elif template == "ids":
        configs = ids_template_config(args)
    elif template == "all-in-one":
        configs = all_template_config(args)
    elif template == "tetraflow":
        configs = tetraflow_template_config(args)
    else:
        raise Exception(f"Invalid template type provided: {template}")
    for config in configs:
        config.print()
    return configs


def create_environment(configs: List[InitArtifactConfig]) -> dict:
    environment = {}
    for config in configs:
        for key in config.keys:
            environment[f"{config.prefix}_{key}"] = config.get(key)
    return environment


def list_template_versions_in_dir(template_type_dir: Path) -> List[float]:
    platform_versions = [float(entry) for entry in os.listdir(template_type_dir)]
    platform_versions.sort()
    platform_versions.reverse()
    return platform_versions


def get_template_dir(template_type: str) -> Path:
    return Path(__file__).parent.joinpath("templates", template_type)


def select_template_version(
    template_versions: List[float], target_version: float
) -> Optional[float]:
    if target_version > MAX_KNOWN_PLATFORM_VERSION:
        emit_warning(
            f"Unrecognized platform version: v{target_version}. Assuming platform version v{MAX_KNOWN_PLATFORM_VERSION}"
        )
        target_version = MAX_KNOWN_PLATFORM_VERSION
    return next(
        (version for version in template_versions if version <= target_version),
        None,
    )


def pick_template(template_type: str, platform_version: str) -> Path:
    template_type_dir = get_template_dir(template_type)
    platform_versions = list_template_versions_in_dir(template_type_dir)
    numeric_platform_version = float(platform_version.replace("v", ""))
    selected_version = select_template_version(
        platform_versions, numeric_platform_version
    )
    if selected_version is None:
        raise CriticalError(
            f"Aborting because version {platform_version} is not supported"
        )
    return template_type_dir.joinpath(str(selected_version))


def resolve_conflicts(
    *, template_directory, target_directory, overwrite, preserve_templates
):
    conflicting_entries = get_conflicts(
        src=template_directory,
        dst=target_directory,
        preserve_templates=preserve_templates,
    )
    if conflicting_entries and not overwrite:
        for entry in conflicting_entries:
            emit_error(f"Conflict at {entry}")
        conflict_count = len(conflicting_entries)
        noun = "file" if conflict_count == 1 else "files"
        verb = "conflicts" if conflict_count == 1 else "conflict"
        raise CriticalError(
            f"Aborting because {conflict_count} {noun} in the target directory {verb} with the template"
        )
    delete(*conflicting_entries)


def init(args):
    template = InitTemplateConfig(args, interactive=args.interactive).template
    environment = create_environment(create_template_config_list(args, template))
    platform_version = (
        CliConfig(args).get("platform_version") or f"v{MAX_KNOWN_PLATFORM_VERSION}"
    )
    template_directory = pick_template(template, platform_version)

    resolve_conflicts(
        template_directory=template_directory,
        target_directory=args.target,
        overwrite=args.overwrite,
        preserve_templates=args.preserve_templates,
    )

    with TemporaryDirectory() as temporary_directory:
        copy(src=template_directory, dst=temporary_directory)
        for path in Path(temporary_directory).glob("**/*.template"):
            template = path.read_text()
            content = Template(template).render(environment)
            path.with_name(path.stem).write_text(content)

            if not args.preserve_templates:
                path.unlink()
        copy(src=temporary_directory, dst=args.target)
