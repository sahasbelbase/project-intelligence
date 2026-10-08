# Third-party skills

Skills in this folder come from other authors. Each one is copied verbatim from the upstream repository at the commit recorded in `registry.json`, and keeps its upstream `LICENSE` file next to it. The installer copies every file in each folder, including the license.

`registry.json` also lists skills we recommend but do not redistribute (`referenced`). Install those from upstream with the command given.

## Updating a vendored skill

1. Check that the upstream license still allows redistribution.
2. Download the files at a specific commit and read them before copying them in.
3. Replace the folder contents, then update `commit` in `registry.json`.
4. Run `python3 validation/test_runner.py`.

Do not edit vendored files. If a rule doesn't fit this framework, record the override in the persona or the framework skill that uses it.
