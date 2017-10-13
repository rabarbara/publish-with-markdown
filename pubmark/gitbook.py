"""Creates a summary.md for gitbook consumption"""

import glob
import itertools
import shutil
import os
import yaml

class Summary(object):

    def __init__(self, gitbook_folder='gitbook', common_folder_name='poglavje', media_folder_name='media'):
        """
        :param gitbook_folder: the name of the folder the gitbook files should be copied to
        :param common_folder_name: the common characters that exist in your folder names for all folders containing your book
        :param media_folder_name: where you keep your images and other files
        """
        self.gitbook_folder = str(gitbook_folder)
        self.common_folder_name = common_folder_name
        self.media_folder_name = media_folder_name
        self.list_of_files = []

    def copy_files_for_gitbook(self):
        """Recreate a folder and copy files to that folder"""
        try:
            shutil.rmtree(self.gitbook_folder)
        except FileNotFoundError:
            print('No folder to delete')

        for item in [item for item in os.listdir('.') if self.common_folder_name in item]:
            shutil.copytree(item, '{}/{}'.format(self.gitbook_folder, item))
        shutil.copytree(self.media_folder_name,
                        '{}/{}'.format(self.gitbook_folder, self.media_folder_name))
        try:
            shutil.copy('README.md', self.gitbook_folder)
        except FileNotFoundError:
            print('Datoteka README.md ne obstaja.')

    def create_a_list_of_files(self, glob_description):
        """Return a sorted list of all files in a directory with relative paths"""

        def sections(section):
            """Returns a tuple of all chapter info"""
            chapter_name = os.path.basename(section)
            # omit the md extension that was giving false results
            return tuple(chapter_name.split('.')[:-1])

        self.list_of_files = self._group_files(sorted([item for item in glob.glob(glob_description)], key=sections))

    @staticmethod
    def _group_files(files):
        """Group a list of files based on the chapter they are in"""
        groups = []
        uniquekeys = []
        for k, g in itertools.groupby(files, key=lambda file: os.path.split(file)[0]): # gitbook/chapter/file.md => sort by chapter
            groups.append(list(g))      # Store group iterator as a list
            uniquekeys.append(k)
        return groups

    @staticmethod
    def _create_summary(list_of_chapters):
        for chapter_group in list_of_chapters:
            for chapter in chapter_group:
                with open(chapter, 'r', encoding='utf-8') as file:
                    header = file.readline()
                    stripped_header = header.strip('#').strip()
                    if header.startswith('###'):
                        yield '\t* [{}]({})\n'.format(stripped_header, chapter)
                    elif header.startswith('##'):
                        yield '* [{}]({})\n'.format(stripped_header, chapter)
                    elif header.startswith('#'):
                        yield '\n\n## {}\n'.format(stripped_header)

    def write_summary(self, path_to_file=''):
        """Writes the gitbook summary to a file
        :parameter path_to_file Path to the file to be written. Default is the same directory where the method is called
        :return None
        """
        path_to_file = path_to_file if path_to_file else self.gitbook_folder
        with open(os.path.join(path_to_file, 'SUMMARY.md'), 'w', encoding='utf-8') as write_to_file:
            # the summary file has to start with a # heading
            write_to_file.write('# Summary\n\n')
            for chapterline in self._create_summary(self.list_of_files):
                write_to_file.write(chapterline)


def convert_yaml_to_json(filepath_or_string):
    """
    Converts the yaml metadata as defined in pandoc for gitbook consumption as a book.json
    @param filepath_or_string: either the filepath to the file or the actual data to be converted
    @return string: json string that has to be put into a file somewhere
    """

    def get_data(file_data):
        """
        Checks if the parameter is a string or file path and returns the data
        @param file_data: either the path or the actual data as a string
        @Return: the data we need for conversion
        """
        if os.path.isfile(file_data):
            with open(file_data, mode='r', encoding='utf-8') as f:
                return f.read()
        return file_data

    meta_data = get_data(filepath_or_string)

    json_data = yaml.safe_load(meta_data)
    return json_data
