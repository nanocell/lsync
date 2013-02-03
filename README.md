lsync
=====

Cloud Sync utility to synchronize files in a collaborative fashion to amazon's S3 store.

lsync has the concept of a "file repository" which is associated (via a config file) with a specific bucket on Amazon's S3. The root of the file repository is indicated by a ".lsync" directory that contains the lsync configuration and a basic (yaml-based) file database.

Getting Started:
=====

Set up your S3 storage, buckets and then your AWS secret keys for 'boto' python module, either in /etc/boto.cfg or as environment variables:

    AWS_ACCESS_KEY_ID - Your AWS Access Key ID
    AWS_SECRET_ACCESS_KEY - Your AWS Secret Access Key

See this page for more information: http://boto.readthedocs.org/en/latest/s3_tut.html
    
Create a new directory, and initialise the lsync repository

    $ mkdir mystuff && cd mystuff
    $ lsync init my_bucket .
    $ touch some_new_file
    $ lsync sync
    
The 'sync' action should synchronise your empty file to the remote 'my_bucket' bucket.

Usage:
=====

Initialise a repository:
-----

Run the init action with the directory you want to set as the repository root:

    $ lsync init <bucket_name> <repo_path>

Syncing a local repository
-----

**NOTE: You have to run cmdline lsync from within a local repo**

**Sync the full repository:**

    $ lsync sync

**Sync files recursively starting at the current directory:**

    $ lsync sync .

**Sync a list of files:**

    $ lsync sync foo1 foo2 foo3 [...]

Push and Pull from a local repository
-----
The above sync behaviour applies to 'push' and 'pull' actions too.
Pull changes from the remote to the local repository:

    $ lsync pull

Push changes from the local to the remote repository:

    $ lsync push
    
Notes
-----
A 'sync' action combines a push and a pull. It will first pull new / modified data from the remote bucket, and then push any newer / modified files back to the remote bucket.

'sync' is the action that is typically used unless the user needs to do more advanced repo manipulation such as resetting the local repository to mirror the remote one exactly, or vice versa. Or possibly just force a push of a specific file irrespective of whether the remote copy is newer or not.

Roadmap
-----

- Finish implementation of behaviour documented above
- Add support for resume-able uploads/downloads
- Add support for nested repositories
- Add support for detection of moved files, and perform server/client side moves
- Add support for removing empty directories (locally and remotely)
- Add 'lsync resolve' action
- Add support for GoogleStore

Known Issues:
-----
- Only Amazon S3 is supported at the moment
- CTRL+C interruption of download just as file finished but before the file was written into 
  local repo config will cause a file to have downloaded with lsync 'knowing' about it. Not entirely
  critical but may lead unexpected behaviour during local/remote file deletion attempts.
