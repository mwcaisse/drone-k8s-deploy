#!/bin/bash

export PLUGIN_TEMPLATE=deployment.yml
export PLUGIN_SERVER=loclahost
export PLUGIN_TOKEN=TOKEN
export PLUGIN_CA="-----BEGIN CERTIFICATE-----
AAAAAAAAAAAAAAAAAAAAAAAAAAAAA
-----END CERTIFICATE-----"

python main.py