from setuptools import setup, find_packages

NAME = 'linkml_model_inference'
DESCRIPTION = 'A Python library and set of command line utilities for exchanging Knowledge Graphs (KGs) that conform to or are aligned to the Biolink Model.'
URL = 'https://github.com/NCATS-Tangerine/linkml_model_inference'
AUTHOR = 'Deepak Unni'
EMAIL = 'deepak.unni3@gmail.com'
REQUIRES_PYTHON = '>=3.7.0'
VERSION = '1.0.0b0'
LICENSE = 'BSD'

with open("requirements.txt", "r") as FH:
    REQUIREMENTS = FH.readlines()

EXTRAS = {}

setup(
    name=NAME,
    author=AUTHOR,
    version=VERSION,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    description=DESCRIPTION,
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license=LICENSE,
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    package_data={'linkml_model_inference': ["config.yml"]},
    keywords='linkml',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3'
    ],
    install_requires=[r for r in REQUIREMENTS if not r.startswith("#")],
    extras_require=EXTRAS,
    include_package_data=True,
    entry_points={
        'console_scripts': ['annotate-enums=linkml_model_enrichment.annotators.enum_annotator:clickmain',
                            'tsv2linkml=linkml_model_enrichment.importers.csv_import_engine:tsv2model',
                            'tsvs2linkml=linkml_model_enrichment.importers.csv_import_engine:tsvs2model',
                            'rdf2linkml=linkml_model_enrichment.importers.rdf_instance_import_engine:rdf2model',
                            'owl2linkml=linkml_model_enrichment.importers.owl_import_engine:owl2model',
                            ]
    }
)
