##########################################################################################
# pdsparser/_utils.py
##########################################################################################
"""Utility functions."""

import re
from filecache import FCPath


def read_label(filepath, *, chars=4000):
    """Read the PDS3 label from a file. Supports attached labels within binary files.

    Parameters:
        filepath (str, pathlib.Path, or filecache.FCPath): The path to the file. If the
            file does not contain a PDS3 label, a detached label (with the same path but
            ending in ".lbl" or ".LBL") is read instead.
        chars (int, optional): Initial number of characters to read from the top of a
            binary file when extracting the label. Reads will continue until the END
            statement is found.

    Returns:
        str: The content of the label as a single string with newline terminators.

    Raises:
        FileNotFoundError: If the label file is missing.
        SyntaxError: If the END statement is not found in a binary file.

    Notes:
        If the `filepath` ends in ".lbl" or ".LBL", it is assumed to refer to a detached
        label and the entire file content is returned. Otherwise, it reads the file
        (which may be binary) until it finds an "END" statement.
    """

    filepath = FCPath(filepath)
    if filepath.suffix.upper() == '.LBL':
        return filepath.read_text(encoding='latin-1')

    # Define regular expressions for label
    _COMMENT = re.compile(rb'(/\*.*?)\n')
    _DOUBLE = re.compile(rb'(".*?")')
    _SINGLE = re.compile(rb"('.*?')")
    _END = re.compile(rb'\n *END *\r?\n')

    # Open file for read; treat it as binary
    with filepath.open(mode='rb') as f:         # pragma: no branch
        content = b''
        end_of_file = False
        while not end_of_file:                  # pragma: no branch

            # Read more content from file
            old_len = len(content)
            content += f.read(chars)
            end_of_file = len(content) < old_len + chars

            # Replace comments with "xxx"; preserve content size and newlines
            parts = _COMMENT.split(content)
            parts[1::2] = [len(part) * b'x' + b'\n' for part in parts[1::2]]
            test = b''.join(parts)

            # Replace quoted text with "xxx"; preserve content size
            parts = _DOUBLE.split(test)
            parts[1::2] = [len(part) * b'x' for part in parts[1::2]]
            test = b''.join(parts)

            # Replace single-quoted text with 'xxx'; preserve content size
            parts = _SINGLE.split(test)
            parts[1::2] = [len(part) * b'x' for part in parts[1::2]]
            test = b''.join(parts)
            assert len(test) == len(content), 'quote replacement error'

            # Now it's safe to search for "END"
            match = _END.search(test)
            if match:
                content = content[:match.end()].replace(b'\r\n', b'\n')
                return content.decode('latin-1')

            # If not found, read more content and try again
            chars *= 2

    # Check for a detached .LBL file
    for suffix in ('.lbl', '.LBL'):
        alt_filepath = filepath.with_suffix(suffix)
        if alt_filepath.exists():
            return read_label(alt_filepath)

    raise SyntaxError(f'missing END statement in {filepath}')


def read_vax_binary_label(filepath):
    """Read an attached PDS3 label from a Vax binary file that uses variable-length
    records.

    Parameters:
        filepath (str, pathlib.Path, or filecache.FCPath): The path to the file. A
            detached label (ending in ".lbl" or ".LBL") is read using "stream" format;
            any other file is read assuming Vax variable-length format (in which the first
            two bytes of each record contain the length of the remaining
            record). If the file does not contain a PDS3 label, a detached label
            (with same path but ending in ".lbl" or ".LBL") is read instead.

    Returns:
        str: The content of the label as a single string with newline terminators.

    Raises:
        FileNotFoundError: If the label file is missing.
    """

    filepath = FCPath(filepath)
    if filepath.suffix.upper() == '.LBL':
        return read_label(filepath)

    # Read from Vax-structured file (where first two bytes are the record length)
    ended = False
    with filepath.open(mode='rb') as f:
        recs = []
        while True:
            header = f.read(2)                   # read two bytes
            if len(header) == 0:                 # at EOF, break
                break
            count = header[1] * 256 + header[0]  # interpret bytes as LSB integer
            rec = f.read(count)                  # read record with this many bytes
            recs.append(rec)                     # append this record to content
            if rec.strip() == b'END':            # on "END", we're done
                ended = True
                break
            if len(rec) % 2 == 1:                # if the record length is odd...
                f.read(1)                        # ... skip the next byte

    if ended:
        content = b'\n'.join(recs) + b'\n'
        return content.decode('latin-1')

    for suffix in ('.lbl', '.LBL'):
        alt_filepath = filepath.with_suffix(suffix)
        if alt_filepath.exists():
            return read_label(alt_filepath)

    raise SyntaxError(f'missing END statement in {filepath}')


def expand_structures(content, fmt_dirs=[], *, repairs=[], label_path=None):
    """Replace any ^STRUCTURE keywords in the label with the content of the associated
    ".FMT" files.

    Parameters:
        fmt_dirs (str, pathlib.Path, filecache.FCPath, or list, optional):
            One or more directory paths to search for the ".FMT" files.
        repairs (tuple or list[tuple]):
            One or more two-element tuples of the form (pattern, replacement), where the
            first item is a regular expression and the second is the string with which to
            replace it. These repair patterns are applied to the label content before it
            is parsed, and make it possible to repair known syntax errors.
        label_path (str, pathlib.Path, filecache.FCPath, optional):
            The path to the label file from which the content was obtained; if provided,
            the parent directory of this files is the first to be searched for .FMT files.

    Returns:
        str: The revised content string.

    Raises:
        FileNotFoundError: If a referenced .FMT file cannot be found in any of the
            directories specified.
    """

    # Define key regular expressions
    _STRUCTURE = re.compile(r' *\^[A-Z0-9_]*STRUCTURE *= *["|\'](.*?)["|\'] *\n')
    _END = re.compile(r' *END *\n*$')

    # Obtain the list of directories to search
    if not isinstance(fmt_dirs, (list, tuple)):
        fmt_dirs = [fmt_dirs]
    fmt_dirs = [FCPath(dir) for dir in fmt_dirs]
    if label_path:
        fmt_dirs = [FCPath(label_path).parent] + fmt_dirs
    if not fmt_dirs:        # if no path is provided, search the local default dir
        fmt_dirs = [FCPath('.')]

    # Replace ^STRUCTURE keywords, one by one...
    while (match := _STRUCTURE.search(content)):
        k0, k1 = match.span()
        fmt_name = match.group(1)

        # Find and read the .FMT file
        for fmt_dir in fmt_dirs:
            fmt_path = fmt_dir / fmt_name
            if fmt_path.exists():
                break

        if not fmt_path.exists():
            raise FileNotFoundError('file not found: ' + fmt_name)

        fmt_content = fmt_path.read_text(encoding='latin-1')

        # Don't include END from .FMT file
        if match := _END.search(fmt_content):
            fmt_content = fmt_content[:match.start()]

        # Repair content if necessary
        if isinstance(repairs, tuple):
            repairs = [repairs]
        for repair in repairs:
            fmt_content = re.sub(repair[0], repair[1], fmt_content)

        # Replace
        content = content[:k0] + fmt_content + content[k1:]

    return content


def _format_float(value):
    """Convert float to string with some cleanup."""

    result = str(value)
    if result.endswith('.0'):
        result = result[:-1]
    if '.' not in result:
        result = result.replace('e', '.e').replace('E', '.E')
    if '.' not in result:
        result += '.'

    return result


def _based_int(radix, digits):
    """The integer value associated with a based integer."""

    value = 0
    for c in digits:
        i = '0123456789ABCDEF'.index(c.upper())
        value = value * radix + i

    return value


def _is_identifier(text):
    if text != text.upper():
        return False
    text = text.replace('_', '')
    if not text[:1].isalpha():
        return False
    return text.isalnum()


def _unique_key(name, dict_, dups=None):
    """This name if it is not in the dict_; otherwise with a numeric suffix appended to
    make it unique.
    """

    if name not in dict_:
        return name

    indx = 2
    while (key := name + '_' + str(indx)) in dict_:
        indx += 1

    if dups is not None:
        dups.add(name)

    return key


def _unwrap(text):
    """Remove indents and extra newlines inside paragraphs."""

    # Strip trailing whitespace from each line
    parts = [t.rstrip() for t in text.split('\n')]

    # Delete leading blank lines
    while parts and not parts[0]:
        parts = parts[1:]

    if not parts:
        return ''

    # Strip indent of first line
    first = parts[0].lstrip()

    # Derive indent from subsequent non-empty strings
    indent = 9999
    for part in parts[1:]:
        if part:
            indent = min(indent, len(part) - len(part.lstrip()))

    # Remove all indents
    parts = [first] + [part[indent:] for part in parts[1:]]

    # Put a newline in front of each residual indent
    for k, part in enumerate(parts):
        if part and part[0].isspace():
            parts[k] = '\n' + part

    # An old-style newline at the end of the last line is unnecessary
    if parts[-1].endswith('\\n'):
        parts[-1] = parts[-1][:-2].rstrip()

    # An old-style newline at the end of a line forces a newline at the front of the next
    for k in range(len(parts) - 1):
        part = parts[k]
        if part.endswith('\\n'):
            parts[k] = parts[k][:-2].rstrip()
            if parts[k+1] and parts[k+1][0] != '\n':
                parts[k+1] = '\n' + parts[k+1]

    # Replace any remaining explicit newlines with the real thing
    for k, part in enumerate(parts):
        subparts = part.split('\\n')
        parts[k] = '\n'.join(subpart.rstrip() for subpart in subparts)

    # Merge paragraphs
    new_parts = parts[:1]
    for part in parts[1:]:
        if not part:
            new_parts.append('\n\n')
        elif part[0].isspace():
            new_parts.append(part)
        elif new_parts[-1][-1].isspace():
            new_parts.append(part)
        else:
            new_parts.append(' ' + part)

    result = ''.join(new_parts)

    # Never more than two blank lines together
    parts = re.split(r'\n\n+', result)
    result = '\n\n'.join(parts)

    return result.strip()


##########################################################################################
