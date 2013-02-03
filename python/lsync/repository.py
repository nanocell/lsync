import os
import yaml
import copy

import storage
import utils

CONFIG_VERSION = 0
APPID = "lsync"

###################################################################################################

def _build_config_filepath(repo_root):
	return os.path.join(repo_root, ".lsync/config")

###################################################################################################

def find_repository_root(start_path):
	"""
	Search for the the .lsync/config file up the directory tree
	"""
	cur_path = os.path.abspath(start_path)
	while not os.path.isfile( _build_config_filepath(cur_path) ):
		if len(cur_path) <= 1:
			return None; # No config found
		cur_path = os.path.split(cur_path)[0]
	return cur_path

###################################################################################################

def _init_repository(repo_path, data, overwrite=False):
	"""
	Initialise a repository config in the specified directory with the given data.
	"""
	cfg_dir = os.path.join(repo_path, ".%s" %APPID)
	if not os.path.exists( repo_path ):
		raise Exception("Given repo destination does not exist.")
	if not os.path.exists( cfg_dir ):
		os.mkdir(cfg_dir)

	cfg_filename = os.path.join(cfg_dir, "config")
	if os.path.exists(cfg_filename):
		raise Exception("Repo config already exists. Set overwrite to force creation.")

	f = file(cfg_filename, "w")
	f.write(yaml.dump(data, default_flow_style=False))
	f.close()

###################################################################################################

def create_repository(repo_path, bucket_name, overwrite=False):
	"""
	Create a new repository configuration. Cannot nest repositories
	"""
	cfg_path = find_repository_root(repo_path);
	if cfg_path == repo_path:
		if not overwrite:
			raise Exception("Cannot create repository here. One exists here already.")
		else:
			print "Warning: overwriting repository."
	elif cfg_path is not None:
		raise Exception("Cannot create a repository inside another repository!")

	d = {}
	d["version"] = 0
	d["bucket_name"] = bucket_name
	d["files"] = {}
	# Initialise the repo in the given path with the above data
	_init_repository(repo_path, d);

	repo = Repository(repo_path)
	return repo;

###################################################################################################

class Repository:
	def __init__(self, repo_path):
		"""
		Initialise a repository object. 
		@repo_path Any path inside the repo. It will automatically locate the root
		"""
		self._root = None
		root = find_repository_root(repo_path)
		self._root = os.path.abspath(root);
		self._cfg = None
		self._read_config();

	###############################################################################################

	def __del__(self):
		"""
		Make sure the config is written to disk upon repo destruction
		"""
		self._write_config();

	###############################################################################################

	def _read_config(self):
		"""
		Load the config from the root of the repo
		"""
		cfg_file = _build_config_filepath(self._root)
		f = file(cfg_file, "r")
		d = yaml.load(f)
		f.close()
		self._cfg = d;

	###############################################################################################

	def _write_config(self):
		"""
		Write the config back into the root of the repo
		"""
		if self._root:
			cfg_file = _build_config_filepath(self._root)
			f = file(cfg_file, "w")
			f.write(yaml.dump(self._cfg, default_flow_style=False))
			f.close()
		else:
			print "Error. No repo root. Could not write config."

	###############################################################################################

	def get_root(self):
		"""
		Get the repo root
		"""
		return self._root

	###############################################################################################

	def get_bucket_name(self):
		"""
		Return the name of the bucket associated with this repo
		"""
		return self._cfg["bucket_name"]

	###############################################################################################

	def get_bucket_connection(self):
		"""
		Return a connection object to the bucket associated with this repo
		"""
		lsync.storage.Bucket( self.get_bucket_name() )

	###############################################################################################

	def get_file_in_repository(self, filepath):
		"""
		Converts the given filepath to be relative to the root of this repo
		"""
		abs_file = os.path.abspath( os.path.join(self._root, filepath) );
		if abs_file.startswith(self._root):
			fname = os.path.relpath(abs_file, self._root)
			return fname
		else:
			raise Exception("The file is not inside the repository: %s" % filepath)

	###############################################################################################

	def set_file_properties(self, filename, timestamp, filesize, md5):
		"""
		Set properties of the given file in the repo cache
		"""
		# Due to a bug in PYYAML, we cannot serialise/deserialise time-zone aware timecodes
		# correctly. Save them as a string instead.
		abs_file = os.path.abspath( os.path.join(self._root, filename) );
		utils.set_timestamp_on_file(abs_file, timestamp)
		str_timestamp = str(timestamp)
		self._cfg["files"][filename] = [str_timestamp, filesize, md5]

	###############################################################################################

	def get_file_properties(self, filename):
		"""
		@return tuple (filename, timestamp, filesize)
		"""
		d = self._cfg["files"].get(filename)
		
		# Parse the 'string' time-zone aware date.
		if d:
			d = copy.copy(d)
			d[0] = utils.parse_iso_date(d[0]);
			return d
		else:
			return None
		# if d:
		# 	# return (filename, d[0], d[1])
		# 	return d
		# return None

	###############################################################################################

	def remove_file_properties(self, filename):
		"""
		Remove the given file's properties from the repository cache
		"""
		d = self._cfg["files"].get(filename)
		if d is not None:
			del self._cfg["files"][filename];

	###############################################################################################

	def ls(self):
		"""
		Generate a listing of the files contained within this repository.
		@returns Dictionary, keyed by filename, that maps to tuple (timestamp, filesize, md5)
		"""
		file_dict = {}
		for root, dirs, files in os.walk(self._root):
			for f in files:
				fname = os.path.join(root, f)
				if fname.startswith("./"):
					fname = fname.split("./",1)[1]
				fname = self.get_file_in_repository(fname)
				full_path = os.path.join(self.get_root(), fname)
				if fname.startswith(".lsync"):
					continue;
				t = utils.get_timestamp_from_file(full_path)
				fs = utils.get_filesize_from_file(full_path)
				file_dict[fname] = (t, fs, None)
		return file_dict

	###############################################################################################

	def add_file(self, filename, timestamp, filesize):
		"""
		Adds a file to the repository. This will set the file timestamp, verify the file size, 
		and write all the given information into the repo cache.

		This method is typically used after a file has been downloaded from the server.
		"""
		pass

	###############################################################################################

	def remove_file(self, filename):
		"""
		Remove a file from the local repository
		"""
		fname = self.get_file_in_repository(filename)
		full_path = os.path.join(self.get_root(), fname)
		os.remove(full_path)
		self.remove_file_properties(fname)
		pass

	###############################################################################################
	
		
