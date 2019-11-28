# paco.models

An object model for semantic cloud infrastructure.

`paco.models` parses a directory of YAML files that compose an Paco project and loads them
into a complete object model.


## What's in the model?

The model defines common logical cloud infrastructure concepts, such as networks, accounts,
applications and environments.

The model uses network and applications as hierarchical trees of configuration that can
have their values over rode when they are placed into environments. Environments live in a
network and contain applications, and typically represent the stages of the software development
lifecycle (SDLC), such as 'development', 'staging' and 'production'.

The model has a declarative schema that explicitly defines the fields for each object type in the model.
This schema declares not only type (e.g. string, integer) but can also declare defaults, min and max values,
constrain to specific values, and define invariants that ensure that if one field has a specific value, another
fields value is compatabile with that. The model will validates these fields when it loads a Paco project.


## Developing

Install this package with your Python tool of choice. Typically set-up a virtualenv
and pip install the dependencies in there:

    python -m venv env

    ./env/bin/pip install -e .

There are unit tests using PyTest. If you are using VS Code you can turn on the
"Py Test Enabled" setting and run "Discover Unit Tests" command.
