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

It installs and starts the systemd service  [tljh-voila-gallery-builder.service](./tljh-voila-gallery/tljh_voila_gallery/systemd-units/tljh-voila-gallery-builder.service) to create a Docker image for each entry in the [gallery.yaml](./tljh-voila-gallery/tljh_voila_gallery/gallery.yaml) file. [repo2docker](https://github.com/jupyterhub/repo2docker) is used to create Docker images.

It takes advantage of [JupyterHub Docker Spawner](https://github.com/jupyterhub/dockerspawner) to spawn single user notebook servers in Docker containers. Additional configuration options can be set in [\_\_init\_\_.py](./tljh-voila-gallery/tljh_voila_gallery/__init__.py) file. 

### Looking at service logs

On the server, run 

#### builder service 

`sudo journalctl -u tljh-voila-gallery-builder.service`

#### traefik service

`sudo journalctl -u traefik.service`

## License

This software is licensed under the BSD-3-Clause license. See the
[LICENSE](LICENSE) file for details.
