from setuptools import setup

setup(
    name='aim.models',
    version='1.0.0',
    description='aim.models: Semantic cloud infrastructure configuration file format and object model',
    url='https://waterbear.cloud',
    install_requires=['Setuptools', 'ruamel.yaml', 'zope.schema'],
    packages=[
        'aim.models',
    ],
    include_package_data=True,
    zip_safe=False,
    package_dir={'': 'src'},
)
