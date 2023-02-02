#!/usr/bin/env python
# -*- coding: utf-8 -*-

import shutil
from pathlib import Path
from typing import Union

import constants_2022

###############################################################################


def unpack_data(
    zipfile: Union[str, Path] = constants_2022.ACCESS_EVAL_2022_EVALS_ZIP,
    dest: Union[str, Path] = constants_2022.ACCESS_EVAL_2022_EVALS_UNPACKED,
    clean: bool = False,
) -> Path:
    """
    Unzips the zipfile to the destination location.

    Parameters
    ----------
    zipfile: Union[str, Path]
        The zipfile to unpack.
        Default: The 2021 campaign accessibility evaluation pre-contact data.
    dest: Union[str, Path]
        The destination to unpack to.
        Default: The default location for unpacked "pre-contact" data.
    clean: bool
        If a directory already exists at the destination location, should the directory
        be removed entirely before unpacking again.
        Default: False (raise an error if a directory already exists)
    """
    zipfile = Path(zipfile).resolve(strict=True)
    dest = Path(dest)

    # Check dest is a dir
    if dest.is_file():
        raise NotADirectoryError(dest)

    # Clean dest if required
    if dest.is_dir():
        dest_is_empty = not any(dest.iterdir())
        if not dest_is_empty:
            if clean:
                shutil.rmtree(dest)
            else:
                raise FileExistsError(
                    f"Files found in target destination directory ({dest}) "
                    f"but parameter `clean` set to False."
                )

    # Make new dir
    dest.mkdir(parents=True, exist_ok=True)

    # Extract
    shutil.unpack_archive(zipfile, dest)

    # Return extracted data dir
    return dest.resolve(strict=True)
