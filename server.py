from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
import json
import mimetypes
import os
import re
import sqlite3
import sys
import unicodedata


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOT_DIR, "data", "finelle.sqlite")
SCHEMA_PATH = os.path.join(ROOT_DIR, "db", "schema.sqlite.sql")
PORT = int(sys.argv[1] if len(sys.argv) > 1 else os.environ.get("PORT", "4173"))

MONTHS = [
    "Januari", "Februari", "Maret", "April", "Mei", "Juni",
    "Juli", "Agustus", "September", "Oktober", "November", "Desember",
]

DIVISIONS = [
    "Premium",
    "Sports",
    "Retail",
    "NTOP",
    "Event DD",
    "POP Culture Malls",
    "Event DH",
    "Studios",
    "Starlight",
    "FV",
    "Finance",
    "HR & GA",
    "Accounting",
    "Operational",
    "Creative",
    "Commerce",
]

SEED_EMPLOYEES = [
    {
        "name": "Patogap Sianturi",
        "access_role": "corporate",
        "divisions": ["Premium", "Sports"],
        "salary": [10000000, 0, 288000, 599040, 0, 0],
    },
    {
        "name": "Anna",
        "access_role": "user",
        "divisions": ["Retail"],
        "salary": [5000000, 0, 157436, 327467, 0, 0],
    },
    {
        "name": "Andini Muliawati",
        "access_role": "user",
        "divisions": ["NTOP"],
        "salary": [5000000, 0, 157436, 327467, 0, 0],
    },
    {
        "name": "Julian Widjaja",
        "access_role": "user",
        "divisions": ["Event DD", "Event DH"],
        "salary": [8000000, 100000, 209915, 537382, 0, 0],
    },
    {
        "name": "Alan Samantha",
        "access_role": "user",
        "divisions": ["POP Culture Malls"],
        "salary": [6000000, 100000, 157436, 327467, 0, 0],
    },
    {
        "name": "Muhammad Rizal",
        "access_role": "user",
        "divisions": ["Studios"],
        "salary": [7000000, 100000, 224000, 573440, 0, 0],
    },
    {
        "name": "Nicky",
        "access_role": "user",
        "divisions": ["Starlight", "FV"],
        "salary": [8000000, 100000, 222299, 572395, 0, 0],
    },
    {
        "name": "Khallensius Wijaya",
        "access_role": "finance",
        "divisions": ["Finance"],
        "salary": [5000000, 100000, 157436, 327467, 0, 0],
    },
    {
        "name": "Angela Chyntia PPER",
        "access_role": "corporate",
        "divisions": ["HR & GA"],
        "salary": [6000000, 100000, 157436, 327467, 0, 0],
    },
    {
        "name": "Fachrul Ramadhan",
        "access_role": "finance",
        "divisions": ["Accounting"],
        "salary": [6000000, 100000, 214735, 556662, 0, 0],
    },
    {
        "name": "Ceffie Setiyawan",
        "access_role": "user",
        "divisions": ["Operational", "Creative"],
        "salary": [10000000, 0, 262394, 537382, 0, 0],
    },
    {
        "name": "IK",
        "access_role": "admin",
        "divisions": ["Commerce", "Finance"],
        "salary": [15000000, 100000, 465474, 1199748, 0, 0],
    },
]

SALARY_FIELDS = [
    "base_salary",
    "phone_quota",
    "bpjs_kantor",
    "bpjs_sendiri",
    "debt",
    "rapel_thr",
]


def normalize_username(value):
    text = unicodedata.normalize("NFKD", str(value or "")).lower()
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    parts = [re.sub(r"[^a-z0-9]", "", part) for part in text.split()]
    parts = [part for part in parts if part]
    return ".".join(parts)


def unique_username(conn, name, exclude_employee_id=None):
    base = normalize_username(name) or "user"
    params = []
    query = "SELECT username FROM employees WHERE username IS NOT NULL AND username != ''"
    if exclude_employee_id is not None:
        query += " AND id != ?"
        params.append(exclude_employee_id)
    existing = {
        row[0]
        for row in conn.execute(query, params).fetchall()
    }
    if base not in existing:
        return base
    counter = 2
    while f"{base}.{counter}" in existing:
        counter += 1
    return f"{base}.{counter}"


def ensure_employee_auth_columns(conn):
    columns = {row[1] for row in conn.execute("PRAGMA table_info(employees)").fetchall()}
    if "username" not in columns:
        conn.execute("ALTER TABLE employees ADD COLUMN username TEXT NOT NULL DEFAULT ''")
    if "password" not in columns:
        conn.execute("ALTER TABLE employees ADD COLUMN password TEXT NOT NULL DEFAULT ''")
    if "can_login" not in columns:
        conn.execute("ALTER TABLE employees ADD COLUMN can_login INTEGER NOT NULL DEFAULT 0")
    rows = conn.execute("SELECT id, name, username, password FROM employees ORDER BY id").fetchall()
    used_usernames = {
        row[0]
        for row in conn.execute(
            "SELECT username FROM employees WHERE username IS NOT NULL AND username != ''"
        ).fetchall()
        if row[0]
    }
    for row in rows:
        employee_id = row[0]
        name = row[1]
        username = row[2] or ""
        password = row[3] or ""
        desired_username = normalize_username(name) or "user"
        if not username or username == "" or username != desired_username:
            candidate = desired_username
            counter = 2
            while candidate in used_usernames and candidate != username:
                candidate = f"{desired_username}.{counter}"
                counter += 1
            used_usernames.discard(username)
            used_usernames.add(candidate)
            username = candidate
            if not password:
                password = candidate
            conn.execute(
                "UPDATE employees SET username = ?, password = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (username, password or candidate, employee_id),
            )
        elif not password:
            conn.execute(
                "UPDATE employees SET password = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (username, employee_id),
            )
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_employees_username ON employees(username)")
    # Ensure can_login is set for any rows where it is NULL (new column migration only)
    conn.execute("UPDATE employees SET can_login = 0 WHERE can_login IS NULL")


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with connect() as conn:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as schema:
            conn.executescript(schema.read())
        ensure_employee_auth_columns(conn)

        if conn.execute("SELECT COUNT(*) FROM divisions").fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO divisions (name, sort_order) VALUES (?, ?)",
                [(name, index + 1) for index, name in enumerate(DIVISIONS)],
            )

        if conn.execute("SELECT COUNT(*) FROM employees").fetchone()[0] == 0:
            seed_period(conn, "2026-01")
            division_ids = {
                row["name"]: row["id"]
                for row in conn.execute("SELECT id, name FROM divisions")
            }
            for employee in SEED_EMPLOYEES:
                username = unique_username(conn, employee["name"])
                cursor = conn.execute(
                    "INSERT INTO employees (name, username, password, access_role, can_login) VALUES (?, ?, ?, ?, 1)",
                    (employee["name"], username, username, employee["access_role"]),
                )
                employee_id = cursor.lastrowid
                conn.executemany(
                    "INSERT INTO employee_divisions (employee_id, division_id) VALUES (?, ?)",
                    [
                        (employee_id, division_ids[division])
                        for division in employee["divisions"]
                    ],
                )
                conn.execute(
                    """
                    INSERT INTO monthly_salaries (
                      period, employee_id, base_salary, phone_quota, bpjs_kantor,
                      bpjs_sendiri, debt, rapel_thr
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    ("2026-01", employee_id, *employee["salary"]),
                )


def seed_period(conn, period):
    year, month = parse_period(period)
    conn.execute(
        """
        INSERT OR IGNORE INTO salary_periods (period, month, year)
        VALUES (?, ?, ?)
        """,
        (period, month, year),
    )


def parse_period(period):
    if not period or len(period) != 7 or period[4] != "-":
        raise ValueError("Period harus format YYYY-MM")
    year = int(period[:4])
    month = int(period[5:])
    if month < 1 or month > 12:
        raise ValueError("Bulan harus 01 sampai 12")
    return year, month


def previous_period(period):
    year, month = parse_period(period)
    month -= 1
    if month == 0:
        month = 12
        year -= 1
    return f"{year}-{month:02d}"


def role_from(handler):
    return handler.headers.get("X-Role", "user").lower()


def require_role(handler, allowed):
    role = role_from(handler)
    if role not in allowed:
        raise PermissionError("Akses tidak diizinkan untuk role ini")
    return role


def rows_to_dicts(rows):
    return [dict(row) for row in rows]


def get_divisions(conn):
    return rows_to_dicts(
        conn.execute("SELECT id, name, sort_order FROM divisions ORDER BY sort_order, name")
    )


def get_employees(conn):
    rows = conn.execute(
        """
        SELECT e.id, e.name, e.username, e.password, e.can_login, e.access_role, e.active,
               COALESCE(GROUP_CONCAT(d.name, '||'), '') AS division_names
        FROM employees e
        LEFT JOIN employee_divisions ed ON ed.employee_id = e.id
        LEFT JOIN divisions d ON d.id = ed.division_id
        WHERE e.active = 1
        GROUP BY e.id
        ORDER BY e.name COLLATE NOCASE
        """
    ).fetchall()
    employees = []
    for row in rows:
        item = dict(row)
        item["divisions"] = [
            division for division in item.pop("division_names").split("||") if division
        ]
        employees.append(item)
    return employees


def ensure_salary_period(conn, period):
    seed_period(conn, period)


def salary_total(row):
    return (
        float(row.get("base_salary") or 0)
        + float(row.get("phone_quota") or 0)
        + float(row.get("bpjs_kantor") or 0)
        + float(row.get("bpjs_sendiri") or 0)
        + float(row.get("rapel_thr") or 0)
        - float(row.get("debt") or 0)
    )


def get_salary_rows(conn, period):
    ensure_salary_period(conn, period)
    rows = conn.execute(
        """
        SELECT e.id AS employee_id, e.name, e.access_role,
               COALESCE(GROUP_CONCAT(DISTINCT d.name), '') AS division_names,
               COALESCE(ms.base_salary, 0) AS base_salary,
               COALESCE(ms.phone_quota, 0) AS phone_quota,
               COALESCE(ms.bpjs_kantor, 0) AS bpjs_kantor,
               COALESCE(ms.bpjs_sendiri, 0) AS bpjs_sendiri,
               COALESCE(ms.debt, 0) AS debt,
               COALESCE(ms.rapel_thr, 0) AS rapel_thr
        FROM employees e
        LEFT JOIN employee_divisions ed ON ed.employee_id = e.id
        LEFT JOIN divisions d ON d.id = ed.division_id
        LEFT JOIN monthly_salaries ms
          ON ms.employee_id = e.id AND ms.period = ?
        WHERE e.active = 1
        GROUP BY e.id
        ORDER BY e.name COLLATE NOCASE
        """,
        (period,),
    ).fetchall()
    salaries = []
    for row in rows:
        item = dict(row)
        item["divisions"] = [
            division for division in item.pop("division_names").split(",") if division
        ]
        for field in SALARY_FIELDS:
            item[field] = float(item[field] or 0)
        item["total"] = salary_total(item)
        salaries.append(item)
    return salaries


def get_report(conn, period):
    divisions = get_divisions(conn)
    grouped = {
        division["name"]: {
            "division": division["name"],
            "employees": [],
            "employee_count": 0,
            "fte_share": 0,
            "total": 0,
        }
        for division in divisions
    }

    for salary in get_salary_rows(conn, period):
        employee_divisions = salary["divisions"] or []
        if not employee_divisions:
            continue
        split_count = len(employee_divisions)
        split_total = salary["total"] / split_count if split_count else 0
        split_share = 1 / split_count if split_count else 0
        for division in employee_divisions:
            if division not in grouped:
                grouped[division] = {
                    "division": division,
                    "employees": [],
                    "employee_count": 0,
                    "fte_share": 0,
                    "total": 0,
                }
            grouped[division]["employees"].append(
                {
                    "employee_id": salary["employee_id"],
                    "name": salary["name"],
                    "split_count": split_count,
                    "allocated_total": split_total,
                    "full_total": salary["total"],
                }
            )
            grouped[division]["employee_count"] += 1
            grouped[division]["fte_share"] += split_share
            grouped[division]["total"] += split_total

    report_rows = list(grouped.values())
    report_rows.sort(key=lambda row: (-row["total"], row["division"]))
    return {
        "period": period,
        "rows": report_rows,
        "total": sum(row["total"] for row in report_rows),
    }


def save_salary_rows(conn, period, salaries):
    ensure_salary_period(conn, period)
    for item in salaries:
        employee_id = int(item.get("employee_id"))
        values = [float(item.get(field) or 0) for field in SALARY_FIELDS]
        conn.execute(
            """
            INSERT INTO monthly_salaries (
              period, employee_id, base_salary, phone_quota, bpjs_kantor,
              bpjs_sendiri, debt, rapel_thr, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(period, employee_id) DO UPDATE SET
              base_salary = excluded.base_salary,
              phone_quota = excluded.phone_quota,
              bpjs_kantor = excluded.bpjs_kantor,
              bpjs_sendiri = excluded.bpjs_sendiri,
              debt = excluded.debt,
              rapel_thr = excluded.rapel_thr,
              updated_at = CURRENT_TIMESTAMP
            """,
            (period, employee_id, *values),
        )


def sync_employee_divisions(conn, employee_id, divisions):
    division_ids = [
        row["id"]
        for row in conn.execute(
            "SELECT id FROM divisions WHERE name IN ({})".format(
                ",".join("?" for _ in divisions)
            ),
            divisions,
        )
    ] if divisions else []
    if not division_ids:
        raise ValueError("Pilih minimal satu divisi")
    conn.execute("DELETE FROM employee_divisions WHERE employee_id = ?", (employee_id,))
    conn.executemany(
        "INSERT INTO employee_divisions (employee_id, division_id) VALUES (?, ?)",
        [(employee_id, division_id) for division_id in division_ids],
    )


def dashboard_payload(conn, period):
    salaries = get_salary_rows(conn, period)
    report = get_report(conn, period)
    total = sum(item["total"] for item in salaries)
    employees = get_employees(conn)
    multi_division = sum(1 for employee in employees if len(employee["divisions"]) > 1)
    top_division = next((row for row in report["rows"] if row["total"] > 0), None)
    periods = rows_to_dicts(
        conn.execute(
            "SELECT period, month, year, status FROM salary_periods ORDER BY period DESC"
        )
    )
    return {
        "period": period,
        "employee_count": len(employees),
        "multi_division_count": multi_division,
        "total_payroll": total,
        "top_division": top_division,
        "periods": periods,
        "division_totals": report["rows"],
        "activities": [
            {
                "icon": "database",
                "title": "SQLite aktif",
                "description": "Data aplikasi tersimpan di data/finelle.sqlite.",
            },
            {
                "icon": "content_copy",
                "title": "Template bulanan",
                "description": "Finance dapat menyalin isi salary dari bulan sebelumnya.",
            },
            {
                "icon": "schema",
                "title": "Schema portable",
                "description": "Schema PostgreSQL dan MySQL tersedia di folder db.",
            },
        ],
    }


class AppHandler(BaseHTTPRequestHandler):
    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_GET(self):
        try:
            parsed = urlparse(self.path)
            if parsed.path.startswith("/api/"):
                self.handle_api_get(parsed.path, parse_qs(parsed.query))
            else:
                self.serve_static(parsed.path)
        except Exception as error:
            self.send_json({"error": str(error)}, 500)

    def do_POST(self):
        self.handle_write("POST")

    def do_PUT(self):
        self.handle_write("PUT")

    def do_DELETE(self):
        self.handle_write("DELETE")

    def handle_api_get(self, path, query):
        period = query.get("period", ["2026-01"])[0]
        with connect() as conn:
            if path == "/api/bootstrap":
                self.send_json(
                    {
                        "divisions": get_divisions(conn),
                        "employees": get_employees(conn),
                        "months": MONTHS,
                        "default_period": "2026-01",
                    }
                )
            elif path == "/api/salaries":
                self.send_json({"period": period, "rows": get_salary_rows(conn, period)})
            elif path == "/api/report":
                self.send_json(get_report(conn, period))
            elif path == "/api/dashboard":
                self.send_json(dashboard_payload(conn, period))
            else:
                self.send_json({"error": "Endpoint tidak ditemukan"}, 404)

    def handle_write(self, method):
        try:
            parsed = urlparse(self.path)
            path = parsed.path
            payload = self.read_json() if method in ("POST", "PUT") else {}
            with connect() as conn:
                if path == "/api/salaries" and method == "POST":
                    require_role(self, {"admin", "finance"})
                    period = payload.get("period", "2026-01")
                    save_salary_rows(conn, period, payload.get("salaries", []))
                    conn.commit()
                    self.send_json({"ok": True, "rows": get_salary_rows(conn, period)})
                elif path == "/api/copy-template" and method == "POST":
                    require_role(self, {"admin", "finance"})
                    target_period = payload.get("period")
                    source_period = payload.get("source_period") or previous_period(target_period)
                    seed_period(conn, target_period)
                    copied = conn.execute(
                        """
                        INSERT INTO monthly_salaries (
                          period, employee_id, base_salary, phone_quota, bpjs_kantor,
                          bpjs_sendiri, debt, rapel_thr, notes, updated_at
                        )
                        SELECT ?, employee_id, base_salary, phone_quota, bpjs_kantor,
                               bpjs_sendiri, debt, rapel_thr, notes, CURRENT_TIMESTAMP
                        FROM monthly_salaries
                        WHERE period = ?
                        ON CONFLICT(period, employee_id) DO UPDATE SET
                          base_salary = excluded.base_salary,
                          phone_quota = excluded.phone_quota,
                          bpjs_kantor = excluded.bpjs_kantor,
                          bpjs_sendiri = excluded.bpjs_sendiri,
                          debt = excluded.debt,
                          rapel_thr = excluded.rapel_thr,
                          notes = excluded.notes,
                          updated_at = CURRENT_TIMESTAMP
                        """,
                        (target_period, source_period),
                    ).rowcount
                    if copied == 0:
                        raise ValueError(f"Data bulan {source_period} belum tersedia")
                    conn.commit()
                    self.send_json(
                        {
                            "ok": True,
                            "source_period": source_period,
                            "rows": get_salary_rows(conn, target_period),
                        }
                    )
                elif path == "/api/employees" and method == "POST":
                    require_role(self, {"admin"})
                    divisions = payload.get("divisions") or []
                    name = payload.get("name", "").strip()
                    if not name:
                        raise ValueError("Nama karyawan wajib diisi")
                    username = unique_username(conn, name)
                    password = (payload.get("password") or username).strip() or username
                    can_login = 1 if payload.get("can_login", False) else 0
                    cursor = conn.execute(
                        "INSERT INTO employees (name, username, password, can_login, access_role) VALUES (?, ?, ?, ?, ?)",
                        (
                            name,
                            username,
                            password,
                            can_login,
                            payload.get("access_role", "user"),
                        ),
                    )
                    sync_employee_divisions(conn, cursor.lastrowid, divisions)
                    conn.commit()
                    self.send_json({"ok": True, "employees": get_employees(conn)})
                elif path == "/api/login" and method == "POST":
                    payload = payload or {}
                    username = (payload.get("username") or "").strip()
                    password = (payload.get("password") or "").strip()
                    if not username or not password:
                        raise ValueError("Username dan password wajib diisi")
                    row = conn.execute(
                        "SELECT id, username, password, access_role, can_login, active FROM employees WHERE username = ?",
                        (username,),
                    ).fetchone()
                    if not row:
                        raise ValueError("User tidak ditemukan")
                    if not row[5]:
                        raise PermissionError("Akun tidak aktif")
                    if not row[4]:
                        raise PermissionError("Akun tidak diberi akses login")
                    if password != row[2]:
                        raise PermissionError("Password salah")
                    # set a simple cookie with user id (insecure, kept minimal)
                    body = json.dumps({"ok": True, "id": row[0], "username": row[1], "access_role": row[3]}, ensure_ascii=False).encode("utf-8")
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.send_header("Content-Length", str(len(body)))
                    self.send_header("Set-Cookie", f"finelle_user={row[0]}; Path=/")
                    self.end_headers()
                    self.wfile.write(body)
                elif path.startswith("/api/employees/") and method == "PUT":
                    require_role(self, {"admin"})
                    employee_id = int(path.rsplit("/", 1)[1])
                    name = payload.get("name", "").strip()
                    role = payload.get("access_role", "user")
                    password = payload.get("password", "").strip()
                    can_login = 1 if payload.get("can_login", False) else 0
                    if not name:
                        raise ValueError("Nama karyawan wajib diisi")
                    if role not in {"admin", "corporate", "finance", "user"}:
                        raise ValueError("Role tidak valid")
                    username = unique_username(conn, name, exclude_employee_id=employee_id)
                    if not password:
                        password = conn.execute(
                            "SELECT password FROM employees WHERE id = ?",
                            (employee_id,),
                        ).fetchone()[0]
                    conn.execute(
                        """
                        UPDATE employees
                        SET name = ?, username = ?, password = ?, can_login = ?, access_role = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                        """,
                        (name, username, password, can_login, role, employee_id),
                    )
                    sync_employee_divisions(conn, employee_id, payload.get("divisions") or [])
                    conn.commit()
                    self.send_json({"ok": True, "employees": get_employees(conn)})
                elif path.startswith("/api/employees/") and method == "DELETE":
                    require_role(self, {"admin"})
                    employee_id = int(path.rsplit("/", 1)[1])
                    conn.execute(
                        "UPDATE employees SET active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                        (employee_id,),
                    )
                    conn.commit()
                    self.send_json({"ok": True, "employees": get_employees(conn)})
                elif path == "/api/upload-excel" and method == "POST":
                    role = require_role(self, {"admin", "finance", "user"})
                    data = payload.get("data", [])
                    period = payload.get("period", "2026-01")
                    if not data:
                        raise ValueError("Data Excel kosong")

                    # Build normalized name map for fuzzy matching to reduce mismatch on upload
                    def _normalize(s):
                        import unicodedata
                        if not s:
                            return ""
                        s = str(s)
                        s = unicodedata.normalize('NFKD', s)
                        s = ''.join(ch for ch in s if not unicodedata.combining(ch))
                        s = ''.join(ch for ch in s.lower() if ch.isalnum())
                        return s

                    employee_rows = conn.execute("SELECT id, name FROM employees WHERE active = 1").fetchall()
                    name_map = { _normalize(row['name']): row['id'] for row in employee_rows }
                    ensure_salary_period(conn, period)
                    created = 0
                    updated = 0
                    divisions_synced = 0
                    for row in data:
                        name = str(row.get("name", "")).strip()
                        if not name:
                            continue

                        # Check if employee exists using normalized name map first
                        norm_name = _normalize(name)
                        existing = None
                        existing_id = name_map.get(norm_name)
                        if existing_id:
                            existing = conn.execute("SELECT id FROM employees WHERE id = ?", (existing_id,)).fetchone()

                        if role == "user":
                            # user role: only update bpjs_kantor and bpjs_sendiri for existing employees
                            # never create new employees, never touch other fields or divisions
                            if not existing:
                                continue
                            bpjs_kantor = float(row.get("bpjs_kantor") or 0)
                            bpjs_sendiri = float(row.get("bpjs_sendiri") or 0)
                            if bpjs_kantor or bpjs_sendiri:
                                conn.execute(
                                    """
                                    INSERT INTO monthly_salaries (
                                      period, employee_id, bpjs_kantor, bpjs_sendiri, updated_at
                                    ) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                                    ON CONFLICT(period, employee_id) DO UPDATE SET
                                      bpjs_kantor = excluded.bpjs_kantor,
                                      bpjs_sendiri = excluded.bpjs_sendiri,
                                      updated_at = CURRENT_TIMESTAMP
                                    """,
                                    (period, existing["id"], bpjs_kantor, bpjs_sendiri),
                                )
                                updated += 1
                            name_map[_normalize(name)] = existing["id"]
                        else:
                            # Map field names to their values; null means "not present in Excel" -> skip update
                            def _fval(v):
                                return None if v is None else float(v)

                            field_map = {
                                "base_salary":  _fval(row.get("base_salary")),
                                "phone_quota":  _fval(row.get("phone_quota")),
                                "bpjs_kantor":  _fval(row.get("bpjs_kantor")),
                                "bpjs_sendiri": _fval(row.get("bpjs_sendiri")),
                                "debt":         _fval(row.get("debt")),
                                "rapel_thr":    _fval(row.get("rapel_thr")),
                            }
                            # Only fields explicitly present in Excel (non-None)
                            present = {k: v for k, v in field_map.items() if v is not None}

                            if existing:
                                # Update only the fields present in the Excel row
                                if present:
                                    set_clause = ", ".join(f"{k} = ?" for k in present)
                                    values = list(present.values())
                                    conn.execute(
                                        f"""
                                        INSERT INTO monthly_salaries (
                                          period, employee_id, {', '.join(present.keys())}, updated_at
                                        ) VALUES (?, ?, {', '.join('?' for _ in present)}, CURRENT_TIMESTAMP)
                                        ON CONFLICT(period, employee_id) DO UPDATE SET
                                          {set_clause},
                                          updated_at = CURRENT_TIMESTAMP
                                        """,
                                        (period, existing["id"], *values, *values),
                                    )
                                    updated += 1

                                # Update divisions from Excel (replace)
                                divisions = row.get("divisions") or []
                                if divisions:
                                    sync_employee_divisions(conn, existing["id"], divisions)
                                    divisions_synced += 1

                                name_map[_normalize(name)] = existing["id"]
                            else:
                                # Create new employee with divisions from Excel
                                emp_role = row.get("access_role", "user")
                                new_username = unique_username(conn, name)
                                cursor = conn.execute(
                                    "INSERT INTO employees (name, username, password, access_role) VALUES (?, ?, ?, ?)",
                                    (name, new_username, new_username, emp_role),
                                )
                                new_id = cursor.lastrowid
                                divisions = row.get("divisions") or []
                                if divisions:
                                    sync_employee_divisions(conn, new_id, divisions)

                                name_map[_normalize(name)] = new_id

                                # For new employees, use 0 for any missing fields
                                insert_values = [
                                    float(field_map.get("base_salary") or 0),
                                    float(field_map.get("phone_quota") or 0),
                                    float(field_map.get("bpjs_kantor") or 0),
                                    float(field_map.get("bpjs_sendiri") or 0),
                                    float(field_map.get("debt") or 0),
                                    float(field_map.get("rapel_thr") or 0),
                                ]
                                conn.execute(
                                    """
                                    INSERT INTO monthly_salaries (
                                      period, employee_id, base_salary, phone_quota, bpjs_kantor,
                                      bpjs_sendiri, debt, rapel_thr, updated_at
                                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                                    """,
                                    (period, new_id, *insert_values),
                                )
                                created += 1
                    conn.commit()
                    self.send_json({
                        "ok": True,
                        "period": period,
                        "created": created,
                        "updated": updated,
                        "divisions_synced": divisions_synced,
                        "total_processed": created + updated,
                        "rows": get_salary_rows(conn, period),
                    })
                else:
                    self.send_json({"error": "Endpoint tidak ditemukan"}, 404)
        except PermissionError as error:
            self.send_json({"error": str(error)}, 403)
        except Exception as error:
            self.send_json({"error": str(error)}, 400)

    def serve_static(self, path):
        if path in ("", "/"):
            path = "/index.html"
        safe_path = os.path.normpath(path.lstrip("/"))
        file_path = os.path.join(ROOT_DIR, safe_path)
        if not file_path.startswith(ROOT_DIR) or not os.path.isfile(file_path):
            self.send_response(404)
            self.end_headers()
            return
        content_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
        with open(file_path, "rb") as file:
            body = file.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print("%s - %s" % (self.address_string(), fmt % args))


if __name__ == "__main__":
    init_db()
    server = ThreadingHTTPServer(("127.0.0.1", PORT), AppHandler)
    print(f"Finelle running at http://127.0.0.1:{PORT}")
    server.serve_forever()
