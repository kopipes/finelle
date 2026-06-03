CREATE TABLE IF NOT EXISTS employees (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  name VARCHAR(160) NOT NULL,
  access_role ENUM('admin', 'corporate', 'finance', 'user') NOT NULL DEFAULT 'user',
  active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_employees_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS divisions (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  name VARCHAR(120) NOT NULL,
  sort_order INT NOT NULL DEFAULT 0,
  PRIMARY KEY (id),
  UNIQUE KEY uq_divisions_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS employee_divisions (
  employee_id BIGINT UNSIGNED NOT NULL,
  division_id BIGINT UNSIGNED NOT NULL,
  PRIMARY KEY (employee_id, division_id),
  CONSTRAINT fk_employee_divisions_employee
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE,
  CONSTRAINT fk_employee_divisions_division
    FOREIGN KEY (division_id) REFERENCES divisions(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS salary_periods (
  period CHAR(7) NOT NULL,
  month TINYINT UNSIGNED NOT NULL,
  year INT NOT NULL,
  status ENUM('draft', 'submitted', 'approved') NOT NULL DEFAULT 'draft',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (period),
  CHECK (month BETWEEN 1 AND 12)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS monthly_salaries (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  period CHAR(7) NOT NULL,
  employee_id BIGINT UNSIGNED NOT NULL,
  base_salary DECIMAL(14, 2) NOT NULL DEFAULT 0,
  phone_quota DECIMAL(14, 2) NOT NULL DEFAULT 0,
  bpjs_kantor DECIMAL(14, 2) NOT NULL DEFAULT 0,
  bpjs_sendiri DECIMAL(14, 2) NOT NULL DEFAULT 0,
  debt DECIMAL(14, 2) NOT NULL DEFAULT 0,
  rapel_thr DECIMAL(14, 2) NOT NULL DEFAULT 0,
  notes TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_monthly_salaries_period_employee (period, employee_id),
  KEY idx_monthly_salaries_period (period),
  KEY idx_monthly_salaries_employee_id (employee_id),
  CONSTRAINT fk_monthly_salaries_period
    FOREIGN KEY (period) REFERENCES salary_periods(period) ON DELETE CASCADE,
  CONSTRAINT fk_monthly_salaries_employee
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
