PayPrint Kiosk Display Frontend
===============================

Layout:
- Left 50%: QR code that opens the customer PDF upload page.
- Right 50%: Billing overview above, print queue below.
- Responsive layout for smaller screens.

FILES
-----
index.html
css/kiosk.css
js/config.js
js/kiosk.js

SETUP
-----
1. Extract this folder into:
   C:\Users\Fixit_Expert\Desktop\PayPrint_v2.1\frontend\PayPrint_Kiosk_Display

2. Open js/config.js and set:
   kioskId: "999"
   customerBaseUrl: "https://YOUR-PUBLIC-HOST/customer/index.html"

3. For a local-only design preview, you can keep:
   customerBaseUrl: "http://127.0.0.1:5502/index.html"
   That QR will NOT work on a different phone/network. localhost always means the device
   opening the link, not the kiosk computer.

CROSS-NETWORK CONNECTION REQUIREMENT
------------------------------------
A phone and kiosk can use different networks, but both must reach a public HTTPS service:
- deploy the customer frontend on a public host/domain; and
- expose the FastAPI backend through HTTPS (domain/reverse proxy or a secure tunnel);
- configure customer frontend API_BASE to the public backend URL;
- configure CORS to allow the deployed customer origin.
Do not expose the backend publicly without HTTPS and appropriate security controls.
Do not put kiosk secrets or Razorpay secret keys in frontend JavaScript.

UNIQUE CUSTOMER SESSIONS
------------------------
The QR includes kiosk_id. The current customer app creates a fresh customer session when
the customer submits "Start printing"; each successful POST /customer-sessions/start
returns a new session_id and session_token. Scanning alone does not create a session in
the current backend. Multiple customers can scan the same kiosk QR and each submit will
create a different session.

BILLING / QUEUE API INTEGRATION
-------------------------------
The visual panels are ready, but the live billing and queue API URLs are intentionally
blank in js/config.js. The API route names alone do not establish the response schema or
which routes are safe for public kiosk display. Confirm the existing admin dashboard and
queue GET endpoint contracts before configuring these URLs. Do not use kiosk authentication
secrets in a public browser page.

Preview:
  cd C:\Users\Fixit_Expert\Desktop\PayPrint_v2.1\frontend\PayPrint_Kiosk_Display
  ..\..\venv\Scripts\python.exe -m http.server 5503 --bind 127.0.0.1

Then open:
  http://127.0.0.1:5503/index.html

This is a frontend-only package; it does not modify existing APIs, payment flow, database,
or print agent.
