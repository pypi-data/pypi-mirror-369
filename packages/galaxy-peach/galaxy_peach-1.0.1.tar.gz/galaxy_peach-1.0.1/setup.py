from setuptools import setup, find_packages

setup(
    name="galaxy-peach",
    version="1.0.0",  # bumped version
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "galaxy": ["labextension/**"]  # ensure frontend assets included
    },
    install_requires=["jupyter_server"],
    entry_points={"jupyter_serverextension": ["galaxy = galaxy"]},
)
