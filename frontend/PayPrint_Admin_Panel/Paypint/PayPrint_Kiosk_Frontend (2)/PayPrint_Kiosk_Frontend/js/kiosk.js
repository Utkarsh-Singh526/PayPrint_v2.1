(() => {
  "use strict";
  const cfg = window.PAYPRINT_KIOSK_CONFIG || {};
  const $ = id => document.getElementById(id);
  const kioskId = String(cfg.kioskId || new URLSearchParams(location.search).get("kiosk_id") || "999").trim();
  $("kioskLabel").textContent = `Kiosk ID: ${kioskId}`;
  const clock = () => $("clock").textContent = new Intl.DateTimeFormat("en-IN",{hour:"2-digit",minute:"2-digit",second:"2-digit"}).format(new Date());
  clock(); setInterval(clock,1000);

  function customerUrl() {
    const base = String(cfg.customerBaseUrl || "").trim();
    if (!base) throw new Error("Set customerBaseUrl in js/config.js.");
    const url = new URL(base, location.href);
    url.searchParams.set("kiosk_id", kioskId);
    return url.toString();
  }

  function showQr() {
    const holder = $("qrcode");
    holder.replaceChildren();
    if (typeof QRCode !== "function") {
      $("qrError").textContent = "QR library could not load. Check the kiosk's internet connection, or host qrcode.min.js locally.";
      $("qrError").classList.remove("hidden");
      return;
    }
    try {
      const url = customerUrl();
      new QRCode(holder, {text:url,width:250,height:250,colorDark:"#102e27",colorLight:"#ffffff",correctLevel:QRCode.CorrectLevel.H});
      $("connectionLabel").textContent = new URL(url).protocol === "https:" ? "Secure customer link" : "Local development link";
      if (new URL(url).hostname === "127.0.0.1" || new URL(url).hostname === "localhost") {
        $("qrError").textContent = "Development URL: this QR only works on the same computer. For phones on another network, configure a public HTTPS customer URL in js/config.js.";
        $("qrError").classList.remove("hidden");
      }
    } catch (err) {
      $("qrError").textContent = err.message || "Could not create the QR code.";
      $("qrError").classList.remove("hidden");
    }
  }

  function setQueue(jobs) {
    if (!Array.isArray(jobs)) return;
    const list = $("queueList");
    const normal = jobs.slice(0, 12);
    const printing = normal.filter(j => String(j.status || "").toUpperCase() === "PRINTING").length;
    const waiting = normal.filter(j => ["QUEUED","PENDING","PAID"].includes(String(j.status || "").toUpperCase())).length;
    const completed = normal.filter(j => String(j.status || "").toUpperCase() === "COMPLETED").length;
    $("queueCount").textContent = `${normal.length} job${normal.length === 1 ? "" : "s"}`;
    $("printingCount").textContent = printing;
    $("waitingCount").textContent = waiting;
    $("completedCount").textContent = completed;
    if (!normal.length) {
      list.innerHTML = '<div class="empty-queue"><span class="empty-icon">▤</span><b>Queue is clear</b><small>New paid print jobs will appear here.</small></div>';
      return;
    }
    list.innerHTML = normal.map(j => {
      const status = String(j.status || "QUEUED").toUpperCase();
      const cls = status === "PRINTING" ? "printing" : status === "COMPLETED" ? "completed" : "";
      const title = String(j.file_name || j.document_name || j.job_id || "Print job");
      const safe = s => String(s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
      return `<div class="job-row"><div><div class="job-name">${safe(title)}</div><div class="job-meta">${safe(j.pages ?? "—")} pages · ${safe(j.job_id || "Job")}</div></div><span class="job-badge ${cls}">${safe(status)}</span></div>`;
    }).join("");
  }

  async function refreshDashboard() {
    const urls = [cfg.billingSummaryUrl, cfg.printQueueUrl].filter(Boolean);
    if (!urls.length) return;
    try {
      if (cfg.billingSummaryUrl) {
        const r = await fetch(cfg.billingSummaryUrl, {cache:"no-store"});
        if (!r.ok) throw new Error(`Billing API returned ${r.status}`);
        const d = await r.json();
        // Expected optional shape: { paid_today: number, pages_today: number }
        if (Number.isFinite(Number(d.paid_today))) $("paidToday").textContent = new Intl.NumberFormat("en-IN",{style:"currency",currency:"INR",maximumFractionDigits:0}).format(Number(d.paid_today));
        if (Number.isFinite(Number(d.pages_today))) $("pagesToday").textContent = Number(d.pages_today).toLocaleString("en-IN");
        $("billingNote").textContent = "Live billing data";
        $("billingNote").previousElementSibling.className = "status-dot";
      }
      if (cfg.printQueueUrl) {
        const r = await fetch(cfg.printQueueUrl, {cache:"no-store"});
        if (!r.ok) throw new Error(`Queue API returned ${r.status}`);
        const d = await r.json();
        setQueue(Array.isArray(d) ? d : (d.jobs || d.items || []));
        $("queueNote").textContent = "Queue refreshed";
      }
      $("lastUpdated").textContent = `Updated ${new Date().toLocaleTimeString("en-IN",{hour:"2-digit",minute:"2-digit"})}`;
    } catch (err) {
      $("queueNote").textContent = "Dashboard API not connected";
      $("lastUpdated").textContent = "Check API/CORS";
      console.warn("PayPrint kiosk dashboard refresh:", err);
    }
  }

  showQr();
  refreshDashboard();
  setInterval(refreshDashboard, Math.max(3000, Number(cfg.refreshIntervalMs) || 5000));
})();
