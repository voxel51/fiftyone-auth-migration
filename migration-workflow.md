# Migrating Fiftyone Teams Auth
This document will help operators migrate an existing Fiftyone Teams
deployment from `legacy` mode to `internal` mode. This will remove the
dependency on Auth0 as a user management system.

## Terms
Fiftyone Teams now has two modes: `legacy` and `internal`.

`legacy` mode is fully dependent on an Auth0 connection to handle
authentication and user management.

By contrast, `internal` mode functions by moving user management to within
the system. After an initial migration of users, operators of Fiftyone Teams
may continue to use Auth0 as an identity provider (IdP) to facilitate
authentication while keeping all other aspects of user management internal.

Additionally, operators may choose to change the target IdP to be something
other than Auth0. This allows individual clients to choose to use their own
IdP as it suits their needs, as well as allows the possibility of running
Fiftyone Teams fully offline, including user management (assuming the client
brings their own offline IdP, such as KeyCloak).


## Requirements
- A running version of Fiftyone Teams version>=1.6.0

- The Fiftyone Auth Migration Script: 
    - https://github.com/voxel51/fiftyone-auth-migration

    - Cloned locally and installed (See [README.md](./README.md) for the script)

- Access to modify environment variables in the running deployment


## Steps

1. Take any action in Fiftyone Teams running in `legacy` mode that interacts
with users. This could include signing in or listing users, as an example.

2. Setup the `.env` file for the Auth Migration Script. See the example template
([env.template](./env.template)). Follow the steps in the README as necessary to ensure the
script is installed and ready to run.

3. The Auth Migration Script must be run in a location that has access
to call REST APIs in the running deployment. This may mean running in the same
cluster as the deployment or in the same network as the VM that runs
Fiftyone Teams.

4. Before running the Auth Migration Script, switch the Fiftyone Teams
deployment to `internal` mode. This is done by updating the `FIFTYONE_AUTH_MODE`
environment variable from `legacy` to `internal`. 

NOTE: After switching to `internal` mode and before running the Auth Migration
Script, users will be unable to log in.

5. Run the Auth Migration Script. The script will move users and organizations
from an existing Auth0 tenant to the new internal system that will manage users
moving forward. 

5a. The script will inform if the migration was successful or if there were
issues. If the script informs that an auth config was not found, it can be
populated by taking any action in the existing Fiftyone Teams deployment that
interacts with users, such as navigating to the user list page in the Admin
Settings.

5b. The script can be run again at this point safely to see that the warning
no longer appears. 

6. Once the script has run succesfully, Fiftyone Teams is now running in 
`internal` mode and the existing users, orgs, and their permissions
will be preserved.

