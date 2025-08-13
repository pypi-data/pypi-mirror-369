# Jupyter TigerVNC/NOVNC proxy

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/jupyter-tigervnc-novnc-proxy.svg)](https://pypi.org/project/jupyter-tigervnc-novnc-proxy/)

jupyter-tigervnc-novnc-proxy description (TODO)

## TODOs

Look for TODOs in files:

```bash
grep -r TODO .
```

## Installation

You can install jupyter-tigervnc-novnc-proxy inside your environment with Jupyter / Jupyterlab:

```bash
python3 -m pip install jupyter-tigervnc-novnc-proxy
```

## Build

```bash
python3 -m pip install hatch

hatch build

ls -la dist/*
```

## Development

Try `make help` to see available commands:

```bash
make help
```

```bash
python3 -m pip install git+https://github.com/huntdatacenter/jupyter-tigervnc-novnc-proxy.git@mainegg=jupyter-tigervnc-novnc-proxy
```

## Testing in docker

Run/rebuild local Jupyterlab service:

```bash
make rebuild
```

Running the command should open a url in the browser http://127.0.0.1:8888/lab

To stop the service run:
```bash
make down
```
