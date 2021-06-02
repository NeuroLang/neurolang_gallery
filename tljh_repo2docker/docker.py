import json
import subprocess
import sys
from urllib.parse import urlparse

import click
import yaml
from aiodocker import Docker
from pkg_resources import resource_stream


async def list_images():
    """
    Retrieve local images built by repo2docker
    """
    async with Docker() as docker:
        r2d_images = await docker.images.list(
            filters=json.dumps(
                {"dangling": ["false"], "label": ["repo2docker.ref"]}
            )
        )
    images = [
        {
            "repo": image["Labels"]["repo2docker.repo"],
            "ref": image["Labels"]["repo2docker.ref"],
            "image_name": image["Labels"]["tljh_repo2docker.image_name"],
            "display_name": image["Labels"]["tljh_repo2docker.display_name"],
            "mem_limit": image["Labels"]["tljh_repo2docker.mem_limit"],
            "cpu_limit": image["Labels"]["tljh_repo2docker.cpu_limit"],
            "status": "built",
        }
        for image in r2d_images
        if "tljh_repo2docker.image_name" in image["Labels"]
    ]
    return images


async def list_containers():
    """
    Retrieve the list of local images being built by repo2docker.
    Images are built in a Docker container.
    """
    async with Docker() as docker:
        r2d_containers = await docker.containers.list(
            filters=json.dumps({"label": ["repo2docker.ref"]})
        )
    containers = [
        {
            "repo": container["Labels"]["repo2docker.repo"],
            "ref": container["Labels"]["repo2docker.ref"],
            "image_name": container["Labels"]["repo2docker.build"],
            "display_name": container["Labels"][
                "tljh_repo2docker.display_name"
            ],
            "mem_limit": container["Labels"]["tljh_repo2docker.mem_limit"],
            "cpu_limit": container["Labels"]["tljh_repo2docker.cpu_limit"],
            "status": "building",
        }
        for container in r2d_containers
        if "repo2docker.build" in container["Labels"]
    ]
    return containers


def get_repo2docker_cmd(repo, ref, name="", memory=None, cpu=None):
    """
    Create the command to build an image with repo2docker given a repo, ref and limits
    """
    ref = ref or "master"
    if len(ref) >= 40:
        ref = ref[:7]

    # default to the repo name if no name specified
    # and sanitize the name of the docker image
    name = name or urlparse(repo).path.strip("/")
    name = name.lower().replace("/", "-")
    image_name = f"{name}:{ref}"

    # memory is specified in GB
    memory = f"{memory}G" if memory else ""
    cpu = cpu or ""

    # add extra labels to set additional image properties
    labels = [
        f"LABEL tljh_repo2docker.display_name={name}",
        f"LABEL tljh_repo2docker.image_name={image_name}",
        f"LABEL tljh_repo2docker.mem_limit={memory}",
        f"LABEL tljh_repo2docker.cpu_limit={cpu}",
    ]
    cmd = [
        sys.executable,
        "-m",
        "repo2docker",
        "--ref",
        ref,
        "--user-name",
        "jovyan",
        "--user-id",
        "1100",
        "--no-run",
        "--image-name",
        image_name,
        "--appendix",
        "\n".join(labels),
        repo,
    ]
    return cmd, image_name


async def build_image(
    repo, ref, name="", memory=None, cpu=None, username=None, password=None
):
    """
    Build an image given a repo, ref and limits
    """
    cmd, image_name = get_repo2docker_cmd(repo, ref, name, memory, cpu)

    config = {
        "Cmd": cmd,
        "Image": "jupyter/repo2docker:master",
        "Labels": {
            "repo2docker.repo": repo,
            "repo2docker.ref": ref,
            "repo2docker.build": image_name,
            "tljh_repo2docker.display_name": name,
            "tljh_repo2docker.mem_limit": memory,
            "tljh_repo2docker.cpu_limit": cpu,
        },
        "Volumes": {
            "/var/run/docker.sock": {
                "bind": "/var/run/docker.sock",
                "mode": "rw",
            }
        },
        "HostConfig": {
            "Binds": ["/var/run/docker.sock:/var/run/docker.sock"],
        },
        "Tty": False,
        "AttachStdout": False,
        "AttachStderr": False,
        "OpenStdin": False,
    }

    if username and password:
        config.update(
            {
                "Env": [
                    f"GIT_CREDENTIAL_ENV=username={username}\npassword={password}"
                ],
            }
        )

    async with Docker() as docker:
        await docker.containers.run(config=config)


@click.command()
@click.option("--repo", help="The path for the repo to clone")
@click.option("--ref", default="master", help="The branch/ref for the repo")
@click.option(
    "--name", default="", help="A unique name for the docker image generated"
)
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

