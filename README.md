# Finelle — Payroll Management App

Finelle adalah aplikasi manajemen payroll berbasis web yang ringan, dibangun dengan Python (stdlib only) dan vanilla JavaScript. Tidak memerlukan framework atau dependency eksternal untuk menjalankannya.

## Fitur

- **Input Gaji Bulanan** — Finance mengisi komponen salary per karyawan setiap bulan
- **Template Bulanan** — Salin data salary dari bulan sebelumnya sebagai template
- **Upload Excel** — Import data salary dari file `.xlsx`/`.xls`
- **Total PV** — Kalkulasi otomatis: Gaji Pokok + HP + BPJS (PV) + Rapel/THR − BPJS (Karyawan) − Hutang
- **Master Data** — Kelola karyawan, divisi, username, password, dan akses login
- **Reports** — Laporan pengeluaran per divisi dengan prorata untuk karyawan multi-divisi
- **Dashboard** — KPI ringkasan payroll, distribusi divisi, dan aktivitas bulan ini
- **Role-based Access** — 4 role: `admin`, `finance`, `corporate`, `user`
- **Login Authentication** — Session berbasis cookie sederhana

## Roles & Akses

| Role | Dashboard | Master Data | Salary Input | Reports |
|---|---|---|---|---|
| admin | ✓ | ✓ (edit) | ✓ (edit) | ✓ |
| finance | ✓ | ✓ (view) | ✓ (edit) | ✓ |
| corporate | ✓ | ✓ (view) | ✓ (view) | ✓ |
| user | — | — | ✓ (BPJS only) | — |

## Komponen Salary

| Field | Keterangan | Efek ke Total PV |
|---|---|---|
| Gaji Pokok | Base salary | + |
| Kuota HP | Tunjangan HP | + |
| BPJS (PV) | BPJS ditanggung perusahaan | + |
| BPJS (Karyawan) | BPJS potongan karyawan | − |
| Hutang | Potongan hutang | − |
| Rapel/THR | Rapel atau THR | + |

## Stack Teknologi

- **Backend**: Python 3 — `http.server`, `sqlite3`, `json` (stdlib only, zero dependencies)
- **Frontend**: Vanilla JavaScript, HTML, CSS (no framework)
- **Database**: SQLite (file-based, portable)
- **Schema alternatif**: PostgreSQL dan MySQL tersedia di folder `db/`

## Struktur Folder

```
finelle/
├── server.py          # HTTP server + API + DB logic
├── app.js             # Frontend logic (SPA)
├── index.html         # Single-page app shell
├── styles.css         # Styling
├── data/
│   └── finelle.sqlite # Database (auto-created)
├── db/
│   ├── schema.sqlite.sql
│   ├── schema.postgres.sql
│   └── schema.mysql.sql
└── design/
    └── finelle-logo.png
```

## Menjalankan Aplikasi

```bash
python3 server.py
```

Default port: `4173`. Buka `http://localhost:4173` di browser.

Untuk port custom:

```bash
python3 server.py 8080
```

Atau via environment variable:

```bash
PORT=8080 python3 server.py
```

Database akan dibuat otomatis di `data/finelle.sqlite` saat pertama kali dijalankan, beserta data seed awal (divisi, karyawan, dan periode `2026-01`).

## API Endpoints

| Method | Path | Deskripsi |
|---|---|---|
| GET | `/api/bootstrap` | Divisi, karyawan, dan konfigurasi awal |
| GET | `/api/salaries?period=YYYY-MM` | Data salary per periode |
| POST | `/api/salaries` | Simpan data salary |
| GET | `/api/report?period=YYYY-MM` | Laporan per divisi |
| GET | `/api/dashboard?period=YYYY-MM` | Data dashboard |
| POST | `/api/copy-template` | Salin salary dari bulan sebelumnya |
| POST | `/api/employees` | Tambah karyawan baru |
| PUT | `/api/employees/:id` | Update data karyawan |
| DELETE | `/api/employees/:id` | Nonaktifkan karyawan |
| POST | `/api/login` | Login |
| POST | `/api/upload-excel` | Import salary dari Excel |

## Database Schema

5 tabel utama:
- `employees` — data karyawan, kredensial, dan role
- `divisions` — master divisi
- `employee_divisions` — relasi many-to-many karyawan ↔ divisi
- `salary_periods` — periode payroll (YYYY-MM)
- `monthly_salaries` — data salary per karyawan per periode

## Deployment (VPS)

Finelle berjalan sebagai systemd service (`finelle.service`) di port `4173` (localhost), di-proxy oleh Nginx.

Deploy update:

```bash
cd /var/www/finelle
git pull origin master
systemctl restart finelle.service
```
