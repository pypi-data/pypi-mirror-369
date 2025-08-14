# Quick contribution guide

```bash
    git clone git@github.com:ggrlab/otycyto

    #  Use uv-managed virtualenv
    uv sync  --python /bin/python3.11

    # Using your default python:
    # uv sync
    uv run pre-commit run --all-files
    uv run pre-commit autoupdate

    # Run common tasks via uv
    uv run pytest                # tests
    uv build                     # build sdist/wheel when ready to publish

    # Documentation
    uv run mkdocs build
    uv run mkdocs serve


    # Push to run the CI
    git push

    # To create a release,
    # 1. Create a tag
    git tag -a v0.0.4 -m "Release v0.0.4"
    # 2. Then push
    git push
    # Then open Releases -> "Draft a new release" -> "Choose a tag" -> pick v0.0.3 -> Publish.
    # https://github.com/ggrlab/otycyto/releases/new

```
