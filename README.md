# mediasorter

A CLI tool to sort and copy images/videos to a defined directory structure. This will look at the metadata for each picture/video in the source directory and copy it to the target directory preserving the files metadata. The target directory is by default in the format %Y/%B/%Y_%m_%d. 

For example if there is an image under ~/phonepics/someimage.jpg with a create date of 2021-10-21. If I run the following:
    
    $ mediasorter --source ~/phonepics --target ~/images

The picture someimage.jpg will be saved under ~/images/2021/October/2021_10_21.

## Installation

    pip install mediasorter

## Usage


    Usage: mediasorter [OPTIONS]

    The mediasorter Python project.

    Options:
    -s, --source PATH  Source directory of Images/Videos  [default: current directory]
    -t, --target PATH  Target directory of Images/Videos  [required]
    -f, --format TEXT  Directory format for how images/videos are saved to target  [default: %Y/%B/%Y_%m_%d]
    -d, --debug
    --version          Show the version and exit.
    --help             Show this message and exit.
