CREATE TABLE IF NOT EXISTS employees (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(160) NOT NULL UNIQUE,
  username VARCHAR(160) NOT NULL UNIQUE,
  password TEXT NOT NULL DEFAULT '',
  can_login BOOLEAN NOT NULL DEFAULT TRUE,
  access_role VARCHAR(20) NOT NULL DEFAULT 'user'
    CHECK (access_role IN ('admin', 'corporate', 'finance', 'user')),
  active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS divisions (
  id BIGSERIAL PRIMARY KEY,
  name VARCHAR(120) NOT NULL UNIQUE,
  sort_order INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS employee_divisions (
  employee_id BIGINT NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
  division_id BIGINT NOT NULL REFERENCES divisions(id) ON DELETE CASCADE,
  PRIMARY KEY (employee_id, division_id)
);

CREATE TABLE IF NOT EXISTS salary_periods (
  period CHAR(7) PRIMARY KEY,
  month SMALLINT NOT NULL CHECK (month BETWEEN 1 AND 12),
  year INTEGER NOT NULL,
  status VARCHAR(20) NOT NULL DEFAULT 'draft'
    CHECK (status IN ('draft', 'submitted', 'approved')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS monthly_salaries (
  id BIGSERIAL PRIMARY KEY,
  period CHAR(7) NOT NULL REFERENCES salary_periods(period) ON DELETE CASCADE,
  employee_id BIGINT NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
  base_salary NUMERIC(14, 2) NOT NULL DEFAULT 0,
  phone_quota NUMERIC(14, 2) NOT NULL DEFAULT 0,
  bpjs_kantor NUMERIC(14, 2) NOT NULL DEFAULT 0,
  bpjs_sendiri NUMERIC(14, 2) NOT NULL DEFAULT 0,
  debt NUMERIC(14, 2) NOT NULL DEFAULT 0,
  rapel_thr NUMERIC(14, 2) NOT NULL DEFAULT 0,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (period, employee_id)
);

CREATE INDEX IF NOT EXISTS idx_employee_divisions_division_id
  ON employee_divisions(division_id);

CREATE INDEX IF NOT EXISTS idx_monthly_salaries_period
  ON monthly_salaries(period);

CREATE INDEX IF NOT EXISTS idx_monthly_salaries_employee_id
  ON monthly_salaries(employee_id);
