import setuptools

"""
README

`setup.py` is only needed for distributing the project as a python package
using `setuptools`.

When developing a python application, the project doesn't need to have `setup.py`
and `setup.cfg`.

Since `python-service` is a package used by other python app as a dependency,
`setup.py` is needed in this project.

install_requires:
    It lists the dependencies that must be installed.
    Python application using this library will automatically install the packages
    listed under `install_requires`.

See readme in `python_service/service.py` for how to deploy package.

"""
setuptools.setup(
    name="jiesu_python_service",
    version="1.18",
    description="A Python Service",
    author="Jie Su",
    install_requires=["requests", "py-eureka-client"],
    packages=setuptools.find_packages(),
    zip_safe=False,
)
