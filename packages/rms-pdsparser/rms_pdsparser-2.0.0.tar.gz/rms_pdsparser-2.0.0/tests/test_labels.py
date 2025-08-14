##########################################################################################
# pdsparser/test_labels.py
##########################################################################################

import datetime
import pathlib
import sys
import unittest

from filecache import FCPath
from pdsparser import Pds3Label, PdsLabel
from pdsparser._PDS3_GRAMMAR import _Text, _Integer

ROOT_DIR = pathlib.Path(sys.modules['pdsparser'].__file__).parent.parent
TEST_FILE_DIR = ROOT_DIR / 'test_files'

MAXDIFF = 300

class Test_labels(unittest.TestCase):

    def test_COVIMS_0xxx(self):

        self.maxDiff = MAXDIFF

        # This file has an un-quoted N/A, so method='loose'
        root = 'v1877838443_1'
        filepath = TEST_FILE_DIR / (root + '.lbl')
        d1 = Pds3Label(filepath, method='loose', types=True, sources=True, expand=False)
        answer = (TEST_FILE_DIR / (root + '-lbl-answer.txt')).read_text()
        answer_dict = eval(answer)
        self.assertEqual(d1.dict, answer_dict)

        d2 = Pds3Label(filepath, method='fast', types=True, sources=True, expand=False)
        self.assertEqual(d2.dict, answer_dict)

        # Test repairs, change strict to True
        d1 = Pds3Label(filepath, method='strict', types=True, sources=True, expand=False,
                       repairs=(r'(?<!["\'])N/A', "'N/A'"))
        for key in ('GAIN_MODE_ID_source',  'BACKGROUND_SAMPLING_MODE_ID_source'):
            answer_dict[key] = answer_dict[key].replace('N/A', "'N/A'")
        self.assertEqual(d1.dict, answer_dict)

        d2 = Pds3Label(filepath, method='fast', types=True, sources=True, expand=False,
                       repairs=(r'(?<!["\'])N/A', "'N/A'"))
        self.assertEqual(d2.dict, answer_dict)

        # Test first_suffix=False
        d3 = Pds3Label(filepath, method='strict', types=True, sources=True, expand=False,
                       repairs=(r'(?<!["\'])N/A', "'N/A'"), first_suffix=False)
        subdict = answer_dict['SPECTRAL_QUBE']
        for key in ('^STRUCTURE_1', '^STRUCTURE_1_type', '^STRUCTURE_1_source',
                    '^STRUCTURE_1_fmt'):
            subdict[key[:10] + key[12:]] = subdict[key]
            del subdict[key]
        self.assertEqual(d3.dict, answer_dict)

        # expand=True
        d1 = Pds3Label(filepath, method='loose', types=True, sources=True, expand=True)
        answer = (TEST_FILE_DIR / (root + '-lbl-expanded.txt')).read_text()
        answer_dict = eval(answer)
        self.assertEqual(d1.dict, answer_dict)

        d1 = Pds3Label(filepath, method='loose', types=True, sources=True, expand=True,
                       fmt_dirs=['./'])     # this value of fmt_dirs is not used
        self.assertEqual(d1.dict, answer_dict)

        d2 = Pds3Label(filepath, method='fast', types=True, sources=True, expand=True)
        self.assertEqual(d2.dict, answer_dict)

        d1 = Pds3Label(filepath, method='strict', types=True, sources=True, expand=True,
                       repairs=(r'(?<!["\'])N/A', "'N/A'"))
        for key in ('GAIN_MODE_ID_source',  'BACKGROUND_SAMPLING_MODE_ID_source'):
            answer_dict[key] = answer_dict[key].replace('N/A', "'N/A'")
        self.assertEqual(d1.dict, answer_dict)

        d2 = Pds3Label(filepath, method='fast', types=True, sources=True, expand=True,
                       repairs=(r'(?<!["\'])N/A', "'N/A'"))
        self.assertEqual(d2.dict, answer_dict)

        # label from qub
        filepath = TEST_FILE_DIR / (root + '.qub')
        d1 = Pds3Label(filepath, method='strict', types=True, sources=True)
        answer = (TEST_FILE_DIR / (root + '-qub-answer.txt')).read_text()
        answer_dict = eval(answer)
        self.assertEqual(d1.dict, answer_dict)

        d2 = Pds3Label(filepath, method='fast', types=True, sources=True)
        self.assertEqual(d2.dict, answer_dict)

        # Labels with syntax errors
        filepath = TEST_FILE_DIR / 'v1877838443_1-EXCEPTION.lbl'
        self.assertRaisesRegex(SyntaxError, "Expected end of text, found .*",
                               Pds3Label, filepath, method='loose')

        filepath = TEST_FILE_DIR / 'v1877838443_1-EXCEPTION2.lbl'
        self.assertRaisesRegex(SyntaxError, 'missing END_OBJECT',
                               Pds3Label, filepath, method='loose')

        filepath = TEST_FILE_DIR / 'v1877838443_1-EXCEPTION3.lbl'
        self.assertRaisesRegex(SyntaxError, 'unbalanced END_OBJECT',
                               Pds3Label, filepath, method='loose')

    def test_GOxxx_v1(self):

        self.maxDiff = MAXDIFF

        root = 'C052079-2800R'
        filepath = TEST_FILE_DIR / (root + '.LBL')
        d1 = Pds3Label(filepath, method='loose', types=True, sources=True, expand=False)
        answer = (TEST_FILE_DIR / (root + '-answer.txt')).read_text()
        self.assertEqual(d1.dict, eval(answer))

        d2 = Pds3Label(filepath, method='fast', types=True, sources=True, expand=False)
        self.assertEqual(d2.dict, eval(answer))

        # vax=True doesn't matter if this is a label file
        d3 = Pds3Label(filepath, method='loose', types=True, sources=True, expand=False,
                       vax=True)
        self.assertEqual(d3.dict, eval(answer))

        d1 = Pds3Label(filepath, method='loose', types=True, sources=True, expand=True)
        answer = (TEST_FILE_DIR / (root + '-expanded.txt')).read_text()
        self.assertEqual(d1.dict, eval(answer))

        d2 = Pds3Label(filepath, method='fast', types=True, sources=True, expand=True)
        self.assertEqual(d2.dict, eval(answer))

    def text_JNOJIR_xxxx(self):

        self.maxDiff = MAXDIFF

        root = 'JIR_LOG_SPE_RDR_2020048T195001_V01'
        filepath = TEST_FILE_DIR / (root + '.LBL')
        d1 = Pds3Label(filepath, method='strict', types=True, sources=True)
        answer = (TEST_FILE_DIR / (root + '-answer.txt')).read_text()
        self.assertEqual(d1.dict, eval(answer))

        d2 = Pds3Label(filepath, method='fast', types=True, sources=True)
        self.assertEqual(d2.dict, eval(answer))

    def text_JNOJNC_0xxx(self):

        self.maxDiff = MAXDIFF

        root = 'JNCE_2022348_47C00007_V01'
        filepath = TEST_FILE_DIR / (root + '.LBL')
        d1 = Pds3Label(filepath, method='strict', types=True, sources=True)
        answer = (TEST_FILE_DIR / (root + '-answer.txt')).read_text()
        self.assertEqual(d1.dict, eval(answer))

        d2 = Pds3Label(filepath, method='fast', types=True, sources=True)
        self.assertEqual(d2.dict, eval(answer))

    def test_NHxxLO_xxxx(self):

        self.maxDiff = MAXDIFF

        root = 'lor_0284676508_0x630_sci'
        filepath = TEST_FILE_DIR / (root + '.lbl')
        d1 = Pds3Label(filepath, method='strict', types=True, sources=True)
        answer = (TEST_FILE_DIR / (root + '-answer.txt')).read_text()
        self.assertEqual(d1.dict, eval(answer))

        d2 = Pds3Label(filepath, method='fast', types=True, sources=True)
        self.assertEqual(d2.dict, eval(answer))

    def test_VGISS_xxxx(self):

        self.maxDiff = MAXDIFF

        root = 'C3450702_GEOMED'
        filepath = TEST_FILE_DIR / (root + '.LBL')
        d1 = Pds3Label(filepath, method='strict', types=True, sources=True)
        answer = (TEST_FILE_DIR / (root + '-answer.txt')).read_text()
        self.assertEqual(d1.dict, eval(answer))

        d2 = Pds3Label(filepath, method='fast', types=True, sources=True)
        self.assertEqual(d2.dict, eval(answer))

        d1 = Pds3Label(filepath, method='strict')
        answer = (TEST_FILE_DIR / (root + '-short.txt')).read_text()
        self.assertEqual(d1.dict, eval(answer))

        d2 = Pds3Label(filepath, method='fast')
        self.assertEqual(d2.dict, eval(answer))

        self.assertEqual(len(d1), 61)
        pairs = [('PDS_VERSION_ID', 'PDS3'),
                 ('RECORD_TYPE', 'FIXED_LENGTH'),
                 ('RECORD_BYTES', 2000),
                 ('FILE_RECORDS', 1001),
                 ('^VICAR_HEADER', 'C3450702_GEOMED.IMG'),
                 ('^VICAR_HEADER_offset', 1),
                 ('^VICAR_HEADER_unit', ''),
                 ('^VICAR_HEADER_fmt', '("C3450702_GEOMED.IMG", 1)'),
                 ('^IMAGE', 'C3450702_GEOMED.IMG'),
                 ('^IMAGE_offset', 2),
                 ('^IMAGE_unit', ''),
                 ('^IMAGE_fmt', '("C3450702_GEOMED.IMG", 2)'),
                 ('DATA_SET_ID', 'VG1/VG2-S-ISS-2/3/4/6-PROCESSED-V1.1'),
                 ('PRODUCT_ID', 'C3450702_GEOMED.IMG'),
                 ('PRODUCT_CREATION_TIME', datetime.datetime(2012, 5, 1, 16, 0)),
                 ('PRODUCT_CREATION_TIME_day', 4504),
                 ('PRODUCT_CREATION_TIME_sec', 57600),
                 ('PRODUCT_CREATION_TIME_fmt', '2012-05-01T16:00:00')]
        self.assertEqual(list(d1.items())[:18], pairs)
        self.assertEqual(list(d1.keys())[:18], [p[0] for p in pairs])
        self.assertEqual(list(d1.values())[:18], [p[1] for p in pairs])
        self.assertEqual(d1['PDS_VERSION_ID'], 'PDS3')
        self.assertEqual(d1.get('PDS_VERSION_ID', 'whatever'), 'PDS3')
        self.assertEqual(d1.get('PDS_VERSION_IDx', 'whatever'), 'whatever')
        self.assertTrue('PDS_VERSION_ID' in d1)
        self.assertTrue('PDS_VERSION_IDx' not in d1)

        for test in (str(d1), repr(d1), str(d2), repr(d2)):
            lines = test.split('\n')
            self.assertEqual(lines[:9],
                             ['PDS_VERSION_ID = PDS3',
                              'RECORD_TYPE = FIXED_LENGTH',
                              'RECORD_BYTES = 2000',
                              'FILE_RECORDS = 1001',
                              '^VICAR_HEADER = ("C3450702_GEOMED.IMG", 1)',
                              '^IMAGE = ("C3450702_GEOMED.IMG", 2)',
                              'DATA_SET_ID = "VG1/VG2-S-ISS-2/3/4/6-PROCESSED-V1.1"',
                              'PRODUCT_ID = "C3450702_GEOMED.IMG"',
                              'PRODUCT_CREATION_TIME = 2012-05-01T16:00:00'])

        test = Pds3Label.from_file(str(filepath))
        self.assertEqual(test.dict, d1.dict)

        test = Pds3Label.from_string(d1.content)
        self.assertEqual(test.dict, d1.dict)

        _ = Pds3Label.load_file(FCPath(filepath))
        test = Pds3Label.from_string(d1.content)
        self.assertEqual(test.dict, d1.dict)

        d3 = Pds3Label(filepath, method='strict', _details=True)
        detail = d3['^VICAR_HEADER_detail']
        self.assertEqual(detail.value, d3['^VICAR_HEADER'])
        self.assertEqual(detail.offset, 1)
        self.assertEqual(detail.unit, '')
        self.assertEqual(detail.source, '("C3450702_GEOMED.IMG", 1)')
        self.assertEqual(str(detail), '("C3450702_GEOMED.IMG", 1)')

        detail = d3['EXPOSURE_DURATION_detail']
        self.assertEqual(detail.value, 1.92)
        self.assertEqual(detail.unit, '<SECOND>')
        self.assertEqual(str(detail), '1.92 <SECOND>')

        detail = d3['FILTER_NAME_detail']
        self.assertEqual(detail.value, 'VIOLET')
        self.assertEqual(str(detail), 'VIOLET')

        # Failover from data file to detached label
        root = 'C3450702_GEOMED'
        filepath = TEST_FILE_DIR / (root + '.empty')
        d1 = Pds3Label(filepath, method='strict', types=True, sources=True)
        answer = (TEST_FILE_DIR / (root + '-answer.txt')).read_text()
        self.assertEqual(d1.dict, eval(answer))

        d1 = Pds3Label(filepath, method='strict', types=True, sources=True, vax=True)
        self.assertEqual(d1.dict, eval(answer))

    def test_VG_0xxx(self):

        self.maxDiff = MAXDIFF

        root = 'C3438954'
        filepath = TEST_FILE_DIR / (root + '.IMQ')
        d1 = Pds3Label(filepath, method='loose', types=True, sources=True, expand=False,
                       vax=True)
        answer = (TEST_FILE_DIR / (root + '-answer.txt')).read_text()
        answer_dict = eval(answer)
        self.assertEqual(d1.dict, answer_dict)

        d2 = Pds3Label(filepath, method='fast', types=True, sources=True, expand=False,
                       vax=True)
        self.assertEqual(d2.dict, answer_dict)

        # sources=False
        for obj in ('IMAGE_HISTOGRAM', 'ENCODING_HISTOGRAM', 'ENGINEERING_TABLE',
                    'IMAGE'):
            for key in list(answer_dict[obj].keys()):
                if key.endswith('_source'):
                    del answer_dict[obj][key]
        for key in list(answer_dict.keys()):
            if key.endswith('_source'):
                del answer_dict[key]

        d1 = Pds3Label(filepath, method='loose', types=True, sources=False, expand=False,
                       vax=True)
        self.assertEqual(d1.dict, answer_dict)

        d2 = Pds3Label(filepath, method='fast', types=True, sources=False, expand=False,
                       vax=True)
        self.assertEqual(d2.dict, answer_dict)

        # expand=True
        d1 = Pds3Label(filepath, method='loose', types=True, sources=True, expand=True,
                       vax=True, first_suffix=False)
        answer = (TEST_FILE_DIR / (root + '-expanded.txt')).read_text()
        self.assertEqual(d1.dict, eval(answer))

        d2 = Pds3Label(filepath, method='fast', types=True, sources=True, expand=True,
                       vax=True, first_suffix=False)
        self.assertEqual(d2.dict, eval(answer))

    def test_VG_2001(self):

        self.maxDiff = MAXDIFF

        root = 'VG2_SAT'
        filepath = TEST_FILE_DIR / (root + '.LBL')
        d1 = Pds3Label(filepath, method='strict', types=True, sources=True, expand=False)
        answer = (TEST_FILE_DIR / (root + '-answer.txt')).read_text()
        answer_dict = eval(answer)
        self.assertEqual(d1.dict, answer_dict)

        d2 = Pds3Label(filepath, method='fast', types=True, sources=True, expand=False)
        self.assertEqual(d2.dict, answer_dict)

        # The name of the ^STRUCTURE file is erroneous
        self.assertRaises(FileNotFoundError, Pds3Label, filepath, method='strict',
                          expand=True)

        # method='loose' because the FMT file has tabs
        d1 = Pds3Label(filepath, method='loose', types=False, sources=True, expand=True,
                       repairs=(r'"IRIS_ROWFMT\.FMT"', '"IRISHEDR.FMT"'))
        answer = (TEST_FILE_DIR / (root + '-expanded.txt')).read_text()
        answer_dict = eval(answer)
        self.assertEqual(d1.dict, answer_dict)

        d2 = Pds3Label(filepath, method='fast', types=False, sources=True, expand=True,
                       repairs=(r'"IRIS_ROWFMT\.FMT"', '"IRISHEDR.FMT"'))
        self.assertEqual(d2.dict, answer_dict)

        # This FMT has a missing quote in the first DESCRIPTION
        self.assertRaisesRegex(SyntaxError, "Expected end of text, found .*",
                               Pds3Label, filepath, method='loose', expand=True,
                               repairs=[(r'"IRIS_ROWFMT\.FMT"',
                                         '"IRISHEDR-with-error.FMT"')])

        d1 = Pds3Label(filepath, method='loose', types=False, sources=True, expand=True,
                       repairs=[(r'"IRIS_ROWFMT\.FMT"', '"IRISHEDR-with-error.FMT"'),
                                (r'data identifier\.', 'data identifier."')])
        self.assertEqual(d1.dict, answer_dict)

        d2 = Pds3Label(filepath, method='fast', types=False, sources=True, expand=True,
                       repairs=[(r'"IRIS_ROWFMT\.FMT"', '"IRISHEDR-with-error.FMT"'),
                                (r'data identifier\.', 'data identifier."')])
        self.assertEqual(d2.dict, answer_dict)

        # Without a fmt_dir to work with, it should search the local default dir; this
        # will still raise FileNotFoundError
        content = filepath.read_text()
        self.assertRaises(FileNotFoundError, Pds3Label, content, expand=True)

    def test_pdsdd(self):

        self.maxDiff = MAXDIFF

        root = 'pdsdd-short'
        filepath = TEST_FILE_DIR / (root + '.full')
        d1 = Pds3Label(filepath, method='compound')
        answer = (TEST_FILE_DIR / (root + '-answer.txt')).read_text()
        answer_dict = eval(answer)
        self.assertEqual(d1.dict, answer_dict)

        root = 'pdsdd-endless'
        filepath = TEST_FILE_DIR / (root + '.full')
        d2 = Pds3Label(filepath, method='loose')    # missing commas in sequences

        d1_dict_endless = {}
        for key, value in d1.dict.items():
            if key.startswith('END_'):
                continue
            d1_dict_endless[key] = value
        d1_dict_endless['END'] = d1['END_21']

        self.assertEqual(d2.dict, d1_dict_endless)

    def test_more(self):

        self.maxDiff = MAXDIFF

        root = 'TESTS'
        filepath = TEST_FILE_DIR / (root + '.LBL')
        d1 = Pds3Label(filepath, method='loose', types=True, sources=True)
        answer = (TEST_FILE_DIR / (root + '-answer.txt')).read_text()
        answer_dict = eval(answer)
        self.assertEqual(d1.dict, answer_dict)

        answer_dict['MIXED_SEQ_unit'] = '<km>'
        d2 = Pds3Label(filepath, method='fast', types=True, sources=True)
        self.assertEqual(d2.dict, answer_dict)

        # Tests of alternative inputs
        root = 'v1877838443_1'
        filepath = TEST_FILE_DIR / (root + '.qub')
        d1 = Pds3Label(filepath, method='strict', types=True, sources=True)
        answer = (TEST_FILE_DIR / (root + '-qub-answer.txt')).read_text()
        answer_dict = eval(answer)
        self.assertEqual(d1.dict, answer_dict)

        d3 = PdsLabel(d1.content, method='strict', types=True, sources=True)
        self.assertEqual(d3.dict, answer_dict)

        d4 = PdsLabel(d1.content.split('\n'), method='strict', types=True, sources=True)
        self.assertEqual(d4.dict, answer_dict)

        self.assertRaises(ValueError, PdsLabel, filepath, method='whatever')
        self.assertRaises(ValueError, PdsLabel, 999)

        # Attached label failure
        filepath = TEST_FILE_DIR / 'empty.dat'
        self.assertRaisesRegex(SyntaxError, r'missing END statement in .*empty\.dat',
                               Pds3Label, filepath)
        self.assertRaisesRegex(SyntaxError, r'missing END statement in .*empty\.dat',
                               Pds3Label, filepath, vax=True)

        # __setitem__
        d4['FOO'] = 'BAR'
        self.assertEqual(d4.dict['FOO'], 'BAR')

        # Mixed units, method='fast'
        content = 'VECTOR = (1 <km>, 10 <s>)\nEND\n'
        d1 = Pds3Label(content)         # no problem if method='strict'
        self.assertRaisesRegex(SyntaxError, 'mixture of units encountered at VECTOR, .*',
                               Pds3Label, content, method='fast')

        # Unbalanced OBJECT/END_OBJECT
        content = 'OBJECT = FOO\nEND\n'
        for method in ('strict', 'loose', 'fast'):
            self.assertRaisesRegex(SyntaxError, 'missing END_OBJECT.*',
                                   Pds3Label, content, method=method)

        content = 'OBJECT = FOO\nEND_OBJECT = BAR\nEND\n'
        for method in ('strict', 'loose', 'fast'):
            self.assertRaisesRegex(SyntaxError, 'unbalanced END_OBJECT = BAR.*',
                                   Pds3Label, content, method=method)

        content = 'END_OBJECT = BAR\nEND\n'
        for method in ('strict', 'loose', 'fast'):
            self.assertRaisesRegex(SyntaxError, 'unbalanced END_OBJECT = BAR.*',
                                   Pds3Label, content, method=method)

        content = 'END_OBJECT\nEND\n'
        self.assertRaisesRegex(SyntaxError, r"found '\\n' .*",
                               Pds3Label, content, method='strict')
        for method in ('loose', 'fast'):
            self.assertRaisesRegex(SyntaxError, 'unbalanced END_OBJECT[^=]*',
                                   Pds3Label, content, method=method)

        content = 'VALUE = "abc\nEND\n'
        for method in ('strict', 'loose', 'fast'):
            self.assertRaisesRegex(SyntaxError, 'Expected \'"\', found end of text.*',
                                   Pds3Label, content, method=method)

        content = 'VALUE = (1,2\nEND\n'
        self.assertRaisesRegex(SyntaxError, 'unbalanced parentheses ()',
                               Pds3Label, content, method='fast')

        content = 'VALUE = {1,2\nEND\n'
        self.assertRaisesRegex(SyntaxError, 'unbalanced braces {}',
                               Pds3Label, content, method='fast')

        content = 'VALUE\nEND\n'
        self.assertRaisesRegex(SyntaxError, 'missing "=" at VALUE, line 1',
                               Pds3Label, content, method='fast')

        # _details=True
        content = 'OBJECT = TEST\nVALUE = 7\nEND_OBJECT\nEND\n'
        d1 = Pds3Label(content, method='loose', _details=True)
        self.assertEqual(d1.dict,
                         {'TEST': {'OBJECT': 'TEST',
                           'OBJECT_detail': _Text('', 0, ['TEST']),
                           'VALUE': 7,
                           'VALUE_detail': _Integer('', 0, ['7']),
                           'END_OBJECT': 'TEST'},
                          'END': None,
                          'objects': ['TEST']})

        # END with no terminator
        content = 'VALUE = 7\nEND'
        d1 = Pds3Label(content, method='loose')
        self.assertEqual(d1.dict, {'VALUE': 7, 'END': None})

        content = 'VALUE = 7\nEND    \t  '
        d1 = Pds3Label(content, method='loose')
        self.assertEqual(d1.dict, {'VALUE': 7, 'END': None})

        # Missing commas in a sequence or set
        content = 'VALUE = (1, 2, 3 4)\n'
        d1 = Pds3Label(content, method='loose')
        self.assertEqual(d1.dict, {'VALUE': [1, 2, 3, 4]})

        content = 'VALUE = {1, 2, 3 4 1}\n'
        d1 = Pds3Label(content, method='loose')
        self.assertEqual(d1.dict, {'VALUE': {1, 2, 3, 4},
                                   'VALUE_list': [1, 2, 3, 4, 1]})

        content = 'VALUE = ((1, 2) (3\n "four"))\n'
        d1 = Pds3Label(content, method='loose')
        self.assertEqual(d1.dict, {'VALUE': [[1, 2], [3, "four"]]})

    def test_as_dict(self):

        self.maxDiff = MAXDIFF

        root = 'AS_DICT_TEST'
        filepath = TEST_FILE_DIR / (root + '.LBL')
        d1 = Pds3Label(filepath)
        test_dict = d1.as_dict()

        # This is the result of a run of the v1 module...
        old_answer = (TEST_FILE_DIR / (root + '-as_dict.txt')).read_text()
        old_answer_dict = eval(old_answer)

        # new parser does not use "Z" suffix
        test_dict['IMAGE_TIME'] = test_dict['IMAGE_TIME'] + 'Z'

        # a line break in an embedded string is now just a space
        test_dict['SOURCE_PRODUCT_ID'][4] = (test_dict['SOURCE_PRODUCT_ID'][4]
                                             .replace(' ', '\n'))

        # old dicts do not have OBJECT and END_OBJECT entries
        for key in ('IMAGE_HEADER', 'TELEMETRY_TABLE', 'BAD_DATA_VALUES_HEADER', 'IMAGE'):
            del test_dict[key]['OBJECT']
            del test_dict[key]['END_OBJECT']

        # old dicts do not contain END statement
        del test_dict['END']

        self.assertEqual(test_dict, old_answer_dict)


##########################################################################################
