# -*- coding: utf-8 -*-

import glob
import os
import platform

MAX_DEPTH_RECUR = 100
''' The maximum depth to reach while recursively exploring sub folders'''


def get_files_from_dir(path, recursive=True, depth=0, file_ext='.py'):
    """Retrieve the list of files from a folder.

    @param path: file or directory where to search files
    @param recursive: if True will search also sub-directories
    @param depth: if explore recursively, the depth of sub directories to
    follow
    @param file_ext: the files extension to get. Default is '.py'
    @return: the file list retrieved. if the input is a file then a one
    element list.
    """
    file_list = []
    if os.path.isfile(path) or path == '-':
        return [path]
    if path[-1] != os.sep:
        path = path + os.sep
    for f in glob.glob(path + "*"):
        if os.path.isdir(f):
            if depth < MAX_DEPTH_RECUR:  # avoid infinite recursive loop
                file_list.extend(get_files_from_dir(f, recursive, depth + 1))
            else:
                continue
        elif f.endswith(file_ext):
            file_list.append(f)
    return file_list


def doxygen_to_epitext(file):
    """Returns a list  of all lines in the file, docstrings reformatted

    :param file: a file to reformat
    :type file: string
    :return: lines_to_write
    :rtype: list
    """
    f = open(file, 'r')
    lines = f.readlines()
    f.close()
    lines_to_write = []
    for index, line in enumerate(lines):
        if "Parameters" in line:
            if lines[index-1] != "    \n":
                lines_to_write.append("\n")
        if "@param[in]" in line:
            if lines[index-1] != "    \n" \
                    and "@param[in]" not in lines[index-1]:
                lines_to_write.append("\n")
            line = line.replace("@param[in]",  "@param")
            words = line.split(" ")
            i = 0
            while words[i] == "":
                i += 1
                continue
            words[i + 1] = words[i + 1] + ":"
            line = " ".join(words)

        elif "@param[out]" in line:
            line = line.replace("@param[out]", "@return")
            words = line.split(" ")
            i = 0
            while words[i] == "":
                i += 1
                continue
            words[i+1] = words[i+1] + ":"
            line = " ".join(words)
        elif "@throw" in line:
            line = line.replace("@throw", "@raise")
            words = line.split(" ")
            i = 0
            while words[i] == "":
                i += 1
                continue
            words[i + 1] = words[i + 1] + ":"
            line = " ".join(words)
        lines_to_write.append(line)

    return lines_to_write


def overwrite_source_file(input_file, lines_to_write):
    """overwrite the file with line_to_write
    :param lines_to_write: lines to write to the file - they
    should be \n terminated
    :type lines_to_write: List[str]
    :return: None
    """
    tmp_filename = '{0}.writing'.format(input_file)
    ok = False
    try:
        with open(tmp_filename, 'w') as fh:
            fh.writelines(lines_to_write)
        ok = True
    finally:
        if ok:
            if platform.system() == 'Windows':
                windows_rename(input_file, tmp_filename)
            else:
                os.rename(tmp_filename, input_file)
        else:
            os.unlink(tmp_filename)


def windows_rename(input_file, tmp_filename):
    """ Workaround the fact that os.rename raises an OSError on
    Windows

    :param tmp_filename: The file to rename

    """

    os.remove(input_file) if os.path.isfile(input_file) else None
    os.rename(tmp_filename, input_file)


def reformat(function, path, recursive=True, depth=0, file_ext='.py'):
    """Reformat all the files in the path using the function given in parameter

    :param function: Function to use to reformat
    :param path: the path of the the directorie or file to reformat
    :type path: string
    :param recursive: True if reformat action is applied to subdirectories
    :type recursive: bool
    :param depth: the maximum depth for the recursively in case path is dir
    :type depth: int
    :param file_ext: the extension of the file to reformat
    :type file_ext: string
    :return: None
    :rtype: None
    """
    file_list = get_files_from_dir(path=path,
                                   recursive=recursive,
                                   depth=depth,
                                   file_ext=file_ext)
    for file in file_list:
        lines_to_write = function(file)
        overwrite_source_file(file, lines_to_write)


if __name__ == "__main__":
    reformat(function=doxygen_to_epitext,
             path=r"C:\Users\quentin\Documents\svn\pyManatee\trunk\pyManatee")

