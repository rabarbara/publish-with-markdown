"""Creates a summary.md for gitbook consumption"""

import glob
import itertools
import shutil
import os

class Gitbook(object):

    def __init__(self, gitbook_folder='gitbook', common_folder_name='poglavje', media_folder_name='media'):
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
            shutil.copytree(item, 'gitbook/{}'.format(item))
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
            return tuple(chapter_name.split('.'))

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

    def write_summary(self):
        with open('SUMMARY.md', 'w', encoding='utf-8') as write_to_file:
            write_to_file.write('# Summary')
            for chapterline in self._create_summary(self.list_of_files):
                write_to_file.write(chapterline)
