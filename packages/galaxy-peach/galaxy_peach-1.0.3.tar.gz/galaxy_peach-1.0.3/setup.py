from setuptools import setup, find_packages

setup(
    name="galaxy-peach",
    version="1.0.2",  # bump
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "galaxy": ["labextension/**"]
    },
    install_requires=["jupyter_server"],
)
