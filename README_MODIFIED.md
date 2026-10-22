# PayPrint Frontend — Modified Admin Workspace

This ZIP contains:
- `frontend/PayPrint_Admin_Panel/`: responsive Super Admin + Regular Admin portal.
- `frontend/PayPrint_Customer_Frontend/`: original customer printing frontend preserved.

## What changed
- Responsive card/box-based UI with a mobile sidebar, searchable admin and kiosk views, assignment management, modal forms and confirmation.
- English/Hindi UI toggle.
- Browser voice assistant: speaks the page summary and supports simple voice navigation commands. Speech features depend on browser/device support and microphone permission.
- Role-aware UI: Super Admin sees global metrics and management tabs; Regular Admin sees a restricted workspace and does not receive Super Admin navigation.
- Uses the existing API endpoints: `/auth/me`, `/auth/login-json` (preferred), `/admin/dashboard/overview`, and `/admin/management/{admins,kiosks,assignments}`.

## Run locally
1. Start the FastAPI backend on `http://127.0.0.1:8000`.
2. Serve `frontend/PayPrint_Admin_Panel/` with VS Code Live Server or:
   ```powershell
   cd "C:\Users\Fixit_Expert\Desktop\PayPrint_v2.1\frontend\PayPrint_Admin_Panel"
   ..\..\venv\Scripts\python.exe -m http.server 5501
   ```
3. Open `http://127.0.0.1:5501/login.html`.

## Backend notes before production
- The login UI first calls `POST /auth/login-json` with JSON. If the backend returns 404/405, it falls back to the legacy `POST /auth/login?email=...&password=...` route. Query-string passwords can appear in access logs; implement/use a JSON-body login endpoint and remove that fallback for production.
- Confirm CORS allows your exact frontend origin.
- Super Admin dashboard requires `/admin/dashboard/overview`; management requires the listed `/admin/management` routes.
- The Regular Admin portal is role-restricted in the UI, but a true assigned-kiosk operational dashboard needs backend endpoints that return only the current admin's assigned kiosks and scope inventory/pricing operations. Do not rely on UI hiding alone for security; backend authorization must enforce it.
- Set `API_BASE` in `admin.js` to your deployed backend URL before deployment. Do not put database passwords, JWT secrets, or Razorpay secret keys in frontend files.
- Voice assistant uses browser `SpeechSynthesis` and `SpeechRecognition`/`webkitSpeechRecognition`; not every browser supports voice input. Use HTTPS or localhost and allow microphone permission where required.
