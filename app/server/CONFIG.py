from pathlib import Path

from app.config import DEBUG as GLOBAL_DEBUG, DATA_MODE, DATA_ENDPOINT

DEBUG = bool(GLOBAL_DEBUG)

testFolder = Path(__file__).parent.parent.parent / "TestData"

app_host = "127.0.0.1"
app_port = 8010
log_level = "debug" if DEBUG else "info"
# Data provider mode for API/UI (sim for simulation, runtime/comm for production).
data_mode = DATA_MODE
# Optional data endpoint when using runtime/production mode.
data_endpoint = DATA_ENDPOINT

