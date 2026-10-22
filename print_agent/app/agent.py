import time
import subprocess
from pathlib import Path

from app.api_client import PayPrintAPIClient
from app.config import (
    POLL_INTERVAL,
    SUMATRA_PATH,
    PRINTER_NAME,
    PRINT_TIMEOUT,
    DOWNLOAD_DIR,
)


class PrintAgent:
    def __init__(self):
        self.client = PayPrintAPIClient()
        self.sumatra_path = Path(SUMATRA_PATH)
        self.download_dir = Path(DOWNLOAD_DIR)

    def authenticate(self):
        print("Connecting to PayPrint Server...")
        data = self.client.login()
        print(f"Agent authenticated successfully: {data['kiosk_id']}")

    def check_kiosk(self):
        data = self.client.get_kiosk_info()
        print(
            f"Kiosk: {data['kiosk_id']} | "
            f"Name: {data['name']} | Active: {data['is_active']}"
        )

    def send_heartbeat(self):
        data = self.client.heartbeat()
        print(f"Heartbeat: {data['status']}")

    def mark_failed(self, job_id, reason):
        try:
            result = self.client.fail_job(job_id, reason[:500])
            print(f"Job marked FAILED: {result}")
        except Exception as error:
            print(
                f"WARNING: Could not mark job {job_id} FAILED: {error}"
            )

    def process_job(self, job):
        job_id = job["job_id"]
        pdf_path = self.download_dir / f"job_{job_id}.pdf"

        print()
        print("===================================")
        print("PRINT JOB FOUND")
        print("===================================")
        print(f"Job ID  : {job_id}")
        print(f"File    : {job.get('file_name', 'Unknown')}")
        print(f"Pages   : {job.get('pages', 'Unknown')}")
        print(f"Amount  : Rs {job.get('amount', 'Unknown')}")
        print(f"Status  : {job.get('status', 'Unknown')}")
        print("===================================")

        print("Claiming print job...")
        claim = self.client.claim_job(job_id)
        print(f"Claimed job: {claim.get('job_id', job_id)}")
        print(f"Job status: {claim.get('status', 'Unknown')}")

        # Download failure happens before any print is submitted.
        try:
            self.download_dir.mkdir(parents=True, exist_ok=True)
            self.client.download_document(job_id, pdf_path)
            print(f"PDF downloaded and validated: {pdf_path}")
        except Exception as error:
            print(f"PDF download failed: {error}")
            self.mark_failed(job_id, f"PDF download failed: {error}")
            pdf_path.unlink(missing_ok=True)
            return

        if not self.sumatra_path.is_file():
            self.mark_failed(job_id, "SumatraPDF executable not found")
            pdf_path.unlink(missing_ok=True)
            return

        print(f"Submitting PDF to printer: {PRINTER_NAME}")

        try:
            result = subprocess.run(
                [
                    str(self.sumatra_path),
                    "-print-to",
                    PRINTER_NAME,
                    "-silent",
                    str(pdf_path),
                ],
                capture_output=True,
                text=True,
                timeout=PRINT_TIMEOUT,
                check=False,
            )
        except subprocess.TimeoutExpired:
            # Printing may already have reached the Windows spooler.
            # Do not mark FAILED or automatically retry: that could
            # produce duplicate paper copies.
            print(
                f"WARNING: Print command timed out for job {job_id}. "
                "Job remains PRINTING for manual verification."
            )
            print(f"Keep this PDF for investigation: {pdf_path}")
            return
        except Exception as error:
            print(f"Could not run SumatraPDF: {error}")
            self.mark_failed(job_id, f"Could not start print command: {error}")
            pdf_path.unlink(missing_ok=True)
            return

        if result.returncode != 0:
            details = (result.stderr or result.stdout or "").strip()
            reason = f"SumatraPDF exited with code {result.returncode}"
            if details:
                reason += f": {details}"

            print(reason)
            self.mark_failed(job_id, reason)
            pdf_path.unlink(missing_ok=True)
            return

        print(
            "SumatraPDF returned success. This confirms command success, "
            "not physical paper delivery."
        )

        try:
            response = self.client.complete_job(job_id)
            print(f"Backend completion response: {response}")
            pdf_path.unlink(missing_ok=True)
        except Exception as error:
            # Do not print this job again automatically: it may already
            # have printed. Check backend status and printer output.
            print(
                f"WARNING: Print command succeeded, but backend completion "
                f"failed for job {job_id}: {error}"
            )
            print("Do not retry this job until its status is verified.")
            print(f"Local PDF retained at: {pdf_path}")

    def check_queue(self):
        data = self.client.get_next_job()
        job = data.get("job")

        if not job:
            print("No print job in queue.")
            return

        self.process_job(job)

    def run(self):
        self.authenticate()
        self.check_kiosk()

        print()
        print("PayPrint Print Agent is running.")
        print(f"Printer: {PRINTER_NAME}")
        print("Waiting for print jobs...")
        print()

        while True:
            try:
                self.send_heartbeat()
                self.check_queue()
            except Exception as error:
                print(f"Agent error: {error}")

            time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    PrintAgent().run()
