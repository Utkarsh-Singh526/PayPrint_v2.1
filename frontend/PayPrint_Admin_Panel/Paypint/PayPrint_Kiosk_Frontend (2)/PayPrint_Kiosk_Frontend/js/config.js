/*
  PayPrint Kiosk Display configuration.
  IMPORTANT: Set customerBaseUrl to a publicly reachable HTTPS URL for cross-network use.
  Example: https://print.your-domain.in/customer/index.html
  Do NOT use localhost or 127.0.0.1 for customers' phones.
*/
window.PAYPRINT_KIOSK_CONFIG = {
  kioskId: "999",
  customerBaseUrl: "http://127.0.0.1:5502/index.html",
  // These API routes are intentionally left unset until the existing admin/dashboard
  // response shapes are confirmed. Do not point them at guessed endpoints.
  billingSummaryUrl: "",
  printQueueUrl: "",
  refreshIntervalMs: 5000
};
