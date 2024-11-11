# -*- coding: utf-8 -*-
"""SQLite parser plugin for Android Native Downloads (DownloadManager API) database files."""

from dfdatetime import java_time as dfdatetime_java_time

from plaso.containers import events
from plaso.parsers import sqlite
from plaso.parsers.sqlite_plugins import interface


class AndroidNativeDownloadsEventData(events.EventData):
  """Android Native Downloads (DownloadProvider) event data.

  # TODO : Where to include source (https://android.googlesource.com/platform/frameworks/base/+/refs/heads/main/core/java/android/app/DownloadManager.java)?
  # TODO : Format attributes to standard.
  Attributes:
    lastmod (dfdatetime.DateTimeValues): Last modified date and time of downloaded file.
    id (int): An identifier for a particular download, unique across the system.
    uri (str): Downloaded URI.
    mimetype (str): Internet Media Type of the downloaded file.
    total_bytes (int): Total size of the download in bytes.
    current_bytes (int): Number of bytes download so far.
    status (int): If an error occurred, this holds the HTTP Status Code for an HTTP error (RFC 2616),
        otherwise it holds one of the ERROR_* constants.
        If the download is paused, this holds one of the PAUSED_* constants.

        // is this one correct? in reference "https://android.googlesource.com/platform/frameworks/base/+/refs/heads/master/core/java/android/provider/Downloads.java"
        // legal values is STATUS_*
        // List of STATUS_* constants :
        //    STATUS_PENDING = 190, This download hasn't stated yet
        //    STATUS_RUNNING = 192, This download has started
        //    STATUS_PAUSED_BY_APP = 193, This download has been paused by the owning app.
        //    STATUS_WAITING_TO_RETRY = 194, This download encountered some network error and is waiting before retrying the request.
        //    STATUS_WAITING_FOR_NETWORK = 195, This download is waiting for network connectivity to proceed.
        //    STATUS_QUEUED_FOR_WIFI = 196, This download exceeded a size limit for mobile networks and is waiting for a Wi-Fi connection to proceed.
        //    STATUS_INSUFFICIENT_SPACE_ERROR = 198, This download couldn't be completed due to insufficient storage space.  Typically, this is because the SD card
                is full.
        //    STATUS_DEVICE_NOT_FOUND_ERROR = 199, This download couldn't be completed because no external storage device was found.  Typically, this is because the SD
                card is not mounted.
        //    STATUS_SUCCESS = 200, This download has successfully completed. Warning: there might be other status values that indicate success in the future.
        //    STATUS_BAD_REQUEST = 400, This request couldn't be parsed. This is also used when processing requests with unknown/unsupported URI schemes.
        //    STATUS_NOT_ACCEPTABLE = 406, This download can't be performed because the content type cannot be handled.
        //    STATUS_LENGTH_REQUIRED = 411, This download cannot be performed because the length cannot be determined accurately. This is the code for the HTTP error
                "Length Required", which is typically used when making requests that require a content length but don't have one, and it is also used in the client when a
                response is received whose length cannot be determined accurately (therefore making it impossible to know when a download completes).
        //    STATUS_PRECONDITION_FAILED = 412, This download was interrupted and cannot be resumed. This is the code for the HTTP error "Precondition Failed", and it is
                also used in situations where the client doesn't have an ETag at all.
        //    MIN_ARTIFICIAL_ERROR_STATUS = 488, The lowest-valued error status that is not an actual HTTP status code.
        //    STATUS_FILE_ALREADY_EXISTS_ERROR = 488, The requested destination file already exists.
        //    STATUS_CANNOT_RESUME = 489, Some possibly transient error occurred, but we can't resume the download.
        //    STATUS_CANCELED = 490, This download was canceled
        //    STATUS_UNKNOWN_ERROR = 491, This download has completed with an error. Warning: there will be other status values that indicate errors in the future.
        //    STATUS_FILE_ERROR = 492, This download couldn't be completed because of a storage issue. Typically, that's because the filesystem is missing or full.
        //    STATUS_UNHANDLED_REDIRECT = 493, This download couldn't be completed because of an HTTP redirect response that the download manager couldn't handle.
        //    STATUS_UNHANDLED_HTTP_CODE = 494, This download couldn't be completed because of an unspecified unhandled HTTP code.
        //    STATUS_HTTP_DATA_ERROR = 495, This download couldn't be completed because of an error receiving or processing data at the HTTP level.
        //    STATUS_HTTP_EXCEPTION = 496, This download couldn't be completed because of an HttpException while setting up the request.
        //    STATUS_TOO_MANY_REDIRECTS = 497, This download couldn't be completed because there were too many redirects.


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
    saved_to (str): Path to the downloaded file on disk.
    deleted (bool): Set to true if this download is deleted. It is completely removed from the database when
        MediaProvider database also deletes the metadata associated with this downloaded file.
    notification_package (str): Package name associated with notification of a running download.
    title (str): Path to the downloaded file on disk.
    media_provider_uri (str): The URI to the corresponding entry in MediaProvider for this downloaded entry. It is
        used to delete the entries from MediaProvider database when it is deleted from the
        downloaded list.
    error_msg (str): The column with errorMsg for a failed downloaded. Used only for debugging purposes.
    is_visible_in_downloads_ui (int) :  Whether or not this download should be displayed in the system's Downloads UI.
        Defaults to true.
    destination (int): The name of the column containing the flag that controls the destination of the download. See the DESTINATION_*
        constants for a list of legal values.
        List of DESTINATION_* constants :
            DESTINATION_EXTERNAL = 0, This download will be saved to the external storage. This is the default behavior, and should be
                used for any file that the user can freely access, copy, delete.
            DESTINATION_CACHE_PARTITION = 1, This download will be saved to the download manager's private partition. This is the behavior
                used by applications that want to download private files that are used and deleted soon after they get downloaded.
            DESTINATION_CACHE_PARTITION_PURGEABLE = 2, This download will be saved to the download manager's private partition and will be
                purged as necessary to make space. This is for private files (similar to CACHE_PARTITION) that aren't deleted immediately
                after they are used, and are kept around by the download manager as long as space is available.
            DESTINATION_CACHE_PARTITION_NOROAMING = 3, This download will be saved to the download manager's private partition, as with
                DESTINATION_CACHE_PARTITION, but the download will not proceed if the user is on a roaming data connection.
            DESTINATION_FILE_URI = 4, This download will be saved to the location given by the file URI in {@link #COLUMN_FILE_NAME_HINT}.
            DESTINATION_SYSTEMCACHE_PARTITION = 5, This download will be saved to the system cache ("/cache") partition. This option is only
                used by system apps and so it requires android.permission.ACCESS_CACHE_FILESYSTEM permission.
            DESTINATION_NON_DOWNLOADMANAGER_DOWNLOAD = 6, This download was completed by the caller (i.e., NOT downloadmanager) and caller wants
                to have this download displayed in Downloads App.
    ui_visibility (int): The name of the column containing the flags that controls whether the download is displayed by
        the UI. See the VISIBILITY_* constants for a list of legal values.
        List of VISIBILITY_* constants :
            VISIBILITY_VISIBLE = 0, This download is visible but only shows in the notifications while it's in progress.
            VISIBILITY_VISIBLE_NOTIFY_COMPLETED = 1, This download is visible and shows in the notifications while
                in progress and after completion.
            VISIBILITY_HIDDEN = 2, This download doesn't show in the UI or in the notifications.
            VISIBILITY_VISIBLE_NOTIFY_ONLY_COMPLETION = 3, This download shows in the notifications after
            completion ONLY. It is usable only with {@link DownloadManager#addCompletedDownload
            (String, String, boolean, String, String, long, boolean)}
    e_tag (str) ETag of this file.
    description (str): The client-supplied description of this download. This will be displayed in system
        notifications. Defaults to the empty string.
  """

  DATA_TYPE = 'android:sqlite:downloads'

  def __init__(self):
    """Initializes event data."""
    super(AndroidNativeDownloadsEventData, self).__init__(data_type=self.DATA_TYPE)
    self.lastmod = None
    self.id = None
    self.uri = None
    self.mimetype = None
    self.total_bytes = None
    self.current_bytes = None
    self.status = None
    self.saved_to = None
    self.deleted = None
    self.notification_package = None
    self.title = None
    self.media_provider_uri = None
    self.error_msg = None
    self.is_visible_in_downloads_ui = None
    self.destination = None
    self.ui_visibility = None
    self.e_tag = None
    self.description = None


class AndroidNativeDownloadsPlugin(interface.SQLitePlugin):
  """SQLite parser plugin for Android native downloads database files.

  The Android native downloads database file is typically stored in:
  com.android.providers.downloads/databases/downloads.db
  """

  NAME = 'android_native_downloads'
  DATA_FORMAT = 'Android native downloads SQLite database (downloads.db) file'

  REQUIRED_STRUCTURE = {
      'downloads': frozenset(['_id', 'uri', '_data', 'mimetype', 'destination', 'visibility', 'status', 'lastmod',
                              'notificationpackage', 'total_bytes', 'current_bytes', 'etag', 'description',
                              'is_visible_in_downloads_ui', 'mediaprovider_uri', 'deleted', 'errorMsg'])}
  QUERIES = [
      ('SELECT _id, uri, _data, mimetype, destination, visibility, status, lastmod, '
          'notificationpackage, total_bytes, current_bytes, etag, description, '
          'is_visible_in_downloads_ui, mediaprovider_uri, deleted, errorMsg FROM downloads',
       'ParseDownloadsRow')]

  SCHEMAS = [{
      'android_metadata': (
          'CREATE TABLE android_metadata (locale TEXT) '),
      'downloads': (
          'CREATE TABLE downloads(_id INTEGER PRIMARY KEY AUTOINCREMENT, uri TEXT, method INTEGER, '
          'entity TEXT, no_integrity BOOLEAN, hint TEXT, otaupdate BOOLEAN, _data TEXT, mimetype TEXT, '
          'destination INTEGER, no_system BOOLEAN, visibility INTEGER, control INTEGER, status INTEGER, '
          'numfailed INTEGER, lastmod BIGINT, notificationpackage TEXT, notificationclass TEXT, '
          'notificationextras TEXT, cookiedata TEXT, useragent TEXT, referer TEXT, total_bytes INTEGER, '
          'current_bytes INTEGER, etag TEXT, uid INTEGER, otheruid INTEGER, title TEXT, description TEXT, ' 
          'scanned BOOLEAN, is_public_api INTEGER NOT NULL DEFAULT 0, allow_roaming INTEGER NOT NULL DEFAULT 0, '
          'allowed_network_types INTEGER NOT NULL DEFAULT 0, is_visible_in_downloads_ui INTEGER NOT NULL DEFAULT 1, '
          'bypass_recommended_size_limit INTEGER NOT NULL DEFAULT 0, mediaprovider_uri TEXT, '
          'deleted BOOLEAN NOT NULL DEFAULT 0, errorMsg TEXT, allow_metered INTEGER NOT NULL DEFAULT 1, '
          'allow_write BOOLEAN NOT NULL DEFAULT 0, flags INTEGER NOT NULL DEFAULT 0, mediastore_uri TEXT DEFAULT NULL)'),
      'request_headers': (
          'CREATE TABLE request_headers(id INTEGER PRIMARY KEY AUTOINCREMENT, download_id INTEGER NOT NULL, '
          'header TEXT NOT NULL,value TEXT NOT NULL)'),
      'sqlite_sequence': (
          'CREATE TABLE sqlite_sequence(name,seq)')}]

  def _GetDateTimeRowValue(self, query_hash, row, value_name):
    """Retrieves a date and time value from the row.

    Args:
      query_hash (int): hash of the query, that uniquely identifies the query
          that produced the row.
      row (sqlite3.Row): row.
      value_name (str): name of the value.

    Returns:
      dfdatetime.JavaTime: date and time value or None if not available.
    """
    timestamp = self._GetRowValue(query_hash, row, value_name)
    if timestamp is None:
      return None

    return dfdatetime_java_time.JavaTime(timestamp=timestamp)

  def ParseDownloadsRow(self, parser_mediator, query, row, **unused_kwargs):
    #TODO
    """Parses a download row.

    Args:
      parser_mediator (ParserMediator): mediates interactions between parsers
          and other components, such as storage and dfVFS.
      query (str): query that created the row.
      row (sqlite3.Row): row.
    """
    # query_hash = hash(query)

    event_data = AndroidNativeDownloadsEventData()
    # event_data.address = self._GetRowValue(query_hash, row, 'address')
    # event_data.body = self._GetRowValue(query_hash, row, 'body')
    # event_data.creation_time = self._GetDateTimeRowValue(
    #     query_hash, row, 'date')
    # event_data.offset = self._GetRowValue(query_hash, row, 'id')
    # event_data.query = query
    # event_data.sms_read = self._GetRowValue(query_hash, row, 'read')
    # event_data.sms_type = self._GetRowValue(query_hash, row, 'type')

    parser_mediator.ProduceEventData(event_data)


sqlite.SQLiteParser.RegisterPlugin(AndroidNativeDownloadsEventData)
