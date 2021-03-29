# LinkML Model Inferences

[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)]()
![Run tests](https://github.com/linkml/linkml-model-inference/workflows/Run%20tests/badge.svg)[![Documentation Status](https://readthedocs.org/projects/linkml_model_inference/badge/?version=latest)](https://linkml_model_inference.readthedocs.io/en/latest/?badge=latest)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=biolink_linkml_model_inference&metric=alert_status)](https://sonarcloud.io/dashboard?id=biolink_linkml_model_inference)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=biolink_linkml_model_inference&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=biolink_linkml_model_inference)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=biolink_linkml_model_inference&metric=coverage)](https://sonarcloud.io/dashboard?id=biolink_linkml_model_inference)
[![PyPI](https://img.shields.io/pypi/v/linkml_model_inference)](https://img.shields.io/pypi/v/linkml_model_inference)
[![Docker](https://img.shields.io/static/v1?label=Docker&message=linkml/linkml-model-inference:latest&color=orange&logo=docker)](https://hub.docker.com/r/linkml/linkml-model-inference)


## Installation

The installation for LINKML_MODEL_INFERENCE requires Python 3.7 or greater.


### Installation for users


#### Installing from PyPI

LINKML_MODEL_INFERENCE is available on PyPI and can be installed using
[pip](https://pip.pypa.io/en/stable/installing/) as follows,

```bash
pip install linkml_model_inference
```

To install a particular version of LINKML_MODEL_INFERENCE, be sure to specify the version number,

```bash
pip install linkml_model_inference==0.5.0
```


#### Installing from GitHub

Clone the GitHub repository and then install,

```bash
git clone https://github.com/linkml/linkml-model-inference
cd linkml_model_inference
python setup.py install
```


### Installation for developers

#### Setting up a development environment

To build directly from source, first clone the GitHub repository,

```bash
git clone https://github.com/linkml/linkml-model-inference
cd linkml_model_inference
```

Then install the necessary dependencies listed in ``requirements.txt``,

```bash
pip3 install -r requirements.txt
```


For convenience, make use of the `venv` module in Python3 to create a
lightweight virtual environment,

```
python3 -m venv env
source env/bin/activate

pip install -r requirements.txt
```

To install LINKML_MODEL_INFERENCE you can do one of the following,

```bash
pip install .

# OR 

python setup.py install
```

### Setting up a testing environment

