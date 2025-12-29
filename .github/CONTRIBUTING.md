
# Contributing

How to contribute to this addon.

<br/>

## TLDR

-   Standard PR based workflow

-   For new files add SPDX or  
    license metadata for icons

-   Open an issue for larger stuff.

<br/>

## Setup

-   Fork & clone the repository

-   Using [uv], install the dev dependencies:

    ```sh
    uv sync
    ```

-   Link the cloned repository folder  
    to your FreeCAD `/Mod/` directory.

<br/>

## Bumping the project version

When preparing a new release or updating the package metadata, use the
provided `bump_version.py` script in the repository root to update the
version in the places changed in the project (FreeCAD `Version.py`,
`package.xml` and `pyproject.toml`).

Usage examples:

- Bump to version 1.2.3 and use today's date (POSIX shells such as zsh
  or bash):

```sh
./bump_version.py 1.2.3 --date "$(date +%F)"
```

- If you want to include the change in a commit automatically, add
  `--git`:

```sh
./bump_version.py 1.2.3 --date "$(date +%F)" --git
```

Notes:

- `date +%F` outputs the date in `YYYY-MM-DD` format, which is what
  `package.xml` expects.
- The script will update the files and (optionally) stage and commit
  them when `--git` is used.


[uv]: https://docs.astral.sh/uv/