const state = {
  page: "salary",
  role: localStorage.getItem("finelle_role") || "admin",
  period: localStorage.getItem("finelle_period") || "2026-01",
  bootstrap: null,
  employees: [],
  salaries: [],
  report: null,
  dashboard: null,
  expandedReports: new Set(),
};

const salaryFields = [
  "base_salary",
  "phone_quota",
  "bpjs_kantor",
  "bpjs_sendiri",
  "debt",
  "rapel_thr",
];

// Fields each role can see
const roleViewFields = {
  admin: salaryFields,
  finance: salaryFields,
  corporate: salaryFields,
  user: ["base_salary", "bpjs_kantor", "bpjs_sendiri"],
};

// Fields each role can edit
const roleEditFields = {
  admin: salaryFields,
  finance: salaryFields,
  corporate: [],
  user: ["bpjs_kantor", "bpjs_sendiri"],
};

const roleLabels = {
  admin: "Admin",
  corporate: "Corporate",
  finance: "Finance",
  user: "User",
};

const fieldLabels = {
  base_salary: "Gaji Pokok",
  phone_quota: "Kuota HP",
  bpjs_kantor: "BPJS Kantor",
  bpjs_sendiri: "BPJS Sendiri",
  debt: "Hutang",
  rapel_thr: "Rapel/THR",
};

const rupiah = new Intl.NumberFormat("id-ID", {
  style: "currency",
  currency: "IDR",
  maximumFractionDigits: 0,
  minimumFractionDigits: 0,
});

const numberFormat = new Intl.NumberFormat("id-ID", {
  maximumFractionDigits: 2,
  minimumFractionDigits: 0,
});

function $(selector) {
  return document.querySelector(selector);
}

function $all(selector) {
  return [...document.querySelectorAll(selector)];
}

function api(path, options = {}) {
  return fetch(path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "X-Role": state.role,
      ...(options.headers || {}),
    },
  }).then(async (response) => {
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || "Request gagal");
    }
    return payload;
  });
}

function formatCurrency(value) {
  const num = Math.round(Number(value) || 0);
  return "Rp " + new Intl.NumberFormat("id-ID", {
    maximumFractionDigits: 0,
    minimumFractionDigits: 0,
  }).format(num);
}

function totalSalary(row) {
  return (
    Number(row.base_salary || 0) +
    Number(row.phone_quota || 0) +
    Number(row.bpjs_kantor || 0) +
    Number(row.rapel_thr || 0) -
    Number(row.bpjs_sendiri || 0) -
    Number(row.debt || 0)
  );
}

function showToast(message, isError = false) {
  const modal = $("#modalNotification");
  const notification = modal.querySelector(".modal-notification");
  const icon = modal.querySelector(".material-symbols-outlined");
  const text = modal.querySelector("p");
  
  text.textContent = message;
  icon.textContent = isError ? "error" : "check_circle";
  notification.className = "modal-notification " + (isError ? "error" : "success");
  modal.classList.add("visible");
}

function closeModal() {
  $("#modalNotification").classList.remove("visible");
}

function periodParts(period = state.period) {
  const [year, month] = period.split("-").map(Number);
  return { year, month };
}

function setPeriod(year, month) {
  state.period = `${year}-${String(month).padStart(2, "0")}`;
  localStorage.setItem("finelle_period", state.period);
}

function periodLabel(period = state.period) {
  const { year, month } = periodParts(period);
  return `${state.bootstrap.months[month - 1]} ${year}`;
}

function renderPeriodControls() {
  const { year, month } = periodParts();
  const years = [2025, 2026, 2027, 2028];
  $all(".period-control").forEach((node) => {
    node.innerHTML = `
      <select class="month-select" aria-label="Bulan">
        ${state.bootstrap.months.map((name, index) => `
          <option value="${index + 1}" ${index + 1 === month ? "selected" : ""}>${name}</option>
        `).join("")}
      </select>
      <select class="year-select" aria-label="Tahun">
        ${years.map((item) => `
          <option value="${item}" ${item === year ? "selected" : ""}>${item}</option>
        `).join("")}
      </select>
    `;
  });
}

function syncNavigation() {
  $all("[data-page]").forEach((button) => {
    button.classList.toggle("active", button.dataset.page === state.page);
  });
  $all(".page").forEach((page) => page.classList.remove("active"));
  $(`#page-${state.page}`).classList.add("active");
}

async function loadBootstrap() {
  state.bootstrap = await api("/api/bootstrap");
  state.employees = state.bootstrap.employees;
  $("#roleSelect").value = state.role;
  renderPeriodControls();
}

async function loadCurrentPage() {
  syncNavigation();
  renderPeriodControls();
  if (state.page === "dashboard") {
    await loadDashboard();
    renderDashboard();
  }
  if (state.page === "master") {
    await refreshEmployees();
    renderMaster();
  }
  if (state.page === "salary") {
    await loadSalaries();
    renderSalary();
  }
  if (state.page === "reports") {
    await loadReport();
    renderReports();
  }
}

async function refreshEmployees() {
  const payload = await api("/api/bootstrap");
  state.bootstrap.divisions = payload.divisions;
  state.employees = payload.employees;
}

async function loadSalaries() {
  const payload = await api(`/api/salaries?period=${state.period}`);
  state.salaries = payload.rows;
}

async function loadReport() {
  state.report = await api(`/api/report?period=${state.period}`);
}

async function loadDashboard() {
  state.dashboard = await api(`/api/dashboard?period=${state.period}`);
}

function renderKpiGrid(target, cards) {
  target.innerHTML = cards.map((card) => `
    <div class="kpi-card">
      <span>${card.label}</span>
      <strong>${card.value}</strong>
      <p>${card.description}</p>
    </div>
  `).join("");
}

function renderDashboard() {
  const dashboard = state.dashboard;
  const topDivision = dashboard.top_division;
  renderKpiGrid($("#dashboardKpis"), [
    {
      label: "Total Payroll",
      value: formatCurrency(dashboard.total_payroll),
      description: `Estimasi untuk ${periodLabel()}.`,
    },
    {
      label: "Karyawan Aktif",
      value: dashboard.employee_count,
      description: "Termasuk akses admin, finance, corporate, dan user.",
    },
    {
      label: "Multi Divisi",
      value: dashboard.multi_division_count,
      description: "Salary mereka diprorata pada report divisi.",
    },
    {
      label: "Divisi Terbesar",
      value: topDivision ? topDivision.division : "-",
      description: topDivision ? formatCurrency(topDivision.total) : "Belum ada salary.",
    },
  ]);

  const max = Math.max(...dashboard.division_totals.map((row) => row.total), 1);
  $("#divisionBars").innerHTML = dashboard.division_totals
    .filter((row) => row.total > 0)
    .map((row) => `
      <div class="bar-row">
        <strong>${row.division}</strong>
        <div class="bar-track"><div class="bar-fill" style="width:${(row.total / max) * 100}%"></div></div>
        <span class="money">${formatCurrency(row.total)}</span>
      </div>
    `).join("") || `<div class="empty-state">Belum ada salary untuk periode ini.</div>`;

  $("#activityList").innerHTML = dashboard.activities.map((item) => `
    <div class="activity-item">
      <span class="material-symbols-outlined">${item.icon}</span>
      <div>
        <strong>${item.title}</strong>
        <small>${item.description}</small>
      </div>
    </div>
  `).join("");
}

function renderMaster() {
  const isAdmin = state.role === "admin";
  const search = $("#masterSearch").value.trim().toLowerCase();
  const employees = state.employees.filter((employee) =>
    employee.name.toLowerCase().includes(search) ||
    employee.divisions.join(" ").toLowerCase().includes(search) ||
    employee.access_role.includes(search)
  );

  $("#addEmployeeBtn").disabled = !isAdmin;
  $("#employeeCount").textContent = `LIST KARYAWAN (${employees.length})`;
  $("#masterAccessNote").classList.toggle("visible", !isAdmin);
  $("#masterAccessNote").textContent = "Master data hanya bisa diedit oleh Admin. Role lain tetap dapat melihat data.";

  $("#masterBody").innerHTML = employees.map((employee) => `
    <tr data-id="${employee.id}">
      <td>
        <input class="inline-input master-name" value="${escapeHtml(employee.name)}" ${isAdmin ? "" : "disabled"}>
      </td>
      <td>
        <select class="inline-select master-role" ${isAdmin ? "" : "disabled"}>
          ${Object.entries(roleLabels).map(([value, label]) => `
            <option value="${value}" ${employee.access_role === value ? "selected" : ""}>${label}</option>
          `).join("")}
        </select>
      </td>
      <td>
        <div class="division-list">
          ${state.bootstrap.divisions.map((division) => `
            <label class="division-chip">
              <input type="checkbox" value="${escapeHtml(division.name)}" ${employee.divisions.includes(division.name) ? "checked" : ""} ${isAdmin ? "" : "disabled"}>
              ${escapeHtml(division.name)}
            </label>
          `).join("")}
        </div>
      </td>
      <td class="right">
        <button class="tiny-button save-master" ${isAdmin ? "" : "disabled"} title="Simpan">
          <span class="material-symbols-outlined">save</span>
        </button>
        <button class="danger-button delete-master" ${isAdmin ? "" : "disabled"} title="Nonaktifkan">
          <span class="material-symbols-outlined">delete</span>
        </button>
      </td>
    </tr>
  `).join("") || `<tr><td colspan="4" class="empty-state">Data tidak ditemukan.</td></tr>`;
}

function renderSalary() {
  const viewFields = roleViewFields[state.role] || [];
  const editFields = roleEditFields[state.role] || [];
  const search = $("#salarySearch").value.trim().toLowerCase();
  const rows = state.salaries.filter((row) => row.name.toLowerCase().includes(search));

  const canCopyTemplate = ["admin", "finance"].includes(state.role);
  const canSave = canCopyTemplate;
  const canReset = canCopyTemplate;

  $("#salaryCount").textContent = `LIST KARYAWAN (${rows.length})`;
  $("#copyTemplateBtn").disabled = !canCopyTemplate;
  $("#saveSalaryBtn").disabled = !canSave;
  $("#resetMonthBtn").disabled = !canReset;

  // Update table header based on role
  const headerLabels = {
    base_salary: "Gaji Pokok",
    phone_quota: "HP",
    bpjs_sendiri: "BPJS (PV)",
    bpjs_kantor: "BPJS (Karyawan)",
    debt: "Hutang",
    rapel_thr: "Rapel/THR",
  };
  const headerRow = salaryFields.map((field) => {
    if (!viewFields.includes(field)) return `<th class="hidden-cell">${headerLabels[field]}</th>`;
    return `<th>${headerLabels[field]}</th>`;
  }).join("");
  const thead = document.getElementById("salaryHead");
  if (thead) {
    thead.innerHTML = `
      <tr>
        <th class="sticky-col">Nama Karyawan</th>
        ${headerRow}
        <th class="right">Total Gaji</th>
      </tr>
    `;
  }

  $("#salaryBody").innerHTML = rows.map((row) => `
    <tr data-id="${row.employee_id}">
      <td class="sticky-col">
        <div class="employee-name">
          ${escapeHtml(row.name)}
          <small>${row.divisions.map(escapeHtml).join(", ") || "Tanpa divisi"}</small>
        </div>
      </td>
      ${salaryFields.map((field) => {
        const canView = viewFields.includes(field);
        const canEdit = editFields.includes(field);
        if (!canView) return `<td class="hidden-cell"></td>`;
        const val = Math.round(row[field] || 0);
        const displayVal = val > 0 ? new Intl.NumberFormat("id-ID").format(val) : "";
        return `
          <td>
            <label class="currency-field">
              <span>Rp</span>
              <input class="data-input salary-input" type="text" min="0" step="1000"
                data-field="${field}" value="${displayVal}" ${canEdit ? "" : "disabled"}
                aria-label="${fieldLabels[field]} ${escapeHtml(row.name)}">
            </label>
          </td>
        `;
      }).join("")}
      <td class="right money total-cell">${formatCurrency(totalSalary(row))}</td>
    </tr>
  `).join("") || `<tr><td colspan="8" class="empty-state">Data tidak ditemukan.</td></tr>`;

  renderSalaryFooter(rows);
}

function renderSalaryFooter(rows = state.salaries) {
  const total = rows.reduce((sum, row) => sum + totalSalary(row), 0);
  $("#totalEmployees").textContent = rows.length;
  $("#grandTotal").textContent = formatCurrency(total);
}

function renderReports() {
  const report = state.report;
  const activeRows = report.rows.filter((row) => row.total > 0);
  const top = activeRows[0];
  renderKpiGrid($("#reportKpis"), [
    {
      label: "Total Pengeluaran",
      value: formatCurrency(report.total),
      description: `Hasil prorata salary ${periodLabel()}.`,
    },
    {
      label: "Divisi Aktif",
      value: activeRows.length,
      description: "Divisi dengan alokasi salary lebih dari nol.",
    },
    {
      label: "Share Tertinggi",
      value: top ? top.division : "-",
      description: top ? formatCurrency(top.total) : "Belum ada salary.",
    },
    {
      label: "Periode",
      value: periodLabel(),
      description: "Pilih bulan untuk melihat report lain.",
    },
  ]);

  $("#reportBody").innerHTML = report.rows.map((row) => {
    const expanded = state.expandedReports.has(row.division);
    const detailRows = expanded ? row.employees.map((employee) => `
      <tr class="report-detail">
        <td class="indent">${escapeHtml(employee.name)}</td>
        <td class="right">1/${employee.split_count}</td>
        <td class="right">${numberFormat.format(1 / employee.split_count)}</td>
        <td class="right money">${formatCurrency(employee.allocated_total)}</td>
      </tr>
    `).join("") : "";
    return `
      <tr class="report-group ${expanded ? "expanded" : ""}" data-division="${escapeHtml(row.division)}">
        <td>
          <button class="report-toggle">
            <span class="material-symbols-outlined">chevron_right</span>
            ${escapeHtml(row.division)}
          </button>
        </td>
        <td class="right">${row.employee_count}</td>
        <td class="right">${numberFormat.format(row.fte_share)}</td>
        <td class="right money">${formatCurrency(row.total)}</td>
      </tr>
      ${detailRows}
    `;
  }).join("");
}

async function saveSalary() {
  await api("/api/salaries", {
    method: "POST",
    body: JSON.stringify({ period: state.period, salaries: state.salaries }),
  });
  showToast(`Data salary ${periodLabel()} berhasil disimpan.`);
  await loadCurrentPage();
}

async function copyTemplate() {
  const payload = await api("/api/copy-template", {
    method: "POST",
    body: JSON.stringify({ period: state.period }),
  });
  state.salaries = payload.rows;
  showToast(`Template dari ${periodLabel(payload.source_period)} berhasil disalin.`);
  renderSalary();
}

async function saveMasterRow(row) {
  const employeeId = row.dataset.id;
  const divisions = [...row.querySelectorAll(".division-chip input:checked")].map((item) => item.value);
  const payload = {
    name: row.querySelector(".master-name").value.trim(),
    access_role: row.querySelector(".master-role").value,
    divisions,
  };
  await api(`/api/employees/${employeeId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
  showToast("Master data berhasil disimpan.");
  await refreshEmployees();
  renderMaster();
}

async function deleteMasterRow(row) {
  const name = row.querySelector(".master-name").value.trim();
  if (!window.confirm(`Nonaktifkan karyawan ${name}?`)) return;
  await api(`/api/employees/${row.dataset.id}`, { method: "DELETE" });
  showToast("Karyawan dinonaktifkan.");
  await refreshEmployees();
  renderMaster();
}

async function addEmployee() {
  const name = window.prompt("Nama karyawan baru");
  if (!name || !name.trim()) return;
  await api("/api/employees", {
    method: "POST",
    body: JSON.stringify({
      name: name.trim(),
      access_role: "user",
      divisions: [state.bootstrap.divisions[0].name],
    }),
  });
  showToast("Karyawan baru ditambahkan.");
  await refreshEmployees();
  renderMaster();
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function attachEvents() {
  // Modal close button
  document.getElementById("modalCloseBtn").addEventListener("click", closeModal);
  document.getElementById("modalNotification").addEventListener("click", (e) => {
    if (e.target.id === "modalNotification") closeModal();
  });
  
  document.addEventListener("click", async (event) => {
    const nav = event.target.closest("[data-page]");
    if (nav) {
      state.page = nav.dataset.page;
      $("#sidebar").classList.remove("open");
      await loadCurrentPage();
      return;
    }

    if (event.target.closest("#mobileMenu")) {
      $("#sidebar").classList.toggle("open");
      return;
    }

    if (event.target.closest("#copyTemplateBtn")) {
      try {
        await copyTemplate();
      } catch (error) {
        showToast(error.message, true);
      }
      return;
    }

    if (event.target.closest("#saveSalaryBtn")) {
      try {
        await saveSalary();
      } catch (error) {
        showToast(error.message, true);
      }
      return;
    }

    if (event.target.closest("#resetMonthBtn")) {
      await loadSalaries();
      renderSalary();
      showToast("Perubahan yang belum disimpan dibatalkan.");
      return;
    }

    if (event.target.closest("#clearMonthBtn")) {
      if (!window.confirm("Kosongkan semua field salary bulan ini?")) return;
      state.salaries.forEach((salary) => {
        salaryFields.forEach((field) => {
          salary[field] = 0;
        });
      });
      renderSalary();
      showToast("Semua field salary telah dikosongkan. Tekan Simpan untuk menyimpan.");
      return;
    }

    if (event.target.closest("#addEmployeeBtn")) {
      try {
        await addEmployee();
      } catch (error) {
        showToast(error.message, true);
      }
      return;
    }

    const saveMaster = event.target.closest(".save-master");
    if (saveMaster) {
      try {
        await saveMasterRow(saveMaster.closest("tr"));
      } catch (error) {
        showToast(error.message, true);
      }
      return;
    }

    const deleteMaster = event.target.closest(".delete-master");
    if (deleteMaster) {
      try {
        await deleteMasterRow(deleteMaster.closest("tr"));
      } catch (error) {
        showToast(error.message, true);
      }
      return;
    }

    const reportGroup = event.target.closest(".report-group");
    if (reportGroup) {
      const division = reportGroup.dataset.division;
      if (state.expandedReports.has(division)) {
        state.expandedReports.delete(division);
      } else {
        state.expandedReports.add(division);
      }
      renderReports();
      return;
    }

    if (event.target.closest("#expandReportsBtn")) {
      const hasCollapsed = state.report.rows.some((row) => !state.expandedReports.has(row.division));
      state.expandedReports = hasCollapsed
        ? new Set(state.report.rows.map((row) => row.division))
        : new Set();
      renderReports();
    }
  });

  document.addEventListener("change", async (event) => {
    if (event.target.matches("#roleSelect")) {
      state.role = event.target.value;
      localStorage.setItem("finelle_role", state.role);
      await loadCurrentPage();
      showToast(`Mode akses: ${roleLabels[state.role]}`);
      return;
    }

    if (event.target.matches(".month-select, .year-select")) {
      const control = event.target.closest(".period-control");
      const month = Number(control.querySelector(".month-select").value);
      const year = Number(control.querySelector(".year-select").value);
      setPeriod(year, month);
      await loadCurrentPage();
      return;
    }
  });

  document.addEventListener("input", (event) => {
    if (event.target.matches("#salarySearch")) {
      renderSalary();
      return;
    }

    if (event.target.matches("#masterSearch")) {
      renderMaster();
      return;
    }

    if (event.target.matches(".salary-input")) {
      const row = event.target.closest("tr");
      const employeeId = Number(row.dataset.id);
      const item = state.salaries.find((salary) => Number(salary.employee_id) === employeeId);
      // Parse value by removing dots from formatted string
      const rawValue = event.target.value.replace(/\./g, "");
      item[event.target.dataset.field] = Number(rawValue || 0);
      // Format display value with thousand separators
      const numVal = Number(rawValue || 0);
      event.target.value = numVal > 0 ? new Intl.NumberFormat("id-ID").format(numVal) : "";
      row.querySelector(".total-cell").textContent = formatCurrency(totalSalary(item));
      renderSalaryFooter(state.salaries.filter((salary) =>
        salary.name.toLowerCase().includes($("#salarySearch").value.trim().toLowerCase())
      ));
    }
  });
}

async function boot() {
  try {
    attachEvents();
    await loadBootstrap();
    await loadCurrentPage();
  } catch (error) {
    showToast(error.message, true);
  }
}

boot();
