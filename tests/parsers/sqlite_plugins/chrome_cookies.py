#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for the Google Chrome cookie database plugin."""

from __future__ import unicode_literals

import unittest

from plaso.lib import definitions
from plaso.parsers.sqlite_plugins import chrome_cookies

from tests.parsers.sqlite_plugins import test_lib


class Chrome17CookiesPluginTest(test_lib.SQLitePluginTestCase):
  """Tests for the Google Chrome 17-65 cookie database plugin."""

  def testProcess(self):
    """Tests the Process function on a Chrome cookie database file."""
    plugin = chrome_cookies.Chrome17CookiePlugin()
    storage_writer = self._ParseDatabaseFileWithPlugin(['cookies.db'], plugin)

    # Since we've got both events generated by cookie plugins and the Chrome
    # cookie plugin we need to separate them.
    events = []
    extra_objects = []

    for event in storage_writer.GetEvents():
      event_data = self._GetEventDataOfEvent(storage_writer, event)
      if event_data.data_type == 'chrome:cookie:entry':
        events.append(event)
      else:
        extra_objects.append(event)

    # The cookie database contains 560 entries:
    #     560 creation timestamps.
    #     560 last access timestamps.
    #     560 expired timestamps.
    # Then there are extra events created by plugins:
    #      75 events created by Google Analytics cookies.
    # In total: 1755 events.
    self.assertEqual(len(events), 3 * 560)
    self.assertEqual(len(extra_objects), 75)

    # Check one www.linkedin.com cookie.
    expected_event_values = {
        'cookie_name': 'leo_auth_token',
        'host': 'www.linkedin.com',
        'httponly': False,
        'timestamp': '2011-08-25 21:50:27.292367',
        'timestamp_desc': definitions.TIME_DESCRIPTION_LAST_ACCESS,
        'url': 'http://www.linkedin.com/'}

    self.CheckEventValues(storage_writer, events[124], expected_event_values)

    expected_message = (
        'http://www.linkedin.com/ (leo_auth_token) '
        'Flags: [HTTP only] = False '
        '[Persistent] = True')
    expected_short_message = 'www.linkedin.com (leo_auth_token)'

    event_data = self._GetEventDataOfEvent(storage_writer, events[124])
    self._TestGetMessageStrings(
        event_data, expected_message, expected_short_message)

    # Check one of the visits to rubiconproject.com.
    expected_event_values = {
        'path': '/',
        'persistent': True,
        'secure': False,
        'timestamp': '2012-04-01 13:54:34.949210',
        'timestamp_desc': definitions.TIME_DESCRIPTION_LAST_ACCESS,
        'url': 'http://rubiconproject.com/'}

    self.CheckEventValues(storage_writer, events[379], expected_event_values)

    expected_message = (
        'http://rubiconproject.com/ (put_2249) '
        'Flags: [HTTP only] = False '
        '[Persistent] = True')

    event_data = self._GetEventDataOfEvent(storage_writer, events[379])
    self._TestGetMessageStrings(
        event_data, expected_message, 'rubiconproject.com (put_2249)')

    # Examine an event for a visit to a political blog site.
    expected_event_values = {
        'host': 'politicalticker.blogs.cnn.com',
        'path': '/2012/03/21/romney-tries-to-clean-up-etch-a-sketch-mess/',
        'timestamp': '2012-03-22 01:47:21.012022'}

    self.CheckEventValues(storage_writer, events[444], expected_event_values)

    # Examine a cookie that has an autologin entry.
    expected_event_values = {
        'cookie_name': 'autologin[timeout]',
        # This particular cookie value represents a timeout value that
        # corresponds to the expiration date of the cookie.
        'data': '1364824322',
        'host': 'marvel.com',
        'timestamp': '2012-04-01 13:52:56.189444',
        'timestamp_desc': definitions.TIME_DESCRIPTION_CREATION}

    self.CheckEventValues(storage_writer, events[1425], expected_event_values)

    # Examine a cookie expiry event.
    expected_event_values = {
        'timestamp': '2013-08-14 14:19:42.000000',
        'timestamp_desc': definitions.TIME_DESCRIPTION_EXPIRATION}

    self.CheckEventValues(storage_writer, events[2], expected_event_values)


class Chrome66CookiesPluginTest(test_lib.SQLitePluginTestCase):
  """Tests for the Google Chrome 66 Cookies database plugin."""

  def testProcess(self):
    """Tests the Process function on a Chrome cookie database file."""
    plugin = chrome_cookies.Chrome66CookiePlugin()
    storage_writer = self._ParseDatabaseFileWithPlugin(
        ['Cookies-68.0.3440.106'], plugin)

    # Since we've got both events generated by cookie plugins and the Chrome
    # cookie plugin we need to separate them.
    events = []
    extra_objects = []

    for event in storage_writer.GetEvents():
      event_data = self._GetEventDataOfEvent(storage_writer, event)
      if event_data.data_type == 'chrome:cookie:entry':
        events.append(event)
      else:
        extra_objects.append(event)

    # The cookie database contains 5 entries:
    #     5 creation timestamps.
    #     5 last access timestamps.
    #     5 expired timestamps.
    # Then there are extra events created by plugins:
    #      1 event created by Google Analytics cookies.
    # In total: 16 events.
    self.assertEqual(len(events), 3 * 5)
    self.assertEqual(len(extra_objects), 1)

    # Test some cookies
    # Check a GA cookie creation event with a path.
    expected_event_values = {
        'cookie_name': '__utma',
        'host': 'google.com',
        'httponly': False,
        'timestamp': '2018-08-14 15:03:43.650324',
        'timestamp_desc': definitions.TIME_DESCRIPTION_CREATION,
        'url': 'http://google.com/gmail/about/'}

    self.CheckEventValues(storage_writer, events[0], expected_event_values)

    expected_message = (
        'http://google.com/gmail/about/ (__utma) '
        'Flags: [HTTP only] = False [Persistent] = True')
    expected_short_message = 'google.com (__utma)'

    event_data = self._GetEventDataOfEvent(storage_writer, events[0])
    self._TestGetMessageStrings(
        event_data, expected_message, expected_short_message)

    # Check one of the visits to fbi.gov for last accessed time.
    expected_event_values = {
        'path': '/',
        'persistent': True,
        'secure': False,
        'timestamp': '2018-08-20 17:19:53.134291',
        'timestamp_desc': definitions.TIME_DESCRIPTION_LAST_ACCESS,
        'url': 'http://fbi.gov/'}

    self.CheckEventValues(storage_writer, events[10], expected_event_values)

    expected_message = (
        'http://fbi.gov/ (__cfduid) '
        'Flags: [HTTP only] = True [Persistent] = True')

    event_data = self._GetEventDataOfEvent(storage_writer, events[10])
    self._TestGetMessageStrings(
        event_data, expected_message, 'fbi.gov (__cfduid)')

    # Examine an event for a cookie with a very large expire time.
    expected_event_values = {
        'host': 'projects.fivethirtyeight.com',
        'timestamp': '9999-08-17 12:26:28.000000'}

    self.CheckEventValues(storage_writer, events[8], expected_event_values)


if __name__ == '__main__':
  unittest.main()
