# -*- coding: utf-8 -*-
"""Tests for mac notes plugin."""
from __future__ import unicode_literals

import unittest

from plaso.lib import definitions
from plaso.parsers.sqlite_plugins import mac_notes

from tests.parsers.sqlite_plugins import test_lib


class MacNotesTest(test_lib.SQLitePluginTestCase):
  """Tests for mac notes database plugin."""

  def testProcess(self):
    """Test the Process function on a Mac Notes file."""
    plugin_object = mac_notes.MacNotesPlugin()
    storage_writer = self._ParseDatabaseFileWithPlugin(
        ['NotesV7.storedata'], plugin_object)

    self.assertEqual(storage_writer.number_of_events, 6)
    self.assertEqual(storage_writer.number_of_warnings, 0)

    events = list(storage_writer.GetEvents())

    # Check the first note.
    expected_title = 'building 4th brandy gibs'
    expected_text = (
        'building 4th brandy gibs microsoft office body soul and peace '
        'example.com 3015555555: plumbing and heating claim#123456 Small '
        'business ')

    expected_event_values = {
        'text': expected_text,
        'timestamp': '2014-02-11 02:38:27.097813',
        'timestamp_desc': definitions.TIME_DESCRIPTION_CREATION,
        'title': expected_title}

    self.CheckEventValues(storage_writer, events[0], expected_event_values)

    expected_message = 'title:{0:s} note_text:{1:s}'.format(
        expected_title, expected_text)
    expected_short_message = 'title:{0:s}'.format(expected_title)

    event_data = self._GetEventDataOfEvent(storage_writer, events[0])
    self._TestGetMessageStrings(
        event_data, expected_message, expected_short_message)

if __name__ == '__main__':
  unittest.main()
