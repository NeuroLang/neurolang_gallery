import subprocess

import click
import yaml
from pkg_resources import resource_stream

from tljh_repo2docker.docker import get_repo2docker_cmd


@click.command()
@click.option("--repo", help="The path for the repo to clone")
@click.option("--ref", default="master", help="The branch/ref for the repo")
@click.option("--name", default="", help="A unique name for the docker image generated")
@click.option(
    "--memory",
    help="memory in GB to allocate when starting a container with this image",
)
@click.option(
    "--cpu",
    help="nb cpus to allocate when starting a container with this image",
)
@click.option(
    "-f",
    "--file",
    is_flag=True,
    help="build the images specified in the gallery.yaml file.",
)
def build_docker_image(repo, ref, name, memory=None, cpu=None, file=False):
    if file:
        with resource_stream(__name__, "gallery.yaml") as f:
            gallery = yaml.safe_load(f)
        for name, infos in gallery.get("images", {}).items():
            click.echo(f"Building image {name} with options {infos}.")
            cmd, _ = get_repo2docker_cmd(name=name, **infos)
            subprocess.run(cmd)
    elif repo is not None:
        click.echo(
            "Building image {} with options {}".format(
                name, {"ref": ref, "name": name, "memory": memory, "cpu": cpu}
            )
        )
        cmd, _ = get_repo2docker_cmd(repo, ref, name, memory, cpu)
        subprocess.run(cmd)
    else:
        click.echo(
            "You must provide either a repo url (using the --repo option) or choose to "
            "build images listed in the gallery.yaml file using the --file option.\n"
            "Use build-image --help for usage details."
        )


if __name__ == "__main__":
    build_docker_image()
