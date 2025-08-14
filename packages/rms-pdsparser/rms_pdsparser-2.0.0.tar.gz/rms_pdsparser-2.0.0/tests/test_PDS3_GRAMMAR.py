##########################################################################################
# pdsparser/test_PDS3_GRAMMAR.py
##########################################################################################

import datetime as dt
import unittest
from pyparsing import ParseException, StringEnd

from pdsparser._PDS3_GRAMMAR import (_Integer,
                                     _BasedInteger,
                                     _Real,
                                     _NumberWithUnit,
                                     _Time,
                                     _HmsTime,
                                     _UtcTime,
                                     _TimeZone,
                                     _ZonedTime,
                                     _Date,
                                     _DateTime,
                                     _Text,
                                     _Set,
                                     _Sequence,
                                     _Sequence2D,
                                     _SimplePointer,
                                     _LocalPointer,
                                     _OffsetPointer,
                                     _SetPointer,
                                     _SequencePointer,
                                     _AttributeID,
                                     _PointerID,
                                     _Statement,
                                     _EndStatement)


def tz(minutes):
    return dt.timezone(dt.timedelta(seconds=60 * minutes))


def _pass(testcase, type_, string, value, strval=None, vtype=None, test=3, super_=True):
    """Test grammar(s) for success, using parsers for this class and all superclasses.

    If test is 1, test grammar; if test is 2, test alt_grammar; if test is 3, test both
    (if they both exist).
    """

    for cls in type_.__mro__:
        if not hasattr(cls, 'grammar'):
            break

        grammars = [cls.grammar] if (test & 1) else []
        if (test & 2) and 'alt_grammar' in cls.__dict__.keys():
            grammars.append(cls.alt_grammar)

        if not grammars:
            raise ValueError(f'no grammar selected: {cls}, test={test}')

        for k, grammar in enumerate(grammars):
            # print('_pass', repr(string), cls, len(grammars), k)
            try:
                obj = (grammar + StringEnd()).parse_string(string)[0]
            except ParseException:
                print('ParseException on', str(grammar), repr(string))
                raise

            testcase.assertIsInstance(obj, type_)
            testcase.assertEqual(obj.value, value)

            if vtype:
                testcase.assertIsInstance(obj.value, vtype)

            if strval:
                testcase.assertEqual(str(obj), strval)

        if not super_:
            break

        cls = super(cls)

    return obj


def _fail(testcase, type_, string, test=3, super_=True):
    """Test grammar(s) for failure, using parsers for this class and all superclasses.

    If test is 1, test grammar; if test is 2, test alt_grammar; if test is 3, test both
    (if they both exist).
    """

    for cls in type_.__mro__:
        if not hasattr(cls, 'grammar'):
            break

        grammars = [cls.grammar] if (test & 1) else []
        if (test & 2) and 'alt_grammar' in cls.__dict__.keys():
            grammars.append(cls.alt_grammar)

        if not grammars:
            raise ValueError(f'no grammar selected: {cls}, test={test}')

        for k, grammar in enumerate(grammars):
            # print('_fail', repr(string), cls, len(grammars), k)
            testcase.assertRaises(ParseException, (grammar + StringEnd()).parse_string,
                                  string)

        if not super_:
            break


class Test_Integer(unittest.TestCase):

    def runTest(self):

        obj = _pass(self, _Integer, '123', 123)
        self.assertEqual(obj.type_, 'integer')
        self.assertEqual(obj.value, 123)
        self.assertEqual(obj.full_value, 123)
        self.assertEqual(str(obj), '123')
        self.assertEqual(repr(obj), '_Integer(123)')
        self.assertEqual(obj, 123)

        _pass(self, _Integer, '-123', -123)
        _pass(self, _Integer, '+123', 123, '123')

        _fail(self, _Integer, '+ 123')
        _fail(self, _Integer, '- 123')


class Test_BasedInteger(unittest.TestCase):

    def runTest(self):

        obj = _pass(self, _BasedInteger, '2#11111111#', 255, '2#11111111#', int)
        self.assertEqual(str(obj), '2#11111111#')
        self.assertEqual(repr(obj), '_BasedInteger(2#11111111#)')
        self.assertEqual(obj, 255)
        self.assertEqual(obj.radix, 2)
        self.assertEqual(obj.digits, '11111111')
        self.assertEqual(obj.fmt,  '2#11111111#')

        _pass(self, _BasedInteger, '2#000011111111#', 255, '2#000011111111#')
        _pass(self, _BasedInteger, '8#7#', 7)
        _pass(self, _BasedInteger, '8#10#', 8)
        _pass(self, _BasedInteger, '8#100#', 64)
        _pass(self, _BasedInteger, '8#1000#', 512)
        _pass(self, _BasedInteger, '8#10000#', 4096)
        _pass(self, _BasedInteger, '16#FF#', 255)

        _fail(self, _BasedInteger, '1#000#')
        _fail(self, _BasedInteger, '7#1#')
        _fail(self, _BasedInteger, '3#123#')
        _fail(self, _BasedInteger, '8# 123#')
        _fail(self, _BasedInteger, '8 #123#')
        _fail(self, _BasedInteger, '8#123 #')

class Test_Real(unittest.TestCase):

    def runTest(self):

        obj = _pass(self, _Real, '123.', 123., '123.', float)
        self.assertEqual(obj.type_, 'real')
        self.assertEqual(str(obj), '123.')
        self.assertEqual(repr(obj), '_Real(123.)')
        self.assertEqual(obj, 123)

        _pass(self, _Real, '1234.5', 1234.5, '1234.5')
        _pass(self, _Real, '+1234.5', 1234.5, '1234.5')
        _pass(self, _Real, '-1234.5', -1234.5, '-1234.5')
        _pass(self, _Real, '1234.5e6', 1234500000., '1234500000.', float)
        _pass(self, _Real, '1234.5e006', 1234500000.)
        _pass(self, _Real, '1234.5e+006', 1234500000.)
        _pass(self, _Real, '1234.5e-006', 0.0012345)
        _pass(self, _Real, '.5e+2', 50, '50.', float)
        _pass(self, _Real, '5e+2', 500, '500.', float)
        _pass(self, _Real, '-1e+20', -1.e20, '-1.e+20')

        _fail(self, _Real, '1234.5e0006')
        _fail(self, _Real, '1234 .5e06')
        _fail(self, _Real, '1234.5 e06')
        _fail(self, _Real, '1234.5e 06')
        _fail(self, _Real, '1234.5e+ 06')


class Test_NumberWithUnit(unittest.TestCase):

    def runTest(self):

        obj = _pass(self, _NumberWithUnit, '123.  <km>', 123., '123. <km>', float)
        self.assertEqual(obj.unit, '<km>')
        self.assertEqual(obj.full_value, (123., '<km>'))
        self.assertEqual(obj.type_, 'real')
        self.assertEqual(str(obj), '123. <km>')
        self.assertEqual(repr(obj), '_NumberWithUnit(123. <km>)')
        self.assertEqual(obj.value, 123.)
        self.assertEqual(obj.unit, '<km>')

        obj = _pass(self, _NumberWithUnit, '-1234.5 < km/s>', -1234.5, '-1234.5 <km/s>')
        self.assertEqual(obj.unit, '<km/s>')
        self.assertEqual(obj.full_value, (-1234.5, '<km/s>'))

        obj = _pass(self, _NumberWithUnit, '+1 < local day >', 1, '1 <local day>', int)
        self.assertEqual(obj.unit, '<local day>')

        self.assertEqual(_NumberWithUnit.grammar.parse_string('100 <km>')[0], 100)


class Test_SimpleTime(unittest.TestCase):

    def runTest(self):

        obj = _pass(self, _HmsTime, '12:34:56', dt.time(12, 34, 56))
        self.assertEqual(obj.type_, 'local_time')
        self.assertEqual(str(obj), '12:34:56')
        self.assertEqual(repr(obj), '_HmsTime(12:34:56)')
        self.assertEqual(obj.sec, 56 + 60 * (34 + 60 * 12))
        self.assertEqual(obj.fmt, '12:34:56')
        self.assertEqual(type(obj.sec), int)

        obj = _pass(self, _HmsTime, '12:34:56.123456', dt.time(12, 34, 56, 123456),
                    strval='12:34:56.123456')
        self.assertEqual(obj.type_, 'local_time')
        self.assertEqual(str(obj), '12:34:56.123456')
        self.assertEqual(repr(obj), '_HmsTime(12:34:56.123456)')
        self.assertEqual(obj.sec, 56.123456 + 60 * (34 + 60 * 12))
        self.assertEqual(obj.fmt, '12:34:56.123456')

        obj = _pass(self, _UtcTime, '12:34:56Z', dt.time(12, 34, 56), '12:34:56')
        self.assertEqual(obj.type_, 'utc_time')

        obj = _pass(self, _UtcTime, '12:34:56.123456Z', dt.time(12, 34, 56, 123456),
                    strval='12:34:56.123456')
        self.assertEqual(obj.type_, 'utc_time')

        obj = _pass(self, _HmsTime, '12:34', dt.time(12, 34), '12:34:00')
        self.assertEqual(obj.type_, 'local_time')

        obj = _pass(self, _UtcTime, '12:34Z', dt.time(12, 34), '12:34:00')
        self.assertEqual(obj.type_, 'utc_time')

        _pass(self, _HmsTime, '"12:34:56"', dt.time(12, 34, 56))
        _pass(self, _HmsTime, '"12:34:56.5"', dt.time(12, 34, 56, 500000),
              strval='12:34:56.500')
        _pass(self, _HmsTime, '"12:34:56.12345678"', dt.time(12, 34, 56, 123457),
              strval='12:34:56.123457')

        # Make sure leading zeros work
        obj = _pass(self, _HmsTime, '"12:34:01"', dt.time(12, 34, 1))
        self.assertIsInstance(obj.sec, int)

        obj = _pass(self, _HmsTime, '"12:34:01."', dt.time(12, 34, 1))
        self.assertIsInstance(obj.sec, float)

        obj = _pass(self, _HmsTime, '"01:01"', dt.time(1, 1, 0))
        self.assertIsInstance(obj.sec, int)

        _pass(self, _HmsTime, '"01:01:01"', dt.time(1, 1, 1))

        _fail(self, _HmsTime, '2:34')
        _fail(self, _HmsTime, '12:3')
        _fail(self, _HmsTime, '123:34')
        _fail(self, _HmsTime, '123 :34')
        _fail(self, _HmsTime, '123: 34')
        _fail(self, _HmsTime, '12:34Z', super_=False)
        _fail(self, _UtcTime, '12:34', super_=False)
        _fail(self, _UtcTime, '12:34 Z')


class Test_TimeZone(unittest.TestCase):

    def runTest(self):

        _pass(self, _TimeZone, '+2:30', tz(2*60 + 30), '+02:30', dt.timezone)
        _pass(self, _TimeZone, '+0:30', tz(30), '+00:30')
        _pass(self, _TimeZone, '-0:30', tz(-30), '-00:30')
        _pass(self, _TimeZone, '+00:30', tz(30), '+00:30')
        _pass(self, _TimeZone, '-00:30', tz(-30), '-00:30')
        _pass(self, _TimeZone, '-0', tz(0), '+00:00')
        _pass(self, _TimeZone, '-00', tz(0), '+00:00')
        _pass(self, _TimeZone, '-1', tz(-60), '-01:00')
        _pass(self, _TimeZone, '-01', tz(-60), '-01:00')
        _pass(self, _TimeZone, '+0', tz(0))
        _pass(self, _TimeZone, '+00', tz(0))
        _pass(self, _TimeZone, '+1', tz(60))
        _pass(self, _TimeZone, '+01', tz(60))
        _pass(self, _TimeZone, '+23:59', tz(23*60 + 59), '+23:59')
        _pass(self, _TimeZone, '-23:59', tz(-23*60 - 59), '-23:59')

        _fail(self, _TimeZone, '0:30')
        _fail(self, _TimeZone, '-000')
        _fail(self, _TimeZone, ' -0:30')
        _fail(self, _TimeZone, '- 0:30')
        _fail(self, _TimeZone, '-0 :30')
        _fail(self, _TimeZone, '-0: 30')
        _fail(self, _TimeZone, '-24')
        _fail(self, _TimeZone, '+24')
        _fail(self, _TimeZone, '+0:60')
        _fail(self, _TimeZone, 'Z')


class Test_ZonedTime(unittest.TestCase):

    def runTest(self):

        obj = _pass(self, _ZonedTime, '12:34+2', dt.time(12, 34, tzinfo=tz(2*60)),
                    '12:34:00+02:00', dt.time, test=2, super_=False)
        self.assertEqual(obj.type_, 'zoned_time')
        self.assertEqual(obj.sec, 3600*12 + 34*60 - 3600*2)
        self.assertEqual(obj.fmt, '12:34:00+02:00')
        self.assertEqual(str(obj), '12:34:00+02:00')
        self.assertEqual(repr(obj), '_ZonedTime(12:34:00+02:00)')
        self.assertEqual(obj.source, '12:34+2')

        obj = _pass(self, _ZonedTime, '12:34+2:30', dt.time(12, 34, tzinfo=tz(2*60 + 30)),
                    '12:34:00+02:30', dt.time, test=2, super_=False)
        self.assertEqual(obj.type_, 'zoned_time')
        self.assertEqual(obj.sec, 3600*12 + 34*60 - 3600*2 - 30*60)
        self.assertEqual(obj.fmt, '12:34:00+02:30')
        self.assertEqual(str(obj), '12:34:00+02:30')
        self.assertEqual(repr(obj), '_ZonedTime(12:34:00+02:30)')
        self.assertEqual(obj.source, '12:34+2:30')

        _pass(self, _ZonedTime, '"12:34-02"', dt.time(12, 34, tzinfo=tz(-2*60)),
              '12:34:00-02:00', dt.time, test=2, super_=False)
        _pass(self, _ZonedTime, '"12:34-02:45"', dt.time(12, 34, tzinfo=tz(-2*60 - 45)),
              '12:34:00-02:45', dt.time, test=2, super_=False)

        _fail(self, _ZonedTime, '12:34 +2:30',)
        _fail(self, _ZonedTime, '12:34 +02:30',)
        _fail(self, _ZonedTime, '12:34 -2',)
        _fail(self, _ZonedTime, '12:34- 2',)


class Test_Time(unittest.TestCase):

    def runTest(self):

        obj = _pass(self, _Time, '12:34:56', dt.time(12, 34, 56))
        self.assertEqual(obj.type_, 'local_time')
        self.assertEqual(str(obj), '12:34:56')
        self.assertEqual(repr(obj), '_HmsTime(12:34:56)')
        self.assertEqual(obj.sec, 56 + 60 * (34 + 60 * 12))
        self.assertEqual(obj.fmt, '12:34:56')
        self.assertEqual(type(obj.sec), int)

        obj = _pass(self, _Time, '12:34:56.123456', dt.time(12, 34, 56, 123456),
                    strval='12:34:56.123456')
        self.assertEqual(obj.type_, 'local_time')
        self.assertEqual(str(obj), '12:34:56.123456')
        self.assertEqual(repr(obj), '_HmsTime(12:34:56.123456)')
        self.assertEqual(obj.sec, 56.123456 + 60 * (34 + 60 * 12))
        self.assertEqual(obj.fmt, '12:34:56.123456')

        obj = _pass(self, _Time, '12:34:56Z', dt.time(12, 34, 56), '12:34:56')
        self.assertEqual(obj.type_, 'utc_time')

        obj = _pass(self, _Time, '12:34:56.123456Z', dt.time(12, 34, 56, 123456),
                    strval='12:34:56.123456')
        self.assertEqual(obj.type_, 'utc_time')

        obj = _pass(self, _Time, '12:34', dt.time(12, 34), '12:34:00')
        self.assertEqual(obj.type_, 'local_time')

        obj = _pass(self, _Time, '12:34Z', dt.time(12, 34), '12:34:00')
        self.assertEqual(obj.type_, 'utc_time')

        _pass(self, _Time, '"12:34:56"', dt.time(12, 34, 56))
        _pass(self, _Time, '"12:34:56.5"', dt.time(12, 34, 56, 500000),
              strval='12:34:56.500')
        _pass(self, _Time, '"12:34:56.12345678"', dt.time(12, 34, 56, 123457),
              strval='12:34:56.123457')

        obj = _pass(self, _Time, '12:34+2:30', dt.time(12, 34, tzinfo=tz(2*60 + 30)),
                    '12:34:00+02:30', dt.time, test=2)
        self.assertEqual(obj.type_, 'zoned_time')
        self.assertEqual(obj.sec, 3600*12 + 34*60 - 3600*2 - 30*60)
        self.assertEqual(obj.fmt, '12:34:00+02:30')
        self.assertEqual(str(obj), '12:34:00+02:30')
        self.assertEqual(repr(obj), '_ZonedTime(12:34:00+02:30)')

        _fail(self, _Time, '12:34 +2:30', test=1)
        _fail(self, _Time, '12:34 +02:30', test=1)


class Test_Date(unittest.TestCase):

    def runTest(self):

        obj = _pass(self, _Date, '2000-01-01', dt.date(2000, 1, 1))
        self.assertEqual(obj.type_, 'date')
        self.assertEqual(obj.day, 0)
        self.assertEqual(str(obj), '2000-01-01')
        self.assertEqual(repr(obj), '_Date(2000-01-01)')

        obj = _pass(self, _Date, '2000-003', dt.date(2000, 1, 3))
        self.assertEqual(obj.type_, 'date')
        self.assertEqual(obj.day, 2)
        self.assertEqual(str(obj), '2000-003')
        self.assertEqual(repr(obj), '_Date(2000-003)')

        _pass(self, _Date, '2000-12-01', dt.date(2000, 12, 1))
        _pass(self, _Date, '2000-12-31', dt.date(2000, 12, 31))

        _fail(self, _Date, '3000-01-01')
        _fail(self, _Date, '2000-00-01')
        _fail(self, _Date, '2000-13-01')
        _fail(self, _Date, '2000-01-00')
        _fail(self, _Date, '2000-01-32')


class Test_DateTime(unittest.TestCase):

    def runTest(self):

        obj = _pass(self, _DateTime, '2000-01-03T12:34', dt.datetime(2000, 1, 3, 12, 34),
                    '2000-01-03T12:34:00', test=1)
        self.assertEqual(obj.type_, 'date_time')
        self.assertEqual(obj.day, 2)
        self.assertEqual(obj.sec, 60 * (34 + 60 * 12))
        self.assertEqual(str(obj), '2000-01-03T12:34:00')
        self.assertEqual(repr(obj), '_DateTime(2000-01-03T12:34:00)')

        obj = _pass(self, _DateTime, '2000-003T12:34Z', dt.datetime(2000, 1, 3, 12, 34),
                    '2000-003T12:34:00', test=1)
        self.assertEqual(obj.day, 2)
        self.assertEqual(obj.sec, 60 * (34 + 60 * 12))
        self.assertEqual(str(obj), '2000-003T12:34:00')
        self.assertEqual(repr(obj), '_DateTime(2000-003T12:34:00)')

        obj = _pass(self, _DateTime, '2000-01-01T01:23+4', dt.datetime(2000, 1, 1, 1, 23,
                                                                       tzinfo=tz(4*60)),
                    '2000-01-01T01:23:00+04:00', test=2)
        self.assertEqual(obj.day, -1)
        self.assertEqual(obj.sec, 60 * (23 + 60) - 4 * 3600 + 86400)
        self.assertEqual(str(obj), '2000-01-01T01:23:00+04:00')
        self.assertEqual(repr(obj), '_DateTime(2000-01-01T01:23:00+04:00)')

        _pass(self, _DateTime, '2000-01-01T12:34Z', dt.datetime(2000, 1, 1, 12, 34),
              '2000-01-01T12:34:00')
        _pass(self, _DateTime, '2000-01-01T12:34:56Z',
              dt.datetime(2000, 1, 1, 12, 34, 56), '2000-01-01T12:34:56')
        _pass(self, _DateTime, '2000-01-01T01:23+4', dt.datetime(2000, 1, 1, 1, 23,
                                                                 tzinfo=tz(4*60)),
              '2000-01-01T01:23:00+04:00', test=2)
        _pass(self, _DateTime, '2000-01-01T12:34:56+7:08',
              dt.datetime(2000, 1, 1, 12, 34, 56, tzinfo=tz(7*60+8)),
              '2000-01-01T12:34:56+07:08', test=2)

        _pass(self, _DateTime, '2004-366T04:38:16.12345678Z',
              dt.datetime(2004, 12, 31, 4, 38, 16, 123457),
              '2004-366T04:38:16.123457')

        _fail(self, _DateTime, '2000-01-01 T12:34')
        _fail(self, _DateTime, '2000-01-01T 12:34')
        _fail(self, _DateTime, '2000-01-01T12:34 Z')

        _fail(self, _DateTime, '2000-01-01T01:23+4', test=1)
        _fail(self, _DateTime, '2000-01-01T12:34:56+7:08', test=1)


class Test_Text(unittest.TestCase):

    def runTest(self):

        obj = _pass(self, _Text, 'ABC', 'ABC', 'ABC')
        self.assertEqual(obj.type_, 'identifier')
        self.assertEqual(str(obj), obj.value)
        self.assertEqual(repr(obj), '_Text(ABC)')
        self.assertEqual(obj, 'ABC')

        obj = _pass(self, _Text, '"abc"', 'abc', '"abc"')
        self.assertEqual(obj.type_, 'quoted_text')
        self.assertEqual(str(obj), '"abc"')
        self.assertEqual(repr(obj), '_Text("abc")')
        self.assertEqual(obj, 'abc')

        obj = _pass(self, _Text, 'abc', 'abc', '"abc"', test=2)
        self.assertEqual(obj.type_, 'identifier')
        self.assertEqual(repr(obj), '_Text("abc")')
        self.assertEqual(obj, 'abc')

        obj = _pass(self, _Text, "'N/A'", 'N/A')
        self.assertEqual(obj.type_, 'quoted_symbol')
        self.assertEqual(repr(obj), "_Text('N/A')")
        self.assertEqual(obj, 'N/A')

        obj = _pass(self, _Text, '"Multiline\ntext"', 'Multiline\ntext')
        self.assertEqual(repr(obj), '_Text("Multiline\ntext")')
        self.assertEqual(obj, 'Multiline\ntext')
        self.assertEqual(obj.source, '"Multiline\ntext"')
        self.assertEqual(obj.unwrap, 'Multiline text')

        _pass(self, _Text, '"abc def"', 'abc def', '"abc def"')
        _pass(self, _Text, '""', '')
        _pass(self, _Text, '"   "', '')
        _pass(self, _Text, "'N/A'", 'N/A')
        _pass(self, _Text, 'N/A', 'N/A', "'N/A'", test=2)

        _fail(self, _Text, 'abc def')
        _fail(self, _Text, 'abc', test=1)
        _fail(self, _Text, 'N/A', test=1)


class Test_Set(unittest.TestCase):

    def runTest(self):

        obj = _pass(self, _Set, '{1, 2, \n3}', {1, 2, 3}, '{1, 2, 3}', set)
        self.assertEqual(obj.type_, 'set')
        self.assertEqual(str(obj), '{1, 2, 3}')
        self.assertEqual(repr(obj), '_Set(1, 2, 3)')
        self.assertEqual(obj, {1, 2, 3, 2})
        self.assertEqual(obj.list, [1, 2, 3])

        _pass(self, _Set, '{1, 2\n,3}', {1, 2, 3}, '{1, 2, 3}')
        _pass(self, _Set, '{1, 2.0, "three"}', {1, 2.0, "three"}, '{1, 2., "three"}')
        _pass(self, _Set, '{1, 2.0, THREE}', {1, 2.0, "THREE"}, '{1, 2., "THREE"}')
        _pass(self, _Set, '{1, 2.0, three}', {1, 2.0, "three"}, '{1, 2., "three"}',
              test=2)
        _pass(self, _Set, '{1, 2.0, N/A}', {1, 2.0, "N/A"}, "{1, 2., 'N/A'}",
              test=2)

        obj = _pass(self, _Set, '{1, 2<km>}', {1, (2, '<km>')}, '{1, 2 <km>}')
        self.assertIn((2, '<km>'), obj.full_value)
        self.assertNotIn(2, obj.full_value)
        self.assertEqual(type(obj[0]), _Integer)
        self.assertEqual(obj[0].value, 1)
        self.assertEqual(type(obj[1]), _NumberWithUnit)
        self.assertEqual(obj[0].value, 1)

        obj = _pass(self, _Set, '{1<km>, 2<km>}', {1, 2}, '{1 <km>, 2 <km>}')
        self.assertEqual(type(obj[0]), _NumberWithUnit)
        self.assertEqual(type(obj[1]), _NumberWithUnit)
        self.assertEqual(type(obj[0].value), int)
        self.assertEqual(type(obj[1].value), int)
        self.assertEqual(obj.unit, '<km>')
        self.assertEqual(type(obj[0]), _NumberWithUnit)

        obj = _pass(self, _Set, '{1, "abc", \'def\', GHI}', {1, "abc", "def", "GHI"},
                    '{1, "abc", \'def\', "GHI"}')
        self.assertEqual(type(obj[1]), _Text)
        self.assertEqual(obj[1].value, 'abc')
        self.assertEqual(obj[1].quote, '"')
        self.assertEqual(type(obj[2]), _Text)
        self.assertEqual(obj[2].value, 'def')
        self.assertEqual(obj[2].quote, "'")
        self.assertEqual(type(obj[3]), _Text)
        self.assertEqual(obj[3].value, 'GHI')
        self.assertEqual(obj[3].quote, '')
        self.assertEqual(obj.quote, '"')

        obj = _pass(self, _Set, '{1, \'def\', GHI}', {1, "def", "GHI"},
                    '{1, \'def\', "GHI"}')
        self.assertEqual(obj[1].quote, "'")
        self.assertEqual(obj[2].quote, '')
        self.assertEqual(obj.quote, "'")

        obj = _pass(self, _Set, '{1, GHI}', {1, "GHI"}, '{1, "GHI"}')
        self.assertEqual(obj[1].quote, '')
        self.assertEqual(obj.quote, '')

        _fail(self, _Set, '{1, (2, 3)}')
        _fail(self, _Set, '{1, {2, 3}}')
        _fail(self, _Set, '{1, 2.0, three}', test=1)
        _fail(self, _Set, '{1, 2.0, N/A}', test=1)


class Test_Sequence(unittest.TestCase):

    def runTest(self):

        obj = _pass(self, _Sequence, '(1, 2, \n3)', [1, 2, 3], '(1, 2, 3)', list)
        self.assertEqual(obj.type_, 'sequence_1D')
        self.assertEqual(str(obj), '(1, 2, 3)')
        self.assertEqual(repr(obj), '_Sequence(1, 2, 3)')
        self.assertEqual(obj, [1, 2, 3])

        _pass(self, _Sequence, '(1, 2\n,3)', [1, 2, 3], '(1, 2, 3)')
        _pass(self, _Sequence, '(1, 2.0, "three")', [1, 2.0, "three"], '(1, 2., "three")')
        _pass(self, _Sequence, '(1, 2.0, THREE)', [1, 2.0, "THREE"], '(1, 2., "THREE")')
        _pass(self, _Sequence, '(1, 2.0, three)', [1, 2.0, "three"], '(1, 2., "three")',
              test=2)
        _pass(self, _Sequence, '(1, 2.0, N/A)', [1, 2.0, "N/A"], "(1, 2., 'N/A')",
              test=2)

        obj = _pass(self, _Sequence, '(1, 2<km>)', [1, 2], '(1, 2 <km>)', list)
        self.assertEqual(obj[0].full_value, 1)
        self.assertEqual(obj[1].full_value, (2, '<km>'))
        self.assertEqual(type(obj[0].value), int)
        self.assertEqual(type(obj[1].value), int)
        self.assertEqual(obj.unit, [None, '<km>'])
        self.assertEqual(type(obj.unit), list)
        self.assertEqual(obj.all_units, [None, '<km>'])

        obj = _pass(self, _Sequence, '(1 <km>, 2.<km>)', [1, 2.], '(1 <km>, 2. <km>)',
                    list)
        self.assertEqual(obj[0].full_value, (1, '<km>'))
        self.assertEqual(obj[1].full_value, (2., '<km>'))
        self.assertEqual(type(obj[0].full_value[0]), int)
        self.assertEqual(type(obj[1].full_value[0]), float)
        self.assertEqual(type(obj[0].value), int)
        self.assertEqual(type(obj[1].value), float)
        self.assertEqual(obj.unit, '<km>')
        self.assertEqual(obj.all_units, ['<km>', '<km>'])

        self.assertEqual(repr(obj), '_Sequence(1 <km>, 2. <km>)')
        self.assertEqual(obj, [1, 2])

        _fail(self, _Sequence, '(1, (2, 3))')
        _fail(self, _Sequence, '(1, {2, 3})')
        _fail(self, _Set, '(1, 2.0, three)', test=1)
        _fail(self, _Sequence, '(1, 2.0, N/A)', test=1)

class Test_Sequence2D(unittest.TestCase):

    def runTest(self):

        obj = _pass(self, _Sequence2D, '((1, 2, 3))', [[1, 2, 3]], '((1, 2, 3))', list)
        self.assertEqual(obj[0].value, [1, 2, 3])
        self.assertEqual(type(obj[0].value), list)

        obj = _pass(self, _Sequence2D, '((1, 2, 3), (4,5))', [[1, 2, 3], [4, 5]],
                    '((1, 2, 3), (4, 5))', list)
        self.assertEqual(obj[0].value, [1, 2, 3])
        self.assertEqual(obj[1].value, [4, 5])
        self.assertEqual(obj[0].full_value, [1, 2, 3])
        self.assertEqual(obj[1].full_value, [4, 5])
        self.assertEqual(obj[0][0].full_value, 1)
        self.assertEqual(obj[1][1].full_value, 5)
        self.assertEqual(obj.unit, None)
        self.assertEqual(obj.all_units, [[None, None, None], [None, None]])

        obj = _pass(self, _Sequence2D, '((1, 2, 3), (4,5 <km>))', [[1, 2, 3], [4, 5]],
                    '((1, 2, 3), (4, 5 <km>))', list)
        self.assertEqual(obj[0].value, [1, 2, 3])
        self.assertEqual(obj[1].value, [4, 5])
        self.assertEqual(obj[0].full_value, [1, 2, 3])
        self.assertEqual(obj[1].full_value, [4, (5, '<km>')])
        self.assertEqual(obj[0][0].full_value, 1)
        self.assertEqual(obj[1][1].full_value, (5, '<km>'))
        self.assertEqual(obj.unit, [[None, None, None], [None, '<km>']])
        self.assertEqual(obj.all_units, [[None, None, None], [None, '<km>']])
        self.assertEqual(type(obj[1][1]), _NumberWithUnit)
        self.assertEqual(type(obj[1][1].value), int)

        _pass(self, _Sequence2D, '(\n(\n\t1, 2\n,3\t))', [[1, 2, 3]], '((1, 2, 3))')
        _pass(self, _Sequence2D, '((1, 2.0, "three"))', [[1, 2.0, "three"]],
              '((1, 2., "three"))')
        _pass(self, _Sequence2D, '((1, 2.0, three))', [[1, 2.0, "three"]],
              '((1, 2., "three"))', test=2)

        obj = _pass(self, _Sequence2D, '((1, 2<km>))', [[1, 2]], '((1, 2 <km>))')
        self.assertEqual(obj[0][0].full_value, 1)
        self.assertEqual(obj[0][1].full_value, (2., '<km>'))
        self.assertEqual(obj[0][1].unit, '<km>')
        self.assertEqual(obj.unit, [[None, '<km>']])
        self.assertEqual(obj.all_units, [[None, '<km>']])

        _pass(self, _Sequence2D, '((1,2)\n(3,4))', [[1, 2], [3, 4]], test=2)

        _fail(self, _Sequence2D, '((1, (2, 3)))')
        _fail(self, _Sequence2D, '((1, {2, 3}))')
        _fail(self, _Sequence2D, '((1,2)\n(3,4))', test=1)
        _fail(self, _Sequence2D, '((1, 2.0, three))', test=1)
        _fail(self, _Sequence2D, '((1, 2.0, N/A))', test=1)


class Test_SimplePointer(unittest.TestCase):

    def runTest(self):

        _pass(self, _SimplePointer, '"DOCUMENT.PDF"', 'DOCUMENT.PDF', '"DOCUMENT.PDF"')
        _pass(self, _SimplePointer, '"DOC.TXT.PDF"', 'DOC.TXT.PDF', '"DOC.TXT.PDF"')
        _pass(self, _SimplePointer, '"DIR/DOC.TXT.PDF"', 'DIR/DOC.TXT.PDF',
              '"DIR/DOC.TXT.PDF"', test=2)

        _fail(self, _SimplePointer, '"DIR/DOC.TXT.PDF"', test=1)


class Test_LocalPointer(unittest.TestCase):

    def runTest(self):

        _pass(self, _LocalPointer, '123', 123, '123', int)
        _pass(self, _LocalPointer, '123\t<BYTES>', 123, '123 <BYTES>', int)
        obj = _pass(self, _LocalPointer, '123<bytes>', 123, '123 <BYTES>', int)
        self.assertEqual(obj.full_value, (123, '<BYTES>'))


class Test_OffsetPointer(unittest.TestCase):

    def runTest(self):

        obj = _pass(self, _OffsetPointer, '("TABLE.TAB", 2)', "TABLE.TAB",
                    '("TABLE.TAB", 2)')
        self.assertEqual(obj.full_value, ("TABLE.TAB", 2))
        self.assertEqual(obj.offset, 2)
        self.assertIsInstance(obj.offset, int)
        self.assertEqual(obj.unit, '')

        obj = _pass(self, _OffsetPointer, '("TABLE.TAB", 800 <bytes>)',
                    "TABLE.TAB", '("TABLE.TAB", 800 <BYTES>)')
        self.assertEqual(obj.full_value, ("TABLE.TAB", 800, '<BYTES>'))
        self.assertEqual(obj.offset, 800)
        self.assertIsInstance(obj.offset, int)
        self.assertEqual(obj.unit, '<BYTES>')

        _pass(self, _OffsetPointer, '("DIR/TABLE.TAB", 2)', "DIR/TABLE.TAB",
              '("DIR/TABLE.TAB", 2)', test=2)
        _pass(self, _OffsetPointer, '("DIR/TABLE.TAB", 800 <bytes>)', "DIR/TABLE.TAB",
              '("DIR/TABLE.TAB", 800 <BYTES>)', test=2)

        _fail(self, _OffsetPointer, '("DIR/TABLE.TAB", 2)', test=1)
        _fail(self, _OffsetPointer, '("DIR/TABLE.TAB", 800 <bytes>)', test=1)


class Test_SetPointer(unittest.TestCase):

    def runTest(self):

        _pass(self, _SetPointer, '{"1.GIF", "2.GIF", "3.GIF"}',
              {"1.GIF", "2.GIF", "3.GIF"}, '{"1.GIF", "2.GIF", "3.GIF"}')
        _pass(self, _SetPointer, '{"1.GIF", "2.GIF", "2.GIF", "3.GIF"}',
              {"1.GIF", "2.GIF", "3.GIF"}, '{"1.GIF", "2.GIF", "3.GIF"}')
        _pass(self, _SetPointer, '{"A/1.GIF", "A/2.GIF", "A/3.GIF"}',
              {"A/1.GIF", "A/2.GIF", "A/3.GIF"}, '{"A/1.GIF", "A/2.GIF", "A/3.GIF"}',
              test=2)

        _fail(self, _SetPointer, '{"A/1.GIF", "A/2.GIF", "A/3.GIF"}', test=1)


class Test_SequencePointer(unittest.TestCase):

    def runTest(self):

        _pass(self, _SequencePointer, '("1.GIF", "2.GIF", "3.GIF")',
              ["1.GIF", "2.GIF", "3.GIF"], '("1.GIF", "2.GIF", "3.GIF")', list)
        _pass(self, _SequencePointer, '("A/1.GIF", "A/2.GIF", "A/3.GIF")',
              ["A/1.GIF", "A/2.GIF", "A/3.GIF"], '("A/1.GIF", "A/2.GIF", "A/3.GIF")',
              test=2)

        _fail(self, _SequencePointer, '("A/1.GIF", "A/2.GIF", "A/3.GIF")', test=1)


class Test_AttributeID(unittest.TestCase):

    def runTest(self):

        _pass(self, _AttributeID, 'OBJECT', 'OBJECT', 'OBJECT')
        _pass(self, _AttributeID, 'OBJECT_2', 'OBJECT_2', 'OBJECT_2')
        _pass(self, _AttributeID, 'N123', 'N123', 'N123')
        _pass(self, _AttributeID, 'N123:X456', 'N123:X456', 'N123:X456')

        _fail(self, _AttributeID, 'NAME_')
        _fail(self, _AttributeID, 'NAME_:MORE')
        _fail(self, _AttributeID, '_NAME')
        _fail(self, _AttributeID, '1NAME')
        _fail(self, _AttributeID, 'Name')
        _fail(self, _AttributeID, 'AAA:BBB:C')


class Test_PointerID(unittest.TestCase):

    def runTest(self):

        _pass(self, _PointerID, '^OBJECT', '^OBJECT', '^OBJECT')
        _pass(self, _PointerID, '^OBJECT_2', '^OBJECT_2', '^OBJECT_2')
        _pass(self, _PointerID, '^N123', '^N123', '^N123')
        _pass(self, _PointerID, '^N123:X456', '^N123:X456', '^N123:X456')

        _fail(self, _PointerID, '^NAME_')
        _fail(self, _PointerID, '^NAME_:MORE')
        _fail(self, _PointerID, '^_NAME')
        _fail(self, _PointerID, '^1NAME')
        _fail(self, _PointerID, '^Name')
        _fail(self, _PointerID, '^AAA:BBB:C')


class Test_Statement(unittest.TestCase):

    def runTest(self):

        _pass(self, _Statement, 'OBJECT\t   = COLUMN\n', ('OBJECT', 'COLUMN'),
              'OBJECT = COLUMN')
        _pass(self, _Statement, 'OBJECT\t   = COLUMN\n   \n\t\r\t\n',
              ('OBJECT', 'COLUMN'), 'OBJECT = COLUMN')
        _pass(self, _Statement, '^CASSINI:INDEX  = ("index.tab", 800 <bytes>)\n',
              ('^CASSINI:INDEX', ("index.tab", 800, '<BYTES>')),
              '^CASSINI:INDEX = ("index.tab", 800 <BYTES>)')
        _pass(self, _Statement, 'END_OBJECT\n', ('END_OBJECT', None), 'END_OBJECT',
              test=2)

        _fail(self, _Statement, 'END_OBJECT\n', test=1)


class Test_EndStatement(unittest.TestCase):

    def runTest(self):

        _pass(self, _EndStatement, 'END  \t\r\n', ('END', None), 'END')


##########################################################################################
