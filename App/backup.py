import datetime
import os
import shutil
import subprocess
import tempfile

BACKUP_DIR = os.getenv("BACKUP_DIR", "backups")
DEFAULT_MYSQL_BIN = r"C:\Program Files\MySQL\MySQL Server 8.0\bin"


def _resolve_tool(exe_name: str) -> str | None:
    mysql_bin = os.getenv("MYSQL_BIN", DEFAULT_MYSQL_BIN)
    candidate = os.path.join(mysql_bin, exe_name)
    if os.path.isfile(candidate):
        return candidate
    return shutil.which(exe_name)


def _run_with_defaults_file(tool_path: str, host: str, user: str, password: str, database: str,
                            stdin_file=None, stdout_file=None):
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as cfg:
        cfg.write("[client]\n")
        cfg.write(f'host="{host}"\n')
        cfg.write(f'user="{user}"\n')
        cfg.write(f'password="{password}"\n')
        cfg_path = cfg.name

    try:
        cmd = [tool_path, f"--defaults-extra-file={cfg_path}", database]
        return subprocess.run(
            cmd,
            stdin=stdin_file,
            stdout=stdout_file,
            stderr=subprocess.PIPE,
            text=True,
        )
    finally:
        if os.path.isfile(cfg_path):
            os.remove(cfg_path)


def create_mysql_backup(user: str, password: str, database: str, host: str = "localhost") -> str | None:
    mysqldump_path = _resolve_tool("mysqldump.exe")
    if not mysqldump_path:
        print("[Σφάλμα] Δεν βρέθηκε mysqldump.")
        return None

    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(BACKUP_DIR, f"backup_{database}_{timestamp}.sql")

    try:
        print("Using mysqldump from:", mysqldump_path)
        with open(filename, "w", encoding="utf-8") as out:
            result = _run_with_defaults_file(
                mysqldump_path, host, user, password, database, stdout_file=out
            )

        if result.returncode != 0:
            print("[Σφάλμα] Η δημιουργία backup απέτυχε")
            print(result.stderr)
            if os.path.isfile(filename):
                os.remove(filename)
            return None

        print(f"[OK] Δημιουργήθηκε backup: {filename}")
        return filename
    except Exception as e:
        print("[Σφάλμα Backup]", e)
        if os.path.isfile(filename):
            os.remove(filename)
        return None


def restore_mysql_backup(user: str, password: str, database: str, backup_file: str,
                         host: str = "localhost") -> bool:
    if not os.path.isfile(backup_file):
        print(f"[Σφάλμα] Το αρχείο backup δεν βρέθηκε: {backup_file}")
        return False

    mysql_path = _resolve_tool("mysql.exe")
    if not mysql_path:
        print("[Σφάλμα] Δεν βρέθηκε mysql client.")
        return False

    try:
        print("Using mysql from:", mysql_path)
        with open(backup_file, "r", encoding="utf-8") as inp:
            result = _run_with_defaults_file(
                mysql_path, host, user, password, database, stdin_file=inp
            )

        if result.returncode != 0:
            print("[Σφάλμα] Η αποκατάσταση backup απέτυχε")
            print(result.stderr)
            return False

        print(f"[OK] Η βάση αποκαταστάθηκε από: {backup_file}")
        return True
    except Exception as e:
        print("[Σφάλμα Restore]", e)
        return False


def create_auto_backup() -> str | None:
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    database = os.getenv("DB_NAME", "asfalies")
    host = os.getenv("DB_HOST", "localhost")

    print("[INFO] Εκτελείται αυτόματο backup...")
    backup_file = create_mysql_backup(user, password, database, host)
    if backup_file:
        print(f"[OK] Αυτόματο backup ολοκληρώθηκε: {backup_file}")
    else:
        print("[ΣΦΑΛΜΑ] Το αυτόματο backup απέτυχε.")
    return backup_file


if __name__ == "__main__":
    create_auto_backup()