# PayPrint Customer Frontend

Copy `index.html`, `css/`, and `js/` into `C:\\Users\\Fixit_Expert\\Desktop\\PayPrint_v2.1\\frontend\\`.

## Local test
1. Start FastAPI from the `server` directory:
   `python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`
2. Open this `index.html` with VS Code Live Server (usually `http://127.0.0.1:5500/index.html?kiosk_id=999`).
3. Use an active kiosk ID in your database and a small, non-sensitive PDF.
4. Use Razorpay test credentials in the backend `.env`, never expose the secret in frontend code.

## CORS
Add the following once in `server/app/main.py` after `app = FastAPI(...)`; merge with existing CORS middleware if present:

```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500", "http://localhost:5500",
        "http://127.0.0.1:5501", "http://localhost:5501",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
```
Use your exact Live Server origin if the port differs. Do not use wildcard origins in production.

## Important
- If opening from a phone, `127.0.0.1` points to the phone, not the PC. Configure API_BASE to the PC's LAN IP, run Uvicorn on a trusted LAN interface, and configure CORS/firewall safely.
- Checkout requires internet and Razorpay test mode credentials.
- Price and stock are calculated by the server, not the browser.
- Live customer status polling is not yet wired because the existing queue status endpoint requires kiosk authentication. A customer-session-authorized status endpoint is a future backend step.
- Ensure backend deletes stored PDFs after successful print/retention policy before claiming automatic deletion in production.
