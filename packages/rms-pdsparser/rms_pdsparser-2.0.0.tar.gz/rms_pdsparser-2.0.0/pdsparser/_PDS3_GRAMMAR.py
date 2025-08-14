##########################################################################################
# pdsparser/_PDS3_GRAMMAR.py
##########################################################################################
"""Definition of the pyparsing grammars _LABEL and _ALT_LABEL."""

import datetime as dt
from pyparsing import (alphanums, alphas, CharsNotIn, Combine, hexnums, Literal, nums,
                       one_of, OneOrMore, Optional, ParserElement, StringEnd, Suppress,
                       Word, ZeroOrMore)

try:
    from ._version import __version__
except ImportError:     # pragma: no cover
    __version__ = 'Version unspecified'

from .utils import _based_int, _format_float, _is_identifier, _unwrap

ParserElement.set_default_whitespace_chars('')
_WHITE = Suppress(Optional(Word(' \t')))
_COMMENT = Literal('/*') + CharsNotIn('\r\n')
_EOL = Suppress(OneOrMore(_WHITE + Optional(_COMMENT) + Word('\r\n')))
_SKIP = Suppress(ZeroOrMore(_COMMENT | Word(' \t\r\n')))
_EQUAL = _WHITE + Suppress('=') + _SKIP
_WHITE = Suppress(Optional(Word(' \t\r\n')))

_caps = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
_middle = _caps + nums
_KEYWORD = Combine(Word(_caps, _middle) + ZeroOrMore(Literal('_') + Word(_middle)))

##########################################################################################
# _Item
##########################################################################################

class _Item():
    """Abstract class for any part of a PDS3 label."""

    # Attribute names to be added to dictionary along with `value`
    suffixes = ()

    @property
    def source(self):
        return str(self)

    @property
    def full_value(self):
        return self.value

    def __repr__(self):
        strval = str(self)
        if strval.startswith('('):
            return type(self).__name__ + str(self)
        return type(self).__name__ + '(' + str(self) + ')'

    def __eq__(self, other):
        if isinstance(other, _Value):
            return type(self) is type(other) and self.value == other.value
        return self.value == other

    def quote_if_text(self):
        """Put quotes around all string values; overridden by _Text."""
        return str(self)

    def wrap(self):
        """Remove newlines and extra whitespace if _Text."""
        return self

##########################################################################################
# _Value
##########################################################################################

class _Value(_Item):
    """Abstract class for anything that can appear on the right side of an equal sign in a
    PDS3 label.
    """

    def __str__(self):      # pragma: no cover (always overridden)
        return str(self.value)

class _Scalar(_Value):
    """Abstract class for any single value that can appear on the right side of an equal
    sign in a PDS3 label.
    """
    pass

class _Number(_Scalar):
    """Abstract class for any single numeric value that can appear on the right side of an
    equal sign in a PDS3 label.
    """
    pass

##########################################################################################
# _Integer
##########################################################################################
_SIGN = one_of('+ -')
_UNSIGNED_INT = Word(nums)
_SIGNED_INT = Combine(Optional(_SIGN) + _UNSIGNED_INT)
_INTEGER = Combine(Optional(_SIGN) + _UNSIGNED_INT)
_INTEGER.set_name('_INTEGER')

class _Integer(_Number):
    """An integer value."""

    type_ = 'integer'
    grammar = _INTEGER

    def __init__(self, s, loc, tokens):
        self.tokens = tokens
        self.value = int(tokens[0])
        self.unit = None

    def __str__(self):
        return str(self.value)

_INTEGER.set_parse_action(_Integer)

##########################################################################################
# _BasedInteger
##########################################################################################
_BINARY_INT = Literal('2') + Suppress('#') + Word('01') + Suppress('#')
_OCTAL_INT = Literal('8') + Suppress('#') + Word('01234567') + Suppress('#')
_HEX_INT = Literal('16') + Suppress('#') + Word(hexnums) + Suppress('#')

_BASED_INT = _BINARY_INT | _OCTAL_INT | _HEX_INT
_BASED_INT.set_name('_BASED_INT')

class _BasedInteger(_Number):
    """An integer value in an alternative radix 2-16."""

    type_ = 'based_integer'
    grammar = _BASED_INT
    suffixes = ('radix', 'digits', 'fmt')

    def __init__(self, s, loc, tokens):
        self.tokens = tokens
        self.radix = int(tokens[0])
        self.digits = tokens[1]
        self.unit = None
        self.value = _based_int(self.radix, self.digits)
        self.fmt = str(self)

    def __str__(self):
        return str(self.radix) + '#' + self.digits + '#'

_BASED_INT.set_parse_action(_BasedInteger)

##########################################################################################
# _Real
##########################################################################################
_EXPONENT = (one_of('e E') + Optional(_SIGN) + Word(nums, max=3))
_REAL_WITH_INT = Combine(_SIGNED_INT + '.' + Optional(_UNSIGNED_INT)
                         + Optional(_EXPONENT))
_REAL_WO_INT = Combine(Optional(_SIGN) + '.' + _UNSIGNED_INT + Optional(_EXPONENT))
_REAL_WO_DOT = Combine(_SIGNED_INT + _EXPONENT)
_REAL_NUMBER = _REAL_WITH_INT | _REAL_WO_INT | _REAL_WO_DOT
_REAL_NUMBER.set_name('REAL')

class _Real(_Number):
    """A floating-point number."""

    type_ = 'real'
    grammar = _REAL_NUMBER

    def __init__(self, s, loc, tokens):
        self.tokens = tokens
        self.value = float(tokens[0])
        self.unit = None

    @property
    def source(self):
        return self.tokens[0]

    def __str__(self):
        return _format_float(self.value)

_REAL_NUMBER.set_parse_action(_Real)

##########################################################################################
# _NumberWithUnit
##########################################################################################
_UNIT_EXPR = Combine(Suppress('<') + OneOrMore(CharsNotIn('\n\r\t>')) + Suppress('>'))
_NUMBER_W_UNIT = (_REAL_NUMBER | _INTEGER) + Optional(_WHITE) + _UNIT_EXPR
_NUMBER_W_UNIT.set_name('_NUMBER_W_UNIT')

class _NumberWithUnit(_Number):
    """A number with units."""

    grammar = _NUMBER_W_UNIT
    suffixes = ('unit',)

    def __init__(self, s, loc, tokens):
        self.tokens = tokens
        self.value = tokens[0].value
        self.type_ = tokens[0].type_
        self.unit = '<' + tokens[1].strip() + '>'

    @property
    def source(self):
        return self.tokens[0].source + ' ' + self.unit

    @property
    def full_value(self):
        return (self.value, self.unit)

    def __str__(self):
        return str(self.tokens[0]) + ' ' + self.unit

    def __eq__(self, other):
        if isinstance(other, _Item):
            return (type(self) is type(other) and self.value == other.value
                    and self.unit == other.unit)
        return self.value == other

_NUMBER_W_UNIT.set_parse_action(_NumberWithUnit)

_NUMBER = _NUMBER_W_UNIT | _REAL_NUMBER | _BASED_INT | _INTEGER     # order matters here!
_Number.grammar = _NUMBER

##########################################################################################
# _Time: value is a string representation of the time
##########################################################################################

class _Time(_Scalar):
    pass

##########################################################################################
# _HmsTime (does not support leap seconds, because datetime module also doesn't)
##########################################################################################
_ZERO_23 = Word('01', nums, exact=2) | Word('2', '0123', exact=2)
_ZERO_59 = Word('012345', nums, exact=2)
_HMS_TIME0 = (_ZERO_23 + Suppress(':') + _ZERO_59
              + Optional(Suppress(':')
                         + Combine(_ZERO_59 + Optional('.' + Optional(_UNSIGNED_INT)))))
_HMS_TIME1 = _HMS_TIME0.copy()
_HMS_TIME = _HMS_TIME0 | (Suppress('"') + _HMS_TIME0 + Suppress('"'))
_HMS_TIME.set_name('_HMS_TIME')

_UTC_TIME0 = (_ZERO_23 + Suppress(':') + _ZERO_59
              + Optional(Suppress(':')
                         + Combine(_ZERO_59 + Optional('.' + Optional(_UNSIGNED_INT))))
              + Suppress(Literal('Z')))
_UTC_TIME1 = _UTC_TIME0.copy()
_UTC_TIME = _UTC_TIME0 | (Suppress('"') + _UTC_TIME0 + Suppress('"'))
_UTC_TIME.set_name('_UTC_TIME')

class _SimpleTime(_Time):
    """Time without time zone, with optional "Z"."""

    suffixes = ('sec', 'fmt')

    def __init__(self, s, loc, tokens):
        self.tokens = tokens
        self.z = ''
        hour = int(tokens[0])
        minute = int(tokens[1])
        if len(tokens) > 2:
            second = float(tokens[2]) if '.' in tokens[2] else int(tokens[2])
        else:
            second = 0
        self.is_float = isinstance(second, float)

        if isinstance(second, int):
            isec = second
            microsec = 0
        else:
            isec = int(second // 1.)
            microsec = int((second - isec) * 1000000 + 0.499999)

        self.value = dt.time(hour, minute, isec, microsec)
        self.sec = second + 60 * (minute + 60 * hour)
        self.fmt = str(self)

    @property
    def source(self):
        return ':'.join(self.tokens) + self.z

    def __str__(self):
        microsec = self.value.microsecond
        result = self.value.isoformat()
        if microsec:
            if microsec % 1000 == 0:   # use msec if it's exact
                result = result[:-3]
        elif self.is_float:
            result += '.000'

        return result

class _HmsTime(_SimpleTime):
    """A time of day, excluding a time zone."""

    type_ = 'local_time'
    grammar = _HMS_TIME

    def __init__(self, s, loc, tokens):
        _SimpleTime.__init__(self, s, loc, tokens)
        self.z = ''

class _UtcTime(_SimpleTime):
    """A time of day with "Z" suffix."""

    type_ = 'utc_time'
    grammar = _UTC_TIME

    def __init__(self, s, loc, tokens):
        _SimpleTime.__init__(self, s, loc, tokens)
        self.z = 'Z'

_HMS_TIME.set_parse_action(_HmsTime)
_UTC_TIME.set_parse_action(_UtcTime)

_HMS_TIME1.set_parse_action(_HmsTime)   # parse action applied but no quotes allowed
_UTC_TIME1.set_parse_action(_UtcTime)

##########################################################################################
# _TimeZone
##########################################################################################
_ALT_ZERO_23 = _ZERO_23 | Word(nums, max=1)
_TIME_ZONE = Combine(_SIGN + _ALT_ZERO_23) + Optional(Suppress(':') + _ZERO_59)
_TIME_ZONE.set_name('_TIME_ZONE')

class _TimeZone(_Item):
    """A time zone."""

    type_ = 'time_zone'
    grammar = _TIME_ZONE
    suffixes = ('sec', 'fmt')

    def __init__(self, s, loc, tokens):
        self.tokens = tokens
        sign = -1 if tokens[0][0] == '-' else 1
        hours = int(tokens[0])
        minutes = 60 * hours + sign * (int(tokens[1]) if len(tokens) > 1 else 0)

        self.sec = 60 * minutes
        self.value = dt.timezone(dt.timedelta(seconds=self.sec))
        self.fmt = str(self)

    @property
    def source(self):
        return ':'.join(self.tokens)

    def __str__(self):
        if len(self.tokens) == 1:
            return '%+03d:00' % int(self.tokens[0])
        else:
            sign = self.tokens[0][0]
            hours = abs(int(self.tokens[0]))
            return sign + '%02d' % hours + ':' + self.tokens[1]

_TIME_ZONE.set_parse_action(_TimeZone)

##########################################################################################
# _ZonedTime
##########################################################################################
_ZONED_TIME0 = _HMS_TIME1 + _TIME_ZONE
_ZONED_TIME = _ZONED_TIME0 | (Suppress('"') + _ZONED_TIME0 + Suppress('"'))
_ZONED_TIME.set_name('_ZONED_TIME')

class _ZonedTime(_Time):
    """A time of day with a time zone."""

    type_ = 'zoned_time'
    alt_grammar = _ZONED_TIME
    suffixes = ('sec', 'fmt')

    def __init__(self, s, loc, tokens):
        self.tokens = tokens
        self.hms_time = tokens[0]
        self.time_zone = tokens[1]
        time = self.hms_time.value
        tz = self.time_zone.value
        self.value = dt.time(time.hour, time.minute, time.second, time.microsecond, tz)
        self.sec = self.hms_time.sec - self.time_zone.sec
        self.fmt = str(self)

    @property
    def source(self):
        return self.hms_time.source + self.time_zone.source

    def __str__(self):
        return str(self.hms_time) + str(self.time_zone)

_ZONED_TIME.set_parse_action(_ZonedTime)

_TIME = _UTC_TIME | _HMS_TIME
_TIME.set_name('_TIME')
_Time.grammar = _TIME

_ALT_TIME = _ZONED_TIME | _UTC_TIME | _HMS_TIME
_ALT_TIME.set_name('_ALT_TIME')
_Time.alt_grammar = _ALT_TIME

_TIME1 = _UTC_TIME1 | _HMS_TIME1    # parse action applied but no quotes allowed
_ALT_TIME1 = _ZONED_TIME | _UTC_TIME1 | _HMS_TIME1

##########################################################################################
# _Date
##########################################################################################
_YEAR = Word('12', nums, exact=4)
_MONTH = Word('0', '123456789', exact=2) | Word('1', '012', exact=2)
_DAY = (Word('0', '123456789', exact=2) | Word('12', nums, exact=2)
        | Word('3', '01', exact=2))
_DOY = (Word('0123', nums, exact=3))
_YMD_DATE = _YEAR + Suppress('-') + _MONTH + Suppress('-') + _DAY
_YD_DATE = _YEAR + Suppress('-') + _DOY
_DATE0 = _YMD_DATE | _YD_DATE
_DATE1 = _DATE0.copy()

_DATE = _DATE0 | (Suppress('"') + _DATE0 + Suppress('"'))
_DATE.set_name('_DATE')

class _Date(_Scalar):
    """A date as year, month and day or year and day-of-year."""

    type_ = 'date'
    grammar = _DATE
    suffixes = ('day', 'fmt')

    def __init__(self, s, loc, tokens):
        self.tokens = tokens
        year = int(tokens[0])
        if len(tokens) == 3:
            self.value = dt.date(year, int(tokens[1]), int(tokens[2]))
        else:
            self.value = dt.date(year, 1, 1) + dt.timedelta(int(tokens[1]) - 1)
        self.day = (self.value - dt.date(2000, 1, 1)).days
        self.fmt = str(self)

    def __str__(self):
        return '-'.join(self.tokens)

_DATE.set_parse_action(_Date)
_DATE1.set_parse_action(_Date)  # parse action applied but no quotes allowed

##########################################################################################
# _DateTime
##########################################################################################
_DATE_TIME0 = _DATE1 + Suppress('T') + _TIME1
_DATE_TIME = _DATE_TIME0 | (Suppress('"') + _DATE_TIME0 + Suppress('"'))
_DATE_TIME.set_name('_DATE_TIME')

_ALT_DATE_TIME0 = _DATE1 + Suppress('T') + _ALT_TIME1
_ALT_DATE_TIME = _ALT_DATE_TIME0 | (Suppress('"') + _ALT_DATE_TIME0 + Suppress('"'))
_ALT_DATE_TIME.set_name('_ALT_DATE_TIME')

class _DateTime(_Scalar):

    type_ = 'date_time'
    grammar = _DATE_TIME
    alt_grammar = _ALT_DATE_TIME
    suffixes = ('day', 'sec', 'fmt')

    def __init__(self, s, loc, tokens):
        self.date = tokens[0]
        self.time = tokens[1]
        date = self.date.value
        time = self.time.value
        self.value = dt.datetime(date.year, date.month, date.day, time.hour,
                                 time.minute, time.second, time.microsecond,
                                 tzinfo=time.tzinfo)
        self.day = self.date.day
        self.sec = self.time.sec
        shift = int(self.sec // 86400)
        self.day += shift
        self.sec -= 86400 * shift
        self.fmt = str(self)

    @property
    def source(self):
        return self.date.source + 'T' + self.time.source

    def __str__(self):
        return str(self.date) + 'T' + str(self.time)

_DATE_TIME.set_parse_action(_DateTime)
_ALT_DATE_TIME.set_parse_action(_DateTime)

##########################################################################################
# _Text
##########################################################################################
_EMPTY_TEXT = Combine('""')
_NON_EMPTY_TEXT = Suppress('"') + Combine(CharsNotIn('"')) + Literal('"')
_QUOTED_SYMBOL = Suppress("'") + Combine(CharsNotIn("'\n")) + Literal("'")
_IDENTIFIER = _KEYWORD
_TEXT_VALUE = _EMPTY_TEXT | _NON_EMPTY_TEXT | _QUOTED_SYMBOL | _IDENTIFIER
_TEXT_VALUE.set_name('_TEXT_VALUE')

_ALT_IDENTIFIER = Combine(Word(alphas, alphanums + '_/'))
_ALT_TEXT_VALUE = (_EMPTY_TEXT | _NON_EMPTY_TEXT | _QUOTED_SYMBOL | _ALT_IDENTIFIER)
_ALT_TEXT_VALUE.set_name('_ALT_TEXT_VALUE')

class _Text(_Scalar):
    """A text string in single quotes, double quotes, or no quotes."""

    grammar = _TEXT_VALUE
    alt_grammar = _ALT_TEXT_VALUE

    def __init__(self, s, loc, tokens):
        self.s = s
        self.loc = loc
        self.tokens = tokens
        self._source = tokens[0]
        if len(tokens) == 1:
            if tokens[0] == '""':
                self.value = ''
                self.quote = '"'
                self._source = ''
            else:
                self.value = tokens[0]
                self.quote = ''
        else:
            self.quote = tokens[1]
            self.unwrap = _unwrap(tokens[0])
            if '\n' in tokens[0]:
                lines = tokens[0].split('\n')
                self._source = ('\n'.join(line.rstrip() for line in lines[:-1])
                                + '\n' + lines[-1])
            if '\n' in tokens[0].strip():
                self.value = self._source
                self.suffixes = self.suffixes + ('unwrap',)
            else:
                self.value = self.unwrap

        self.type_ = ('quoted_text' if self.quote == '"'
                      else 'quoted_symbol' if self.quote == "'" else 'identifier')

    @property
    def source(self):
        return self.quote + self._source + self.quote

    def __str__(self):
        if _is_identifier(self.value):
            return self.value
        if self.quote:
            return self.quote + self.value + self.quote
        if self.value == 'N/A':
            return "'N/A'"
        return '"' + self.value + '"'

    def quote_if_text(self):
        result = str(self)
        if result[0] not in {'"', "'"}:
            return '"' + result + '"'
        return result

    def __eq__(self, other):
        if isinstance(other, _Text):
            return repr(self) == repr(other)
        return self.value == other

    def wrap(self):
        return _Text(self.s, self.loc, [' '.join(self.value.split()), self.quote])

_TEXT_VALUE.set_parse_action(_Text)
_ALT_TEXT_VALUE.set_parse_action(_Text)

_SCALAR = _DATE_TIME | _DATE | _TIME | _NUMBER | _TEXT_VALUE    # Order counts!
_SCALAR.set_name('_SCALAR')
_Scalar.grammar = _SCALAR

_ALT_SCALAR = _ALT_DATE_TIME | _DATE | _ALT_TIME | _NUMBER | _ALT_TEXT_VALUE
_ALT_SCALAR.set_name('_ALT_SCALAR')
_Scalar.alt_grammar = _ALT_SCALAR

##########################################################################################
# _Vector
##########################################################################################

class _Vector(_Value):
    """Abstract class for 1D sequence, 2D sequence, and set."""

    def __init__(self, s, loc, tokens, delim='()'):
        self.tokens = list(tokens)
        self.delim = delim
        self.items = [token.wrap() for token in tokens]     # no internal newlines in list
        self.value = [item.value for item in self.items]

    def _fill_unit(self):
        self.all_units = [item.__dict__.get('unit', None) for item in self.items]
        unique_units = set(self.all_units)
        if len(unique_units) == 1:
            self.unit = unique_units.pop()
            if self.unit:
                self.suffixes = self.suffixes + ('unit',)
        else:
            self.unit = self.all_units
            self.suffixes = self.suffixes + ('unit',)

    def _fill_quote(self):
        unique_quotes = {item.__dict__.get('quote', None) for item in self.items} - {None}
        if unique_quotes:
            self.suffixes + ('quote',)
            self.quote = ''
            for quote in ('"', "'"):
                if quote in unique_quotes:
                    self.quote = quote
                    break

    @property
    def source(self):
        return (self.delim[0] + ', '.join(v.source.strip() for v in self.tokens)
                + self.delim[1])

    @property
    def full_value(self):
        return [item.full_value for item in self.items]

    def __str__(self):
        return (self.delim[0] + ', '.join(item.quote_if_text() for item in self.items)
                + self.delim[-1])

    def __getitem__(self, indx):
        return self.items[indx]

##########################################################################################
# _Set
##########################################################################################
_EMPTY_SET = Suppress('{') + _SKIP + Suppress('}')
_NON_EMPTY_SET = (Suppress('{') + _SKIP + _SCALAR + _SKIP
                  + ZeroOrMore(Suppress(',') + _SKIP + _SCALAR + _SKIP)
                  + Suppress('}'))
_SET = _EMPTY_SET | _NON_EMPTY_SET
_SET.set_name('_SET')

_ALT_NON_EMPTY_SET = (Suppress('{') + _SKIP + _ALT_SCALAR + _SKIP
                      + ZeroOrMore(Suppress(Optional(',')) + _SKIP + _ALT_SCALAR + _SKIP)
                      + Suppress('}'))
_ALT_SET = _EMPTY_SET | _ALT_NON_EMPTY_SET
_ALT_SET.set_name('_ALT_SET')

class _Set(_Vector):
    """A set of scalar values in curly braces {}."""

    type_ = 'set'
    grammar = _SET
    alt_grammar = _ALT_SET
    suffixes = ('list',)

    def __init__(self, s, loc, tokens):
        _Vector.__init__(self, s, loc, tokens, '{}')
        self._fill_unit()
        self._fill_quote()

        self.list = self.value      # save original values as list as well

        unique = []
        for item in tokens:
            if item not in unique:
                unique.append(item)
        self.unique = unique        # list of unique items in original order

        # Re-handle the units
        if isinstance(self.unit, (str, type(None))):
            self.value = {item.value for item in self.unique}
        else:
            self.value = {item.full_value for item in self.unique}
            self.unit = None

    @property
    def full_value(self):
        return {item.full_value for item in self.items}

    def __repr__(self):
        return '_Set(' + str(self)[1:-1] + ')'

_SET.set_parse_action(_Set)
_ALT_SET.set_parse_action(_Set)

##########################################################################################
# _Sequence
##########################################################################################
_SEQUENCE = (Suppress('(') + _SKIP + _SCALAR + _SKIP
             + ZeroOrMore(Suppress(',') + _SKIP + _SCALAR + _SKIP)
             + Suppress(')'))
_SEQUENCE.set_name('_SEQUENCE')

_ALT_SEQUENCE = (Suppress('(') + _SKIP + _ALT_SCALAR + _SKIP
                 + ZeroOrMore(Suppress(Optional(',')) + _SKIP + _ALT_SCALAR + _SKIP)
                 + Suppress(')'))
_ALT_SEQUENCE.set_name('_ALT_SEQUENCE')

class _Sequence(_Vector):
    """A 1-D set of scalar values in parentheses."""

    type_ = 'sequence_1D'
    grammar = _SEQUENCE
    alt_grammar = _ALT_SEQUENCE

    def __init__(self, s, loc, tokens):
        _Vector.__init__(self, s, loc, tokens, '()')
        self._fill_unit()
        self._fill_quote()

_SEQUENCE.set_parse_action(_Sequence)
_ALT_SEQUENCE.set_parse_action(_Sequence)

##########################################################################################
# _Sequence2D
##########################################################################################
_SEQUENCE_2D = (Suppress('(') + _SKIP + _SEQUENCE + _SKIP
                + ZeroOrMore(Suppress(',') + _SKIP + _SEQUENCE + _SKIP)
                + Suppress(')'))
_SEQUENCE_2D.set_name('_SEQUENCE_2D')

_ALT_SEQUENCE_2D = (Suppress('(') + _SKIP + _ALT_SEQUENCE + _SKIP
                    + ZeroOrMore(Suppress(Optional(',')) + _SKIP + _ALT_SEQUENCE + _SKIP)
                    + Suppress(')'))
_ALT_SEQUENCE_2D.set_name('_ALT_SEQUENCE_2D')

class _Sequence2D(_Vector):
    """A 2-D set of scalar values in nested parentheses."""

    type_ = 'sequence_2D'
    grammar = _SEQUENCE_2D
    alt_grammar = _ALT_SEQUENCE_2D

    def __init__(self, s, loc, tokens):
        _Vector.__init__(self, s, loc, tokens, '()')
        self._fill_quote()

        self.all_units = [item.all_units for item in self.items]
        unique_units = set()
        for unit_list in self.all_units:
            unique_units |= set(unit_list)

        if len(unique_units) == 1:
            self.unit = unique_units.pop()
            if self.unit:
                self.suffixes = self.suffixes + ('unit',)
        else:
            self.unit = self.all_units

    @property
    def full_value(self):
        return [item.full_value for item in self.items]

_SEQUENCE_2D.set_parse_action(_Sequence2D)
_ALT_SEQUENCE_2D.set_parse_action(_Sequence2D)

_VECTOR = _SET | _SEQUENCE | _SEQUENCE_2D
_VECTOR.set_name('_VECTOR')
_Vector.grammar = _VECTOR

_ALT_VECTOR = _ALT_SET | _ALT_SEQUENCE | _ALT_SEQUENCE_2D
_ALT_VECTOR.set_name('_ALT_VECTOR')
_Vector.alt_grammar = _ALT_VECTOR

_VALUE = _VECTOR | _SCALAR
_VALUE.set_name('_VALUE')
_Value.grammar = _VALUE

_ALT_VALUE = _ALT_VECTOR | _ALT_SCALAR
_ALT_VALUE.set_name('_ALT_VALUE')
_Value.alt_grammar = _ALT_VALUE

##########################################################################################
# _Pointer
##########################################################################################

class _Pointer(_Item):
    """An abstract class describing simple pointers and pointers with offsets."""
    pass

##########################################################################################
# _SimplePointer
##########################################################################################
_FILENAME = Combine(Word(alphanums + '_') + OneOrMore('.' + Word(alphanums + '_')))
_FILENAME.set_name('_FILENAME')
_SIMPLE_POINTER = Suppress('"') + _FILENAME + Suppress('"')
_SIMPLE_POINTER.set_name('_SIMPLE_POINTER')

_ALT_FILENAME = Combine(Word(alphanums + '_/') + OneOrMore('.' + Word(alphanums + '_')))
_ALT_FILENAME.set_name('_ALT_FILENAME')
_ALT_FILE_POINTER = Suppress('"') + _ALT_FILENAME + Suppress('"')
_ALT_APOS_FILE_POINTER = Suppress(Literal("'")) + _ALT_FILENAME + Literal("'")
_ALT_SIMPLE_POINTER = _ALT_APOS_FILE_POINTER | _ALT_FILE_POINTER
_ALT_SIMPLE_POINTER.set_name('_ALT_SIMPLE_POINTER')

class _SimplePointer(_Pointer):
    """A filename for a detached label."""

    type_ = 'file_pointer'
    grammar = _SIMPLE_POINTER
    alt_grammar = _ALT_SIMPLE_POINTER
    suffixes = ('fmt',)

    def __init__(self, s, loc, tokens):
        self.tokens = tokens
        self.value = tokens[0]
        if len(tokens) > 1:
            self.quote = "'" if tokens[1] == "'" else '"'
        else:
            self.quote = '"'
        self.fmt = str(self)

    @property
    def source(self):
        return self.quote + self.tokens[0] + self.quote

    def __str__(self):
        return '"' + self.tokens[0] + '"'

_SIMPLE_POINTER.set_parse_action(_SimplePointer)
_ALT_SIMPLE_POINTER.set_parse_action(_SimplePointer)

##########################################################################################
# _LocalPointer
##########################################################################################
_BYTE_UNIT = Literal('<BYTES>') | Literal('<bytes>')
_ROW_OFFSET = _UNSIGNED_INT
_BYTE_OFFSET = _ROW_OFFSET + _WHITE + _BYTE_UNIT
_LOCAL_POINTER = _BYTE_OFFSET | _ROW_OFFSET
_LOCAL_POINTER.set_name('_LOCAL_POINTER')

class _LocalPointer(_Pointer):
    """A file offset in units of bytes or records for an attached label."""

    type_ = 'offset_pointer'
    grammar = _LOCAL_POINTER
    suffixes = ('unit', 'fmt')

    def __init__(self, s, loc, tokens):
        self.tokens = tokens
        self.value = int(tokens[0])
        self.unit = '<BYTES>' if len(tokens) > 1 else ''
        self.fmt = str(self)

    def __str__(self):
        return str(self.value) + (' <BYTES>' if self.unit else '')

    @property
    def source(self):
        return str(self.value) + (' ' + self.tokens[1] if self.unit else '')

    @property
    def full_value(self):
        return (self.value, self.unit) if self.unit else self.value

_LOCAL_POINTER.set_parse_action(_LocalPointer)

##########################################################################################
# _OffsetPointer
##########################################################################################
_OFFSET_POINTER = (Suppress('(') + _SKIP + _SIMPLE_POINTER + _SKIP
                   + Suppress(',') + _SKIP + _LOCAL_POINTER + _SKIP + Suppress(')'))
_OFFSET_POINTER.set_name('_OFFSET_POINTER')

_ALT_OFFSET_POINTER = (Suppress('(') + _SKIP + _ALT_SIMPLE_POINTER + _SKIP
                       + Suppress(',') + _SKIP + _LOCAL_POINTER + _SKIP + Suppress(')'))
_ALT_OFFSET_POINTER.set_name('_ALT_OFFSET_POINTER')

class _OffsetPointer(_Pointer):
    """A pointer as a filename plus an offset in units of bytes or records."""

    type_ = 'file_offset_pointer'
    grammar = _OFFSET_POINTER
    alt_grammar = _ALT_OFFSET_POINTER
    suffixes = ('offset', 'unit', 'fmt')

    def __init__(self, s, loc, tokens):
        self.tokens = tokens
        self.value = tokens[0].value
        self.offset = tokens[1].value
        self.unit = tokens[1].unit
        self.quote = '"'
        self.fmt = str(self)

    @property
    def source(self):
        return '(' + self.tokens[0].source + ', ' + self.tokens[1].source + ')'

    @property
    def full_value(self):
        if not self.unit:
            return (self.value, self.offset)
        return (self.value, self.offset, self.unit)

    def __str__(self):
        return ('("' + self.value + '", ' + str(self.offset)
                + (' <BYTES>)' if self.unit else ')'))

_OFFSET_POINTER.set_parse_action(_OffsetPointer)
_ALT_OFFSET_POINTER.set_parse_action(_OffsetPointer)

##########################################################################################
# _SetPointer
##########################################################################################
_SET_POINTER = (Suppress('{') + _SKIP + _SIMPLE_POINTER + _SKIP
                + ZeroOrMore(Suppress(',') + _SKIP + _SIMPLE_POINTER + _SKIP)
                + Suppress('}'))
_SET_POINTER.set_name('_SET_POINTER')

_ALT_SET_POINTER = (Suppress('{') + _SKIP + _ALT_SIMPLE_POINTER + _SKIP
                    + ZeroOrMore(Suppress(',') + _SKIP + _ALT_SIMPLE_POINTER + _SKIP)
                    + Suppress('}'))
_ALT_SET_POINTER.set_name('_ALT_SET_POINTER')

class _SetPointer(_Pointer):
    """A set of simple pointers in curly braces {}."""

    type_ = 'set_pointer'
    grammar = _SET_POINTER
    alt_grammar = _ALT_SET_POINTER
    suffixes = ('list',)

    def __init__(self, s, loc, tokens):
        self.tokens = tokens
        self.list = [item.value for item in self.tokens]
        unique = []
        for item in tokens:
            if item not in unique:
                unique.append(item)
        self.items = unique         # list of unique items in original order
        self.value = {item.value for item in unique}

    @property
    def source(self):
        return '{' + ', '.join(token.source for token in self.tokens) + '}'

    def __str__(self):
        return '{' + ', '.join('"' + item.value + '"' for item in self.items) + '}'

_SET_POINTER.set_parse_action(_SetPointer)
_ALT_SET_POINTER.set_parse_action(_SetPointer)

##########################################################################################
# _SequencePointer
##########################################################################################
_SEQUENCE_POINTER = (Suppress('(') + _SKIP + _SIMPLE_POINTER + _SKIP
                     + ZeroOrMore(Suppress(',') + _SKIP + _SIMPLE_POINTER + _SKIP)
                     + Suppress(')'))
_SEQUENCE_POINTER.set_name('_SEQUENCE_POINTER')

_ALT_SEQUENCE_POINTER = (Suppress('(') + _SKIP + _ALT_SIMPLE_POINTER + _SKIP
                         + ZeroOrMore(Suppress(',') + _SKIP + _ALT_SIMPLE_POINTER + _SKIP)
                         + Suppress(')'))
_ALT_SEQUENCE_POINTER.set_name('_ALT_SEQUENCE_POINTER')

class _SequencePointer(_Pointer):
    """A set of simple pointers in parentheses ()."""

    type_ = 'sequence_pointer'
    grammar = _SEQUENCE_POINTER
    alt_grammar = _ALT_SEQUENCE_POINTER

    def __init__(self, s, loc, tokens):
        self.tokens = tokens
        self.items = tokens
        self.value = [item.value for item in self.items]

    @property
    def source(self):
        return '(' + ', '.join(token.source for token in self.tokens) + ')'

    def __str__(self):
        return '(' + ', '.join('"' + item.value + '"' for item in self.items) + ')'

_SEQUENCE_POINTER.set_parse_action(_SequencePointer)
_ALT_SEQUENCE_POINTER.set_parse_action(_SequencePointer)

_POINTER_VALUE = (_SIMPLE_POINTER | _LOCAL_POINTER | _OFFSET_POINTER | _SET_POINTER
                  | _SEQUENCE_POINTER)
_POINTER_VALUE.set_name('_POINTER_VALUE')
_Pointer.grammar = _POINTER_VALUE

_ALT_POINTER_VALUE = (_ALT_SIMPLE_POINTER | _LOCAL_POINTER | _ALT_OFFSET_POINTER
                      | _ALT_SET_POINTER | _ALT_SEQUENCE_POINTER)
_ALT_POINTER_VALUE.set_name('_ALT_POINTER_VALUE')
_Pointer.alt_grammar = _ALT_POINTER_VALUE

##########################################################################################
# _AttributeID
##########################################################################################
_caps = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
_middle = _caps + nums
_KEYWORD = Combine(Word(_caps, _middle) + ZeroOrMore(Literal('_') + Word(_middle)))
_SINGLE_ATTR_ID = _KEYWORD
_DOUBLE_ATTR_ID = _KEYWORD + Suppress(':') + _KEYWORD
_ATTRIBUTE_ID = _DOUBLE_ATTR_ID | _SINGLE_ATTR_ID               # Order matters
_ATTRIBUTE_ID.set_name('_ATTRIBUTE_ID')

class _AttributeID(_Item):
    """A simple attribute with option namespace prefix."""

    grammar = _ATTRIBUTE_ID

    def __init__(self, s, loc, tokens):
        self.tokens = tokens
        self.name = tokens[-1]
        self.namespace = '' if len(tokens) == 1 else tokens[0]
        self.value = ':'.join(self.tokens)

    def __str__(self):
        return self.value

_ATTRIBUTE_ID.set_parse_action(_AttributeID)

##########################################################################################
# _PointerID
##########################################################################################
_POINTER_ID = Suppress('^') + _ATTRIBUTE_ID
_POINTER_ID.set_name('_POINTER_ID')

class _PointerID(_Item):
    """A pointer."""

    grammar = _POINTER_ID

    def __init__(self, s, loc, tokens):
        self.tokens = tokens
        self.value = '^' + tokens[0].value

    def __str__(self):
        return self.value

_POINTER_ID.set_parse_action(_PointerID)

##########################################################################################
# _Statement
##########################################################################################
_POINTER_STMT = _POINTER_ID + _EQUAL + _POINTER_VALUE
_ATTRIBUTE_STMT = _ATTRIBUTE_ID + _EQUAL + _VALUE
_STATEMENT = _WHITE + (_POINTER_STMT | _ATTRIBUTE_STMT) + _EOL
_STATEMENT.set_name('_STATEMENT')

_ALT_POINTER_STMT = _POINTER_ID + _EQUAL + _ALT_POINTER_VALUE
_ALT_ATTRIBUTE_STMT = _ATTRIBUTE_ID + _EQUAL + _ALT_VALUE
_ALT_END_OBJECT = one_of(['END_OBJECT', 'END_GROUP'])

_ALT_STATEMENT = _WHITE + (_ALT_POINTER_STMT | _ALT_ATTRIBUTE_STMT
                           | _ALT_END_OBJECT) + _EOL
_ALT_STATEMENT.set_name('_ALT_STATEMENT')

class _Statement(_Item):

    grammar = _STATEMENT
    alt_grammar = _ALT_STATEMENT

    def __init__(self, s, loc, tokens):
        self.tokens = tokens
        self.name = tokens[0] if isinstance(tokens[0], str) else tokens[0].value
        self.item = tokens[1] if len(tokens) > 1 else None
        self.value = (self.name, self.item and self.item.full_value)

    def __str__(self):
        if self.item is None:
            return self.name
        return self.name + ' = ' + str(self.item)

_STATEMENT.set_parse_action(_Statement)
_ALT_STATEMENT.set_parse_action(_Statement)

##########################################################################################
# _EndStatement
##########################################################################################

_END_STATEMENT = _WHITE + Literal('END') + _EOL
_END_STATEMENT.set_name('_END_STATEMENT')

_ALT_END_STATEMENT = _WHITE + Literal('END') + _WHITE + Optional(_EOL)
_ALT_END_STATEMENT.set_name('_ALT_END_STATEMENT')

class _EndStatement(_Item):

    grammar = _END_STATEMENT
    alt_grammar = _ALT_END_STATEMENT

    def __init__(self, s, loc, tokens):
        self.tokens = tokens
        self.name = 'END'
        self.item = None
        self.value = ('END', None)

    def __str__(self):
        return 'END'

_END_STATEMENT.set_parse_action(_EndStatement)
_ALT_END_STATEMENT.set_parse_action(_EndStatement)

_PDS3_LABEL = (Optional(_EOL) + OneOrMore(_STATEMENT) + _END_STATEMENT + _WHITE
               + StringEnd())
_ALT_PDS3_LABEL = (Optional(_EOL) + OneOrMore(_ALT_STATEMENT)
                   + Optional(_ALT_END_STATEMENT) + Optional(_EOL) + StringEnd())
_COMPOUND_LABEL = (Optional(_EOL) + OneOrMore(_ALT_STATEMENT | _END_STATEMENT)
                   + Optional(_ALT_END_STATEMENT) + StringEnd())

##########################################################################################
