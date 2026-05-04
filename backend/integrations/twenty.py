import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

import httpx


logger = logging.getLogger(__name__)

TWENTY_GRAPHQL_URL = os.getenv("TWENTY_GRAPHQL_URL")
TWENTY_API_KEY = os.getenv("TWENTY_API_KEY")
TWENTY_ENABLED = os.getenv("TWENTY_ENABLED", "true").lower() in {"1", "true", "yes"}

CREATE_ZADACHA_STUDENTA_MUTATION = """
mutation CreateZadachaStudenta($data: ZadachaStudentaCreateInput!) {
  createZadachaStudenta(data: $data) {
    id
  }
}
"""


def _iso(dt_value: Optional[datetime]) -> Optional[str]:
    if not dt_value:
        return None
    return dt_value.isoformat()


def create_zadacha_studenta_record(student_task: Any) -> Optional[Dict[str, Any]]:
    if not TWENTY_ENABLED:
        return None
    if not TWENTY_GRAPHQL_URL or not TWENTY_API_KEY:
        logger.warning("Twenty CRM sync skipped: missing TWENTY_GRAPHQL_URL or TWENTY_API_KEY")
        return None

    payload_data = {
        "idStudTask": float(student_task.id),
        "studentId": float(student_task.student_id),
        "taskId": float(student_task.task_id),
        "deadline": _iso(student_task.deadline),
        "status": student_task.status,
        "completedAt": _iso(student_task.completed_at),
        "name": f"Task {student_task.task_id} for student {student_task.student_id}",
    }
    payload_data = {key: value for key, value in payload_data.items() if value is not None}

    body = {
        "query": CREATE_ZADACHA_STUDENTA_MUTATION,
        "variables": {"data": payload_data},
    }
    headers = {"Authorization": f"Bearer {TWENTY_API_KEY}"}

    try:
        response = httpx.post(TWENTY_GRAPHQL_URL, json=body, headers=headers, timeout=10.0)
        response.raise_for_status()
        payload = response.json()
        if payload.get("errors"):
            logger.warning("Twenty CRM returned errors: %s", payload["errors"])
        return payload
    except Exception as exc:
        logger.warning("Failed to sync StudentTask to Twenty CRM: %s", exc)
        return None
