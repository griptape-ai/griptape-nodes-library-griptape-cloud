- **Breaking:** `Get Assistant`, `Run Assistant`, `Get Structure`, `Run Structure`,
  `Griptape Cloud Published Workflow`, `Griptape Cloud Start Flow` and `Griptape Cloud End Flow`
  are removed, along with the Griptape Cloud published workflow template and the
  `GT_CLOUD_PUBLISH_BUCKET_ID`, `GT_CLOUD_PUBLISH_DOWNLOAD_MODELS` and
  `GT_CLOUD_PUBLISH_UPLOAD_TIMEOUT_SECONDS` settings. A saved workflow that uses one of these nodes
  no longer loads. Before updating, replace `Griptape Cloud Start Flow` and `Griptape Cloud End Flow`
  with `Start Flow` and `End Flow`, and delete the other nodes.
