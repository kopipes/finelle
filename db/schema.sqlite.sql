PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS employees (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  username TEXT NOT NULL UNIQUE,
  password TEXT NOT NULL DEFAULT '',
  can_login INTEGER NOT NULL DEFAULT 0,
  access_role TEXT NOT NULL DEFAULT 'user'
    CHECK (access_role IN ('admin', 'corporate', 'finance', 'user')),
  active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS divisions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  sort_order INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS employee_divisions (
  employee_id INTEGER NOT NULL,
  division_id INTEGER NOT NULL,
  PRIMARY KEY (employee_id, division_id),
  FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
  FOREIGN KEY (division_id) REFERENCES divisions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS salary_periods (
  period TEXT PRIMARY KEY,
  month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
  year INTEGER NOT NULL,
  status TEXT NOT NULL DEFAULT 'draft'
    CHECK (status IN ('draft', 'submitted', 'approved')),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS monthly_salaries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  period TEXT NOT NULL,
  employee_id INTEGER NOT NULL,
  base_salary REAL NOT NULL DEFAULT 0,
  phone_quota REAL NOT NULL DEFAULT 0,
  bpjs_kantor REAL NOT NULL DEFAULT 0,
  bpjs_sendiri REAL NOT NULL DEFAULT 0,
  debt REAL NOT NULL DEFAULT 0,
  rapel_thr REAL NOT NULL DEFAULT 0,
  notes TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (period, employee_id),
  FOREIGN KEY (period) REFERENCES salary_periods(period) ON DELETE CASCADE,
  FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_employee_divisions_division_id
  ON employee_divisions(division_id);

CREATE INDEX IF NOT EXISTS idx_monthly_salaries_period
  ON monthly_salaries(period);

CREATE INDEX IF NOT EXISTS idx_monthly_salaries_employee_id
  ON monthly_salaries(employee_id);
