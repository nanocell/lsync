
import os

###################################################################################################

def get_version():
    """
    @return The version of lsync.
    """
    return '0.0.0'

###################################################################################################

def pull_files(repo_obj, bucket_obj, verbose=False):
	"""
	Pull files from the given store object into the given directory

	@repo_obj Object representing the local file repository
	@bucket_obj Object representing remote bucket
	"""
	# remote_path = bucket_cache.bucket_name()
	# repo_path = bucket_cache.repo_path()

	remote_files = bucket_obj.ls();
	if verbose:
		# Find all the files on the remote side, and parse the output from gsutil
		print "REMOTE FILES:"	
		for f in sorted(remote_files):
			print f, remote_files[f]
		print "done."

	# Build a list of all the local files with timestamps and sizes
	local_files = repo_obj.ls()
	if verbose:
		print "LOCAL FILES:"	
		for f in sorted(local_files):
			print f, local_files[f]
		print "done."

	# Step 1: Remove remotely deleted files
	# Find files that exists locally (on disk and in cache), but not remotely, and remove them.
	print "======================================================="
	print " [pull] Remove remotely deleted files "
	print "======================================================="
	remotely_deleted_files = []
	for f in sorted(local_files):
		lfile = local_files[f]
		cfile = repo_obj.get_file_properties(f)
		if cfile and f not in remote_files and f in local_files:
			# If we have a file in the local repo, and in the repo cache (meaning it was transfered
			# at some point) but it is not present remotely anymore, it implies the files has been
			# remotely deleted. Therefor, delete it locally.

			# If the file on disk's time stamp matches the cache timestamp, delete it.
			# If it is newer than the cache entry, remove the outdated cache entry.
			
			# if cfile is None:
			# 	# We have a local file with the same name as a remote file, but wasn't 
			# 	# recorded as being downloaded with lsync. Generate conflict here
			# 	raise NotImplementedError("Conflict between local and remote file: %s" % (f))
			# else:
			if lfile[0] > cfile[0]:
				# The file on disk is newer than the cached entry. Don't delete the
				# local file, but remove the cached entry immediately
				if verbose: 
					print "Removing cached entry for file: ", f
				repo_obj.remove_files([f]);
			else:
				# This file should be deleted
				if verbose: 
					print "Appending file for deletion: ", f
				remotely_deleted_files.append(f)
		elif cfile is None and f in remote_files and f in local_files:
			# We have a local file with the same name as a remote file, but wasn't 
			# recorded as being downloaded with lsync. Generate conflict here
			raise NotImplementedError("Conflict between local and remote file: %s" % (f))


	# Delete remotely-removed files, and remove them from the cache
	for f in remotely_deleted_files:
		print "Deleting local file: %s" % f
		repo_obj.remove_file(f)

	print "======================================================="
	print " [pull] Download new/updated files"
	print "======================================================="
	
	# Step 2: Download new / remotely updated files
	# For each remote file, check whether we have a local copy. If we don't, copy the file over.
	# If we do, check whether the local file is older. If it is, copy the remote file locally.
	downloaded_files = {}
	for remote_file in sorted(remote_files):
		rfile = remote_files[remote_file]
		cfile = repo_obj.get_file_properties(remote_file)
		if remote_file in local_files:
			# Check the time difference between the remote and local file
			lfile = local_files[remote_file]
			if rfile[0] > remote_files[remote_file][0]:
				print "remote file is strictly newer. download file", rfile[0], lfile[0]
				pass
			else:
				print "local file up to date. skipping '%s'" % remote_file
				continue;
		elif cfile:
			# We have this file in the cache, and in the remote, but not locally, which
			# means this file has been deleted locally. If the remote file timestamp matches the
			# cached timestamp, don't download
			if rfile[0] <= cfile[0]:
				# No updates. Don't download.
				if verbose: print "No remote updates on missing (local) file. Skipping."
				print "file has been locally deleted. skipping '%s'" % remote_file
				continue
			else:
				if verbose: print "We have remote updates. Downloading file."

		# Make sure the filename is relative to the root of the repository
		fname = repo_obj.get_file_in_repository(remote_file)
		local_path = os.path.join(repo_obj.get_root(), fname)
		# Download the remote file
		print "[downloading] [%d KB] %s ..." % (rfile[1]/1024, remote_file)
		bucket_obj.download(remote_file, local_path);
		
		#Register the file after download
		repo_obj.set_file_properties(remote_file, rfile[0], rfile[1], rfile[2])

	return

###################################################################################################

def push_files(repo_obj, bucket_obj, verbose=False):
	"""
	Push files from the local path to the remote location

	@store_obj Store from which the files should be retrieved
	@remote_path Retrieve all files recursively start at the given remote path
	@dest Destination for the store
	"""
	remote_files = bucket_obj.ls();
	if verbose:
		print "REMOTE FILES:"	
		for f in remote_files:
			print f, remote_files[f]
		print "done."

	# Build a list of all the local files with timestamps and sizes
	local_files = repo_obj.ls()
	if verbose:
		print "LOCAL FILES:"	
		for f in local_files:
			print f, local_files[f]
		print "done."

	print "======================================================="
	print " [push] Remove remote files"
	print "======================================================="
	# Step 1: Determine which remote files should be removed
	for f in sorted(remote_files):
		# Find remote files that is present in the repo cache, but not on disk
		file_properties = repo_obj.get_file_properties(f)
		if file_properties and f not in local_files:
			# Delete the remote file
			print "Deleting remote file: %s" % f
			bucket_obj.remove_file(f)
			# Remove the file properties from the repo cache
			repo_obj.remove_file_properties(f)
			

	print "======================================================="
	print " [push] Upload local files "
	print "======================================================="
	# Step 2: Determine which local files should be uploaded
	for f in sorted(local_files):
		lfile = local_files.get(f)
		rfile = remote_files.get(f)
		cfile = repo_obj.get_file_properties(f);
		if verbose:
			print "processing file: ", f
			print "cfile: ", cfile
			print "rfile: ", rfile
			print "lfile: ", lfile
		if rfile is not None:
			# If the remote file is newer, don't push
			if rfile[0] > lfile[0]:
				print "Remote file is strictly newer (>>). Skipping %s" % f
				continue

			if rfile[0] == lfile[0]:
				print "Remote file is up to date     (==). Skipping %s" % f
				continue

			if cfile and lfile[0] > cfile[0] and rfile[0] > cfile[0]:
				print "Conflict between local and remote file. Skipping: %s" % f
				print "Fix with 'lsync resolve' command"
				continue
		else:
			if verbose:
				print "No remote counterpart was found. Upload commencing..."

		# At this point, the local file is ready to be uploaded:
		if verbose:
			print "uploading: %s" % (f)
			if rfile:
				print "server time: ", rfile[0]
			print "local time: ", lfile[0]
		
		# Make sure the filename is relative to the root of the repository
		relname = repo_obj.get_file_in_repository(f)
		full_path = os.path.join(repo_obj.get_root(), relname)

		# Upload the current file
		print "[uploading] [%d KB] %s ..." % (lfile[1]/1024, relname)
		bucket_obj.upload(full_path, relname)
		#Register uploaded files immediately with the local repository
		repo_obj.set_file_properties( f, lfile[0], lfile[1], lfile[2] )

###################################################################################################

def sync_files(repo_obj, bucket_obj, verbose=False):
	"""
	Sync files between local repository and remote bucket by performing a pull, followed by a push.

	@repo_obj Instance of repository.Repository class
	@bucket_obj Instance of storage.Bucket class
	"""
	pull_files(repo_obj, bucket_obj, verbose=verbose)
	push_files(repo_obj, bucket_obj, verbose=verbose)

###################################################################################################