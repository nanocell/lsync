
import os
import dateutil
import datetime

###################################################################################################

def get_timestamp_from_file(filepath):
	"""
	Return non-naive UTC timestamp for the given file
	"""
	timestamp = os.path.getmtime(filepath)
	from_zone = dateutil.tz.tzlocal()
	t = datetime.datetime.fromtimestamp(timestamp, tz=from_zone)
	print "file tstamp: ", filepath, t
	return t

###################################################################################################

def set_timestamp_on_file(filepath, tstamp):
	"""
	Set non-naive timestamp, given datetime timestamp object
	"""
	# Set the modified time of the downloaded file to match that of the remote file
	d = tstamp.astimezone(dateutil.tz.tzlocal()) # Local time
	print "setting local time on file: ", d
	t = int(time.mktime( d.timetuple() ))
	print "setting time on file:", filepath, t, tstamp
	os.utime(filepath, (t,t))

###################################################################################################

def get_filesize_from_file(filepath):
	return os.path.getsize(filepath)

###################################################################################################

def parse_iso_date(iso_date):
	GMT = dateutil.tz.gettz('UTC')                  #label for GMT
	d = dateutil.parser.parse(iso_date)
	d = d.astimezone(GMT)
	print "given date: ", iso_date
	print "GMT: ", d
	LOCAL = dateutil.tz.tzlocal()
	print "LOCAL: ", d.astimezone(LOCAL)
	return d

###################################################################################################