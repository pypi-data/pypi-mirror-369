##########################################################################################
# pdsparser/test_labels.py
##########################################################################################

import unittest

# Note: most functions in _utils.py are tested fully by test_labels.py.
from pdsparser.utils import _unwrap


class Test_utils(unittest.TestCase):

    def test_unwrap(self):

        text = ('\n   \nThis image is the result of geometrically   \n'
                '    correcting the corresponding CALIB image (C3450702_CALIB.IMG).  \n'
                '\n')
        self.assertEqual(_unwrap(text),
                         'This image is the result of geometrically '
                         'correcting the corresponding CALIB image (C3450702_CALIB.IMG).')

        note = """Input data type.  Identify input type
        as follows:

         00000000 - Voyager 2;                               \\n
         00000001 - Voyager 1;                               \\n
         00000010 - Proof Test Model data;                   \\n
         00000011 - Not Used;                                \\n
         00000100 - External Simulation (DSN spacecraft 41); \\n
         00000101 - External Simulation (DSN spacecraft 42); \\n
         00000110 - Voyager 2 test data;                     \\n
         00000111 - Voyager 1 test data;                     \\n
         00001000 - Internal Simulation.                     """

        self.assertEqual(_unwrap(note),
                         'Input data type.  Identify input type as follows:\n'
                         '\n'
                         ' 00000000 - Voyager 2;\n'
                         ' 00000001 - Voyager 1;\n'
                         ' 00000010 - Proof Test Model data;\n'
                         ' 00000011 - Not Used;\n'
                         ' 00000100 - External Simulation (DSN spacecraft 41);\n'
                         ' 00000101 - External Simulation (DSN spacecraft 42);\n'
                         ' 00000110 - Voyager 2 test data;\n'
                         ' 00000111 - Voyager 1 test data;\n'
                         ' 00001000 - Internal Simulation.')

        note = """Input data type.  Identify input type
        as follows:

         00000000 - Voyager 2;
         00000001 - Voyager 1;                               \\n
         00000010 - Proof Test Model data;
         00000011 - Not Used;                                \\n
         00000100 - External Simulation (DSN spacecraft 41);
         00000101 - External Simulation (DSN spacecraft 42); \\n
         00000110 - Voyager 2 test data;
         00000111 - Voyager 1 test data;                     \\n
         00001000 - Internal Simulation.                     """

        self.assertEqual(_unwrap(note),
                         'Input data type.  Identify input type as follows:\n'
                         '\n'
                         ' 00000000 - Voyager 2;\n'
                         ' 00000001 - Voyager 1;\n'
                         ' 00000010 - Proof Test Model data;\n'
                         ' 00000011 - Not Used;\n'
                         ' 00000100 - External Simulation (DSN spacecraft 41);\n'
                         ' 00000101 - External Simulation (DSN spacecraft 42);\n'
                         ' 00000110 - Voyager 2 test data;\n'
                         ' 00000111 - Voyager 1 test data;\n'
                         ' 00001000 - Internal Simulation.')

        note = """Input data type.  Identify input type
        as follows:
         00000000 - Voyager 2;                               \\n
         00001000 - Internal Simulation.                     """

        self.assertEqual(_unwrap(note),
                         'Input data type.  Identify input type as follows:\n'
                         ' 00000000 - Voyager 2;\n'
                         ' 00001000 - Internal Simulation.')

        note = """Input data type.  Identify input type
        as follows:


         00000000 - Voyager 2;                               \\n
         00001000 - Internal Simulation.                     """

        self.assertEqual(_unwrap(note),
                         'Input data type.  Identify input type as follows:\n'
                         '\n'
                         ' 00000000 - Voyager 2;\n'
                         ' 00001000 - Internal Simulation.')

        desc = ('Telemetry format id from the minor frame of this line.\n'
                'Valid is 5-HIS, 6-HMA, 7-HCA, 17-HIM, 22-IM8, 23-AI8, and 25-IM4\n'
                '\n'
                'This is a second paragraph.\n'
                '\n'
                'This\n'
                'is\n'
                'a    \n'
                'third\n'
                'paragraph.\n'
                '\n'
                'This one has a\\nforced split.')

        answer = ('Telemetry format id from the minor frame of this line. '
                  'Valid is 5-HIS, 6-HMA, 7-HCA, 17-HIM, 22-IM8, 23-AI8, and 25-IM4\n'
                  '\n'
                  'This is a second paragraph.\n'
                  '\n'
                  'This is a third paragraph.\n'
                  '\n'
                  'This one has a\n'
                  'forced split.')

        self.assertEqual(_unwrap(desc), answer)


##########################################################################################
