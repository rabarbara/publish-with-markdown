"""Creates a summary.md for gitbook consumption"""

import glob
import itertools


def create_a_list_of_files(glob_description):
    """Return a sorted list of all files in a directory with relative paths"""

    def sections(section):
        """Returns a tuple of all chapter info"""
        chapter_name = section[12:]
        chapter_name = chapter_name[:-3]
        return tuple(chapter_name.split('.'))

    return sorted([item for item in glob.glob(glob_description)], key=sections)

def group_files(files):
    """Group a list of files based on the chapter they are in"""
    groups = []
    uniquekeys = []
    for k, g in itertools.groupby(files, key=lambda file: file.split('/')[0]):
        groups.append(list(g))      # Store group iterator as a list
        uniquekeys.append(k)
    return groups

def create_summary(list_of_chapters):
    for chapter_group in list_of_chapters:
        for chapter in chapter_group:
            with open(chapter, 'r', encoding='utf-8') as file:
                header = file.readline()
                stripped_header = header.strip('#').strip()
                if header.startswith('###'):
                    yield '\t\t* [{}]({})\n'.format(stripped_header, chapter)
                elif header.startswith('##'):
                    yield '\t* [{}]({})\n'.format(stripped_header, chapter)
                elif header.startswith('#'):
                    yield '\n\n ---\n * [{}]({})\n'.format(stripped_header, chapter)
if __name__ == '__main__':
    ALL_FILES_GROUPED = group_files(create_a_list_of_files('poglavje-*/*'))
    with open('summary.md', 'w', encoding='utf-8') as write_to_file:
        write_to_file.write('# Summary\n\n')
        for line in create_summary(ALL_FILES_GROUPED):
            write_to_file.write(line)
