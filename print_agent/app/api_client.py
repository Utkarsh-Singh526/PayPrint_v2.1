import requests

from app.config import (
    SERVER_URL,
    KIOSK_ID,
    KIOSK_SECRET,
)


class PayPrintAPIClient:

    def __init__(self):
        self.server_url = SERVER_URL.rstrip("/")
        self.kiosk_id = KIOSK_ID
        self.kiosk_secret = KIOSK_SECRET

        self.access_token = None

    # --------------------------------------------------
    # KIOSK LOGIN
    # --------------------------------------------------

    def login(self):
        response = requests.post(
            f"{self.server_url}/kiosk/login",
            params={
                "kiosk_id": self.kiosk_id,
                "kiosk_secret": self.kiosk_secret,
            },
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        self.access_token = data["access_token"]

        return data

    # --------------------------------------------------
    # AUTH HEADERS
    # --------------------------------------------------

    def _headers(self):
        if not self.access_token:
            raise RuntimeError(
                "Agent is not authenticated"
            )

        return {
            "Authorization": (
                f"Bearer {self.access_token}"
            )
        }

    # --------------------------------------------------
    # KIOSK INFORMATION
    # --------------------------------------------------

    def get_kiosk_info(self):
        response = requests.get(
            f"{self.server_url}/kiosk/me",
            headers=self._headers(),
            timeout=10,
        )

        response.raise_for_status()

        return response.json()

    # --------------------------------------------------
    # HEARTBEAT
    # --------------------------------------------------

    def heartbeat(self):
        response = requests.post(
            f"{self.server_url}/kiosk/heartbeat",
            headers=self._headers(),
            timeout=10,
        )

        response.raise_for_status()

        return response.json()

    # --------------------------------------------------
    # NEXT PRINT JOB
    # --------------------------------------------------

    def get_next_job(self):
        response = requests.get(
            f"{self.server_url}/print-queue/next",
            headers=self._headers(),
            timeout=10,
        )

        response.raise_for_status()

        return response.json()

    # --------------------------------------------------
    # CLAIM JOB
    # --------------------------------------------------

    def claim_job(self, job_id):
        response = requests.post(
            f"{self.server_url}/print-queue/{job_id}/claim",
            headers=self._headers(),
            timeout=10,
        )

        response.raise_for_status()

        return response.json()


    
    # --------------------------------------------------
    # DOWNLOAD PDF FOR A CLAIMED JOB
    # --------------------------------------------------

    def download_document(self, job_id, destination_path):
        from pathlib import Path

        destination = Path(destination_path)
        destination.parent.mkdir(parents=True, exist_ok=True)

        response = requests.get(
            f"{self.server_url}/print-queue/{job_id}/document",
            headers=self._headers(),
            timeout=(10, 60),
            stream=True,
        )
        response.raise_for_status()

        try:
            content_type = response.headers.get(
                "Content-Type", ""
            ).lower()

            if "application/pdf" not in content_type:
                raise ValueError(
                    f"Expected PDF, received: {content_type}"
                )

            with destination.open("wb") as file:
                for chunk in response.iter_content(
                    chunk_size=64 * 1024
                ):
                    if chunk:
                        file.write(chunk)

            with destination.open("rb") as file:
                if file.read(5) != b"%PDF-":
                    raise ValueError(
                        "Downloaded file is not a valid PDF"
                    )

            return destination

        except Exception:
            destination.unlink(missing_ok=True)
            raise

        finally:
            response.close()



    # --------------------------------------------------
    # COMPLETE JOB
    # --------------------------------------------------

    def complete_job(self, job_id):
        response = requests.post(
            f"{self.server_url}/print-queue/{job_id}/complete",
            headers=self._headers(),
            timeout=10,
        )

        response.raise_for_status()

        return response.json()

    # --------------------------------------------------
    # FAILED JOB
    # --------------------------------------------------

    def fail_job(self, job_id, reason):
        response = requests.post(
            f"{self.server_url}/print-queue/{job_id}/failed",
            params={
                "reason": reason,
            },
            headers=self._headers(),
            timeout=10,
        )

        response.raise_for_status()

        return response.json()