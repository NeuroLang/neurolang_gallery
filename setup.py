from setuptools import setup, find_packages

setup(
    name="tljh-repo2docker",
    version="0.0.1",
    entry_points={
        "tljh": ["tljh_repo2docker = tljh_repo2docker"],
        "console_scripts": [
            "build-image = tljh_repo2docker.docker:build_docker_image",
        ],
    },
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "click",
        "pyyaml",
        "nullauthenticator",
        "dockerspawner~=0.11",
        "jupyter_client~=6.1",
        "aiodocker~=0.19",
    ],
)