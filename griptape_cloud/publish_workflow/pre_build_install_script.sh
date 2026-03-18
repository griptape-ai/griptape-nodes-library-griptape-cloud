#!/bin/bash

apt-get update && apt-get install -y curl gcc python3.12-dev
curl -LsSf https://astral.sh/uv/install.sh | sh