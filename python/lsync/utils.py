
import os
import datetime
import time

import dateutil

###################################################################################################

def get_timestamp_from_file(filepath, verbose=False):
	"""
	Return non-naive UTC timestamp for the given file
	"""
	timestamp = os.path.getmtime(filepath)
	from_zone = dateutil.tz.tzlocal()
	t = datetime.datetime.fromtimestamp(timestamp, tz=from_zone)
	if verbose:
		print "file tstamp: ", filepath, t
	return t

###################################################################################################

def set_timestamp_on_file(filepath, tstamp, verbose=False):
	"""
	Set non-naive timestamp, given datetime timestamp object
	"""
	# Set the modified time of the downloaded file to match that of the remote file
	d = tstamp.astimezone(dateutil.tz.tzlocal()) # Local time
	t = int(time.mktime( d.timetuple() ))
	if verbose:
		print "setting time on file:", filepath, t, tstamp
	os.utime(filepath, (t,t))

###################################################################################################

def get_filesize_from_file(filepath):
	return os.path.getsize(filepath)

###################################################################################################

def parse_iso_date(iso_date, verbose=False):
	GMT = dateutil.tz.gettz('UTC')                  #label for GMT
	d = dateutil.parser.parse(iso_date)
	d = d.astimezone(GMT)
	LOCAL = dateutil.tz.tzlocal()
	if verbose:
		print "given date: ", iso_date
		print "GMT: ", d
		print "LOCAL: ", d.astimezone(LOCAL)
	return d

###################################################################################################