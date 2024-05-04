# Migrating Fiftyone Teams Auth
This document will help operators migrate an existing Fiftyone Teams
deployment from `legacy` mode to `internal` mode. This will remove the
dependency on Auth0 as a user management system.

## Terms
Fiftyone Teams now has two authentication modes: `legacy` and `internal`.

`legacy` mode is fully dependent on an Auth0 connection to handle
authentication and user management.

By contrast, `internal` mode functions by moving user management to within
the system. After an initial migration of users, operators of Fiftyone Teams
may continue to use Auth0 as an Identity Provider (IdP) to facilitate
authentication while keeping all other aspects of user management internal.

Additionally, operators may change the target IdP to be something
other than Auth0. This allows individual clients to choose to use their own
IdP as it suits their needs, as well as allows the possibility of running
Fiftyone Teams fully offline, including user management (assuming the client
brings their own offline IdP, such as KeyCloak).


## Requirements
- A running version of Fiftyone Teams version>=1.6.0

- The Fiftyone Auth Migration Script: 
    - https://github.com/voxel51/fiftyone-auth-migration

    - Cloned locally and installed (See [README.md](./README.md) for the script)

- Modifying environment variables in the running deployment


## Steps

1. Take any action in Fiftyone Teams running in `legacy` mode that interacts
with users. This could include signing in or listing users, as an example.

1. Setup the `.env` file for the Auth Migration Script. See the example template
([env.template](./env.template)). Follow the steps in the README as necessary to ensure the
script is installed and ready to run. Do not run `migrate.py` at this point.

1. Ensure that the `/cas` path is available for your FiftyOne Teams deployment. This may
require special steps if using path-based routing (see instructions for
[docker compose](https://github.com/voxel51/fiftyone-teams-app-deploy/tree/main/docker#central-authentication-service)
or [helm](https://helm.fiftyone.ai/#central-authentication-service) deployments).

4. Switch your Fiftyone Teams
deployment from `legacy` to `internal` mode.

    a. For docker compose deployments

    - Copy your `compose.override.yaml` and `.env` files into the `internal-auth` [directory of your fiftyone-teams-app-deploy](https://github.com/voxel51/fiftyone-teams-app-deploy/tree/main/docker/internal-auth) clone.
    - Set the `BASE_URL` variable in the `.env` file of your FiftyOne Teams deployment now in the `internal-auth` directory.
See the example [env.template](https://github.com/voxel51/fiftyone-teams-app-deploy/blob/main/docker/internal-auth/env.template).
    - [Deploy FiftyOne Teams](https://github.com/voxel51/fiftyone-teams-app-deploy/tree/main/docker#deploying-fiftyone-teams) in the `internal-auth` directory.
  
   b. For Kubernetes/helm deployments

   - In the [values.yaml](https://github.com/voxel51/fiftyone-teams-app-deploy/blob/3c063ba3e72b19df28e331b9353be1cde35829d0/helm/values.yaml#L87) file of your FiftyOne Teams deployment, switch the `FIFTYONE_AUTH_MODE` from `legacy` to `internal`.
   - [Deploy FiftyOne Teams](https://helm.fiftyone.ai/#deploying-fiftyone-teams).

> **NOTE**: After switching to `internal` mode and before running the Auth Migration
> Script, users will be unable to log in.

5. Run the [Auth Migration Script](./README.md#usage). The script will move users and organizations
from an existing Auth0 tenant to the new internal system that will manage users
moving forward. 

    1. The script will inform if the migration was successful or if there were
       issues. If the script informs that an auth config was not found, it can be
       populated by taking any action in the existing Fiftyone Teams deployment that
       interacts with users, such as navigating to the user list page in the Admin
       Settings.

    2. The script can be run again at this point safely to see that the warning
       no longer appears. 

6. Once the script has run succesfully, Fiftyone Teams is now running in 
`internal` mode and the existing users, orgs, and their permissions
will be preserved.

