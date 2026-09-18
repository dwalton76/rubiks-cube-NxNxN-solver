# standard libraries
import logging
import os
import shutil
from subprocess import call

logger = logging.getLogger(__name__)


class NoIDASolution(Exception):
    pass


def download_file_if_needed(filename: str) -> None:
    """Download and unpack a lookup-table artifact when it is not installed."""
    if not os.path.exists(filename):
        filename_gz = filename + ".gz"
        filename_gz_no_dir = filename_gz.split("/")[-1]

        if not os.path.exists(filename_gz):
            url = f"https://rubiks-cube-lookup-tables.s3.amazonaws.com/{filename_gz_no_dir}"
            logger.info(f"Downloading table via 'wget {url}'")
            call(["wget", url])

            if not os.path.exists(filename_gz_no_dir):
                raise RuntimeError(f"failed to download {filename_gz} via {url}")

            shutil.move(filename_gz_no_dir, filename_gz)

        logger.info(f"gunzip {filename_gz}")
        call(["gunzip", filename_gz])
