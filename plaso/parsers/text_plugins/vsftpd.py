# -*- coding: utf-8 -*-
"""Text parser plugin for vsftpd log files."""

import pyparsing

from dfdatetime import time_elements as dfdatetime_time_elements

from plaso.containers import events
from plaso.lib import errors
from plaso.parsers import text_parser
from plaso.parsers.text_plugins import interface


class VsftpdLogEventData(events.EventData):
  """vsftpd log event data.

  Attributes:
    added_time (dfdatetime.DateTimeValues): date and time the log entry
        was added.
    text (str): vsftpd log message.
  """

  DATA_TYPE = 'vsftpd:log'

  def __init__(self):
    """Initializes event data."""
    super(VsftpdLogEventData, self).__init__(data_type=self.DATA_TYPE)
    self.added_time = None
    self.text = None


class VsftpdLogTextPlugin(interface.TextPlugin):
  """Text parser plugin for vsftpd log files."""

  NAME = 'vsftpd'
  DATA_FORMAT = 'vsftpd log file'

  _MONTH_DICT = {
      'jan': 1,
      'feb': 2,
      'mar': 3,
      'apr': 4,
      'may': 5,
      'jun': 6,
      'jul': 7,
      'aug': 8,
      'sep': 9,
      'oct': 10,
      'nov': 11,
      'dec': 12}

  _ONE_OR_TWO_DIGITS = pyparsing.Word(pyparsing.nums, max=2).setParseAction(
      text_parser.PyParseIntCast)

  _TWO_DIGITS = pyparsing.Word(pyparsing.nums, exact=2).setParseAction(
      text_parser.PyParseIntCast)

  _FOUR_DIGITS = pyparsing.Word(pyparsing.nums, exact=4).setParseAction(
      text_parser.PyParseIntCast)

  _THREE_LETTERS = pyparsing.Word(pyparsing.alphas, exact=3)

  # Whitespace is suppressed by pyparsing.

  # Date and time values are formatted as: Mon Jun  6 18:43:28 2016
  _DATE_TIME = pyparsing.Group(
      _THREE_LETTERS + _THREE_LETTERS + _ONE_OR_TWO_DIGITS +
      _TWO_DIGITS + pyparsing.Suppress(':') +
      _TWO_DIGITS + pyparsing.Suppress(':') +
      _TWO_DIGITS + _FOUR_DIGITS)

  _LOG_LINE = (
      _DATE_TIME.setResultsName('date_time') +
      pyparsing.SkipTo(pyparsing.lineEnd).setResultsName('text'))

  _LINE_STRUCTURES = [('logline', _LOG_LINE)]

  _SUPPORTED_KEYS = frozenset([key for key, _ in _LINE_STRUCTURES])

  def _ParseLogLine(self, parser_mediator, structure):
    """Parses a log line.

    Args:
      parser_mediator (ParserMediator): mediates interactions between parsers
          and other components, such as storage and dfVFS.
      structure (pyparsing.ParseResults): structure of tokens derived from
          a line of a text file.
    """
    time_elements_structure = self._GetValueFromStructure(
        structure, 'date_time')

    event_data = VsftpdLogEventData()
    event_data.added_time = self._ParseTimeElements(time_elements_structure)
    # TODO: extract pid and username.
    event_data.text = self._GetValueFromStructure(structure, 'text')

    parser_mediator.ProduceEventData(event_data)

  def _ParseRecord(self, parser_mediator, key, structure):
    """Parses a pyparsing structure.

    Args:
      parser_mediator (ParserMediator): mediates interactions between parsers
          and other components, such as storage and dfVFS.
      key (str): name of the parsed structure.
      structure (pyparsing.ParseResults): tokens from a parsed log line.

    Raises:
      ParseError: when the structure type is unknown.
    """
    if key not in self._SUPPORTED_KEYS:
      raise errors.ParseError(
          'Unable to parse record, unknown structure: {0:s}'.format(key))

    try:
      self._ParseLogLine(parser_mediator, structure)
    except errors.ParseError as exception:
      parser_mediator.ProduceExtractionWarning(
          'unable to parse log line with error: {0!s}'.format(exception))

  def _ParseTimeElements(self, time_elements_structure):
    """Parses date and time elements of a log line.

    Args:
      time_elements_structure (pyparsing.ParseResults): date and time elements
          of a log line.

    Returns:
      dfdatetime.TimeElements: date and time value.

    Raises:
      ParseError: if a valid date and time value cannot be derived from
          the time elements.
    """
    try:
      _, month_string, day_of_month, hours, minutes, seconds, year = (
          time_elements_structure)

      month = self._MONTH_DICT.get(month_string.lower(), 0)

      time_elements_tuple = (year, month, day_of_month, hours, minutes, seconds)
      date_time = dfdatetime_time_elements.TimeElements(
          time_elements_tuple=time_elements_tuple)
      date_time.is_local_time = True

      return date_time

    except (TypeError, ValueError) as exception:
      raise errors.ParseError(
          'Unable to parse time elements with error: {0!s}'.format(exception))

  def CheckRequiredFormat(self, parser_mediator, text_file_object):
    """Check if the log record has the minimal structure required by the plugin.

    Args:
      parser_mediator (ParserMediator): mediates interactions between parsers
          and other components, such as storage and dfVFS.
      text_file_object (dfvfs.TextFile): text file.

    Returns:
      bool: True if this is the correct parser, False otherwise.
    """
    try:
      line = self._ReadLineOfText(text_file_object)
    except UnicodeDecodeError:
      return False

    if line and (' [pid ' not in line or ': Client ' not in line):
      return False

    try:
      parsed_structure = self._LOG_LINE.parseString(line)
    except pyparsing.ParseException:
      return False

    time_elements_structure = self._GetValueFromStructure(
        parsed_structure, 'date_time')

    try:
      self._ParseTimeElements(time_elements_structure)
    except errors.ParseError:
      return False

    return True


text_parser.SingleLineTextParser.RegisterPlugin(VsftpdLogTextPlugin)
