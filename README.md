# Neurolang Gallery plugin for The Littlest JupyterHub

A plugin for [The Littlest JupyterHub (TLJH)](https://tljh.jupyter.org) to build and use Docker images as user environments. The Docker images are built using [`repo2docker`](https://repo2docker.readthedocs.io/en/latest/).

This plugin has been adapted from [tljh-repo2docker](https://github.com/plasmabio/tljh-repo2docker) to serve [Voila](https://github.com/voila-dashboards/voila/tree/stable) apps for [neurolang_web](https://github.com/NeuroLang/neurolang_web).


## Installation

Neurolang_gallery needs to be installed as a plugin for The Littlest JupyterHub:

During the [TLJH installation process](http://tljh.jupyter.org/en/latest/install/index.html), use the following post-installation script:

```bash
#!/bin/bash

# install Docker
sudo apt update && sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository -y "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"
sudo apt update && sudo apt install -y docker-ce

# pull the repo2docker image
sudo docker pull jupyter/repo2docker:master

# install TLJH
curl https://raw.githubusercontent.com/jupyterhub/the-littlest-jupyterhub/master/bootstrap/bootstrap.py \
  | sudo python3 - \
    --admin admin \
    --plugin git+https://github.com/NeuroLang/neurolang_gallery@master#"egg=neurolang-gallery"
```

Refer to [The Littlest JupyterHub documentation](http://tljh.jupyter.org/en/latest/topic/customizing-installer.html?highlight=plugins#installing-tljh-plugins)
for more info on installing TLJH plugins.

The first part of the script installs docker on the machine and pulls the repo2docker image which is used to run repo2docker in a docker container. The last part of the script installs TLJH with the neurolang_gallery plugin.

## Updating

Once TLJH has been installed on a server with the neurolang_gallery plugin, to update neurolang_gallery when code changes, use:

```bash
sudo /opt/tljh/hub/bin/python3 -m pip install -U  git+https://github.com/NeuroLang/neurolang_gallery@master#"egg=neurolang-gallery"
```

## How it works
The application installs TLJH which comes with traefik.service that runs a [traefik](https://github.com/traefik/traefik) reverse proxy.

[repo2docker](https://github.com/jupyterhub/repo2docker) is used to create Docker images. `repo2docker` options are specified in [docker.py](./tljh_repo2docker/docker.py) file.

It takes advantage of [JupyterHub Docker Spawner](https://github.com/jupyterhub/dockerspawner) to spawn single user notebook servers in Docker containers. Additional configuration options can be set in [\_\_init\_\_.py](./tljh_repo2docker/__init__.py) file. 


## Usage

### List the environments

The *Environments* page shows the list of built environments, as well as the ones currently being built:

![environments](https://user-images.githubusercontent.com/591645/80962805-056df500-8e0e-11ea-81ab-6efc1c97432d.png)

### Add a new environment

Just like on [Binder](https://mybinder.org), new environments can be added by clicking on the *Add New* button and providing a URL to the repository. Optional names, memory, and CPU limits can also be set for the environment:

![add-new](https://user-images.githubusercontent.com/591645/80963115-9fce3880-8e0e-11ea-890b-c9b928f7edb1.png)

### Follow the build logs

Clicking on the *Logs* button will open a new dialog with the build logs:

![logs](https://user-images.githubusercontent.com/591645/82306574-86f18580-99bf-11ea-984b-4749ddde15e7.png)

### Select an environment

Once ready, the environments can be selected from the JupyterHub spawn page:

![select-env](https://user-images.githubusercontent.com/591645/81152248-10e22d00-8f82-11ea-9b5f-5831d8f7d085.png)

### Private Repositories

There is support for building environments from private repositories.

It is possible to provide the `username` and `password` in the `Credentials` section of the form:

![image](https://user-images.githubusercontent.com/591645/107362654-51567480-6ad9-11eb-93be-74d3b1c37828.png)

On GitHub and GitLab, a user might have to first create an access token with `read` access to use as the password:

![image](https://user-images.githubusercontent.com/591645/107350843-39c3bf80-6aca-11eb-8b82-6fa95ba4c7e4.png)

### Run repo2docker as a command-line script

You can also build docker images by running repo2docker directly as a command line script, instead of from the web interface which runs repo2docker in a docker container :

```bash
build-image --ref=master --name=neurolangweb --repo=https://github.com/NeuroLang/neurolang_web
```

This lets you build images from a local repository by specifying a path to a local repo:

```bash
build-image --ref=master --name=dev_neuroweb --repo=/local/path/to/repository
```

You can also choose to build all the images listed in the `gallery.yaml` file by using the `--file` option:

```bash
build-image --file
```

## Building JupyterHub-ready images

See: https://repo2docker.readthedocs.io/en/latest/howto/jupyterhub_images.html

## Run Locally

Check out the instructions in [CONTRIBUTING.md](./CONTRIBUTING.md) to setup a local environment.

# The gallery

The application is a jupyterhub server, which allows admins to create docker images (**Environments**) containing all the required environment to run the code in a specified repository. See the doc for repo2docker for details on what these images look like. Once an **Environment** has been created by an admin of the application, any user with an account on the jupyterhub application can start a docker container running its personal jupyter-notebook instance setup to execute the notebooks in the repository.

The **neurolang_gallery** application is setup to serve a single-page gallery by default. This is configured in the jupyterhub config in [`tljh_repo2docker/__init__.py`](tljh_repo2docker/__init__.py).
This gallery page is served by the **GalleryHandler** in [`gallery.py`. ](tljh_repo2docker/gallery.py)
The examples to display on the page are listed in the [`gallery.yaml`](tljh_repo2docker/gallery.yaml) page. Each example has a title, description, and the name of a docker image (which must be one of the **Environments** generated on the server by an admin).

When the user clicks on one of the examples in the gallery, the **GalleryHandler** will create a new jupyter-hub user and start a server for this user using the docker image that is specified for the example in the `gallery.yaml` file. The page is then redirected to the url of this running server, with the auth token to identify the temporary jupyter-hub user whose server is running.

## DockerSpawner configuration

The jupyterhub configuration and more specifically the DockerSpawner parameter can be used to configure how the notebook servers are created/run.

For example, in order to be able to use **Voila** in the example notebooks, the [DockerSpawner](tljh_repo2docker/__init.py) starts the notebook servers with extra parameters:

```python
args = [
    "--VoilaConfiguration.enable_nbextensions=True",
    '--VoilaConfiguration.extension_language_mapping={".py": "python"}',
]
```

We also mount a shared volume on the docker containers so that example data for the notebooks doesn't have to be downloaded each time a new container is created:

```python
c.DockerSpawner.volumes = {
    "neurolang_volume": os.path.join(
        notebook_dir, "gallery/neurolang_data"
    )
}
```