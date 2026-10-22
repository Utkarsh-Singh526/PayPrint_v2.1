// Change API_BASE if your FastAPI server runs on another host/port.
const API_BASE = "http://10.232.196.179:8000";
const state = { sessionId:null, token:null, kioskId:null, document:null, job:null, order:null };
const $ = id => document.getElementById(id);
const panels = {upload:$("upload"),settings:$("settings"),status:$("status")};
function notice(message,type=""){const n=$("notice");n.textContent=message;n.className=`notice ${type}`;n.classList.remove("hidden");n.scrollIntoView({behavior:"smooth",block:"center"});}
function unlock(panel){panel.classList.remove("locked");}
function auth(){if(!state.token)throw Error("Session missing. Please start again.");return {"X-Session-Token":state.token};}
async function api(path,options={}){const r=await fetch(API_BASE+path,options);let data;try{data=await r.json()}catch{data={detail:await r.text()}}if(!r.ok)throw Error(data.detail||data.message||`Request failed (${r.status})`);return data;}
function esc(s){return String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));}
function money(n){return new Intl.NumberFormat("en-IN",{style:"currency",currency:"INR"}).format(Number(n));}

// Read the kiosk's public ID from the QR URL.
const params = new URLSearchParams(window.location.search);
const kioskIdFromQR = params.get("kiosk_id");
const kioskField = $("kiosk");
const sessionSubmitButton = $("sessionForm").querySelector(
    'button[type="submit"], input[type="submit"]'
);

if (kioskIdFromQR && kioskField) {
    kioskField.value = kioskIdFromQR.trim();
    kioskField.readOnly = true;
    kioskField.setAttribute("aria-label", "Kiosk ID detected from QR code");
} else {
    notice(
        "Kiosk ID missing. Please scan the QR code displayed on the PayPrint machine.",
        "error"
    );

    if (sessionSubmitButton) {
        sessionSubmitButton.disabled = true;
    }
}


$("sessionForm").addEventListener("submit",async e=>{e.preventDefault();const btn=e.submitter;btn.disabled=true;notice("Starting your sessionâ€¦");try{const d=await api("/customer-sessions/start",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({customer_name:$("name").value.trim(),kiosk_id:$("kiosk").value.trim()})});state.sessionId=d.session_id;state.token=d.session_token;state.kioskId=d.kiosk_id;unlock(panels.upload);document.querySelectorAll('[data-step="1"]').forEach(x=>x.classList.add("active"));e.target.querySelectorAll("input,button").forEach(x=>x.disabled=true);notice(`Session started for kiosk ${d.kiosk_id}. Upload your PDF.`,`success`);}catch(err){notice(err.message,"error");btn.disabled=false;}});
$("file").addEventListener("change",()=>{const f=$("file").files[0];$("fileName").textContent=f?f.name:"ï¼‹ Choose a PDF to upload";$("fileInfo").textContent=f?`${(f.size/1048576).toFixed(2)} MB`:"PDF only Â· Maximum 10 MB";$("uploadBtn").disabled=!f||!state.sessionId;});
$("uploadForm").addEventListener("submit",async e=>{e.preventDefault();const f=$("file").files[0];if(!f||(!f.name.toLowerCase().endsWith(".pdf")&&f.type!=="application/pdf"))return notice("Only PDF files are allowed.","error");if(f.size===0||f.size>10*1024*1024)return notice("PDF must be non-empty and 10 MB or smaller.","error");const b=$("uploadBtn");b.disabled=true;b.textContent="Uploadingâ€¦";try{const fd=new FormData();fd.append("file",f);const d=await api(`/customer-uploads/${state.sessionId}/pdf`,{method:"POST",headers:auth(),body:fd});state.document=d;$("docName").textContent=d.file_name;$("pages").textContent=`${d.page_count} pages Â· ${(d.file_size/1024).toFixed(1)} KB`;$("uploadResult").textContent=`PDF uploaded. ${d.page_count} page(s) detected.`;$("uploadResult").classList.remove("hidden");unlock(panels.settings);notice("PDF uploaded. Choose your print settings.","success");}catch(err){notice(err.message,"error");}finally{b.disabled=false;b.textContent="Upload PDF â†’";}});
$("jobForm").addEventListener("submit",async e=>{e.preventDefault();if(!state.document)return notice("Upload a PDF first.","error");const b=$("jobBtn");b.disabled=true;b.textContent="Calculatingâ€¦";try{const fd=new FormData(e.target);const d=await api(`/customer-print-jobs/${state.sessionId}`,{method:"POST",headers:{...auth(),"Content-Type":"application/json"},body:JSON.stringify({document_id:state.document.document_id,paper_size:fd.get("paper_size"),print_mode:fd.get("print_mode"),copies:Number($("copies").value)})});state.job=d;$("billPages").textContent=d.pages;$("amount").textContent=money(d.amount);$("bill").classList.remove("hidden");e.target.querySelectorAll("input,select,button").forEach(x=>x.disabled=true);notice("Price confirmed by server. Continue to payment when ready.","success");}catch(err){notice(err.message,"error");b.disabled=false;b.textContent="Calculate total â†’";}});
$("pay").addEventListener("click",async()=>{if(!state.job)return notice("Calculate the total first.","error");if(typeof Razorpay!=="function")return notice("Razorpay Checkout did not load. Check internet connection.","error");const b=$("pay");b.disabled=true;b.textContent="Preparing paymentâ€¦";try{const order=await api(`/customer-payments/${state.sessionId}/create-order/${encodeURIComponent(state.job.job_id)}`,{method:"POST",headers:auth()});state.order=order;const checkout=new Razorpay({key:order.key_id,amount:Math.round(Number(state.job.amount)*100),currency:order.currency||"INR",name:"PayPrint",description:`Print job ${state.job.job_id}`,order_id:order.razorpay_order_id,prefill:{name:$("name").value.trim()},theme:{color:"#0d6b56"},handler:verify,modal:{ondismiss:()=>{notice("Payment window closed. The job has not been queued. You can retry.","");b.disabled=false;b.textContent="Continue to payment â†’";}}});checkout.on("payment.failed",r=>{notice("Payment failed. The job has not been queued. Please retry.","error");b.disabled=false;b.textContent="Retry payment â†’";});checkout.open();}catch(err){notice(err.message,"error");b.disabled=false;b.textContent="Continue to payment â†’";}});
async function verify(r){notice("Verifying payment securely with PayPrintâ€¦");try{const d=await api(`/customer-payments/${state.sessionId}/verify`,{method:"POST",headers:{...auth(),"Content-Type":"application/json"},body:JSON.stringify({razorpay_order_id:r.razorpay_order_id,razorpay_payment_id:r.razorpay_payment_id,razorpay_signature:r.razorpay_signature})});$("statusTitle").textContent="Payment verified";$("statusContent").innerHTML=`<div class="result"><h3>âœ“ ${esc(d.message)}</h3><p>Job ID: <b>${esc(d.job_id||state.job.job_id)}</b></p><p>Status: <b>${esc(d.job_status||"QUEUED")}</b></p><p>Amount: <b>${esc(money(state.job.amount))}</b></p><p>Keep this tracking code for reference:</p><span class="tracking">${esc(state.job.tracking_code||"PAYPRINT")}</span></div>`;unlock(panels.status);$("pay").disabled=true;notice("Payment verified. Your print job is queued.","success");}catch(err){notice(`${err.message} Do not pay again immediately. Check payment status before retrying.`,"error");$("pay").disabled=false;$("pay").textContent="Retry verification / payment";}}
$("lang").addEventListener("click",()=>notice("Hindi labels are being added in the next UI pass. Payment and job logic is unchanged."));


