import os

from dotenv import load_dotenv


load_dotenv()


SERVER_URL = os.getenv(
    "PAYPRINT_SERVER_URL",
    "http://127.0.0.1:8000",
)

KIOSK_ID = os.getenv(
    "PAYPRINT_KIOSK_ID",
    "",
)

KIOSK_SECRET = os.getenv(
    "PAYPRINT_KIOSK_SECRET",
    "" ,
)

AGENT_NAME = os.getenv(
    "PAYPRINT_AGENT_NAME",
    "PayPrint Print Agent",
)

POLL_INTERVAL = int(
    os.getenv(
        "PAYPRINT_POLL_INTERVAL",
        "5",
    )
)
SUMATRA_PATH = os.getenv(
    "PAYPRINT_SUMATRA_PATH",
    os.path.join(
        os.environ.get("LOCALAPPDATA", ""),
        "SumatraPDF",
        "SumatraPDF.exe",
    ),
)

PRINTER_NAME = os.getenv(
    "PAYPRINT_PRINTER_NAME",
    "Hewlett-Packard HP LaserJet 1022",
)

PRINT_TIMEOUT = int(
    os.getenv("PAYPRINT_PRINT_TIMEOUT", "120")
)

DOWNLOAD_DIR = os.getenv(
    "PAYPRINT_DOWNLOAD_DIR",
    os.path.join(os.environ.get("TEMP", "."), "PayPrintAgent"),
)
