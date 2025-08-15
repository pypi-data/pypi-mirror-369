import logging
import sys
from collections import deque
from os import chdir, getenv
from pathlib import PosixPath

import click
import click_pathlib
import docker
import requests
import yaml

from nomnomdata.auth import NNDAuth

from .docker_logging_utils import stream_output
from .util import NomitallSession

_logger = logging.getLogger(__name__)


@click.command(name="deploy")
@click.option(
    "-p",
    "--path",
    "buildp",
    default=".",
    show_default=True,
    help="Docker build context path",
    type=click_pathlib.Path(exists=True, file_okay=False),
)
@click.option(
    "-f",
    "--model-file",
    "mpath",
    default="./",
    type=click_pathlib.Path(exists=True, file_okay=True, dir_okay=True, readable=True),
    help="Path to the engine model.yaml to build, if this is a folder model.yaml will be assumed to be in there "
    "Examples: nomnom/test/waittask/model.yaml",
)
@click.option(
    "-d",
    "--docker-file",
    "dpath",
    default="./",
    type=click_pathlib.Path(exists=True, file_okay=True, dir_okay=True, readable=True),
    help="Path to the engine dockerfile to build, if this is a folder Dockerfile will be assumed to be in there "
    "Examples: nomnom/test/waittask/engine.dockerfile",
)
@click.option(
    "-n",
    "--nomitall",
    default="nomitall-prod",
    help="Specify the nomitall to update [nomitall-prod,nomitall-stage,custom_url]",
)
@click.option(
    "-c",
    "--channel",
    default="dev",
    type=click.Choice(["stable", "beta", "dev"]),
    help="Channel to deploy to",
)
@click.option("--dry-run", is_flag=True, help="Build engine but do not deploy")
@click.option(
    "-y", "--yes", "skip_confirm", is_flag=True, help="Skip confirmation prompt"
)
@click.option("-nc", "--no-cache", is_flag=True, help="Do not use the docker cache")
@click.option("--package-repository-username", help="Package repository username")
@click.option("--package-repository-password", help="Package repository password")
def deploy(
    buildp: PosixPath,
    mpath: PosixPath,
    dpath: PosixPath,
    nomitall: str,
    channel: str,
    dry_run: bool,
    skip_confirm: bool,
    no_cache: bool,
    package_repository_username: str | None = None,
    package_repository_password: str | None = None,
):
    "Build engine docker images and optionally run tests."
    if nomitall == "nomitall-prod":
        nomitall_url = "https://user.api.nomnomdata.com/api/1/"
    elif nomitall == "nomitall-stage":
        nomitall_url = "https://user.api.staging.nomnomdata.com/api/1/"
    else:
        nomitall_url = nomitall
    chdir(buildp)
    if mpath.is_dir():
        mpath = mpath / "model.yaml"
    if dpath.is_dir():
        dpath = dpath / "Dockerfile"

    engine_model = yaml.full_load(mpath.read_text())
    engine_uuid = engine_model["uuid"]
    if channel == "beta":
        c_color = click.style(channel, fg="yellow", bold=True)
    elif channel == "stable":
        c_color = click.style(channel, fg="red", bold=True)
    else:
        c_color = click.style(channel, fg="green", bold=True)

    if not skip_confirm:
        click.confirm(
            text=f"Confirm deploy engine:\n\tUUID: {engine_uuid}\n\tChannel: {c_color}\n\tNomitall: {nomitall}\n",
            abort=True,
        )

    session = NomitallSession(prefix_url=nomitall_url)
    session.auth = NNDAuth()
    resp = session.request("get", f"engine/create-deploy-token/{engine_uuid}")
    data = resp.json()
    engine_name = data["repoUrl"]
    try:
        client = docker.from_env()
        client.ping()
    except (
        requests.ConnectionError,
        docker.errors.APIError,
        docker.errors.DockerException,
    ) as e:
        raise Exception(
            "There was a problem connecting to the docker agent, ensure docker is running and in a good state"
        ) from e
    if package_repository_password and package_repository_username:
        _logger.info("Using package repository credentials specified via command line")
        buildargs = {
            "GITLAB_USER": package_repository_username,
            "GITLAB_TOKEN": package_repository_password,
        }
    elif getenv("GITLAB_USER") and getenv("GITLAB_TOKEN"):
        _logger.info(
            "Using package repository credentials specified via environment variables"
        )
        buildargs = {
            "GITLAB_USER": getenv("GITLAB_USER"),
            "GITLAB_TOKEN": getenv("GITLAB_TOKEN"),
        }
    else:
        _logger.info("Package repository credentials were not specified")
        buildargs = None

    build_engine(
        engine_name=engine_name,
        channel=channel,
        docker_file=dpath,
        no_cache=no_cache,
        buildargs=buildargs,
    )
    if not dry_run:
        deploy_engine(engine_name, channel, data)
        if channel == "stable" and nomitall == "nomitall-prod":
            client.api.tag(f"{engine_name}:stable", f"{engine_name}:prod")
            deploy_engine(engine_name, "prod", data)


def deploy_engine(engine_name, channel, creds):
    client = docker.from_env()

    _logger.info(f"----Pushing image {engine_name}:{channel}----")
    auth_config = {"username": creds["user"], "password": creds["token"]}
    push_logs = client.api.push(
        engine_name, tag=channel, auth_config=auth_config, stream=True
    )
    deque(stream_output(push_logs, sys.stdout), maxlen=0)
    _logger.info("----Successfully pushed image----")


def build_engine(engine_name, channel, docker_file, no_cache=False, buildargs=None):
    client = docker.from_env()

    _logger.info(f"----Building image {engine_name}:{channel}----")
    build_logs = client.api.build(
        dockerfile=docker_file.resolve(),
        tag=f"{engine_name}:{channel}",
        rm=True,
        path=".",
        pull=True,
        buildargs=buildargs,
        nocache=no_cache,
    )
    deque(stream_output(build_logs, sys.stdout), maxlen=0)
    _logger.info("----Finished building image----")
