from inspect import isawaitable
from jupyterhub.handlers.base import BaseHandler
from jupyterhub.utils import admin_only
from binderhub.launcher import Launcher
from tornado import web
from .docker import list_containers, list_images
import yaml
from pkg_resources import resource_stream
from urllib.parse import urlencode, urljoin


# Read gallery.yaml. Only keep the examples that have a corresponding Docker image
async def get_gallery():
    with resource_stream(__name__, "gallery.yaml") as f:
        gallery = yaml.safe_load(f)
    images = await list_images()
    containers = await list_containers()
    image_names = {i["image_name"] for i in images + containers}
    gallery = {
        name: ex
        for name, ex in gallery.get("examples", {}).items()
        if ex["image_name"] in image_names
    }
    return gallery


class GalleryHandler(BaseHandler):
    """
    Handler to show the list of notebooks that can be run
    """

    # @web.authenticated
    # @admin_only
    async def get(self):
        gallery = await get_gallery()
        result = self.render_template(
            "gallery.html",
            gallery=gallery,
            url=self.request.uri,
            default_mem_limit=self.settings.get("default_mem_limit"),
            default_cpu_limit=self.settings.get("default_cpu_limit"),
        )
        if isawaitable(result):
            self.write(await result)
        else:
            self.write(result)

    async def post(self):
        print("HELLO")
        image_name = self.get_body_argument("image_name")
        repo_url = self.get_body_argument("repo_url")
        path = self.get_body_argument("path")

        launcher = Launcher(
            # hub_api_token=os.environ["JUPYTERHUB_API_TOKEN"],
            # hub_url=os.environ["JUPYTERHUB_BASE_URL"],
            hub_api_token="SOME_TOKEN",
            hub_url="SOME_API_URL",
        )
        response = await launcher.launch(
            image_name, launcher.unique_name_from_repo(repo_url)
        )
        redirect_url = (
            urljoin(response["url"], path)
            + "?"
            + urlencode({"token": response["token"]})
        )
        self.redirect(redirect_url)
