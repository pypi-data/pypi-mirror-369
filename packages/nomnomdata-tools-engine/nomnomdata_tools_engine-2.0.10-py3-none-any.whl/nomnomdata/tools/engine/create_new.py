import shutil
from os import makedirs, path
from pathlib import Path

import click
from jinja2 import Template


@click.command()
@click.argument("engine_name", required=True)
def create_new(engine_name):
    """Create a new engine template folder at the given ENGINE_NAME"""
    t_dir = path.join(path.dirname(__file__), "template")

    def ignore(dir, files):
        return [f for f in files if f == "__pycache__" or f.endswith(".pyc")]

    def copymap(src, dest):
        if src.endswith(".pyc"):
            return
        template = Template(Path(src).read_text())
        makedirs(path.dirname(dest), exist_ok=True)
        template = template.render(engine_name=engine_name)
        with open(dest, "w") as outfile:
            outfile.write(template)

    shutil.copytree(t_dir, engine_name, ignore=ignore, copy_function=copymap)
