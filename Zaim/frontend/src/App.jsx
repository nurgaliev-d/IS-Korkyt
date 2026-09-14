import { useEffect, useMemo, useState } from "react";

import {
  createApplication,
  listApplications,
  updateApplicationStatus,
} from "./api";
import {
  ANNUAL_RATE,
  MAX_AMOUNT,
  MAX_TERM_MONTHS,
  MIN_AMOUNT,
  MIN_TERM_MONTHS,
  calculateLoan,
} from "./calculator";
import { translations } from "./translations";

const initialForm = { fullName: "", phone: "", iin: "" };

function getInitialLanguage() {
  if (typeof window === "undefined") return "ru";
  return window.localStorage.getItem("nesie-language") || "ru";
}

function formatMoney(value, language) {
  const locale = language === "kk" ? "kk-KZ" : "ru-RU";
  return `${new Intl.NumberFormat(locale).format(value)} ₸`;
}

function formatDate(value, language) {
  if (!value) return "—";
  const locale = language === "kk" ? "kk-KZ" : "ru-RU";
  return new Intl.DateTimeFormat(locale, {
    day: "2-digit",
    month: "short",
    year: "numeric",
  }).format(new Date(value));
}

function StatusChip({ status, copy }) {
  return <span className={`status-chip status-${status}`}>{copy.statuses[status]}</span>;
}

function LanguageSwitcher({ language, onChange, copy }) {
  return (
    <div className="language-switcher" aria-label={copy.languageName}>
      <button
        type="button"
        className={language === "ru" ? "is-active" : ""}
        onClick={() => onChange("ru")}
        aria-label={copy.switchToRussian}
      >
        RU
      </button>
      <button
        type="button"
        className={language === "kk" ? "is-active" : ""}
        onClick={() => onChange("kk")}
        aria-label={copy.switchToKazakh}
      >
        KZ
      </button>
    </div>
  );
}

function App() {
  const [language, setLanguage] = useState(getInitialLanguage);
  const [view, setView] = useState("borrower");
  const [amount, setAmount] = useState(150000);
  const [termMonths, setTermMonths] = useState(6);
  const [form, setForm] = useState(initialForm);
  const [fieldErrors, setFieldErrors] = useState({});
  const [submittedApplication, setSubmittedApplication] = useState(null);
  const [applications, setApplications] = useState([]);
  const [loadingApplications, setLoadingApplications] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [apiError, setApiError] = useState("");
  const [staffFilter, setStaffFilter] = useState("all");
  const [selectedApplication, setSelectedApplication] = useState(null);
  const [actionLoading, setActionLoading] = useState("");
  const [staffError, setStaffError] = useState("");

  const copy = translations[language];
  const estimate = useMemo(() => calculateLoan(amount, termMonths), [amount, termMonths]);

  useEffect(() => {
    window.localStorage.setItem("nesie-language", language);
    document.documentElement.lang = language === "kk" ? "kk" : "ru";
  }, [language]);

  useEffect(() => {
    let cancelled = false;
    const status = view === "staff" && staffFilter !== "all" ? staffFilter : "";

    setLoadingApplications(true);
    listApplications(status)
      .then((data) => {
        if (!cancelled) {
          setApplications(data);
          if (selectedApplication) {
            const current = data.find((item) => item.id === selectedApplication.id);
            setSelectedApplication(current || null);
          }
        }
      })
      .catch(() => {
        if (!cancelled) setApiError(copy.common.offline);
      })
      .finally(() => {
        if (!cancelled) setLoadingApplications(false);
      });

    return () => {
      cancelled = true;
    };
    // Loading is tied to the selected view/filter. The language only changes the message.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [view, staffFilter]);

  function changeLanguage(nextLanguage) {
    setLanguage(nextLanguage);
    setApiError("");
    setStaffError("");
  }

  function changeView(nextView) {
    setView(nextView);
    setApiError("");
    setStaffError("");
    if (nextView === "borrower") setSelectedApplication(null);
  }

  function validateForm() {
    const nextErrors = {};
    if (form.fullName.trim().length < 3) nextErrors.fullName = copy.common.requiredName;
    if (form.phone.replace(/\D/g, "").length < 10) nextErrors.phone = copy.common.requiredPhone;
    if (!/^\d{12}$/.test(form.iin)) nextErrors.iin = copy.common.requiredIin;
    setFieldErrors(nextErrors);
    return Object.keys(nextErrors).length === 0;
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setApiError("");
    if (!validateForm()) return;

    setSubmitting(true);
    try {
      const created = await createApplication({
        full_name: form.fullName.trim(),
        phone: form.phone.trim(),
        iin: form.iin,
        amount,
        term_months: termMonths,
      });
      setSubmittedApplication(created);
      setApplications((current) => [created, ...current]);
    } catch (error) {
      setApiError(error.message || copy.common.requestFailed);
    } finally {
      setSubmitting(false);
    }
  }

  function resetForm() {
    setSubmittedApplication(null);
    setForm(initialForm);
    setFieldErrors({});
    setApiError("");
  }

  async function handleStatusUpdate(application, nextStatus) {
    const key = `${application.id}-${nextStatus}`;
    setActionLoading(key);
    setStaffError("");
    try {
      const updated = await updateApplicationStatus(application.id, nextStatus);
      const status = staffFilter !== "all" ? staffFilter : "";
      const refreshed = await listApplications(status);
      setApplications(refreshed);
      setSelectedApplication(refreshed.find((item) => item.id === updated.id) || null);
    } catch (error) {
      setStaffError(error.message || copy.common.requestFailed);
    } finally {
      setActionLoading("");
    }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-block">
          <span className="brand-mark">{copy.brand}</span>
          <span className="product-note">{copy.productNote}</span>
        </div>
        <nav className="main-nav" aria-label="Основная навигация">
          <button
            type="button"
            className={view === "borrower" ? "nav-button is-active" : "nav-button"}
            onClick={() => changeView("borrower")}
          >
            <span className="nav-dot" />
            {copy.nav.borrower}
          </button>
          <button
            type="button"
            className={view === "staff" ? "nav-button is-active" : "nav-button"}
            onClick={() => changeView("staff")}
          >
            <span className="nav-dot" />
            {copy.nav.staff}
          </button>
        </nav>
        <div className="sidebar-footnote">
          <span className="small-status-dot" />
          <span>{language === "kk" ? "Жергілікті нұсқа" : "Локальная версия"}</span>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="mobile-brand">
            <span className="brand-mark">{copy.brand}</span>
          </div>
          <LanguageSwitcher language={language} onChange={changeLanguage} copy={copy} />
        </header>

        {view === "borrower" ? (
          <BorrowerView
            copy={copy}
            language={language}
            amount={amount}
            termMonths={termMonths}
            estimate={estimate}
            form={form}
            fieldErrors={fieldErrors}
            submittedApplication={submittedApplication}
            applications={applications}
            loadingApplications={loadingApplications}
            submitting={submitting}
            apiError={apiError}
            onAmountChange={setAmount}
            onTermChange={setTermMonths}
            onFormChange={(field, value) => setForm((current) => ({ ...current, [field]: value }))}
            onSubmit={handleSubmit}
            onReset={resetForm}
            onOpenStaff={() => changeView("staff")}
            formatMoney={(value) => formatMoney(value, language)}
            formatDate={(value) => formatDate(value, language)}
          />
        ) : (
          <StaffView
            copy={copy}
            language={language}
            applications={applications}
            loadingApplications={loadingApplications}
            staffFilter={staffFilter}
            selectedApplication={selectedApplication}
            actionLoading={actionLoading}
            staffError={staffError}
            apiError={apiError}
            onFilterChange={setStaffFilter}
            onSelect={setSelectedApplication}
            onStatusUpdate={handleStatusUpdate}
            onBack={() => changeView("borrower")}
            formatMoney={(value) => formatMoney(value, language)}
            formatDate={(value) => formatDate(value, language)}
          />
        )}
      </main>
    </div>
  );
}

function BorrowerView({
  copy,
  amount,
  termMonths,
  estimate,
  form,
  fieldErrors,
  submittedApplication,
  applications,
  loadingApplications,
  submitting,
  apiError,
  onAmountChange,
  onTermChange,
  onFormChange,
  onSubmit,
  onReset,
  onOpenStaff,
  formatMoney,
  formatDate,
}) {
  return (
    <div className="page-content">
      <div className="page-intro">
        <div>
          <h1>{copy.dashboard.title}</h1>
          <p>{copy.dashboard.lead}</p>
        </div>
        <button type="button" className="text-button" onClick={onOpenStaff}>
          {copy.dashboard.openStaff}
        </button>
      </div>

      <section className="planner-section" aria-labelledby="planner-title">
        <div className="section-heading">
          <h2 id="planner-title">{copy.dashboard.planner}</h2>
          <span className="step-note">01 / 02</span>
        </div>
        <div className="planner-grid">
          <div className="planner-controls">
            <div className="field amount-field">
              <div className="label-row">
                <label htmlFor="amount-range">{copy.dashboard.amount}</label>
                <span className="range-value">{formatMoney(amount)}</span>
              </div>
              <input
                id="amount-range"
                type="range"
                min={MIN_AMOUNT}
                max={MAX_AMOUNT}
                step="5000"
                value={amount}
                onChange={(event) => onAmountChange(Number(event.target.value))}
              />
              <div className="amount-input-row">
                <input
                  id="amount-number"
                  type="number"
                  min={MIN_AMOUNT}
                  max={MAX_AMOUNT}
                  step="5000"
                  value={amount}
                  aria-label={copy.dashboard.amount}
                  onChange={(event) => {
                    const nextAmount = Number(event.target.value);
                    if (!Number.isNaN(nextAmount)) {
                      onAmountChange(Math.min(MAX_AMOUNT, Math.max(MIN_AMOUNT, nextAmount)));
                    }
                  }}
                />
                <span>₸</span>
              </div>
              <div className="range-edges">
                <span>50 000 ₸</span>
                <span>500 000 ₸</span>
              </div>
              <span className="field-hint">{copy.dashboard.amountHint}</span>
            </div>
            <div className="field term-field">
              <label htmlFor="term-select">{copy.dashboard.term}</label>
              <select
                id="term-select"
                value={termMonths}
                onChange={(event) => onTermChange(Number(event.target.value))}
              >
                {Array.from({ length: MAX_TERM_MONTHS - MIN_TERM_MONTHS + 1 }, (_, index) => {
                  const value = index + MIN_TERM_MONTHS;
                  return (
                    <option value={value} key={value}>
                      {value} {copy.dashboard.months}
                    </option>
                  );
                })}
              </select>
            </div>
          </div>
          <aside className="estimate-card">
            <p className="card-label">{copy.dashboard.estimate}</p>
            <div className="estimate-main">
              <span className="estimate-number" data-testid="monthly-payment">
                {formatMoney(estimate.monthlyPayment)}
              </span>
              <span className="estimate-caption">{copy.dashboard.monthlyPayment}</span>
            </div>
            <div className="estimate-details">
              <div>
                <span>{copy.dashboard.totalPayment}</span>
                <strong>{formatMoney(estimate.totalPayment)}</strong>
              </div>
              <div>
                <span>{copy.dashboard.term}</span>
                <strong>{termMonths} {copy.dashboard.months}</strong>
              </div>
              <div>
                <span>{copy.dashboard.rate}</span>
                <strong>{copy.dashboard.rateValue}</strong>
              </div>
            </div>
          </aside>
        </div>
      </section>

      <section className="application-section" aria-labelledby="form-title">
        <div className="section-heading">
          <div>
            <h2 id="form-title">{copy.dashboard.formTitle}</h2>
            <p>{copy.dashboard.formLead}</p>
          </div>
          <span className="step-note">02 / 02</span>
        </div>

        {apiError && <div className="inline-alert" role="alert">{apiError}</div>}

        {submittedApplication ? (
          <div className="success-panel">
            <div className="success-icon">✓</div>
            <div>
              <h3>{copy.dashboard.sentTitle}</h3>
              <p>{copy.dashboard.sentLead}</p>
              <dl className="application-summary">
                <div>
                  <dt>{copy.dashboard.applicationNumber}</dt>
                  <dd>№ {submittedApplication.id}</dd>
                </div>
                <div>
                  <dt>{copy.dashboard.amount}</dt>
                  <dd>{formatMoney(submittedApplication.amount)}</dd>
                </div>
                <div>
                  <dt>{copy.dashboard.monthlyPayment}</dt>
                  <dd>{formatMoney(submittedApplication.monthly_payment)}</dd>
                </div>
              </dl>
              <button type="button" className="secondary-button" onClick={onReset}>
                {copy.dashboard.newApplication}
              </button>
            </div>
          </div>
        ) : (
          <form className="application-form" onSubmit={onSubmit} noValidate>
            <div className="form-grid">
              <div className="field">
                <label htmlFor="full-name">{copy.dashboard.fullName}</label>
                <input
                  id="full-name"
                  value={form.fullName}
                  placeholder={copy.dashboard.fullNamePlaceholder}
                  onChange={(event) => onFormChange("fullName", event.target.value)}
                  aria-invalid={Boolean(fieldErrors.fullName)}
                />
                {fieldErrors.fullName && <span className="field-error">{fieldErrors.fullName}</span>}
              </div>
              <div className="field">
                <label htmlFor="phone">{copy.dashboard.phone}</label>
                <input
                  id="phone"
                  value={form.phone}
                  placeholder={copy.dashboard.phonePlaceholder}
                  onChange={(event) => onFormChange("phone", event.target.value)}
                  aria-invalid={Boolean(fieldErrors.phone)}
                />
                {fieldErrors.phone && <span className="field-error">{fieldErrors.phone}</span>}
              </div>
              <div className="field">
                <label htmlFor="iin">{copy.dashboard.iin}</label>
                <input
                  id="iin"
                  inputMode="numeric"
                  maxLength="12"
                  value={form.iin}
                  placeholder={copy.dashboard.iinPlaceholder}
                  onChange={(event) => onFormChange("iin", event.target.value.replace(/\D/g, ""))}
                  aria-invalid={Boolean(fieldErrors.iin)}
                />
                {fieldErrors.iin && <span className="field-error">{fieldErrors.iin}</span>}
              </div>
            </div>
            <div className="form-actions">
              <p className="form-note">
                {copy.dashboard.totalPayment}: {formatMoney(estimate.totalPayment)}
              </p>
              <button type="submit" className="primary-button" disabled={submitting}>
                {submitting ? copy.dashboard.submitting : copy.dashboard.submit}
              </button>
            </div>
          </form>
        )}
      </section>

      <section className="recent-section" aria-labelledby="recent-title">
        <div className="section-heading">
          <div>
            <h2 id="recent-title">{copy.dashboard.recentTitle}</h2>
            <p>{copy.dashboard.recentLead}</p>
          </div>
        </div>
        {loadingApplications ? (
          <p className="loading-line">{copy.common.loading}</p>
        ) : applications.length === 0 ? (
          <div className="empty-state">{copy.dashboard.noApplications}</div>
        ) : (
          <div className="recent-list">
            {applications.slice(0, 5).map((application) => (
              <div className="recent-row" key={application.id}>
                <div>
                  <strong>№ {application.id}</strong>
                  <span>{formatDate(application.created_at)}</span>
                </div>
                <div>
                  <strong>{formatMoney(application.amount)}</strong>
                  <span>{application.term_months} {copy.dashboard.months}</span>
                </div>
                <StatusChip status={application.status} copy={copy} />
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

function StaffView({
  copy,
  applications,
  loadingApplications,
  apiError,
  staffFilter,
  selectedApplication,
  actionLoading,
  staffError,
  onFilterChange,
  onSelect,
  onStatusUpdate,
  onBack,
  formatMoney,
  formatDate,
}) {
  const filters = [
    ["all", copy.staff.all],
    ["new", copy.staff.new],
    ["approved", copy.staff.approved],
    ["rejected", copy.staff.rejected],
  ];

  return (
    <div className="page-content">
      <div className="page-intro">
        <div>
          <h1>{copy.staff.title}</h1>
          <p>{copy.staff.lead}</p>
        </div>
        <button type="button" className="text-button" onClick={onBack}>
          {copy.staff.backToBorrower}
        </button>
      </div>

      <section className="staff-section" aria-labelledby="staff-table-title">
        <div className="staff-toolbar">
          <div className="filter-list" aria-label={copy.staff.title}>
            {filters.map(([value, label]) => (
              <button
                type="button"
                key={value}
                className={staffFilter === value ? "filter-button is-active" : "filter-button"}
                onClick={() => onFilterChange(value)}
              >
                {label}
              </button>
            ))}
          </div>
          <span className="count-label">{applications.length} {copy.staff.count}</span>
        </div>

        {staffError && <div className="inline-alert" role="alert">{staffError}</div>}
        {apiError && <div className="inline-alert" role="alert">{apiError}</div>}

        {loadingApplications ? (
          <p className="loading-line">{copy.common.loading}</p>
        ) : applications.length === 0 ? (
          <div className="empty-state">{copy.staff.noApplications}</div>
        ) : (
          <div className="staff-layout">
            <div className="application-table">
              <div className="table-header">
                <span>{copy.staff.applicant}</span>
                <span>{copy.staff.amount}</span>
                <span>{copy.staff.term}</span>
                <span>{copy.staff.created}</span>
                <span />
              </div>
              {applications.map((application) => (
                <button
                  type="button"
                  className={
                    selectedApplication?.id === application.id
                      ? "application-row is-selected"
                      : "application-row"
                  }
                  key={application.id}
                  onClick={() => onSelect(application)}
                >
                  <span className="applicant-cell">
                    <strong>{application.full_name}</strong>
                    <small>№ {application.id}</small>
                  </span>
                  <span>{formatMoney(application.amount)}</span>
                  <span>{application.term_months} {copy.dashboard.months}</span>
                  <span>{formatDate(application.created_at)}</span>
                  <StatusChip status={application.status} copy={copy} />
                </button>
              ))}
            </div>

            {selectedApplication && (
              <aside className="detail-panel">
                <p className="card-label">{copy.staff.details}</p>
                <h2>{selectedApplication.full_name}</h2>
                <span className="detail-number">№ {selectedApplication.id}</span>
                <StatusChip status={selectedApplication.status} copy={copy} />
                <dl className="detail-list">
                  <div>
                    <dt>{copy.staff.phone}</dt>
                    <dd>{selectedApplication.phone}</dd>
                  </div>
                  <div>
                    <dt>{copy.staff.iin}</dt>
                    <dd>{selectedApplication.iin}</dd>
                  </div>
                  <div>
                    <dt>{copy.staff.amount}</dt>
                    <dd>{formatMoney(selectedApplication.amount)}</dd>
                  </div>
                  <div>
                    <dt>{copy.staff.monthlyPayment}</dt>
                    <dd>{formatMoney(selectedApplication.monthly_payment)}</dd>
                  </div>
                </dl>
                <p className="detail-label">{copy.staff.changeStatus}</p>
                <div className="status-actions">
                  {["new", "approved", "rejected"].map((nextStatus) => (
                    <button
                      type="button"
                      key={nextStatus}
                      className={
                        selectedApplication.status === nextStatus
                          ? `status-action is-current status-${nextStatus}`
                          : "status-action"
                      }
                      disabled={Boolean(actionLoading)}
                      onClick={() => onStatusUpdate(selectedApplication, nextStatus)}
                    >
                      {actionLoading === `${selectedApplication.id}-${nextStatus}`
                        ? "…"
                        : copy.statuses[nextStatus]}
                    </button>
                  ))}
                </div>
              </aside>
            )}
          </div>
        )}
      </section>
    </div>
  );
}

export default App;
