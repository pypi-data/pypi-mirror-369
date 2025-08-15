import base64
import logging
import sys
from os import path
from pathlib import Path
from pprint import pformat
from urllib.parse import urlparse

import click
import fsspec
import yaml
from click.exceptions import ClickException

from nomnomdata.auth import DEFAULT_PROFILE, NNDAuth, get_profiles
from nomnomdata.auth.util import get_nomitall_config

from .model_validator import validate_model
from .util import NomitallSession

_logger = logging.getLogger(__name__)


def fetch_yaml(relpath):
    return yaml.full_load(Path(relpath).read_text())


def fetch_include(fpath, model_fp):
    final_path = (Path(path.abspath(model_fp)).parent / Path(fpath)).resolve()
    return yaml.full_load(final_path.read_text())


def include_includes(parameters, model_fp):
    parsed_params = []
    assert isinstance(
        parameters, list
    ), "Parameters lists must be a list of dictionaries ( `- foo:bar` , not `foo:bar` )"
    for parameter in parameters:
        assert isinstance(
            parameter, dict
        ), "Parameters lists must be a list of dictionaries ( `- foo:bar` , not `foo:bar` )"
        if "parameters" in parameter:
            parameter["parameters"] = include_includes(parameter["parameters"], model_fp)
            parsed_params.append(parameter)
        elif "include" in parameter:
            for include in parameter["include"]:
                _logger.info("\tIncluding file {include}")
                include_doc = fetch_include(include, model_fp)
                _logger.debug(f"FETCHED INCLUDE: \n{pformat(include_doc)}")
                _logger.debug("PARSING FETCHED FOR INCLUDES")
                include_doc = include_includes(include_doc, model_fp)
                _logger.debug(
                    f"FETCHED INCLUDE AFTER RESCURSIVE INCLUDE: \n{pformat(include_doc)}"
                )
                parsed_params.extend(include_doc)
        else:
            parsed_params.append(parameter)
    return parsed_params


@click.command()
@click.option(
    "-n",
    "--nomitall",
    default="nomitall-prod",
    help="Specify the nomitall to update [nomitall-prod,nomitall-stage,custom_url]",
)
@click.option(
    "-dr",
    "--dry-run",
    is_flag=True,
    help="Do not update nomitall, just output parsed model json",
)
@click.option(
    "-f",
    "--file",
    "model_fn",
    default="model.yaml",
    help="Model YAML file to deploy",
)
@click.option(
    "-o",
    "--org",
    "org",
    help="UUID of the organization to publish the model as",
)
@click.option(
    "-c",
    "--channel",
    "channel",
    type=click.Choice(["stable", "beta", "dev"]),
    help="The release channel to deploy to",
    default="dev",
)
@click.option("-y", "skip_confirm", is_flag=True, help="Skip confirmation prompt")
def model_update(
    channel=None,
    nomitall_secret=None,
    nomitall=None,
    dry_run=None,
    model_fn=None,
    org=None,
    skip_confirm=None,
):
    """Update staging or prod nomitall model definitions. Defaults to using files from git master/staging branch for prod/staging"""
    if nomitall == "nomitall-prod":
        nomitall_url = "https://user.api.nomnomdata.com/api/1/"
    elif nomitall == "nomitall-stage":
        nomitall_url = "https://user.api.staging.nomnomdata.com/api/1/"
    else:
        nomitall_url = nomitall
    if not org:
        profile = get_profiles()[DEFAULT_PROFILE]

        config = get_nomitall_config(nomitall_url)
        org = profile.get(config["COGNITO_USERPOOL_ID"], {}).get("default-org")
        if not org:
            raise ClickException(f"User not authenticated.  Please run 'nnd login'")
    if channel == "beta":
        c_color = click.style(channel, fg="yellow", bold=True)
    elif channel == "stable":
        c_color = click.style(channel, fg="red", bold=True)
    else:
        c_color = click.style(channel, fg="green", bold=True)

    doc = yaml.full_load(Path(model_fn).read_text())
    if not skip_confirm:
        click.confirm(
            text=f"Confirm model update:"
            f"\n\tUUID: {doc.get('uuid','Not Found')}"
            f"\n\tModel File: {model_fn}"
            f"\n\tChannel: {c_color}"
            f"\n\tNomitall: {nomitall}\n",
            abort=True,
        )

    model_type = doc.get("type")
    if not model_type:
        _logger.error("Model does not have a type, this is required")
        sys.exit(1)
    # add legacy model verison if it doesn't exit
    if model_type == "engine":
        for action, action_dict in doc["actions"].items():
            _logger.info("Parsing {}".format(action))
            action_dict["parameters"] = include_includes(
                action_dict["parameters"], model_fn
            )
    else:
        doc["parameters"] = include_includes(doc["parameters"], model_fn)

    if not validate_model(doc):
        raise click.Abort("Model did not pass validation")

    if dry_run:
        _logger.info("PARSED MODEL :")
        _logger.info(pformat(doc))
        sys.exit()

    update_model(
        nomitall_url=nomitall_url,
        nomitall_secret=nomitall_secret,
        model=doc,
        model_type=model_type,
        org=org,
        channel=channel,
    )


def load_icons(icons):
    for size, icon_uri in icons.items():
        _logger.info(f"Loading {icon_uri}")
        openfile = fsspec.open(icon_uri, mode="rb")
        with openfile as f:
            icons[size] = base64.b64encode(f.read()).decode("utf-8")
    return icons


def load_help_file(md_path):
    _logger.info(f"Loading {md_path}")
    openfile = fsspec.open(md_path, mode="rb")
    with openfile as f:
        md_file = base64.b64encode(f.read()).decode("utf-8")
    return md_file


def process_help(doc, key="root"):
    help_files = {}
    if isinstance(doc, list):
        for subele in doc:
            help_files.update(process_help(subele, key=key))
    if isinstance(doc, dict):
        process_help
        for k, subele in doc.items():
            if k == "help":
                if "file" in subele:
                    if "name" in doc:
                        key += "." + doc["name"]
                    help_files[key] = load_help_file(subele["file"])
                    doc[k] = {"key": key}
            else:
                help_files.update(
                    process_help(
                        subele,
                        key=".".join([key, k]),
                    )
                )
    return help_files


def update_model(nomitall_url, nomitall_secret, model, model_type, org, channel):
    session = NomitallSession(prefix_url=nomitall_url)
    session.auth = NNDAuth()
    if model_type == "engine":
        model["help_files"] = process_help(model)
        model["icons"] = load_icons(model.pop("icons", {}))
        _logger.info("Pushing engine to nomitall")
        session.request(
            "POST", f"engine/deploy/{org}", params={"channel": channel}, json=model
        )

    elif model_type == "shared_config_type":
        _logger.info("Pushing shared config type to nomitall")
        resp = session.request("POST", "shared_config_type/update", json=model)

    elif model_type == "shared_field_type":
        _logger.info("Pushing shared field type to nomitall")
        resp = session.request("POST", "shared_field_type/update", json=model)

    elif model_type == "shared_object_type":
        _logger.info("Pushing shared object type to nomitall")
        session.request("POST", "shared_object_type/update", json=model)

    elif model_type == "connection":
        _logger.info("Pushing connection type to nomitall")
        session.request("POST", "connection_type/update", json=model)
