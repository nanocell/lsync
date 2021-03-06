
import os
import sys
import utils
import boto.s3.connection

class Bucket:
	STORAGE="s3"

	###############################################################################################

	def __init__(self, bucket_name, debug=False, create_bucket=False):
		self._bucket_name = bucket_name
		self._debug = debug		
		self._conn = None
		self._bucket = None

		self._open_connection(create_bucket=create_bucket)

	###############################################################################################

	def _open_connection(self, create_bucket=False, bucket_region=''):
		"""
		Open a connection to the this bucket
		"""
		self._conn = boto.s3.connection.S3Connection()
		if create_bucket:
			self._bucket = self._conn.create_bucket(self._bucket_name, location=bucket_region)
		else:
			self._bucket = self._conn.get_bucket(self._bucket_name)

	###############################################################################################

	def bucket_name(self):
		"""
		Return the name of this bucket
		"""
		return self._bucket_name;

	###############################################################################################

	def ls(self):
		"""
		Perform an object listing for this bucket
		"""
		results = {}
		for key in self._bucket.list():
			fdate = utils.parse_iso_date(key.last_modified)
			results[key.name] = [fdate, key.size, key.etag]
		return results

	###############################################################################################

	def remove_file(self, remote_file):
		self._bucket.delete_key(remote_file)
		

	###############################################################################################

	def upload(self, local_file, remote_file, verbose=True):
		"""
		Upload a file into the current bucket
		@return some relevent file properties
		"""
		global i
		ctr = ["-", "\\", "|", "/"]
		i = 0
		def callback(uploaded, total_size):
			global i
			i = (i + 1) % len(ctr)
			c = ctr[i]
			if total_size == 0:
				pct = 100
			else:
				pct = (uploaded/float(total_size))*100
			sys.stdout.write( "\r-> %d / %d (%d%s) %s" % (uploaded, total_size, pct, "%", c) )
			sys.stdout.flush()
			
		dst_uri = boto.storage_uri(self._bucket_name + "/" + remote_file, Bucket.STORAGE)
		
		if not verbose:
			callback = None

		f = file(local_file, "r")
		key = self._bucket.new_key(remote_file)
		key.set_contents_from_file(f, cb=callback)
		f.close()
		print ""

		# Update the key info
		key = self._bucket.get_key(remote_file)
		modified_date = utils.parse_iso_date(key.last_modified)
		
		return [modified_date, key.size, key.etag]

	###############################################################################################

	def download(self, remote_file, local_file, set_timestamp=True, verbose=True):
		"""
		Download a file from the bucket to the given local file path, and
		@return some relevent file properties
		"""		
		global i
		ctr = ["-", "\\", "|", "/"]
		i = 0
		def callback(uploaded, total_size):
			global i
			i = (i + 1) % len(ctr)
			c = ctr[i]
			if total_size == 0:
				pct = 100
			else:
				pct = (uploaded/float(total_size))*100
			sys.stdout.write( "\r <- [%d KB] %d / %d (%d%s) %s" % (total_size/1024, uploaded, total_size, pct, "%", c) )
			sys.stdout.flush()

		if not verbose:
			callback = None

		path, filen = os.path.split(local_file)
		if not os.path.exists(path) and len(path.strip()) > 0:
			os.makedirs(path);

		key = self._bucket.get_key(remote_file)
		key.get_contents_to_filename(local_file, cb=callback);
		print ""

		if set_timestamp:
			modified_date = utils.parse_iso_date(key.last_modified)
			utils.set_timestamp_on_file(local_file, modified_date)

		return [key.last_modified, key.size, key.md5]

	###############################################################################################