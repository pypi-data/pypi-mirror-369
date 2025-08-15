# EHNPY: Envri Hub Next Python library

# Installing the Local Python Package

This guide shows how to install the local Python package from the development directory.

## Prerequisites

- Python 3.x installed
- `pip` available
- Access to the development repository on GitLab

## Installation

To install the package locally in **editable (development) mode**, run:

```bash
pip install -e ./ehnpy 
```
Where `ehnpy` is the directory where you cloned the repository to. 

This will link the package to your Python environment, so any changes made in the source directory are immediately reflected without needing to reinstall.

## Notes

- Make sure to use forward slashes (`/`) or escape backslashes (`\\`) if running this on Windows in certain environments (like Git Bash or WSL).
- You can verify installation with:

```bash
pip list | findstr ehnpy
```
