##########################################################################################
# pdsparser/__init__.py
##########################################################################################
"""PDS Ring-Moon Systems Node, SETI Institute

``pdsparser`` is a Python module that reads a PDS3 label file and converts its entire
content to a Python dictionary.

The typical way to use this is as follows::

    from pdsparser import Pds3Label
    label = Pds3Label(label_path)

where `label_path` is the path to a PDS3 label file or a data file containing an attached
PDS3 label. The returned object `label` is an object of class :class:`Pds3Label`, which
supports the Python dictionary API and provides access to the content of the label.

#########
Example 1
#########

Suppose this is the content of a PDS3 label::

    PDS_VERSION_ID                  = PDS3
    RECORD_TYPE                     = FIXED_LENGTH
    RECORD_BYTES                    = 2000
    FILE_RECORDS                    = 1001
    ^VICAR_HEADER                   = ("C3450702_GEOMED.IMG", 1)
    ^IMAGE                          = ("C3450702_GEOMED.IMG", 2000 <BYTES>)

    /* Image Description  */

    INSTRUMENT_HOST_NAME            = "VOYAGER 1"
    INSTRUMENT_HOST_NAME            = VG1
    IMAGE_TIME                      = 1980-10-29T09:58:10.00
    FILTER_NAME                     = VIOLET
    EXPOSURE_DURATION               = 1.920 <SECOND>

    DESCRIPTION                     = "This image is the result of geometrically
    correcting the corresponding CALIB image (C3450702_CALIB.IMG)."

    OBJECT                          = VICAR_HEADER
      HEADER_TYPE                   = VICAR
      BYTES                         = 2000
      RECORDS                       = 1
      INTERCHANGE_FORMAT            = ASCII
      DESCRIPTION                   = "VICAR format label for the image."
    END_OBJECT                      = VICAR_HEADER

    OBJECT                          = IMAGE
      LINES                         = 1000
      LINE_SAMPLES                  = 1000
      SAMPLE_TYPE                   = LSB_INTEGER
      SAMPLE_BITS                   = 16
      BIT_MASK                      = 16#7FFF#
    END_OBJECT                      = IMAGE
    END

The returned dictionary will be as follows::

    {'PDS_VERSION_ID': 'PDS3',
     'RECORD_TYPE': 'FIXED_LENGTH',
     'RECORD_BYTES': 2000,
     'FILE_RECORDS': 1001,
     '^VICAR_HEADER': 'C3450702_GEOMED.IMG',
     '^VICAR_HEADER_offset': 1,
     '^VICAR_HEADER_unit': '',
     '^VICAR_HEADER_fmt': '("C3450702_GEOMED.IMG", 1)',
     '^IMAGE': 'C3450702_GEOMED.IMG',
     '^IMAGE_offset': 2000,
     '^IMAGE_unit': '<BYTES>',
     '^IMAGE_fmt': '("C3450702_GEOMED.IMG", 2000 <BYTES>)',
     'INSTRUMENT_HOST_NAME_1': 'VOYAGER 1',
     'INSTRUMENT_HOST_NAME_2': 'VG1',
     'IMAGE_TIME': datetime.datetime(1980, 10, 29, 9, 58, 10),
     'IMAGE_TIME_day': -7003,
     'IMAGE_TIME_sec': 35890.0,
     'IMAGE_TIME_fmt': '1980-10-29T09:58:10.000',
     'FILTER_NAME': 'VIOLET',
     'EXPOSURE_DURATION': 1.92,
     'EXPOSURE_DURATION_unit': '<SECOND>',
     'DESCRIPTION': 'This image is the result of geometrically\n
    correcting the corresponding CALIB image (C3450702_CALIB.IMG).',
     'DESCRIPTION_unwrap': 'This image is the result of geometrically correcting the
    corresponding CALIB image (C3450702_CALIB.IMG).',
     'VICAR_HEADER': {'OBJECT': 'VICAR_HEADER',
                      'HEADER_TYPE': 'VICAR',
                      'BYTES': 2000,
                      'RECORDS': 1,
                      'INTERCHANGE_FORMAT': 'ASCII',
                      'DESCRIPTION': 'VICAR format label for the image.',
                      'END_OBJECT': 'VICAR_HEADER'},
     'IMAGE': {'OBJECT': 'IMAGE',
               'LINES': 1000,
               'LINE_SAMPLES': 1000,
               'SAMPLE_TYPE': 'LSB_INTEGER',
               'SAMPLE_BITS': 16,
               'BIT_MASK': 32767,
               'BIT_MASK_radix': 16,
               'BIT_MASK_digits': '7FFF',
               'BIT_MASK_fmt': '16#7FFF#',
               'END_OBJECT': 'IMAGE'},
     'END': '',
     'objects': ['VICAR_HEADER', 'IMAGE']}

As you can see:

* Most PDS3 label keywords become keys in the dictionary without change.
* OBJECTs and GROUPs are converted to sub-dictionaries and are keyed by the value of the
  PDS3 keyword. In this example, `label['VICAR_HEADER']['HEADER_TYPE']` returns 'VICAR'.
* If a keyword is repeated at the top level or within an object or group, it receives a
  suffix "_1", "_2", "_3", etc. to distinguish it.
* If a value has units, there is an additional keyword in the dictionary with "_unit" as
  a suffix, containing the name of the unit.
* For text values that contain a newline, trailing blanks are suppressed. In addition, a
  dictionary key with the suffix "_unwrap" contains the same text as full paragraphs
  separated by newlines.
* For a file pointer of the form `(filename, offset)` or `(filename, offset <BYTES>)`, the
  keyed value is just the filename. The offset value provided with "_offset" appended to
  the dictionary key, and the unit is provided with "_unit" appended to the key.
* For based integers of the form "radix#digits#", the dictionary value is converted to an
  integer. However, the radix and the digit string are provided using keys with the suffix
  "_radix" and "_digits". Also, the key with suffix "_fmt" provides a full, PDS3-formatted
  version of the value.
* Dates and times are converted to Python datetime objects. However, additional dictionary
  keys appear with the suffix "_day" for the day number relative to Janary 1, 2000 and
  "_sec" for the elapsed seconds within that day.
* For items that have special formatting within a label, such file pointers, dates, and
  integers with a radix, the key with a "_fmt" suffix provides the PDS3-formatted value
  for reference.
* Each dictionary containing OBJECTs ends with an entry keyed by "objects", which returns
  the ordered list of all the OBJECT keys in that dictionary. Similarly, each dictionary
  containing GROUPs has an entry keyed by "groups", which returns the list of all the
  GROUP keys. These provide a easy way to iterate through objects and groups in the label.

#########
Example 2
#########

Within TABLE and SPREADSHEET objects, the dictionary keys of the embedded COLUMN,
BIT_COLUMN, FIELD, and ELEMENT_DEFINITION objects are keyed by the value of the NAME
keyword (rather than by using repeated keywords "COLUMN_1", "COLUMN_2", "COLUMN_3", etc.).
For example, suppose this appears in a PDS3 label::

    OBJECT = TABLE
      OBJECT = COLUMN
        NAME = VOLUME_ID
        START_BYTE = 1
      END_OBJECT = COLUMN
      OBJECT = COLUMN
        NAME = FILE_SPECIFICATION_NAME
        START_BYTE = 15
      END_OBJECT = COLUMN
    END_OBJECT = TABLE

The returned section of the dictionary will look like this::

    {'TABLE': {'OBJECT': 'TABLE',
               'VOLUME_ID': {'OBJECT': 'COLUMN',
                             'NAME': 'VOLUME_ID',
                             'START_BYTE': 1,
                             'END_OBJECT': 'COLUMN'},
               'FILE_SPECIFICATION_NAME': {'OBJECT': 'COLUMN',
                                           'NAME': 'FILE_SPECIFICATION_NAME',
                                           'START_BYTE': 15,
                                           'END_OBJECT': 'COLUMN'},
               'END_OBJECT': 'TABLE'},
               'objects': ['VOLUME_ID', 'FILE_SPECIFICATION_NAME']}

#########
Example 3
#########

"Set" notation (using curly braces "{}") was sometimes mis-used in PDS3 labels where
"sequence" notation (using parentheses "()") was meant. For example, this might appear in
a label::

    CUTOUT_WINDOW = {1, 1, 200, 800}

which is supposed to define the four boundaries of an image region. The user might be
surprised to learn that in the dictionary, its value is the Python set {1, 200, 800}. To
address this situation, for every set value, the dictionary also has a key with the same
name but suffix "_list", which contains the elements of the value as list in their
original order and including duplicates. In this example, the dictionary contains::

    'CUTOUT_WINDOW': {1, 200, 800},
    'CUTOUT_WINDOW_list': [1, 1, 200, 800]

#######
Options
#######

The :meth:`Pds3Label` constructor provides a variety of additional options for how to
parse the label and present its content.

* You can provide the label to be parsed as a string containing the label's content rather
  than as a path to a file.
* Use `types=True` to include the type of each keyword the file and interpret its content
  (e.g., "integer", "based_integer", "text", "date_time", or "file_offset_pointer") in the
  dictionary using the keyword plus suffix "_type".
* Use `sources=True` to include the source text as extracted from the PDS3 label in the
  dictionary using the keyword plus suffix "_source".
* Use `expand=True` to insert the content of any referenced `^STRUCTURE` keywords into the
  returned dictionary.
* Use `vax=True` to read attached labels from old-style Vax variable-length record files.
* Use the `repairs` to correct any known syntax errors in the label prior to parsing using
  regular expressions.

Four methods of parsing the label are provided.

* `method="strict"` uses a strict implementation of the PDS3 syntax. It is sure to provide
  accurate results, but can be rather slow. This method can also be used to validate the
  syntax within a PDS3 label, because it will raise a SyntaxError if anything goes wrong.
* `method="loose"` uses a variant of the "strict" method, in which allowance is made for
  certain common syntax errors. Specifically,

  * It allows slashes in file names and in text strings that are not quoted (e.g., 'N/A').
  * It allows the value of `END_OBJECT` and `END_GROUP` to be absent, as long as they are
    still properly paired with associated `OBJECT` and `GROUP` keywords.
  * It allows time zone expressions (where were disallowed after the PDS2 standard).
  * Commas can be missing between the elements of a sequence or set.
  * The final line terminator after `END` can be missing from a detached label.

* `method="fast"` is a different and much faster (often 30x faster) parser, which takes
  various "shortcuts" during the parsing. As a result, it may fail on occasions where the
  other methods succeed, and it may not return correct results in the cases of some
  oddly-formatted labels. However, it handles all the most common aspects of the PDS3
  syntax correctly, and so may be a good choice when handling large numbers of labels.
* `method="compound"`" is similar to "loose", but it parses a "compound" label, i.e., one
  that might  contain more than one `END` statement.

#########
Utilities
#########

The `pdsparser` module provides several additional utilities for handling PDS3 labels.

- :meth:`~utils.read_label`: Reads a PDS3 label from a file. Supports attached labels
  within binary files.
- :meth:`~utils.read_vax_binary_label`: Reads the attached PDS3 label from an old-style
  Vax binary file that uses variable-length records.
- :meth:`~utils.expand_structures`: Replaces any `^STRUCTURE` keywords in a label string
  with the content of the associated ".FMT" files.
"""

import datetime as dt
import pathlib
import re
from filecache import FCPath
from pyparsing import ParseException

try:
    from ._version import __version__
except ImportError:         # pragma: no cover
    __version__ = 'Version unspecified'

from .utils import read_label, read_vax_binary_label, expand_structures, _unique_key
from ._fast_dict import _fast_dict
from ._PDS3_GRAMMAR import _PDS3_LABEL, _ALT_PDS3_LABEL, _COMPOUND_LABEL

_PARSERS = {'strict': _PDS3_LABEL, 'loose': _ALT_PDS3_LABEL, 'compound': _COMPOUND_LABEL}

##########################################################################################
# Pds3Label
##########################################################################################

class Pds3Label():
    """Class representing the parsed content of a PDS3 label."""

    def __init__(self, label, method='strict', *, expand=False, fmt_dirs=[],
                 repairs=[], vax=False, types=False, sources=False, first_suffix=True,
                 _details=False):
        """Constructor for a Pds3Label.

        Parameters:
            label (str, list, pathlib.Path, or filecache.FCPath):
                The label, defined as a path to a file or as the content of a label. The
                content can be represented by a single string with <LF> or <CR><LF>
                terminators, or as a list of strings with optional terminators. If the
                file contains an attached PDS3 label, that file is read up to the END
                statement and the remainder is ignored. If the file does not contain a
                label but a detached label (ending in ".lbl" or ".LBL" exists), that file
                is read instead.

            method (str, optional):
                The method of parsing to apply to the label. One of:

                * "strict" performs strict parsing, which requires that the label conform
                  to the full PDS3 standard.
                * "loose" is similar to the above, but tolerates some common syntax
                  errors.
                * "compound" is similar to "loose", but it parses a "compound" label,
                  i.e., one that might contain more than one "END" statement. This option
                  is not supported for attached labels.
                * "fast": uses s a different parser, which executes ~ 30x fast than the
                  above and handles all the most common aspects of the PDS3 standard.
                  However, it is not guaranteed to provide an accurate parsing under all
                  circumstances.

            expand (bool, optional):
                True to replace the content of any ^STRUCTURE keyword in the label with
                the content of the associated ".FMT" file.

            fmt_dirs (str, pathlib.Path, filecache.FCPath, or list, optional):
                One or more directory paths to search for ".FMT" files. Note that if
                `label` indicates a file path, the parent directory of that file is always
                searched first.

            repairs (tuple or list[tuple]):
                One or more two-element tuples of the form (pattern, replacement), where
                the first item is a regular expression and the second is the string with
                which to replace it. These repair patterns are applied to the label
                content before it is parsed, and make it possible to repair known syntax
                errors.  For example, this tuple uses a "negative look-behind" pattern
                (?<!...) tow ensure that every occurrence of "N/A" is surrounded by
                quotes::

                    (r'(?<!["\\'])N/A', "'N/A'")

                The `replacement` can include back-references ("\\1", "\\2", etc.) to
                captured substrings of `tuple`; see any documentation about regular
                expressions for more details.

            vax (bool, optional):
                True to read an attached label from a Vax binary file.

            types (bool, optional):
                If True, for each PDS keyword in the label, there will be an extra key in
                the dictionary with the same name but suffix "_type" identifying the PDS3
                data type, e.g., "integer", "based_integer", "text", "date_time",
                "file_offset_pointer", etc.

            sources (bool, optional):
                If True, for each PDS keyword in the label, there will be an extra key in
                the dictionary with the same name but suffix "_source" returning the
                substring of the label from which this value was derived.

            first_suffix (bool, optional):
                If True and a keyword is duplicated, append a suffix "_1" to the first
                occurrence; otherwise, the first occurrence of the keyword has no suffix.

            _details (bool, optional):
                Used for debugging. If True, for each PDS keyword in the label, there will
                be an extra key in the dictionary with the same name but suffix "_detail"
                returning an object (of class internal to this module) containing details
                about how the entry was parsed. Not provided if `fast=True`.

        Raises:
            FileNotFoundError: If the label file is missing.
            SyntaxError: If the label content contains invalid syntax.

        Notes:
            The label information is preserved as a dictionary using the value before
            each equal sign as the key. If a keyword is repeated in the label, later
            dictionary keys have a suffix "_1", "_2", "_3", etc.

            OBJECT and GROUP elements are described by internal dictionaries, which are
            organized the same as the overall label. The key for COLUMN, BIT_COLUMN,
            FIELD, and ELEMENT_DEFINITION objects is their NAME attribute; for others, it
            is the value after the equal sign in the OBJECT or GROUP statement.

            Numeric values are represented as ints or floats. If the value has a unit, the
            unit value can be accessed by appending "_unit" to the key. Integers given
            with a radix are provided as ints, but you can view the radix value and the
            digit string by appending "_radix" and "_digits" to the key; in addition,
            suffix "_fmt" returns the full formatted value using the radix notation.

            Text strings are represented as Python str values. For those that extend
            beyond a single line, you can append "_unwrap" to the key to get a version of
            the text in which indents and newlines within paragraphs have been removed.

            Dates, times, and date-times are all represented using classes of the python
            datetime module. Dates and date-times have an additional dictionary entry
            using suffix "_day" returning the elapsed days since January 1, 2000. Times
            and date-times have an additional entry using suffix "_sec" returning the
            number of elapsed seconds since the beginning of that day. In additiona, all
            of these have an additional entry with suffix

            Sequences are represented by lists. 2-D sequences are represented by list of
            lists. Append "_unit" to the key to see any unit values that appeared within
            the sequence; if all units are the same, the "_unit" suffix returns a single
            value; otherwise, it returns a list or list of lists containing the unit
            value associated with each value in the sequence.

            Set values (enclosed in curly braces {}) are represented by Python set
            objects. However, because this notation was sometimes mis-used in labels for
            values that should have been given as sequences, you can also view these
            values as an ordered list by appending "_list" to the key.

            For pointers involving a filename and an offset, the keyword name in the label
            returns the filename only; Append "_offset" to the key to get the offset and
            "_unit" to get the unit, which is either "<BYTES>" or an empty string
            (meaning the unit is records).

        Attributes:
            content (str): The full content of the label as a string with <LF> line
                separators. If expand is True, this will be the expanded content, with any
                ^STRUCTURE values replaced.
            dict (dict): The actual dictionary containing all the label content. However,
                note that most of the Python dictionary API is implemented directly by
                this class, so label[keyword] is the same as label.dict[keyword].
        """

        if method not in {'strict', 'loose', 'compound', 'fast'}:
            raise ValueError('invalid method: ' + repr(method))

        self._filepath = ''
        self._fast = (method == 'fast')
        self.content = ''

        # Interpret `label` input
        if isinstance(label, list):
            self.content = '\n'.join(rec.rstrip() for rec in label) + '\n'
        elif isinstance(label, str):
            # Is this a file path or a content string?
            if '\n' in label:
                self.content = label
            else:
                self._filepath = FCPath(label)
        elif isinstance(label, (pathlib.Path, FCPath)):
            self._filepath = FCPath(label)
        else:
            raise ValueError('invalid label')

        # Read the label content if necessary
        if self._filepath:
            if vax:
                self.content = read_vax_binary_label(self._filepath)
            elif method == 'compound':
                self.content = FCPath(self._filepath).read_text(encoding='latin-1')
            else:
                self.content = read_label(self._filepath)

        # Repair content if necessary
        # We need to repair the content before expanding structures in case the repair
        # applies to the ^STRUCTURE statement (which it does for VG2_SAT.LBL in VG_2001).
        if isinstance(repairs, tuple):
            repairs = [repairs]
        for repair in repairs:
            self.content = re.sub(repair[0], repair[1], self.content)

        # Replace ^STRUCTURE if necessary
        if expand:
            self.content = expand_structures(self.content, fmt_dirs=fmt_dirs,
                                             repairs=repairs, label_path=self._filepath)

        # Parse label
        if method == 'fast':
            self.dict, self._statements = _fast_dict(self.content, types=types,
                                                     sources=sources,
                                                     first_suffix=first_suffix)
        else:
            try:
                self._statements = _PARSERS[method].parse_string(self.content)
            except ParseException as err:       # convert parse exception to SyntaxError
                message = str(err)
                if message[:2] == ', ':
                    message = message[2:]
                raise SyntaxError(message)

            self.dict = self._python_dict(types=types, sources=sources,
                                          first_suffix=first_suffix, details=_details)

    def __str__(self):

        indent = 0
        result = []
        for statement in self._statements:
            if self._fast:
                name, value = statement
            else:
                name = statement.name
                value = statement.item and str(statement.item)

            if name in ('END_OBJECT', 'END_GROUP'):
                indent -= 2
            result += [indent * ' ', name]
            if value is not None:
                result += [' = ', value]
            result.append('\n')
            if name in ('OBJECT', 'GROUP'):
                indent += 2

        return ''.join(result)

    def __repr__(self):
        return str(self)

    # Implement the core dict interface
    def __getitem__(self, key):
        return self.dict[key]

    def __setitem__(self, key, value):
        self.dict[key] = value

    def __len__(self):
        return len(self.dict)

    def __contains__(self, key):
        return key in self.dict

    def get(self, key, default=None):
        """The value for key if key is in the label; otherwise, the specified default."""
        return self.dict.get(key, default)

    def items(self):
        """Iterator over (key, value) tuples for this dictionary."""
        return self.dict.items()

    def keys(self):
        """Iterator over this dictionary's keys."""
        return self.dict.keys()

    def values(self):
        """Iterator over this dictionary's values."""
        return self.dict.values()

    def _as_item_dict(self, first_suffix=True):
        """A dictionary returning _Item objects, keyed by the label attribute name.

        If the item is an OBJECT or GROUP, it returns a sub-dictionary of _Items instead.
        For COLUMN, FIELD, BIT_COLUMN, and ELEMENT_DEFINITION objects that have a NAME
        attribute, the key is that name rather than the object type.

        Duplicated keys get assigned suffixes "_1", "_2", "_3", etc.

        If the value of END_OBJECT or END_GROUP is missing, it is filled in from the
        matching OBJECT or GROUP.
        """

        def apply_first_suffix(dict_, dups):
            if first_suffix and dups:
                # Update the first occurrence of duplicated keys, preserving order
                new_dict = {}
                for key, value in dict_.items():
                    if key in dups:
                        key = key + '_1'
                    new_dict[key] = value
                return new_dict

            return dict_

        dict_list = [{}]
        key_list = ['']
        dup_sets = [set()]
        for statement in self._statements:
            name = statement.name
            item = statement.item
            dict_ = dict_list[-1]

            # If this is an object or group, start a new dictionary
            if name in ('OBJECT', 'GROUP'):
                object_dict = {name: item}
                dict_list.append(object_dict)
                key_list.append(item.value)
                dup_sets.append(set())
                continue

            # Replace the key for a COLUMN or FIELD by its NAME value if found
            if key_list[-1] in {'COLUMN', 'FIELD', 'BIT_COLUMN', 'ELEMENT_DEFINITION',
                                'GENERIC_OBJECT_DEFINITION',
                                'SPECIFIC_OBJECT_DEFINITION'} and name == 'NAME':
                key_list[-1] = item.value

            # Make the key unique and add its value to the dictionary
            key = _unique_key(name, dict_, dup_sets[-1])
            dict_[key] = item
            if name not in ('END_OBJECT', 'END_GROUP'):
                continue

            # Check for END_OBJECT without OBJECT
            tail = '' if item is None else ' = ' + item.value
            if name[4:] not in dict_:
                raise SyntaxError(f'unbalanced {name}{tail}')

            # Get a missing value for END_OBJECT or END_GROUP
            if item is None:
                item = dict_[name[4:]]
                dict_[name] = item
                dict_[name + '_source'] = ''    # override because there's no source

            # Check for OBJECT/END_OBJECT mismatch
            if item.value != dict_[name[4:]].value:
                raise SyntaxError(f'unbalanced {name}{tail}')

            # Pop this dictionary and insert it into the higher-level dictionary
            dict_ = dict_list.pop()
            dups = dup_sets.pop()
            dict_ = apply_first_suffix(dict_, dups)

            key = _unique_key(key_list.pop(), dict_list[-1], dup_sets[-1])
            dict_list[-1][key] = dict_

        if len(dict_list) > 1:
            name = list(dict_list[-1].keys())[0]    # dicts preserve key order
            raise SyntaxError(f'missing END_{name}')

        return apply_first_suffix(dict_list[0], dup_sets[0])

    def _python_dict(self, types=False, sources=False, first_suffix=True, details=False):
        """The label content as a Python dictionary.

        Keys are the attribute names (with numeric suffix for duplicates).
        """

        def from_item_dict(item_dict):
            dict_ = {}
            object_keys = []
            group_keys = []
            for key, item in item_dict.items():
                if key.endswith('_source'):             # save these for below
                    continue

                if isinstance(item, dict):
                    local_dict = from_item_dict(item)   # recursive call
                    dict_[key] = local_dict
                    if 'OBJECT' in local_dict:
                        object_keys.append(key)
                    else:
                        group_keys.append(key)
                    continue

                if not item:
                    dict_[key] = item
                    continue

                dict_[key] = item.value
                suffixes = list(item.suffixes)
                if types:
                    dict_[key + '_type'] = item.type_
                if sources:
                    dict_[key + '_source'] = item.source

                for suffix in suffixes:
                    dict_[key + '_' + suffix.rstrip('_')] = getattr(item, suffix)

                if details:
                    dict_[key + '_detail'] = item

            if object_keys:
                dict_['objects'] = object_keys
            if group_keys:
                dict_['groups'] = group_keys

            # When there's no associated object, the "_source" key provided in item_dict
            # contains the override source value. Used for END_OBJECT with no value.
            for key, value in item_dict.items():
                if key.endswith('_source'):     # there's no source object
                    if sources:
                        dict_[key] = value
                    if details:
                        del dict_[key.replace('source', 'detail')]

            return dict_

        item_dict = self._as_item_dict(first_suffix=first_suffix)
        return from_item_dict(item_dict)

    # Old, deprecated API
    def as_dict(self):
        """This label as a Python dictionary. Part of the old PdsLabel API.

        DEPRECATED; use the `dict_` attribute or apply the dict API directoy to this
        Pds3Label object.

        Note that this function matches the previous output of as_dict(). Specifically,

        * dates, times, and datetimes are returned as strings in ISO format.
        * file_offset_pointers are returned as a tuple (filename, offset, unit).
        * set values are returns as lists.
        * units are omitted.
        """

        def to_old_dict(dict_):
            old = {}
            for key, value in dict_.items():
                if key != key.upper():
                    continue

                if isinstance(value, dict):
                    old[key] = to_old_dict(value)
                elif isinstance(value, (dt.date, dt.time, dt.datetime)):
                    old[key] = dict_[key + '_fmt']
                elif isinstance(value, set):
                    old[key] = dict_[key + '_list']
                elif key + '_offset' in dict_:
                    old[key] = (value, dict_[key + '_offset'],
                                'BYTES' if dict_[key + '_unit'] else 'RECORDS')
                else:
                    old[key] = value
            return old

        return to_old_dict(self.dict)

    @staticmethod
    def from_file(filename):
        """Load and parse a PDS label. Part of the old PdsLabel API.

        DEPRECATED; use Pds3Label(filename).
        """

        return Pds3Label(filename)

    @staticmethod
    def load_file(filepath):
        """Load a PDS label, possibly attached, returning a list of strings. Part of the
        old PdsLabel API.

        DEPRECATED; use read_label(filepath).
        """

        content = read_label(filepath)
        recs = content.split('\n')
        return [rec + '\n' for rec in recs[:-1]]

    @staticmethod
    def from_string(string):
        """Construct a Pds3Label from a string or list of strings. Part of the old
        PdsLabel API.

        DEPRECATED; just use Pds3Label(string).
        """

        return Pds3Label(string)

# Deprecated name for the class
PdsLabel = Pds3Label

##########################################################################################
