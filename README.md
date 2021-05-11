# LinkML Model Enrichments

## Reccomended Installation

The installation for LINKML_MODEL_ENRICHMENT requires Python 3.9 or greater.

```bash
git clone https://github.com/linkml/linkml-model-enrichment
cd linkml_model_enrichment
```

_more to come_

----

_Tests temporarily disabled_

[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)]()
![Run tests](https://github.com/linkml/linkml-model-enrichment/workflows/Run%20tests/badge.svg)[![Documentation Status](https://readthedocs.org/projects/linkml_model_enrichment/badge/?version=latest)](https://linkml_model_enrichment.readthedocs.io/en/latest/?badge=latest)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=biolink_linkml_model_enrichment&metric=alert_status)](https://sonarcloud.io/dashboard?id=biolink_linkml_model_enrichment)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=biolink_linkml_model_enrichment&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=biolink_linkml_model_enrichment)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=biolink_linkml_model_enrichment&metric=coverage)](https://sonarcloud.io/dashboard?id=biolink_linkml_model_enrichment)
[![PyPI](https://img.shields.io/pypi/v/linkml_model_enrichment)](https://img.shields.io/pypi/v/linkml_model_enrichment)
[![Docker](https://img.shields.io/static/v1?label=Docker&message=linkml/linkml-model-enrichment:latest&color=orange&logo=docker)](https://hub.docker.com/r/linkml/linkml-model-enrichment)


## Installation


### Installation for users


#### Installing from PyPI

_Not deployed to PyPI yet_

LINKML_MODEL_ENRICHMENT is available on PyPI and can be installed using
[pip](https://pip.pypa.io/en/stable/installing/) as follows,

```bash
pip install linkml_model_enrichment
```

To install a particular version of LINKML_MODEL_ENRICHMENT, be sure to specify the version number,

```bash
pip install linkml_model_enrichment==0.5.0
```


#### Installing from GitHub

_See new, less-automated installation directions above_

Clone the GitHub repository and then install,

```bash
git clone https://github.com/linkml/linkml-model-enrichment
cd linkml_model_enrichment
python setup.py install
```


### Installation for developers

_See new, less-automated installation directions above_

#### Setting up a development environment

To build directly from source, first clone the GitHub repository,

```bash
git clone https://github.com/linkml/linkml-model-enrichment
cd linkml_model_enrichment
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

To install LINKML_MODEL_ENRICHMENT you can do one of the following,

```bash
pip install .

# OR 

python setup.py install
```

### Setting up a testing environment

