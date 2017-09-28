#pylint: disable=import-error
import os
import sys
import pytest
from collections import namedtuple
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import publish.gitbook as gb

#pylint: disable=import-error


@pytest.fixture
def set_book():
    gitbook = 'gitbook'
    media = 'media'
    folder = 'poglavje'
    gb_book = gb.Gitbook(gitbook_folder=gitbook,
                      common_folder_name=folder,
                      media_folder_name=media)
    book = namedtuple('Book', 'book, gitbook, media, folder')
    git_book = book(gb_book, gitbook, media, folder)
    return git_book

def test_copy_files_for_gitbook(set_book):
    set_book.book.copy_files_for_gitbook()
    # assert that files are created
    assert os.path.isdir(set_book.gitbook)
    assert os.path.isdir(os.path.join(set_book.gitbook, set_book.media))
    assert any([item for item in os.listdir(set_book.gitbook) if set_book.folder in item])

def test_create_list_of_files(set_book):

    set_book.book.copy_files_for_gitbook()
    set_book.book.create_a_list_of_files('poglavje-*/*')
    assert len(set_book.book.list_of_files) == len([item for item in os.listdir(set_book.gitbook) if set_book.folder in item])


def test_create_list_of_files_ugly_path(set_book):
    set_book.book.copy_files_for_gitbook()
    set_book.book.create_a_list_of_files('asdf-*/*')

    assert len(set_book.book.list_of_files) == 0

def test_internal_function_summary(set_book):
    book = set_book.book
    set_book.book.copy_files_for_gitbook()
    book.create_a_list_of_files('poglavje-*/*')
    print(list(book._create_summary(book.list_of_files)))
    assert len(list(book._create_summary(book.list_of_files))) > 1
