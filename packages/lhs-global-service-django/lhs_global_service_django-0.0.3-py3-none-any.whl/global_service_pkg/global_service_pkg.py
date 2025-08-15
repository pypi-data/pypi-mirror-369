import os
import json
import logging
import threading
import time
import socket
import requests
import configparser
from datetime import datetime
import cx_Oracle

# Configuration class for user-supplied settings
class GlobalServiceConfig:
    def __init__(self, GLOBAL_LOG_URL=None, PROJECT_TYPE=None, FAILED_LOG_FILE=None, FLUSH_INTERVAL_SEC=None, APP_CODE=None,
                 ORACLE_DB_HOST=None, ORACLE_DB_PORT=None, ORACLE_DB_SERVICE=None, ORACLE_USER=None, ORACLE_PASS=None, ORACLE_DSN=None):
        self.GLOBAL_LOG_URL = GLOBAL_LOG_URL or os.getenv("GLOBAL_LOG_URL")
        self.PROJECT_TYPE = PROJECT_TYPE or os.getenv("PROJECT_TYPE")
        self.FAILED_LOG_FILE = FAILED_LOG_FILE or os.getenv("FAILED_LOG_FILE")
        self.FLUSH_INTERVAL_SEC = FLUSH_INTERVAL_SEC or int(os.getenv("FLUSH_INTERVAL_SEC") or 15)
        self.APP_CODE = APP_CODE or os.getenv("APP_CODE")
        self.ORACLE_DB_HOST = ORACLE_DB_HOST or os.getenv("ORACLE_DB_HOST")
        self.ORACLE_DB_PORT = ORACLE_DB_PORT or os.getenv("ORACLE_DB_PORT")
        self.ORACLE_DB_SERVICE = ORACLE_DB_SERVICE or os.getenv("ORACLE_DB_SERVICE")
        self.ORACLE_USER = ORACLE_USER or os.getenv("ORACLE_DB_USER")
        self.ORACLE_PASS = ORACLE_PASS or os.getenv("ORACLE_DB_PASS")
        self.ORACLE_DSN = ORACLE_DSN or self._build_dsn()

    def _build_dsn(self):
        if self.ORACLE_DB_HOST and self.ORACLE_DB_PORT and self.ORACLE_DB_SERVICE:
            return cx_Oracle.makedsn(
                self.ORACLE_DB_HOST,
                int(self.ORACLE_DB_PORT),
                service_name=self.ORACLE_DB_SERVICE
            )
        return None

    def configure(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
        # Rebuild DSN if any DB param is updated and DSN not set directly
        if any(k in kwargs for k in ["ORACLE_DB_HOST", "ORACLE_DB_PORT", "ORACLE_DB_SERVICE"]):
            self.ORACLE_DSN = self._build_dsn()

# Singleton config instance
config = GlobalServiceConfig()

def flush_failed_logs():
    """
    Periodically send logs stored in the JSON file to the GLOBAL_LOG_URL.
    Only delete logs from the file after receiving a 200 OK response.
    """
    while True:
        try:
            if os.path.exists(config.FAILED_LOG_FILE):
                with open(config.FAILED_LOG_FILE, "r+", encoding="utf-8") as f:
                    logs = f.readlines()
                    if logs:
                        remaining_logs = []
                        for log in logs:
                            try:
                                payload = json.loads(log.strip())
                                resp = requests.post(config.GLOBAL_LOG_URL, json=payload, timeout=2.0)
                                if resp.status_code == 200:
                                    logging.info(f"Log sent successfully: {payload}")
                                else:
                                    logging.warning(f"Failed to send log (status {resp.status_code}): {payload}")
                                    remaining_logs.append(log)  # Keep the log if not successful
                            except Exception as e:
                                logging.warning(f"Failed to resend log: {e}")
                                remaining_logs.append(log)  # Keep the log if an exception occurs
                        # Rewrite the file with remaining logs
                        f.seek(0)
                        f.truncate()
                        f.writelines(remaining_logs)
        except Exception as e:
            logging.error(f"Error in periodic log flushing: {e}")
        time.sleep(config.FLUSH_INTERVAL_SEC)  # Wait for the specified interval before retrying

# Start the background thread
threading.Thread(target=flush_failed_logs, daemon=True).start()

# ── Utility: Hostname/IP detection ──
def resolve_hostname(ip: str) -> str:
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        return hostname
    except Exception as e:
        logging.warning(f"Could not resolve hostname for IP {ip}: {e}")
        return "unknown"

class MachineIPDetector:
    def get_info(self):
        try:
            hostname = socket.gethostname()
            ip_address = socket.gethostbyname(hostname)
            logging.debug(f"Detected machine IP address: {ip_address}, hostname: {hostname}")
            return ip_address, hostname
        except Exception as e:
            logging.error(f"Error detecting machine IP/hostname: {e}")
            return "Unknown", "Unknown"

MACHINE_IP, MACHINE_HOSTNAME = MachineIPDetector().get_info()

def get_app_version():
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'config.properties'))
    return config.get('APP VERSION', 'app_version', fallback="Unknown")

# ── Step-wise Logger ─
class StepLogger:
    def __init__(self):
        self.steps = []

    def log(self, step_name):
        self.steps.append(step_name)  # Save step name directly without timestamp or numbering

    def get_log_remark(self):
        return "\n".join(self.steps)

def get_real_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get("REMOTE_ADDR", "")

def build_global_log_payload(request, user_menu=None, logout_time=None, logout_method=None, app_version=None, request_body=None, response_body=None):
    session = request.session
    # Get client IP from X-Forwarded-For if present, else REMOTE_ADDR
    # x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    # if x_forwarded_for:
    #     client_ip = x_forwarded_for.split(',')[0].strip()
    # else:
    #     client_ip = request.META.get('REMOTE_ADDR', '')
    client_ip = get_real_client_ip(request)
    logging.info(f"Detected client IP: {client_ip} from headers: {request.META.get('HTTP_X_FORWARDED_FOR')}")
    browser_user_agent = session.get("client_browser", "")
    # Normalize 'UnKnown' and 'Unknown' (case-insensitive)
    if not browser_user_agent or browser_user_agent.lower().startswith("unknown"):
        browser_user_agent = request.META.get("HTTP_USER_AGENT", "")

    payload = {
        "APP_CODE": config.APP_CODE,
        "LOGIN_RRN": session.get("session_id", ""),
        "LOGIN_TIME": session.get("last_login", ""),
        "LOGOUT_TIME": logout_time or "",
        "LOGOUT_METHOD": logout_method or "",
        "APP_VERSION": app_version if app_version is not None else get_app_version(),
        "GROUP_CODE": session.get("group_code") or "LHS",
        "CLIENT_IP": session.get("client_address") or client_ip,
        "CLIENT_HOSTNAME": resolve_hostname(client_ip),
        "CALLING_APP_NAME": session.get("calling_app_name", ""),
        "SERVER_HOSTNAME": MACHINE_HOSTNAME,
        "BROWSER_USER_AGENT": browser_user_agent,
        "USER_USED_MENU": user_menu or request.path,
        "USER_CODE": session.get("user_code", ""),
        "LASTUPDATE": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "APPKEY": session.get("appkey", ""),
        "CALLING_APP_NAME": session.get("calling_app_name", ""),
        # "FLAG": "T",
    }
    return payload


def send_log_to_global_service(payload: dict):
    try:
        # Only process logs where LOGIN_RRN is not null or empty
        if payload.get("LOGIN_RRN"):
            resp = requests.post(config.GLOBAL_LOG_URL, json=payload, timeout=2.0)
            resp.raise_for_status()
    except Exception as e:
        logging.warning(f"Failed to send log to {config.GLOBAL_LOG_URL}, saving locally. Reason: {e}")
        try:
            # Save log locally only if LOGIN_RRN is not null or empty
            if payload.get("LOGIN_RRN"):
                with open(config.FAILED_LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(json.dumps(payload) + "\n")
        except Exception as e2:
            logging.error(f"Could not save failed log to file: {e2}")

# ── Oracle DB Logging ─
def save_step_logs_to_oracle(payload: dict, step_logger: 'StepLogger', request_body: str, response_body: str, log_type="INFO"):
    """
    Save each step in StepLogger as a separate row in LHSWMA_PY_WEB_ACTIVITY_LOGS.
    Prevent duplicate logs for the same session, endpoint, and step_name.
    """
    try:
        connection = cx_Oracle.connect(user=config.ORACLE_USER, password=config.ORACLE_PASS, dsn=config.ORACLE_DSN)
        cursor = connection.cursor()
        insert_sql = """
        INSERT INTO LHSWMA_PY_WEB_ACTIVITY_LOGS (
        ENTRY_ROWID_SEQ,  APP_CODE,LOGIN_RRN, ENDPOINT, LOG_TIMESTAMP, LOG_EVENT, LOG_EVENT_SLNO, LOG_REMARK, USER_CODE, LASTUPDATE, FLAG
        )
        VALUES (
          LHSWMA_PY_WEB_ACTIVITY_LOGS_SEQ.NEXTVAL, :app_code, :login_rrn, :endpoint, SYSDATE, :log_event, :log_event_slno, :log_remark, :user_code, SYSDATE, :flag
        )
        """
        check_sql = """
        SELECT COUNT(*) FROM LHSWMA_PY_WEB_ACTIVITY_LOGS
        WHERE LOGIN_RRN = :login_rrn
          AND ENDPOINT = :endpoint
          AND LOG_EVENT_SLNO = :log_event_slno
          AND LOG_REMARK = :log_remark
        """
        for idx, entry in enumerate(step_logger.steps, start=1):
            step_name = entry
            cursor.execute(check_sql, {
                "login_rrn": payload.get("LOGIN_RRN", ""),
                "endpoint": payload.get("ENDPOINT", ""),
                "log_event_slno": idx,
                "log_remark": step_name,
            })
            exists = cursor.fetchone()[0]
            if not exists:
                cursor.execute(insert_sql, {
                    "app_code": payload.get("APP_CODE", config.APP_CODE),
                    "login_rrn": payload.get("LOGIN_RRN", ""),
                    "endpoint": payload.get("ENDPOINT", ""),
                    "log_event": log_type,
                    "log_event_slno": idx,
                    "log_remark": step_name,
                    "user_code": payload.get("USER_CODE", ""),
                    "flag": payload.get("FLAG", "T"),
                })
        connection.commit()
    except Exception as e:
        logging.error(f"Failed to save step logs to Oracle DB: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
    # Clear logged steps to avoid duplicate inserts in subsequent calls
    step_logger.steps.clear()
