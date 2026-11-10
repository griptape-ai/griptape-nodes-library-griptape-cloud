- Griptape Cloud nodes report failures as structured node errors. A missing or refused
  `GT_CLOUD_API_KEY` links to Settings, and an API failure shows Griptape Cloud's own message with
  the status code, request ID and response under "More info". A missing key is reported on its own
  when a node runs, and inputs are checked when the node runs instead of at flow start.
  [#42](https://github.com/griptape-ai/griptape-nodes-library-griptape-cloud/issues/42)
