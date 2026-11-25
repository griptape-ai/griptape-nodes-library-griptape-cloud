# Changelog

All notable changes to the Griptape Nodes Griptape Cloud Library will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and each version is
the `library_version` in `griptape_nodes_library.json`.
**Breaking** marks a change that can stop a saved workflow from working without edits.

## [Unreleased]

<!-- Entries go in changelog.d/, one file each. See changelog.d/README.md. -->

## [0.77.0] - 2026-11-25

### Deprecated

- The Griptape Cloud Library declares itself deprecated, so the editor shows it as deprecated and
  no longer maintained. Remove it from your installed libraries.
  [#53](https://github.com/griptape-ai/griptape-nodes-library-griptape-cloud/issues/53)

## [0.76.0] - 2026-11-20

### Changed

- **Breaking:** Griptape Cloud Library requires engine 0.105.0 or later. Update the engine before
  updating the library.
  [#42](https://github.com/griptape-ai/griptape-nodes-library-griptape-cloud/issues/42)
- Griptape Cloud nodes report failures as structured node errors. A missing or refused
  `GT_CLOUD_API_KEY` links to Settings, and an API failure shows Griptape Cloud's own message with
  the status code, request ID and response under "More info". A missing key is reported on its own
  when a node runs, and inputs are checked when the node runs instead of at flow start.
  [#42](https://github.com/griptape-ai/griptape-nodes-library-griptape-cloud/issues/42)

### Deprecated

- `Get Assistant` and `Run Assistant` are deprecated because Griptape Cloud Assistants are no longer
  supported. The editor flags them when the library or a workflow that uses them loads, and a later
  version removes them.
  [#2555](https://github.com/griptape-ai/griptape-cloud/issues/2555)
- `Get Structure`, `Run Structure` and `Griptape Cloud Published Workflow` are deprecated because
  Griptape Cloud Structures are no longer supported. `Griptape Cloud Start Flow` and
  `Griptape Cloud End Flow` are deprecated too; use `Start Flow` and `End Flow` instead. The editor
  flags them when the library or a workflow that uses them loads, and a later version removes them.

### Removed

- Workflows can no longer be published to Griptape Cloud. The editor no longer offers
  "Publish to Griptape Cloud".

### Fixed

- Griptape Cloud nodes added before `GT_CLOUD_API_KEY` is set now load, and ask for the key when
  they run. Get Assistant, Get Bucket and Get Structure still need the key to load.
  [#42](https://github.com/griptape-ai/griptape-nodes-library-griptape-cloud/issues/42)
- A Griptape Cloud error such as a rate limit or a gateway failure now shows a readable message
  with the status code, instead of `unexpected response type <class 'NoneType'>`.
  [#42](https://github.com/griptape-ai/griptape-nodes-library-griptape-cloud/issues/42)

[Unreleased]: https://github.com/griptape-ai/griptape-nodes-library-griptape-cloud/compare/v0.77.0...HEAD
[0.77.0]: https://github.com/griptape-ai/griptape-nodes-library-griptape-cloud/compare/v0.76.0...v0.77.0
[0.76.0]: https://github.com/griptape-ai/griptape-nodes-library-griptape-cloud/compare/v0.74.0...v0.76.0
