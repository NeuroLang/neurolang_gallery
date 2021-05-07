# Neurolang Gallery plugin for The Littlest JupyterHub

A plugin for [The Littlest JupyterHub (TLJH)](https://tljh.jupyter.org) that installs a [Voilà](https://voila-gallery.org/) Gallery for [neurolang_web](https://github.com/NeuroLang/neurolang_web) example notebooks.

## Installation

To install an instance of neurolang-gallery as a plugin for The Littlest JupyterHub:

```
$ sudo apt install python3 python3-dev git curl

$ curl -L https://tljh.jupyter.org/bootstrap.py  | sudo python3 - --plugin \
git+https://github.com/NeuroLang/neurolang_gallery@master#"egg=neurolang-gallery&subdirectory=tljh-voila-gallery"
```


This will install [The Littlest JupyterHub](https://github.com/jupyterhub/the-littlest-jupyterhub) and neurolang-gallery as a plugin.

The install process might take between 5 and 10 minutes to complete. 

The gallery will be available at [localhost](http://localhost).

## Modifying the gallery

[gallery.yaml](./tljh-voila-gallery/tljh_voila_gallery/gallery.yaml)  file defines which notebooks to display in the gallery. This file should be edited to change the contents of the gallery.

## How it works
The application installs TLJH which comes with traefik.service that runs a [traefik](https://github.com/traefik/traefik) reverse proxy.

It installs and starts the systemd service  [tljh-voila-gallery-builder.service](./tljh-voila-gallery/tljh_voila_gallery/systemd-units/tljh-voila-gallery-builder.service) to create a Docker image for each entry in the [gallery.yaml](./tljh-voila-gallery/tljh_voila_gallery/gallery.yaml) file. 

[repo2docker](https://github.com/jupyterhub/repo2docker) is used to create Docker images. `repo2docker` options are specified in [build_images.py](https://github.com/NeuroLang/neurolang_gallery/blob/master/tljh-voila-gallery/tljh_voila_gallery/build_images.py) file.

It takes advantage of [JupyterHub Docker Spawner](https://github.com/jupyterhub/dockerspawner) to spawn single user notebook servers in Docker containers. Additional configuration options can be set in [\_\_init\_\_.py](./tljh-voila-gallery/tljh_voila_gallery/__init__.py) file. 


### Note

neurolang_gallery project displays notebooks from [neurolang_web]() project. 3 basic modifications are made in [\_\_init\_\_.py](./tljh-voila-gallery/tljh_voila_gallery/__init__.py) file to display the notebooks correctly and efficiently.

* notebooks use [neurolang_ipywidgets](https://github.com/NeuroLang/neurolang_ipywidgets). To be able to use nbextenssions `--VoilaConfiguration.enable_nbextensions=True` flag should be set while spawning notebooks as in https://github.com/NeuroLang/neurolang_gallery/blob/0ec4ab84cd4686b49e5363b7fdadcfd9e428bb33/tljh-voila-gallery/tljh_voila_gallery/__init__.py#L38.

* notebooks are in `.py` format rather than `.ipynb` format. To display the notebooks correctly `--VoilaConfiguration.extension_language_mapping={".py": "python"}` flag should be set as in https://github.com/NeuroLang/neurolang_gallery/blob/0ec4ab84cd4686b49e5363b7fdadcfd9e428bb33/tljh-voila-gallery/tljh_voila_gallery/__init__.py#L39.

* notebooks download data. A shared volume is used not to download the same data for each generated container. This is possible by adding the following line:

```
self.volumes['neurolang_volume'] = {
            'bind': '/home/jovyan/notebooks/neurolang_data',
            'mode': 'rw',
        }
```

in https://github.com/NeuroLang/neurolang_gallery/blob/0ec4ab84cd4686b49e5363b7fdadcfd9e428bb33/tljh-voila-gallery/tljh_voila_gallery/__init__.py#L50.

### Updating gallery installation

If update is due to a change in the **neurolang_gallery** project:

```
$ sudo /opt/tljh/hub/bin/python3 -m pip install -U  \
git+https://github.com/NeuroLang/neurolang_gallery@master#"egg=neurolang-gallery&subdirectory=tljh-voila-gallery"

$ sudo systemctl restart jupyterhub.service
```

If container images should be regenerated: 

```
$ curl -L https://tljh.jupyter.org/bootstrap.py  | sudo python3 - --plugin \
git+https://github.com/NeuroLang/neurolang_gallery@master#"egg=neurolang-gallery&subdirectory=tljh-voila-gallery"
```

### Looking at service logs

On the server, run 

#### builder service 

`$ sudo journalctl -u tljh-voila-gallery-builder.service`

#### traefik service

`$ sudo journalctl -u traefik.service`

## Setting up neurolang_gallery for a local development environment (macOS)

It is recommended to not install TLJH directly on your laptop or personal computer! It will most likely open up exploitable security holes when run directly on your personal computer. Instead, [TLJH](https://tljh.jupyter.org/en/latest/contributing/dev-setup.html#contributing-dev-setup) recommends running locally inside a docker container for development, which also allows you to run TLJH on a macOS machine.

Follow the steps in the [tutorial](https://tljh.jupyter.org/en/latest/contributing/dev-setup.html#contributing-dev-setup) to create a docker image with systemd and tljh and start a container in the background.
When starting the container, add a mount volume pointing to your local working directory to be able to install `neurolang_gallery` and `neurolang_web` projects from file instead of from a git repository:

```sh
docker run \
  --privileged \
  --detach \
  --name=tljh-dev \
  --publish 12000:80 \
  --mount type=bind,source=$(pwd),target=/srv/src \
  --mount type=bind,source=<your-working-dir>,target=/srv/workspace
  tljh-systemd
```

Replace `<your-working-dir>` with the path to your working directory containing `neurolang_gallery` and `neurolang_web`.

You can then get a shell inside the running docker container.

```sh
docker exec -it tljh-dev /bin/bash
```

Once inside the container, you can install TLJH with your local clone of the `neurolang_gallery` plugin :

```sh
sudo python3 /srv/src/bootstrap/bootstrap.py --admin admin --plugin /srv/workspace/neurolang_gallery/tljh-voila-gallery/
```

This allows you to also add local repositories in the `gallery.yaml` file by pointing the url to `srv/workspace/<a-python-repo-with-notebooks>` :

```yaml
examples:
  localdestrieux:
    title: Destrieux
    description: Run queries using Neurolang library with destrieux cortical atlas (2009) dataset and explore results.
    url: voila/render/gallery/Destrieux.py
    repo_url: /srv/workspace/neurolang_web
    ref: master
    image_url: https://avatars2.githubusercontent.com/u/35116292?s=200&v=4
```

---
**NOTE**

The `tljh-voila-gallery` plugin installs docker using apt inside the docker container, since it is required to build the images for the repositories in gallery.yaml. However it sometimes fails to start the docker service required to use docker. Run `sudo systemctl status docker` to check that docker is running, and if it is not, run `sudo systemctl start docker` to start it.

Also note that the `tljh-voila-gallery-builder` service builds docker images for each repository in the `gallery.yaml` file, and these images are quite large (>3GB) and can quickly run out the memory allocated to the docker container in which tljh runs. If the `tljh-voila-gallery-builder` service fails because of memory issues, increase the memory allocated to the docker container.

---

If you update the `gallery.yaml` file or any other part of the `neurolang_gallery` app, it can be reinstalled with :

```sh
sudo /opt/tljh/hub/bin/python3 -m pip install -U /srv/workspace/neurolang_gallery/tljh-voila-gallery/
```

Make sure to restart the required services. The `jupyter-hub` service serves the web page displaying the notebooks at `localhost:12000` (the 12000 port comes from the publish mapping specified when creating the docker container)

```sh
sudo systemctl restart jupyterhub.service
```

The `tljh-voila-gallery-builder` service builds the docker images for the repositories specified in `gallery.yaml`. Check that the images are built correctly with

```sh
sudo journalctl -u tljh-voila-gallery-builder.service
```

and eventually restart it to rebuild the images.

However, building the images for the notebooks is quite inefficient when done in a docker container. It is preferable to build them on your host machine, by running

```sh
python -m tljh_voila_gallery.build_images
```

This script will create docker images for each entry in `gallery.yaml`. These images then need to be mounted 


## License

This software is licensed under the BSD-3-Clause license. See the
[LICENSE](LICENSE) file for details.
