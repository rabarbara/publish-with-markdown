"""Creates a file ready for handoff to the typesetter"""

import os
import pkg_resources
from itertools import zip_longest
from collections import OrderedDict
from itertools import islice

import pypandoc


class FileCreator(object):
    """Opens the specified file and converts it to docx"""

    def __init__(self, filename, style=".", start=None):
        self.filename = os.path.basename(filename)
        if start == None:
            self.start = self.filename
        else:
            self.start = start
        self.filepath = filename
        assert style in [".", '/'], "Slog ni pravilen"
        self.style = style
        self.file = self.open_file()
        self.docx_name = self.filename.strip('.md')

    def __repr__(self):
        return '{}'.format(self.filename)

    def open_file(self):
        """
            Opens the file and read the contents
        """
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                return f.readlines()
        except FileNotFoundError:
            raise FileNotFoundError('Datoteke ni bilo mogoče najti.')

    def create_word(self, filename=None):
        """
            Creates a word file from the supplied text in markdown
        """
        if filename is None:
            filename = self.filename
        pypandoc.convert_text(self.file, to='docx', format='md',
                              outputfile="{}.docx".format(filename))

    def number_headers(self):
        # if the starting numbering should be taken from file

        header_map = self.header_mapping(name_or_start=self.start)
        file_container = []
        # iterate over the file and replace all headers with numbered headers
        # it is a code smell but it is only used here
        
        for line in self.file:
            if line.startswith('###### '):
                # start by increasing the count of your own header by one
                # this way the count is valid for all later headings that are "contained" by this heading, otherwise, the count is up by 1, which is wrong
                header_map['h6'] += 1
                # strip the header signature and re-add it later
                header_level = 6
                numbered_line = self.header_string(line, header_map, header_level, style=self.style)
                file_container.append(numbered_line)
                
            elif line.startswith('##### '):
                header_map['h5'] += 1
                # strip the header signature and re-add it later
                header_level = 5
                numbered_line = self.header_string(line, header_map, header_level, style=self.style)
                file_container.append(numbered_line)
                
                
            elif line.startswith('#### '):
                header_map['h4'] += 1
                # strip the header signature and re-add it later
                print(header_map)
                header_level = 4
                numbered_line = self.header_string(line, header_map, header_level, style=self.style)
                file_container.append(numbered_line)
            
            elif line.startswith('### '):
                header_map['h3'] += 1
                # strip the header signature and re-add it later
                
                header_level = 3
                numbered_line = self.header_string(line, header_map, header_level, style=self.style)
                file_container.append(numbered_line)
            
            elif line.startswith('## '):
                header_map['h2'] += 1
                # strip the header signature and re-add it later
                header_level = 2
                numbered_line = self.header_string(line, header_map, header_level, style=self.style)
                file_container.append(numbered_line)

            elif line.startswith('# '):
                header_map['h1'] += 1
                # strip the header signature and re-add it later
                header_level = 1
                numbered_line = self.header_string(line, header_map, header_level, style=self.style)
                file_container.append(numbered_line)
            else:
                file_container.append(line)
        self.file=file_container

    @staticmethod
    def header_string(line, header_mapping, header_level, style="."):
        """
        Returns the correct header string based on header mapping and header_level
        """
        headers = {
            1: "# ",
            2: "## ",
            3: "### ",
            4: "#### ",
            # 5: "##### ",
            # 6: "###### "
        }
        # the numbering is generated by taking the ordered dict from headermapping and creating string
        # representations of these values and just join them together
        if style == ".":
            numbering = '.'.join([str(item) for item in islice(header_mapping.values(), header_level)])
        else:
            h1 = str(header_mapping['h1'])
            rest_of_headers = '.'.join([str(item) for item in islice(header_mapping.values(), 1, header_level)])
            numbering = '{}/{}'.format(h1, rest_of_headers)
        stripped_line = line.strip(headers[header_level])
        numbered_header = ('{}{} {}').format(headers[header_level], numbering, stripped_line)
        return numbered_header


    @staticmethod
    def header_mapping(name_or_start):
        """
        Returns a clean header mapping for later use
        return: header mapping dictionary
        """
        header_values = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
        try:
            headers = [int(item) for item in name_or_start.strip('.md').split('.')]
            # important bit: in order for the count be correct later on, reduce the last available count by one
            # for example [3,5,3] => [3,5,2].
            # This couples it quite tightly but it is meant just for this.
            headers[-1] -= 1
        except ValueError:
            raise ValueError('Ime datoteke ni pravilno. Vnesi pravo številčenje ali popravi ime.')
        #combine the two lists and create a dict
        # fill value should be zero since they don't exist yet
        header_mapping = OrderedDict(zip_longest(header_values, headers, fillvalue=0))
        
        return header_mapping

    def convert_with_filter(self, filename=None):
        """
            Creates a word file but adds an additional filter replacing paragraphs with themselves
            and additional empty paragraphs
        """
        # outputs a docx file with replaced items
        resource_package = __name__
        resource_path = '/'.join(('filters', 'typesetter_filter.py'))
        typesetter_filter = pkg_resources.resource_stream(resource_package, resource_path)
        print(typesetter_filter.name)
        if filename is None:
            filename = self.docx_name
        combined_file = ''.join(self.file)
        pypandoc.convert_text(combined_file, to="docx", format="md",
                              filters=[typesetter_filter.name],
                              extra_args=['--atx-headers'],
                              outputfile="{}.docx".format(self.docx_name))

    def convert_with_filter_to_markdown(self, filename=None):
        """
            Creates a word file but adds an additional filter replacing paragraphs with themselves
            and additional empty paragraphs
        """
        # outputs a docx file with replaced items
        absolute_filter_path = os.path.abspath('typesetter_filter.py')
        if filename is None:
            filename = self.docx_name
        pypandoc.convert_text(''.join(self.file), to="md", format="md",
                              filters=[absolute_filter_path],
                              extra_args=['--atx-headers'],
                              )
