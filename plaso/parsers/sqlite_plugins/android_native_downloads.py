# -*- coding: utf-8 -*-
"""SQLite parser plugin for Native Downloads (DownloadManager API) database files."""

from dfdatetime import java_time as dfdatetime_java_time

from plaso.containers import events
from plaso.parsers import sqlite
from plaso.parsers.sqlite_plugins import interface


class NativeDownloadsEventData(events.EventData):
  """Native Downloads (DownloadManager API) event data.

  # TODO : Where to include source (https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/core/java/android/app/DownloadManager.java)?

  Attributes:
    id (int): An identifier for a particular download, unique across the system.
    uri (str): Downloaded URI.
    ... (TODO : Evaluate columns between)
    data (str): Path to the downloaded file on disk.
    mimetype (str): Internet Media Type of the downloaded file.
    ... (TODO : Evaluate columns between)
    status (int): If an error occurred, this holds the HTTP Status Code for an HTTP error (RFC 2616),
        otherwise it holds one of the ERROR_* constants.
        If the download is paused, this holds one of the PAUSED_* constants.
        (TODO : status vs reason column. Status column only contains 4 codes, shouldn't have http codes. Why status = reason?)
        List of ERROR_* constants :
            ERROR_UNKNOWN = 1000,  when the download has completed with an error that doesn't fit
                under any other error code.
            ERROR_FILE_ERROR = 1001, when a storage issue arises which doesn't fit under any
                other error code.
            ERROR_UNHANDLED_HTTP_CODE = 1002, when an HTTP code was received that download manager can't handle.
            ERROR_HTTP_DATA_ERROR = 1004, when an error receiving or processing data occurred at the HTTP level.
            ERROR_TOO_MANY_REDIRECTS = 1005, when there were too many redirects.
            ERROR_DEVICE_NOT_FOUND = 1007, when no external storage device was found. Typically,
                this is because the SD card is not mounted.
            ERROR_CANNOT_RESUME = 1008, when some possibly transient error occurred but we can't resume the download.
            ERROR_FILE_ALREADY_EXISTS = 1009, when the requested destination file already exists (the
                download manager will not overwrite an existing file).
            ERROR_BLOCKED = 1010, when the download has failed because of
                {@link NetworkPolicyManager} controls on the requesting application.

        List of PAUSED_* constants :
            PAUSED_WAITING_TO_RETRY = 1, when the download is paused because some network error
                occurred and the download manager is waiting before retrying the request.
            PAUSED_WAITING_FOR_NETWORK = 2, when the download is waiting for network connectivity to proceed.
            PAUSED_QUEUED_FOR_WIFI = 3, when the download exceeds a size limit for downloads over
                the mobile network and the download manager is waiting for a Wi-Fi connection to proceed.
            PAUSED_UNKNOWN = 4, when the download is paused for some other reason.
    ... (TODO : Evaluate 1 column between)
    lastmod (dfdatetime.DateTimeValues): Last modified date and time of downloaded file.
    notificationpackage (str): Package name associated with notification of a running download.
    ... (TODO : Evaluate columns between)
    total_bytes (str): Total size of the download in bytes.
    current_bytes (str): Number of bytes download so far.
    ... (TODO : Evaluate columns between)
    title (str):  The client-supplied title for this download.  This will be displayed in system notifications.
        Defaults to the empty string.
    description (str): The client-supplied description of this download.  This will be displayed in system
        notifications.  Defaults to the empty string.
    ... (TODO : Evaluate columns between)
    mediaprovider_uri (str): The URI to the corresponding entry in MediaProvider for this downloaded entry. It is
        used to delete the entries from MediaProvider database when it is deleted from the
        downloaded list.
    ... (TODO : Evaluate columns between)
  """

  DATA_TYPE = 'android:sqlite:downloads'

  def __init__(self):
    """Initializes event data."""
    super(NativeDownloadsEventData, self).__init__(data_type=self.DATA_TYPE)
    self.id = None
    self.body = None
    self.creation_time = None
    self.offset = None
    self.query = None
    self.sms_read = None
    self.sms_type = None
