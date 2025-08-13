import tempfile
import os
from pycodebox.utils import read_tab_delim_file_to_dict


def test_read_tab_delim_file_to_dict():
    test_data = (
        'key1\tvalue1\tvalue2\tvalue3\n'
        'key2\tvalue4\tvalue5\n'
        'key3\tvalue6\tvalue7\tvalue8\tvalue9\n'
    )

    with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
        f.write(test_data)
        f.flush()

        result = read_tab_delim_file_to_dict(f.name)

    os.unlink(f.name)

    expected = {
        'key1': ['value1', 'value2', 'value3'],
        'key2': ['value4', 'value5'],
        'key3': ['value6', 'value7', 'value8', 'value9'],
    }
    assert result == expected
