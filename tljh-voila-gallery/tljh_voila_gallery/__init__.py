import socket
import sys
from ruamel.yaml import YAML
from tljh.hooks import hookimpl
from tornado import web

from dockerspawner import DockerSpawner
from nullauthenticator import NullAuthenticator

from .install_builder_units import ensure_builder_units

yaml = YAML()


class GallerySpawner(DockerSpawner):
    cmd = ['jupyter-notebook']

    # rm containers when they stop
    remove = False

    # events = False

    http_timeout = 30

    def get_args(self):
        args = [
            '--ip=0.0.0.0',
            '--port=%i' % self.port,
            '--NotebookApp.base_url=%s' % self.server.base_url,
            '--NotebookApp.token=%s' % self.user_options['token'],
            '--NotebookApp.tornado_settings.trust_xheaders=True',
            # stop idle servers
            '--NotebookApp.shutdown_no_activity_timeout=600',
            '--MappingKernelManager.cull_idle_timeout=600',
            '--MappingKernelManager.cull_interval=60',
            '--MappingKernelManager.cull_connected=True',
            # voila params
            '--VoilaConfiguration.enable_nbextensions=True',
            '--VoilaConfiguration.extension_language_mapping={".py": "python"}'
        ]
        return args + super().get_args()

    def start(self):
        if 'token' not in self.user_options:
            raise web.HTTPError(400, "token required")
        if 'image' not in self.user_options:
            raise web.HTTPError(400, "image required")
        self.image = self.user_options['image']

        self.volumes['neurolang_volume'] = {
            'bind': '/home/jovyan/notebooks/neurolang_data',
            'mode': 'rw',
        }
        return super().start()


class GalleryAuthenticator(NullAuthenticator):
    auto_login = True

    def login_url(self, base_url):
        return '/services/gallery'


@hookimpl
def tljh_custom_jupyterhub_config(c):
    c.JupyterHub.spawner_class = GallerySpawner
    c.JupyterHub.authenticator_class = GalleryAuthenticator

    c.JupyterHub.hub_connect_ip = socket.gethostname()

    # Don't kill servers when hub restarts
    c.JupyterHub.cleanup_servers = False

    c.JupyterHub.services = [{
        'name': 'gallery',
        'admin': True,
        'url': 'http://127.0.0.1:9888',
        'command': [
            sys.executable, '-m', 'tljh_voila_gallery.gallery'
        ]
    }]


@hookimpl
def tljh_extra_apt_packages():
    return [
        'docker.io'
    ]


@hookimpl
def tljh_post_install():
    ensure_builder_units()
