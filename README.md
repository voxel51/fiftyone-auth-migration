# NOTE: This repository is currently under construction

---

# Fiftyone Teams Auth Migration Script

## Intent

This tool is provided to help users move from the Legacy auth environments of Fiftyone Teams to the Internal environment.

Specifically, it helps facilitate moving organizations and users from an existing Auth0 Tenant to the Internal ecosystem so that user and role information can be preserved.

## Usage

Using python>=3.10, install requirements from the root:

```
pip install -r requirements.txt
```

Populate the values of the `config.py` file at the root. These values can be found in your Fiftyone Teams deployment. If you need help finding these files, please contact your Voxel51 Customer Success representative.

Run

```
python migrate.py
```

It is safe to run this script additional times if necessary. Existing users and orgs will be updated if found.

## TODO

- An editing/polishing pass on instructions in this README
- Additional messaging to the user on the activity of the script
