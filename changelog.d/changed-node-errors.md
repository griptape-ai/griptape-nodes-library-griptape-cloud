- Griptape Cloud nodes report failures as structured node errors. A missing or refused
  `GT_CLOUD_API_KEY` shows a link to Settings and to the Griptape Cloud API keys page, and an API
  failure shows Griptape Cloud's own message with the status code, request ID and response under
  "More info". A missing key is reported on its own when a node runs, and the nodes no longer check
  inputs when the flow starts. Get Structure, Get Assistant, Get Bucket, Run Structure, Run
  Assistant, Upload Asset and Griptape Cloud Published Workflow are affected.
  [#42](https://github.com/griptape-ai/griptape-nodes-library-griptape-cloud/issues/42)
