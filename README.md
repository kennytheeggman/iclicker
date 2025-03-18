# Automatic iClicker

This is a small python executable script to automatically run iClicker in the background by
emulating its network calls. 

## Installation

The only option for installation right now is to build from source. 

Step 1: Clone repository and create virtual environment

First, clone the repository:

```sh
git clone https://github.com/kennytheeggman/iClicker
```

If on MacOS/Linux:

```sh
python3 -m venv ./venv && source venv/bin/activate
```

If on Windows:

```sh
python3 -m venv ./venv && venv/Scripts/activate
```

Step 2: Build the library

First, install build dependencies

```sh
pip install build setuptools
```

Then, build the library

```sh
python -m build
```

Step 3: Install the library

Use your favorite python global package manager, e.g. `pipx`, `pip --break-system-packages`, `uv`, etc.

Installation with `pipx`:

```sh
pipx install dist/iclicker-*.tar.gz
```

Installation with `pip`:

```sh
pip install dist/iclicker-*.tar.gz --break-system-packages
```

# Usage

Use your email and password to start the script. Note this will only work if remote answering is
allowed.

```sh
iclicker <email> <password>
```
