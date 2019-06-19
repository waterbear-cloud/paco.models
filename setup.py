from setuptools import setup

setup(
    name='aim',
    version='1.0.0.dev0',
    description='aim.models: Semantic cloud infrastructure configuration file format and data model.',
    url='https://waterbear.cloud',
    install_requires=['Setuptools', 'click', 'ruamel.yaml', 'boto3', 'tldextract', 'zope.schema'],
    packages=[
        'aim.models',
    ],
    include_package_data=True,
    zip_safe=False,
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'aim = aim.commnads.cli:cli'
        ]
    },
)
