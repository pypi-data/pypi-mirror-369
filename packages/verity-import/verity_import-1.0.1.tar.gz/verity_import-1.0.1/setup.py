from setuptools import find_packages, setup

setup(
    name='verity-import',
    version='1.0.1',
    description='Import a Verity system into Netbox',
    install_requires=[],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)