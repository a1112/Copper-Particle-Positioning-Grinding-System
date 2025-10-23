"""Compatibility shims for legacy imports.

Historically, server modules imported configuration from ``app.server.CONFIG``.
Configuration now lives in ``app.config``, so this module simply proxies the
attributes consumers expect.
"""

from app import config as _config

DEBUG = _config.DEBUG
testFolder = _config.testFolder
app_host = _config.app_host
app_port = _config.app_port
log_level = _config.log_level
data_mode = _config.data_mode
data_endpoint = _config.data_endpoint

