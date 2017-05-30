import errno
import os
import string
import unicodedata
from urllib.parse import urlparse


REPLACEMENT_CHAR = {'&': '-', ',': '.', ';': '-', '=': '_'}


def clean_filename(filename):
    return ''.join([
        c for c in unicodedata.normalize(
            'NFKD',
            ''.join([replace_char(c) for c in filename])
        )
        if not unicodedata.combining(c) and c in '-_.() {0}{1}'.format(string.ascii_letters, string.digits)
    ])


def make_dirs(file_path):
    try:
        os.makedirs(os.path.dirname(file_path))
    except OSError as exc:  # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise


def replace_char(char, replacements=None):
    return REPLACEMENT_CHAR.get(char, char) if not replacements else replacements.get(char, char)


def default_url_transform(url):
    parsed_url = urlparse(url)

    path_segments = [
        clean_filename(path_segment) for path_segment in parsed_url.path.split('/')[1:]
        ]
    if not len(path_segments):
        path_segments = ['index']

    params = clean_filename(parsed_url.params)
    if len(params):
        params = '(' + params + ')'

    query = clean_filename(parsed_url.query)
    if len(query):
        query = '_' + query

    return os.path.sep.join([parsed_url.netloc] + path_segments) + params + query
