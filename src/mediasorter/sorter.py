"""Sorter API, version 1."""
import imghdr
from datetime import datetime
import os
from pathlib import Path
import shutil
import time


import exifread
import filetype

from hachoir.parser import createParser
from hachoir.core.tools import makePrintable
from hachoir.metadata import extractMetadata
from hachoir.core.i18n import getTerminalCharset
from PIL import Image
from PIL.ExifTags import TAGS
from tqdm import tqdm


def get_pil_exif_data(fname):
    """Get embedded EXIF data from image file."""
    ret = {}
    try:
        img = Image.open(fname)
        if hasattr(img, "_getexif"):
            exifinfo = img._getexif()
            if exifinfo != None:
                for tag, value in exifinfo.items():
                    decoded = TAGS.get(tag, tag)
                    ret[decoded] = value
    except Exception():
        ret = {}
    return ret


def get_exif_data(fname):
    """Get embedded EXIF data from image file."""
    tags = {}
    try:
        img = open(fname, "rb")
        tags = exifread.process_file(img)
        img.close()
    except Exception:
        tags = get_pil_exif_data(fname)
    return tags


def get_pil_create_date(exif_data):
    """Get embedded create date from EXIF data."""
    retval = None

    for (k, v) in exif_data.items():
        key = str(k)
        if "DateTimeOriginal" in key:
            retval = v.strip()

    return retval


def get_create_date(exif_data):
    """Get embedded create date from EXIF data."""
    retval = None
    try:
        date_str = exif_data["EXIF DateTimeOriginal"].values
    except:
        try:
            date_str = get_pil_create_date(exif_data)
        except:
            date_str = None

    if date_str:
        try:
            retval = datetime.strptime(str(date_str), "%Y:%m:%d %H:%M:%S")
        except:
            try:
                retval = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            except:
                retval = None

    return retval


def has_thm_file(filename):
    """For given AVI filename, find corresponding THM file. Return true if found"""
    retval = (False, "", "")
    dir_name = filename.parent
    file_name = filename.name
    f_name = filename.stem
    thm_file1 = Path(dir_name) / f"{f_name}.THM"
    thm_file2 = Path(dir_name) / f"{f_name}.thm"

    if thm_file1.exists():
        retval = (True, f_name + ".THM", thm_file1)
    elif thm_file2.exists():
        retval = (True, f_name + ".thm", thm_file2)

    return retval


def get_hachoir_create_date(fname):
    """Get media create date using hachoir library"""
    retval = None
    parser = createParser(fname.as_posix())
    if not parser:
        print("Unable to parse file " + fname)
        return retval
    try:
        metadata = extractMetadata(parser)
    except Exception() as err:
        print("Metadata extraction error for " + fname + " - " + unicode(err))
        metadata = None
    if not metadata:
        print("Unable to extract metadata for " + fname)
        return retval

    metaitems = metadata.getItems("creation_date")
    if not metaitems:
        print("Unable to extract metaitmes for " + fname)
        return retval

    retval = metaitems.values[0].value
    if not retval:
        print("Unable to extract creation date for " + fname)

    return retval


def createdirpath(format, tstamp, target=None):
    """Return target directory location based on format and date"""

    has_folder = False
    formatted_str = tstamp.strftime(format)
    if formatted_str.find("/") > 0:
        tokens = formatted_str.split("/")
        has_folder = True
    elif formatted_str.find("\\") > 0:
        tokens = formatted_str.split("\\")
        has_folder = True
    else:
        tokens = formatted_str

    if has_folder:
        if target:
            destpath = Path(target, *tokens)
        else:
            destpath = Path(*tokens)
    else:
        if target:
            destpath = Path(target, tokens)
        else:
            destpath = Path(tokens)

    return destpath


def run(source: Path, target: Path, format: str, debug: bool) -> None:
    """Execute imagesorter and sort the images/video based in Input params."""
    paths = list(Path(source).glob("**/*"))
    files = tqdm(paths)
    mylist = []
    for file in files:
        try:
            if debug:
                files.set_description(f"Processing {file}")
            if file.is_file():
                kind = filetype.guess(file.as_posix())
                if kind is None:
                    continue
                file_type, file_format = kind.mime.split("/")
                if file_type not in ["image", "video"]:
                    continue
                create_date = None
                has_thm = False
                thm_fullpath = None
                thm_filename = None
                if file_type == "image":
                    if debug:
                        files.set_description(f"Getting Metadata for {file}")
                    exif = get_exif_data(file)
                    create_date = get_create_date(exif)
                elif file_type == "video":
                    if file.suffix.lower() == ".avi":
                        has_thm, thm_filename, thm_fullpath = has_thm_file(file)
                    if has_thm:
                        exif = get_exif_data(thm_fullpath)
                        create_date = get_create_date(exif)
                    else:
                        create_date = get_hachoir_create_date(file)

                if create_date:
                    destpath = createdirpath(format, create_date, target)

                    destpath.mkdir(parents=True, exist_ok=True)
                    dest_file = destpath / file.name
                    if dest_file.is_file():
                        if debug:
                            files.set_description(f"Skipping copying {file} as exists")
                        continue
                    else:
                        shutil.copy2(file, destpath)
                        if debug:
                            files.set_description(
                                f"Copying {file} to {destpath.as_posix()}"
                            )
                        if has_thm:
                            shutil.copy2(thm_fullpath, destpath)
                            if debug:
                                files.set_description(
                                    f"Copying {thm_fullpath} to {destpath.as_posix()}"
                                )
                else:
                    files.set_description(f"No Metadata found for {file}")
        except Exception as ex:
            files.set_description(f"Error Processing {file}")
