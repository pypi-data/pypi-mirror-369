<!--
SPDX-FileCopyrightText: 2023 Helge

SPDX-License-Identifier: MIT
-->

# Fediverse Pasture

This python package contains tools to test Fediverse applications. This
package uses [bovine](https://bovine.readthedocs.io/en/latest/) for a lot
of the Fediverse related logic. It should also be noted that the aim here
is to debug issues caused by federation, thus everything involves starting
a webserver and running requests against it.

## Usage

For usage information, see the [documentation](https://funfedi.dev/python_package/).

## Development

Install the necessary dependencies via

```bash
poetry install --with test,dev --all-extras
```

To lint and check code formatting run

```bash
poetry run ruff check .
poetry run ruff format .
```

To test the code run

```bash
poetry run pytest
```

## Releasing

Bump version via

```bash
poetry version $TAG
git commit -a -m "new version"
git push origin main
```

Check that the build was successful [![status-badge](https://ci.codeberg.org/api/badges/13093/status.svg)](https://ci.codeberg.org/repos/13093)

```bash
git tag $TAG
git push origin $TAG
```

## Funding

This code was created as part of [Fediverse Test Framework](https://nlnet.nl/project/FediverseTestFramework/).

A project funded through the [NGI0 Core](https://nlnet.nl/core) Fund,
a fund established by [NLnet](https://nlnet.nl/) with financial support from
the European Commission's [Next Generation Internet](https://ngi.eu/) programme,
under the aegis of DG Communications Networks, Content and Technology
under grant agreement No 101092990.
