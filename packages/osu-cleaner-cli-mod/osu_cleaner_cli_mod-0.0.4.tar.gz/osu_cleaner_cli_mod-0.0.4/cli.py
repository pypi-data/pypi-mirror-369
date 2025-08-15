#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This is a modified version of osu-cli-cleaner by Layerex
# Copyright (C) 2022 Layerex
# Licensed under the GNU GPL v3 (see LICENSE file for details)
#

__prog__ = "osu-cleaner-cli-mod"
__version__ = "0.0.4"
__author__ = "Layerex"
__desc__ = "Remove unwanted files from osu! Songs directory. Modified Version"

import argparse
import glob
import os
import re
import shutil
import stat

extensions = {
    "videos": ("avi", "flv", "mp4", "wmv"),
    "images": ("png", "jpg", "jpeg"),
    "hitsounds": "wav",
    "beatmaps": "osu",
    "storyboards": "osb",
    "skin_initialization_files": "ini",
}

skin_file_names = (
    "cursor",
    "hit",
    "lighting",
    "particle",
    "sliderpoint",
    "approachcircle",
    "followpoint",
    "hitcircle",
    "reversearrow",
    "slider",
    "default-",
    "spinner-",
    "sliderscorepoint",
    "taiko",
    "pippidon",
    "fruit-",
    "lighting",
    "scorebar-",
    "score-",
    "selection-mod-",
    "comboburst",
    "menu-button-background",
    "multi-skipped",
    "play-",
    "star2",
    "inputoverlay-",
    "scoreentry-",
    "ready",
    "count",
    "go.png",
    "section-fail",
    "section-pass",
    "ranking-",
    "pause-",
    "fail-background",
)

quotation_marks_re = re.compile(r"\"(.*?)\"")


def force_remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def main():
    parser = argparse.ArgumentParser(
        prog=__prog__,
        description=__desc__,
        epilog="If no arguments or only osu! Songs directory specified, script will start in interactive mode.",
    )

    parser.add_argument(
        "working_directory_path",
        metavar="osu_songs_directory",
        type=str,
        nargs="?",
        help="path to your osu! Songs directory",
    )
    parser.add_argument(
        "--delete-videos",
        action="store_true",
    )
    parser.add_argument(
        "--delete-hitsounds",
        action="store_true",
    )
    parser.add_argument(
        "--delete-backgrounds",
        action="store_true",
    )
    parser.add_argument(
        "--delete-skin-elements",
        action="store_true",
    )
    parser.add_argument(
        "--delete-storyboard-elements",
        action="store_true",
    )
    parser.add_argument(
        "--delete-all",
        action="store_true",
    )

    args = parser.parse_args()

    if args.working_directory_path:
        working_directory_path = args.working_directory_path
    else:
        working_directory_path = input("Enter the path to your osu! Songs directory: ")
    os.chdir(working_directory_path)

    delete_videos = args.delete_videos or args.delete_all
    delete_hitsounds = args.delete_hitsounds or args.delete_all
    delete_backgrounds = args.delete_backgrounds or args.delete_all
    delete_skin_elements = delete_skin_initialization_files = (
        args.delete_skin_elements or args.delete_all
    )
    delete_storyboard_elements = args.delete_storyboard_elements or args.delete_all

    if not (
        delete_videos
        or delete_hitsounds
        or delete_backgrounds
        or delete_skin_elements
        or delete_skin_initialization_files
        or delete_storyboard_elements
    ):
        print("No delete flags specified. Nothing to do.")
        return

    if delete_backgrounds and delete_skin_elements and delete_storyboard_elements:
        delete_images = True
        delete_backgrounds = False
        delete_skin_elements = False
        delete_storyboard_elements = False
    else:
        delete_images = False

    print("Scanning...")
    directories = os.listdir(".")
    files_to_remove = set()
    for directory in directories:
        if os.path.isdir(directory):
            print(os.path.basename(directory))
            os.chdir(directory)
            files = glob.glob("**/*", recursive=True)
            if files:
                for file in files:
                    if not os.path.isfile(file):
                        if os.path.isdir(file):
                            abs_dir = os.path.abspath(file)
                            print("Removing directory '%s'..." % abs_dir)
                            try:
                                shutil.rmtree(file, onerror=force_remove_readonly)
                            except OSError as e:
                                print("Failed to remove directory '%s': %s" % (abs_dir, e))
                        continue

                    file_lowercase = file.lower()
                    if (
                        (delete_videos and file_lowercase.endswith(extensions["videos"]))
                        or (
                            delete_images
                            and (
                                file_lowercase.endswith(extensions["images"])
                                or file_lowercase.endswith(extensions["storyboards"])
                            )
                        )
                        or (delete_hitsounds and file_lowercase.endswith(extensions["hitsounds"]))
                        or (
                            delete_skin_initialization_files
                            and file_lowercase.endswith(extensions["skin_initialization_files"])
                        )
                        or (
                            delete_skin_elements
                            and os.path.basename(file_lowercase).startswith(skin_file_names)
                            and file.endswith(extensions["images"])
                        )
                    ):
                        files_to_remove.add(os.path.abspath(file))
                        
                    elif delete_backgrounds and file_lowercase.endswith(extensions["beatmaps"]):
                        for extracted_file_path in use_re_on_file(file, quotation_marks_re):
                            extracted_file_path_lowercase = extracted_file_path.lower()
                            if extracted_file_path_lowercase.endswith(
                                extensions["images"]
                            ) and os.path.isfile(extracted_file_path):
                                files_to_remove.add(os.path.abspath(extracted_file_path))
                    elif delete_storyboard_elements and file_lowercase.endswith(
                        extensions["storyboards"]
                    ):
                        for extracted_file_path in use_re_on_file(file, quotation_marks_re):
                            extracted_file_path_lowercase = extracted_file_path.lower()
                            if (
                                extracted_file_path_lowercase.endswith(extensions["images"])
                                or extracted_file_path_lowercase.endswith(extensions["videos"])
                                and os.path.isfile(extracted_file_path)
                            ):
                                files_to_remove.add(os.path.abspath(extracted_file_path))
                        files_to_remove.add(os.path.abspath(file))
            os.chdir("..")
        else:
            files_to_remove.add(os.path.abspath(directory))

    for file_to_remove in files_to_remove:
        print("Removing '%s'..." % file_to_remove)
        try:
            os.remove(file_to_remove)
        except OSError:
            print("Failed to remove '%s'." % file_to_remove)


def use_re_on_file(file, regex):
    try:
        with open(file, "r", errors="ignore") as fh:
            return regex.findall(fh.read())
    except OSError:
        return []


if __name__ == "__main__":
    main()
