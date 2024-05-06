# NOTE: This repository is currently under construction

---

# Fiftyone Teams Auth Migration Script

This tool is provided to help users move from the Legacy auth environments of Fiftyone Teams to the Internal environment.

Specifically, it helps facilitate moving organizations and users from an existing Auth0 Tenant to the Internal ecosystem so that user and role information can be preserved.

## Migrating FiftyOne Teams to internal mode

See the [migration workflow](./migration-workflow.md) document for instructions on how to use this repository to migrate your FiftyOne Teams deployment to `internal` auth mode.

Read more about FiftyOne authentication modes [here](https://docs.voxel51.com/teams/pluggable_auth.html#fiftyone-authentication-modes).



## Usage

### Setup

This script is designed to be used with a running version of Fiftyone Teams version >= 1.6.0.

> Note: For the script to run properly, your Fiftyone Teams deployment must be running in `internal` mode.

Using python>=3.10, install requirements from the root of this repository:

```
pip install -r requirements.txt
```

Create an environment file, `.env` at the root of the project by copying the [`env.template`](./env.template) file.

Copy the relevant values from your Fiftyone Teams deployment (the `.env` file for docker compose deployments or `values.yaml` file for Kubernetes deployments) to the newly created `.env` file in this project.

> If you have trouble locating these values or the `.env` or `values.yaml` file for your Fiftyone Teams deployment, please contact your Voxel51 Customer Success representative.

Set those variables for your current terminal session by running the following from the root of the project:

```
export $(grep -v '^#' .env | xargs)
```


After the environment variables for this repository have been set, you are ready to run the migration script.

### Running the migration

> **Warning**: Read the [migration workflow](./migration-workflow.md) document to ensure your FiftyOne Teams deployment is ready to be migrated.

```
python migrate.py
```

If needed, the script can be run additional times without duplicating data.

It will always attempt to retrieve all users in the provided Auth0 organization (the ORGANIZATION_ID in `config.py`)
and populate the internal database with the same user information.

Once completed, the specified organization and associated users will be available to use in Fiftyone Teams.
