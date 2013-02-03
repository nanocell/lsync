lsync
=====

Cloud Sync utility to synchronize files in a collaborative fashion to amazon's S3 store.

lsync has the concept of a "file repository" which is associated (via a config file) with a specific bucket on Amazon's S3. The root of the file repository is indicated by a ".lsync" directory that contains the lsync configuration and a basic (yaml-based) file database.

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
- Add support for nested repositories
