"""
| Copyright 2017-2024, Voxel51, Inc.
| `voxel51.com <https://voxel51.com/>`_
|
"""

def generate_slug(name: str) -> str:
    """Generates a URL-friendly slug for a dataset name"""
    min_length = 1
    max_length = 100

    if not isinstance(name, str):
        raise ValueError(f"Expected string; found {name}, which is {type(name)}")

    partial = re.sub(r"[^a-zA-Z0-9\s\-\_\.\+]", "", name)
    partial = re.sub(r"[\s\+\.\_]", "-", partial)
    partial = re.sub(r"[-]{2,}", "-", partial)
    slug = partial.strip("-").lower()

    if len(slug) < min_length or len(slug) > max_length:
        raise ValueError(
            f"Invalid name length: {len(slug)}. Length must be between "
            f"{min_length} and {max_length}"
        )

    return slug
