# CHANGELOG

## main

- Put updates here

## 1.0.8 / 2025-08-11
- Rev allowable numpy version to >=1.26.

## 1.0.7 / 2025-03-08
- Make getRuptureContext optionally return arrays.

## 1.0.6 / 2024-08-23
- Remove circular imports of shakelib contexts.

## 1.0.5 / 2024-08-16
- Remove ps2ff dependencies; point-source rrup and rjb now return rhypo and repi, respectively.
- Refactor to use new dummy contexts.
- Allow retrieval of Rupture class's geojson.

## 1.0.4 / 2024-02-05
- Remove cap on python version.

## 1.0.3 / 2023-05-19
- Add CHANGELOG.md
- Update README.md and installation instructions
- Remove zmq dependency causing issues
- Convert setup and installation workflow to use pyproject.toml and optional dependencies for pip installation
- Add "reviewed" status to origin object; fix unit tests
- Add "reviewed" status to event.xml
