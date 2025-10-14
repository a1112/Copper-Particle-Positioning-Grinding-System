from pathlib import Path
DEBUG = True

testFolder = Path(__file__).parent.parent.parent/"TestData"

app_host = "127.0.0.1"
app_port = 8010
log_level= "debug" if DEBUG else "info"
# Data provider mode for API/UI (sim for simulation, comm for external comms)
data_mode = 'sim'

