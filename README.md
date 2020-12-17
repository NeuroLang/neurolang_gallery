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


Note:
-----
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

## License

This software is licensed under the BSD-3-Clause license. See the
[LICENSE](LICENSE) file for details.
