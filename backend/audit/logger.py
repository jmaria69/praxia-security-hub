"""Cryptographic & Structured Audit Logger for Praxia Security Hub."""
import hashlib
import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Optional
from backend.core.config import settings

class AuditLogger:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or settings.AUDIT_STORAGE_DB
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                project_id TEXT,
                severity TEXT NOT NULL,
                user TEXT NOT NULL,
                action TEXT NOT NULL,
                details_json TEXT NOT NULL,
                payload_hash TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                project_id TEXT,
                category TEXT NOT NULL,
                severity TEXT NOT NULL,
                summary TEXT NOT NULL,
                details_json TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'OPEN'
            )
        """)
        conn.commit()
        conn.close()

    def log_event(
        self,
        event_type: str,
        action: str,
        severity: str = "INFO",
        project_id: Optional[str] = None,
        user: str = "system",
        details: Optional[dict[str, Any]] = None,
        sensitive_payload: Optional[str] = None
    ) -> int:
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        details = details or {}
        
        # NEVER log raw plaintext prompts or secrets
        payload_hash = None
        if sensitive_payload:
            payload_hash = hashlib.sha256(sensitive_payload.encode("utf-8")).hexdigest()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO audit_events 
            (timestamp, event_type, project_id, severity, user, action, details_json, payload_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (now, event_type, project_id, severity, user, action, json.dumps(details), payload_hash))
        event_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return event_id

    def log_incident(
        self,
        category: str,
        severity: str,
        summary: str,
        project_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None
    ) -> int:
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO security_incidents
            (timestamp, project_id, category, severity, summary, details_json, status)
            VALUES (?, ?, ?, ?, ?, ?, 'OPEN')
        """, (now, project_id, category, severity, summary, json.dumps(details or {})))
        incident_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return incident_id

    def list_events(self, limit: int = 50, project_id: Optional[str] = None) -> list[dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if project_id:
            cursor.execute("""
                SELECT * FROM audit_events WHERE project_id = ? ORDER BY id DESC LIMIT ?
            """, (project_id, limit))
        else:
            cursor.execute("SELECT * FROM audit_events ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        result = [dict(row) for row in rows]
        conn.close()
        return result

    def list_incidents(self, limit: int = 50, project_id: Optional[str] = None) -> list[dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        if project_id:
            cursor.execute("""
                SELECT * FROM security_incidents WHERE project_id = ? ORDER BY id DESC LIMIT ?
            """, (project_id, limit))
        else:
            cursor.execute("SELECT * FROM security_incidents ORDER BY id DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        result = [dict(row) for row in rows]
        conn.close()
        return result

audit_logger = AuditLogger()
