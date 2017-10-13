# pylint: disable=import-error
import os
import sys
import pytest
from collections import namedtuple

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pubmark import gitbook as gb

import shutil


# pylint: disable=import-error


@pytest.fixture
def set_book():
    gitbook = 'gitbook'
    media = 'media'
    folder = 'poglavje'
    gb_book = gb.Summary(gitbook_folder=gitbook,
                         common_folder_name=folder,
                         media_folder_name=media)
    book = namedtuple('Book', 'book, gitbook, media, folder')
    git_book = book(gb_book, gitbook, media, folder)
    gb_book.copy_files_for_gitbook()
    yield git_book
    # shutil.rmtree(gitbook)
    # shutil.rmtree(os.path.join(gitbook,media))


def test_copy_files_for_gitbook(set_book):
    set_book.book.copy_files_for_gitbook()
    # assert that files are created
    assert os.path.isdir(set_book.gitbook)
    assert os.path.isdir(os.path.join(set_book.gitbook, set_book.media))
    assert any([item for item in os.listdir(set_book.gitbook) if set_book.folder in item])


def test_create_list_of_files(set_book):
    set_book.book.create_a_list_of_files('poglavje-*/*')
    assert len(set_book.book.list_of_files) == len(
        [item for item in os.listdir(set_book.gitbook) if set_book.folder in item])


def test_create_list_of_files_ugly_path(set_book):
    set_book.book.create_a_list_of_files('asdf-*/*')

    assert len(set_book.book.list_of_files) == 0


def test_internal_function_summary(set_book):
    book = set_book.book

    book.create_a_list_of_files('poglavje-*/*')
    assert len(list(book._create_summary(book.list_of_files))) > 1
    assert all([item for item in book._create_summary(book.list_of_files)
                if item.startswith('*') or item.startswith('\t') or item.startswith('\n\n')])


def test_write_summary(set_book):
    book = set_book.book
    book.create_a_list_of_files('poglavje-*/*')
    book.write_summary()
    assert os.path.isfile(os.path.join(set_book.gitbook,'SUMMARY.md'))
    with open(os.path.join(set_book.gitbook,'SUMMARY.md'), 'r', encoding='utf-8') as summary:
        assert summary.readline().startswith('# Summary')

def test_convert_yaml_to_json_file():
    # give string and receive json dump string
    with open(os.path.join(os.path.dirname(__file__), 'meta.md'), mode='r', encoding='utf-8') as meta_data:
        assert isinstance(gb.convert_yaml_to_json(meta_data.read()), str)

@pytest.mark.yaml
def test_missing_title_error():
    test_data_without_title = """
---
subtitle: Subtitle
author:
  - Author 2
  - Author 1
creator:
- role: Editor
  text: Main editor
- role: Production editor
  text: Prod editor
- role: Proofreader
  text: Proofreader 1
identifier: ISSN 3456-3412
publisher: Publishin company
date: 2016
cover-image: cover-image.jpg
rights: | 
  All rights reserved
...
                    """

    with pytest.raises(ValueError, message='Missing data from metadata: title'):
        gb.convert_yaml_to_json(test_data_without_title)

