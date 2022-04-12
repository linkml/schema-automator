from setuptools import setup, find_packages

NAME = 'schema_automator'
DESCRIPTION = 'toolkit that assists with generating LinkML schemas from existing serializations like JSON-schema'
URL = 'https://github.com/linkml/schema_automator'
AUTHOR = 'Mark Miller'
EMAIL = 'mam@lbl.gov'
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
    include_package_data=True,
    keywords='linkml',
    classifiers=[
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3'
    ],
    install_requires=[r for r in REQUIREMENTS if not r.startswith("#")],
    extras_require=EXTRAS,
    entry_points={
        'console_scripts': ['annotate-enums=schema_automator.annotators.enum_annotator:clickmain',
                            'annotate-schema=schema_automator.annotators.schema_annotator:annotate_schema',
                            'tsv2linkml=schema_automator.importers.csv_import_engine:tsv2model',
                            'tsvs2linkml=schema_automator.importers.csv_import_engine:tsvs2model',
                            'rdf2linkml=schema_automator.importers.rdf_instance_import_engine:rdf2model',
                            'owl2linkml=schema_automator.importers.owl_import_engine:owl2model',
                            'dosdp2linkml=schema_automator.importers.owl_import_engine:dosdp2model',
                            'jsondata2linkml=schema_automator.importers.json_instance_import_engine:json2model',
                            'jsonschema2linkml=schema_automator.importers.jsonschema_import_engine:jsonschema2model',
                            ]
    }
)
