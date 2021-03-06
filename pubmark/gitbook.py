"""Creates a summary.md for gitbook consumption"""

import glob
import itertools
import shutil
import os
import yaml
import json
import re
import datetime

class Gitbook(object):
    def __init__(self, gitbook_folder='gitbook', common_folder_name='poglavje', media_folder_name='media'):
        """
        :param gitbook_folder: the name of the folder the gitbook files should be copied to
        :param common_folder_name: the common characters that exist in your folder names for all folders containing your book
        :param media_folder_name: where you keep your images and other files
        """
        self.gitbook_folder = os.path.join(
            os.environ['HOME'], 'Desktop', gitbook_folder)
        self.common_folder_name = common_folder_name
        self.media_folder_name = media_folder_name
        self.list_of_files = []
        self.list_of_files_relative = []
        

    def copy_files_for_gitbook(self):
        """Recreate a folder and copy files to that folder"""
        try:
            items = os.listdir(self.gitbook_folder)
            for item in items:
                if item.endswith('book') or item.endswith('node_modules'):
                    pass
                elif os.path.isdir(os.path.join(self.gitbook_folder, item)):
                    shutil.rmtree(os.path.join(self.gitbook_folder, item))
                else:
                    os.remove(os.path.join(self.gitbook_folder, item))
        except FileNotFoundError:
            print('No folder to delete')
        for item in [item for item in os.listdir('.') if self.common_folder_name in item]:
            shutil.copytree(item, '{}/{}'.format(self.gitbook_folder, item))
        shutil.copytree(self.media_folder_name,
                        '{}/{}'.format(self.gitbook_folder, self.media_folder_name))
        try:
            # shutil.copy('README.md', self.gitbook_folder)
            shutil.copy('README.md', os.path.join(self.gitbook_folder, "UVOD.md"))
        except FileNotFoundError:
            print('Datoteka README.md ne obstaja. Zato je bila ustvarjena in narejena kot UVOD.md')
            f = open(os.path.join(self.gitbook_folder,
                    'UVOD.md'), 'w+', encoding='utf-8')
            f.close()
            
        
        self.create_readme_from_metadata()
        
        
        try:
            shutil.copy('kolofon.md', self.gitbook_folder)
        except FileNotFoundError:
            print('Datoteka kolofon.md ne obstaja.')
        try:
            shutil.copy('book.json', self.gitbook_folder)
        except FileNotFoundError:
            try:
                with open('meta.md', 'r', encoding='utf-8') as f:
                    print('Datoteka book.json ne obstaja. Zato je bila ustvarjena iz meta.md. Preveri, če vse štima')
                    book_json_path = os.path.join(self.gitbook_folder, 'book.json')
                    with open(book_json_path, 'w', encoding='utf-8') as w:
                        w.write(convert_metayaml_to_metajson(f.read()))
            except FileNotFoundError:
                print('Datoteka book.json ne obstaja. Zato je bila ustvarjena. Popravi, kar ni v redu.')
                book_json = {
            'gitbook': '>=3.x.x', # support for gitbook 3 or later
            'plugins': ["-lunr", "-search", "search-plus-mod", "block-alignblock-align"], # disable default search
            'title': '',
            'language': 'sl-SI',
            'isbn': '',
            'author': '', # gitbook has no option for multiple authors so leave it this way for now
            'theme-default': {
                'showLevel': False,
            }
        }
                with open(book_json_path, 'w', encoding='utf-8') as w:
                        w.write(json.dumps(book_json, indent=4))

    def create_a_list_of_files(self, glob_description):
        """Return a sorted list of all files in a directory with absolute paths"""
        # it should list the gitbook folder paths, not the origin paths
        # big mistake
        def sections(section):
            """Returns a tuple of all chapter info"""
            chapter_name = os.path.basename(section)
            # omit the md extension that was giving false results
            return tuple(chapter_name.split('.')[:-1])
        self.list_of_files = self._group_files(
            sorted([os.path.join(self.gitbook_folder, item) for item in glob.glob(glob_description)], key=sections))
        self.list_of_files_relative = self._group_files(
            sorted([item for item in glob.glob(glob_description)], key=sections))

    def remove_all_sidenotes(self):
        for group in self.list_of_files:
            for element in group:
                contents = ''
                with open(element, 'r', encoding='utf-8') as readf:
                    contents = readf.read()
                # we had multiple sidenote version so we have to chech against each version, the second version pattern is the new standard
                first_version_pattern = re.compile(
                    r'<[\*,\_,\?,](.*?)[\*,\_,\?,]>', re.DOTALL)
                second_version_pattern = re.compile(r'{{(.*?)}}', re.DOTALL)
                contents = re.sub(first_version_pattern, ' ', contents)
                contents = re.sub(second_version_pattern, ' ', contents)
                with open(element, 'w', encoding='utf-8') as write:
                    write.write(contents)

    def adapt_media(self):
        for group in self.list_of_files:
            for element in group:
                contents = []
                new_contents = []
                with open(element, 'r', encoding='utf-8') as readf:
                    contents = readf.readlines()
                    for line in contents:

                        if line.startswith('![](media'):
                            # replace media with ../media
                            replaced_line = line.replace('media', '../media')
                            new_contents.append(replaced_line)
                        else:
                            new_contents.append(line)
                with open(element, 'w', encoding='utf-8') as write:
                    write.write(''.join(new_contents))


    def remove_widths_and_heights(self):
        for group in self.list_of_files:
            for element in group:
                contents = ''
                with open(element, 'r', encoding='utf-8') as readf:
                    contents = readf.read()
                # remove width and height patterns that are useless for gitbook
                pat = re.compile(r'{width=.*?height=.*?}', re.DOTALL)
                contents = re.sub(pat, ' ', contents)

                with open(element, 'w', encoding='utf-8') as write:
                    write.write(contents)


    @staticmethod
    def _group_files(files):
        """Group a list of files based on the chapter they are in"""
        groups = []
        uniquekeys = []
        # gitbook/chapter/file.md => sort by chapter
        for k, g in itertools.groupby(files, key=lambda file: os.path.split(file)[0]):
            groups.append(list(g))  # Store group iterator as a list
            uniquekeys.append(k)
        return groups

    @staticmethod
    def _create_numbered_headline(filename, line):
            '''
            Returns a numbered name of the file
            :line str the line to be numbered
            :return numbered string of the file
            '''
            if line.startswith('###'):
                return '### {} {}'.format(filename, line.strip('# '))
            elif line.startswith('##'):
                return '## {} {}'.format(filename, line.strip('# '))
            elif line.startswith('#'):
                return '# {} {}'.format(filename, line.strip('# '))

    @staticmethod
    def clean_filename_element(element):
        '''
        Returns a clean filename based on the element with the extension md removed
        '''
        el = '.'.join([str(int(item)) for item in os.path.basename(
            element).strip('.md').split('.')])
        return el

    def insert_numbering(self):
        # this is a pattern that will be used to detect if the numbering is already present and will not number the line unneccessarily
        numbering_pattern = re.compile(
            r'\d{1,2}\.\d{1,2}\.\d{1,2}\s|\d{1,2}\.\d{1,2}\s|\d{1}\s', re.MULTILINE)
        for group in self.list_of_files:
            for element in group:
                # we need just the last part of the filepath to remove the padding and insert numbering into the file
                # we split the filename and convert it to int to remove the left pad and then put it back together
                # we also remove the file extension because we don't need it
                first_line_contents = ''
                contents = ''
                with open(element, 'r', encoding='utf-8') as readf:
                    # read the first line
                    first_line_contents = readf.readline()
                    # only proceed with the writing if the numbering is not present in the file => this way we avoid duplicating the numbering
                    matches = re.search(numbering_pattern, first_line_contents)
                    if  matches is None:
                        # get the rest of the text
                        contents = readf.read()
                        with open(element, 'w', encoding='utf-8') as w:
                            w.write('{}{}'.format(self._create_numbered_headline(self.clean_filename_element(element), first_line_contents), contents))

    def remove_numbering(self):
        ''' removes numbering from files
        This is useful when there insert numbering function was more too many times'''
        # this removal pattern catches all repeated patterns up to the third level
        removal_pattern = re.compile(r'\d{1,2}\.\d{1,2}\.\d{1,2}\s|\d{1,2}\.\d{1,2}\s|\d{1}\s', re.MULTILINE)
        for group in self.list_of_files:
            for element in group:
                # we need just the last part of the filepath to remove the padding and insert numbering into the file
                # we split the filename and convert it to int to remove the left pad and then put it back together
                # we also remove the file extension because we don't need it
                first_line_contents = ''
                contents = ''
                with open(element, 'r', encoding='utf-8') as readf:
                    # read the first line and remove the numbering
                    first_line_contents = readf.readline()
                    header = re.sub(removal_pattern, '', first_line_contents)
                    # get the rest of the text
                    contents = readf.read()
                with open(element, 'w', encoding='utf-8') as w:
                    w.write('{}{}'.format(header, contents))

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

    @staticmethod
    def _create_numbered_summary(list_of_chapters, clean_name, numbered_headline):
        for chapter_group in list_of_chapters:
            for chapter in chapter_group:
                with open(chapter, 'r', encoding='utf-8') as file:
                    header = file.readline()
                    splitted = os.path.split(chapter)
                    if header.startswith('###'):
                        yield '\t* [{}]({})\n'.format(header.strip('# ').strip(), os.path.join(os.path.split(splitted[0])[1], splitted[1]))
                    elif header.startswith('##'):
                        yield '* [{}]({})\n'.format(header.strip('# ').strip(), os.path.join(os.path.split(splitted[0])[1], splitted[1]))
                    elif header.startswith('#'):
                        yield '\n\n## {}\n'.format(header.strip('# ').strip())
                        if len(file.readlines()) > 3:
                            yield '* [{}]({})\n'.format(header.strip('# ').strip(), os.path.join(os.path.split(splitted[0])[1], splitted[1]))

    
    def create_readme_from_metadata(self):
        try:
            with open('meta.md', 'r', encoding='utf-8') as f:
                data = json.loads(convert_metayaml_to_metajson(f.read()))
                readme_path = os.path.join(self.gitbook_folder, 'README.md')

                authors_list = "<br>\n".join(data['authors'])
                curr_date = datetime.date.today().strftime('%B %Y')
                title = data['title']
                subtitle = data['subtitle']

                readme_contents="""
{{% center %}} 
{}
{{% endcenter %}}




<br><br>
{{% center %}}

# {}

## {}

{{% endcenter %}}

<br><br><br><br><br><br><br>

{{% center %}} {} {{% endcenter %}}
                """.format(authors_list, title, subtitle, curr_date)
                with open(readme_path, 'w', encoding='utf-8') as w:
                    w.write(readme_contents)
        except FileNotFoundError:
            print("Ni datoteke meta.md")
        except KeyError as e:
            print("""
            
            Manjka key v meta.md. Več info tukaj: {}
            
            
            """.format(e))




    def write_summary(self, path_to_file=''):
        """Writes the gitbook summary to a file
        :parameter path_to_file Path to the file to be written. Default is the same directory where the method is called
        :return None
        """
        path_to_file = path_to_file if path_to_file else self.gitbook_folder
        with open(os.path.join(path_to_file, 'SUMMARY.md'), 'w', encoding='utf-8') as write_to_file:
            # the summary file has to start with a # heading
            write_to_file.write('# Summary\n\n')
            write_to_file.write('* [Naslovnica](README.md)\n')
            write_to_file.write('* [Uvod](UVOD.md)\n')
            write_to_file.write('* [Kolofon](kolofon.md)\n\n')

            for chapter_line in self._create_summary(self.list_of_files):
                write_to_file.write(chapter_line)

    def write_numbered_summary(self, path_to_file=''):
        """Writes the gitbook summary to a file
        :parameter path_to_file Path to the file to be written. Default is the same directory where the method is called
        :return None
        """
        path_to_file = path_to_file if path_to_file else self.gitbook_folder
        with open(os.path.join(path_to_file, 'SUMMARY.md'), 'w', encoding='utf-8') as write_to_file:
            # the summary file has to start with a # heading
            write_to_file.write('# Summary\n\n')
            write_to_file.write('* [Uvod](README.md)\n')
            write_to_file.write('* [Kolofon](kolofon.md)\n\n')
            for chapter_line in self._create_numbered_summary(self.list_of_files, self.clean_filename_element, self._create_numbered_headline):
                write_to_file.write(chapter_line)


def convert_metayaml_to_metajson(data, language='sl'):
    """
    Converts the yaml metadata as defined in pandoc for gitbook consumption as a book.json
    @param data: the data to be converted

    @return string: json string that has to be put into a file somewhere
    """

    def _check_for_missing_data(data_to_check):
        """
            Simple function to check missing data in a supplied yaml file
            @param data_to_check: the data to check for missing
            @return list: list of missing data
        """
        mandatory_data = ['title', 'subtitle', 'creator', 'identifier', 'publisher', 'date', 'cover-image', 'rights']
        json_data = yaml.load(data_to_check)
        missing_data = []
        for item in mandatory_data:
            if item not in json_data:
                missing_data.append(item)
        return missing_data

    # if there are missing entries, error out since the file is not correct and there is nothing we can do
    missing_entries = _check_for_missing_data(data)
    json_data = yaml.load(data)
    if missing_entries:
        raise ValueError('Missing data from metadata: {}'.format('- \n'.join(missing_entries)))
    else:
        # create the dictionary that will enventually become book.json for gitbook
        # if authors should be kept in a list or just as the first author

        
        authors = json_data['author']
        
        book_json = {
            'gitbook': '>=3.x.x', # support for gitbook 3 or later
            'plugins': ["-lunr", "-search", "search-plus-mod", "block-align"], # disable default search
            'title': json_data['title'][0]['text'],
            'subtitle': json_data['subtitle'],
            'language': language,
            'isbn': json_data['identifier'],
            'authors': authors,
            'author': json_data['creator'][0]['text'],
            'theme-default': {
                'showLevel': False,
            }

        }
    
    return json.dumps(book_json, indent=4)
