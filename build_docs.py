#!/usr/bin/env python2
# -*- coding: utf-8 -*- #
#
# Builds the GitHub Wiki documentation into a static HTML site.
#
# Copyright (c) 2015 carlosperate https://github.com/carlosperate/
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This script does the following to build the documentation:
#    Pulls the latest changes from the GitHub Wiki repository
#    Edits the MkDocs configuration file to include all the markdown files
#    Creates an index.html file to have root redirected to a specific page
#    Builds the static site using MkDocs
#    REMOVES the root Documentation folder
#    Copies the generate content into the root Documentation folder
#
from __future__ import unicode_literals, absolute_import
import os
import sys
import shutil
import subprocess
from tempfile import mkstemp
import re

# mkdocs used only in the command line, imported just to ensure it's installed
# try:
#     import mkdocs
# except ImportError:
#     print("You need to have mkdocs installed !")
#     sys.exit(1)


# Path data
GITHUB_USER = "8BitMixtape"
WIKI_NAME = "8Bit-Mixtape-NEO.wiki"
GITHUB_WIKI_REPO = "github.com/%s/%s.git" % (GITHUB_USER, WIKI_NAME)

MKDOCS_FOLDER = ""
THIS_FILE_DIR = os.path.dirname(os.path.realpath(__file__))
MKDOCS_DIR = os.path.join(THIS_FILE_DIR, MKDOCS_FOLDER)

DEFAULT_INDEX = 'Home'

chap_re = re.compile("^([0-9]*[_-] .*)+$")
sub_re = re.compile("^([0-9].*_[0-9].*[_ -].*)+$")


def pull_wiki_repo():
    """
    Pulls latest changes from the wiki repo.
    :return: Boolean indicating if the operation was successful.
    """
    # Set working directory to the wiki repository
    wiki_folder = os.path.join(MKDOCS_DIR, WIKI_NAME)
    if os.path.isdir(wiki_folder):
        os.chdir(wiki_folder)
    else:
        print("ERROR: Wiki repo directory is not correct: %s" % wiki_folder)
        return False

    # Ensure the submodule is initialised, progress is printed to stderr so just
    # call subprocess with all data sent to console and error check later
    subprocess.call(["git", "submodule", "update", "--init", "--recursive"])

    # Ensure the subfolder selected is the correct repository
    pipe = subprocess.PIPE
    git_process = subprocess.Popen(
        ["git", "config", "--get", "remote.origin.url"],
        stdout=pipe, stderr=pipe)
    std_op, std_err_op = git_process.communicate()

    if std_err_op:
        print("ERROR: Could not get the remote information from the wiki "
              "repository !\n%s" + std_err_op)
        return False

    if not GITHUB_WIKI_REPO in std_op:
        print(("ERROR: Wiki repository:\n\t%s\n" % GITHUB_WIKI_REPO) +
              "not found in directory %s url:\n\t%s\n" % (wiki_folder, std_op))
        return False

    # Git Fetch prints progress in stderr, so cannot check for erros that way
    print("\nPull from Wiki repository...")
    subprocess.call(["git", "pull", "origin", "master"])
    print("")

    return True


def generate_sidebar():
    path_list = []

    list_dir = os.listdir(os.path.join(MKDOCS_DIR, WIKI_NAME))
    list_dir.sort()

    for file in list_dir:
      
      if file.endswith(".md"):

        if (sub_re.match(file)):
          path_list.append("  - [%s](%s)" % (file[:-3].replace("-", " ").replace("_","."), file))
        else:
          path_list.append("- %s:" % (file[:-3].replace("-", " ").replace("_",".")))
          path_list.append("  - [%s](%s)" % (file[:-3].replace("-", " ").replace("_","."), file))

    if not path_list:
      print(("ERROR: No markdown files found in %s ! " % MKDOCS_DIR) +
          "Check if repository has been set up correctly.")
      return False

    
    pages_str = "" + "\n".join(path_list) + "\n"
    return pages_str

def save_sidebar():
    html_code = ""
    print("Creating the _sidebar.md file...\n")
    generated_site_dir = THIS_FILE_DIR
    if not os.path.exists(generated_site_dir):
        try:
            os.makedirs(generated_site_dir)
        except IOError:
            print("ERROR: Could not create site folder in %s !\n" %
                  generated_site_dir)
            return False
    try:
        sidebar_file = open(os.path.join(generated_site_dir, "_sidebar.md"), "w")
        sidebar_file.write(generate_sidebar())
        sidebar_file.close()
        return True
    except IOError:
        print("ERROR: Could not create _sidebar.md file in %s !\n" %
              generated_site_dir)
        return False


def build_docs():
    """ Builds the documentation HTML pages from the Wiki repository. """
    success = pull_wiki_repo()
    if success is False:
        sys.exit(1)

    success = save_sidebar()
    if success is False:
        sys.exit(1)
    print("Build process finished!")


if __name__ == "__main__":
    build_docs()
