<a href="https://pypi.org/project/libquery/">
    <img alt="Newest PyPI version" src="https://img.shields.io/pypi/v/libquery.svg">
</a>
<a href="https://github.com/psf/black">
    <img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg">
</a>
<a href="http://commitizen.github.io/cz-cli/">
    <img alt="Commitizen friendly" src="https://img.shields.io/badge/commitizen-friendly-brightgreen.svg">
</a>
<a href="https://pepy.tech/projects/libquery">
    <img alt="Pepy Total Downloads" src="https://img.shields.io/pepy/dt/libquery">
</a>

# libquery

A Python package for querying digital libraries and archives.
Supports multiple data sources including [David Rumsey Map Collection](https://www.davidrumsey.com/), [Gallica](https://gallica.bnf.fr/), [Internet Archive](https://archive.org/), and [Library of Congress](https://www.loc.gov/).

## Installation

```sh
pip install libquery
```

## Usage Example

Query metadata and images in [David Rumsey Map Collection](https://www.davidrumsey.com/):

```python
from libquery import DavidRumseyMapCollection
querier = DavidRumseyMapCollection("./metadata/", "./imgs/")
querier.fetch_metadata(["https://www.davidrumsey.com/luna/servlet/as/search?q=type=chart"])
querier.fetch_image()
```

## Documentation

See our [documentation website](https://oldvis.github.io/libquery/).
