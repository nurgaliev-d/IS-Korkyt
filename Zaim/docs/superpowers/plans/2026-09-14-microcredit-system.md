# Microcredit System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a practical Russian/Kazakh microcredit prototype with a React borrower dashboard, a small Django JSON API, and a staff application review view.

**Architecture:** A Vite React single-page app communicates with a Django API under `/api`. Django persists `LoanApplication` records in SQLite, calculates authoritative repayment values, and exposes list/create/status endpoints. The frontend owns calculator state, translations, form validation, and view state; the backend owns persistence and validation.

**Tech Stack:** React 18, Vite, plain CSS, Vitest, Django, Django REST Framework, django-cors-headers, SQLite, Python unittest.

**Spec:** `docs/superpowers/specs/2026-09-14-microcredit-system-design.md`

## Global Constraints

- Keep the first release limited to borrower applications and basic staff review.
- Use Russian and Kazakh copy from one translation object; do not scatter translated strings through components.
- Use the fixed 24% annual rate and 1–12 month / 50,000–500,000 ₸ limits from the spec.
- Keep the UI practical: no gradients, decorative blobs, fake metrics, or excessive animation.
- Keep the demo staff link unauthenticated and document that it is not production-ready.
- Backend values are authoritative when an application is submitted.

### Task 1: Scaffold the project and local development commands

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/manage.py`
- Create: `backend/config/__init__.py`
- Create: `backend/config/settings.py`
- Create: `backend/config/urls.py`
- Create: `backend/config/wsgi.py`
- Create: `backend/loans/__init__.py`
- Create: `backend/loans/apps.py`
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`
- Create: `README.md`

**Interfaces:**
- Produces a Django project runnable with `python manage.py runserver 8000`.
- Produces a Vite project runnable with `npm run dev` and proxying `/api` to `http://127.0.0.1:8000`.

- [ ] **Step 1: Create the Django and Vite configuration files**

  Configure Django with `INSTALLED_APPS = ["django.contrib.contenttypes", "django.contrib.auth", "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles", "corsheaders", "rest_framework", "loans"]`, SQLite at `backend/db.sqlite3`, and `CORS_ALLOW_ALL_ORIGINS = True` for local development only. Configure Vite to proxy `/api` to port 8000.

- [ ] **Step 2: Add the smallest frontend shell**

  Add React and test scripts to `frontend/package.json`:

  ```json
  {
    "scripts": { "dev": "vite", "build": "vite build", "test": "vitest run" },
    "dependencies": { "@vitejs/plugin-react": "latest", "vite": "latest", "react": "latest", "react-dom": "latest", "vitest": "latest", "jsdom": "latest" },
    "devDependencies": {}
  }
  ```

  The initial `index.html` should provide only the root element and a readable document title: `Несие — микрокредит`.

- [ ] **Step 3: Add setup and run instructions**

  Document separate terminal commands for the backend and frontend, database migration, tests, and the demo limitation that staff review has no authentication yet.

- [ ] **Step 4: Verify the scaffold**

  Run: `python -m compileall backend`

  Expected: PASS with no syntax errors.

  Run: `npm install && npm run build` from `frontend/`.

  Expected: Vite creates `frontend/dist/` without errors.

### Task 2: Implement the loan domain and JSON API

**Files:**
- Create: `backend/loans/models.py`
- Create: `backend/loans/calculator.py`
- Create: `backend/loans/serializers.py`
- Create: `backend/loans/views.py`
- Create: `backend/loans/urls.py`
- Create: `backend/loans/admin.py`
- Create: `backend/loans/tests.py`
- Modify: `backend/config/urls.py`
- Create: `backend/loans/migrations/__init__.py`

**Interfaces:**
- `calculate_loan(amount: int, term_months: int) -> dict[str, int]` returns `monthly_payment` and `total_payment`.
- `POST /api/applications/` returns a saved application with `id`, `full_name`, `phone`, `iin`, `amount`, `term_months`, `monthly_payment`, `total_payment`, `status`, and `created_at`.
- `GET /api/applications/` returns newest applications first; `?status=` filters by `new`, `approved`, or `rejected`.
- `PATCH /api/applications/<int:application_id>/status/` accepts a JSON object containing `status`.

- [ ] **Step 1: Write failing domain tests**

  Add tests like:

  ```python
  class LoanCalculatorTests(SimpleTestCase):
      def test_calculates_six_month_plan(self):
          result = calculate_loan(150000, 6)
          self.assertEqual(result["monthly_payment"], 26779)
          self.assertEqual(result["total_payment"], 160674)

      def test_rejects_amount_outside_limits(self):
          with self.assertRaises(ValidationError):
              calculate_loan(10000, 6)
  ```

- [ ] **Step 2: Implement the calculator and model validation**

  Use the annuity formula with monthly rate `0.24 / 12`, round each displayed repayment to the nearest tenge, and validate amount/term in `LoanApplication.clean()`. Keep the field limits as named constants in `calculator.py` so serializers and tests share them.

- [ ] **Step 3: Write failing API tests**

  Cover `GET /api/health/`, valid creation, missing/invalid IIN, status filtering, and PATCH status updates. Assert that submitted `monthly_payment` values are ignored and recalculated on the server.

- [ ] **Step 4: Implement serializers and views**

  Use DRF `APIView` classes. Return `400` with `{ "detail": "..." }` for invalid input, `404` for unknown application IDs, and `200` with the updated record for valid status changes. Only allow the three statuses in the spec.

- [ ] **Step 5: Add URL routes and admin registration**

  Mount `loans.urls` at `/api/`, add the health endpoint, register `LoanApplication` in Django admin, and create migrations.

- [ ] **Step 6: Run the backend test suite**

  Run from `backend/`: `python manage.py test`.

  Expected: all calculator, model, and API tests pass.

### Task 3: Build the localized React app shell and borrower dashboard

**Files:**
- Create: `frontend/src/main.jsx`
- Create: `frontend/src/App.jsx`
- Create: `frontend/src/api.js`
- Create: `frontend/src/translations.js`
- Create: `frontend/src/styles.css`

**Interfaces:**
- `translations.js` exports `translations` with `ru` and `kk` keys and the same nested keys in each language.
- `api.js` exports `createApplication(payload)`, `listApplications(status)`, and `updateApplicationStatus(id, status)`.
- `App.jsx` accepts no props and manages `{ language, view, form, submittedApplication, applications, loading, error }`.

- [ ] **Step 1: Write the translation map and API client**

  Include labels for navigation, form fields, statuses, validation messages, server errors, empty states, and the repayment summary. Use `localStorage` key `nesie-language` and default to `ru`.

  The client should call relative paths and throw an `Error` containing the server `detail` when `response.ok` is false.

- [ ] **Step 2: Add the application shell**

  Render a left rail with the product mark `несие`, borrower/staff navigation, and a visible RU/KZ toggle. On mobile, render the same navigation as a compact top bar.

- [ ] **Step 3: Add the borrower loan planner**

  Render an amount range input plus numeric amount field, a term select, and a dark summary panel. Update the summary locally on every control change with the same `calculateLoan` math as the backend. Show amount, term, monthly payment, total payment, and the fixed rate in plain language.

- [ ] **Step 4: Add the borrower form**

  Add full name, phone, and IIN fields with inline errors. On submit, send `{ full_name, phone, iin, amount, term_months }`. Keep values when submission fails. On success show the application number and status with a “new application” action.

- [ ] **Step 5: Load and render recent applications**

  Load `GET /api/applications/` when the dashboard mounts. Render a compact list with date, amount, term, and status. Show a useful empty state and an inline server-offline message without breaking the calculator.

### Task 4: Build the staff review view

**Files:**
- Modify: `frontend/src/App.jsx`
- Modify: `frontend/src/translations.js`
- Modify: `frontend/src/styles.css`

**Interfaces:**
- The staff view uses the existing `listApplications(status)` and `updateApplicationStatus(id, status)` functions.
- Status filter values are `all`, `new`, `approved`, and `rejected`.

- [ ] **Step 1: Add filter and table rendering**

  Add a staff page title, filter buttons, count text, and a table with applicant, amount, term, created date, and status. On small screens, turn each row into a stacked record without horizontal scrolling.

- [ ] **Step 2: Add the application detail panel**

  Selecting a row opens a small detail panel showing phone, IIN, calculated repayment, and current status. Keep it in the page rather than adding a modal dependency.

- [ ] **Step 3: Add status actions**

  Provide buttons for `new`, `approved`, and `rejected`; disable them while the PATCH request is in flight; refresh the list after a successful update. Show an inline error if the update fails.

### Task 5: Apply the visual system and responsive behavior

**Files:**
- Modify: `frontend/src/styles.css`
- Modify: `frontend/index.html`

**Interfaces:**
- Defines the design tokens from the spec as CSS custom properties.
- Provides keyboard-visible focus styles and `prefers-reduced-motion` behavior.

- [ ] **Step 1: Add typography, colors, and layout tokens**

  Use a system sans-serif stack with Cyrillic support, `#f6f7f5` page background, navy ink, muted green, orange action color, white surfaces, and gray borders. Use 10px/14px radius values consistently and a compact content max width.

- [ ] **Step 2: Style the practical dashboard composition**

  Keep the rail quiet, the planner prominent, the summary panel dark and readable, and the applications list dense. Avoid gradient backgrounds, decorative shapes, excessive shadows, and all-caps labels.

- [ ] **Step 3: Add responsive styles**

  At `max-width: 760px`, stack the planner columns, make the rail a top bar, let form controls use full width, and replace the staff table with stacked rows.

- [ ] **Step 4: Verify the frontend build**

  Run from `frontend/`: `npm run build`.

  Expected: build succeeds with no CSS or JSX errors.

### Task 6: Add focused frontend tests and finish verification

**Files:**
- Create: `frontend/src/App.test.jsx`
- Create: `frontend/src/calculator.js`
- Modify: `frontend/src/App.jsx`
- Modify: `frontend/package.json`
- Modify: `README.md`

**Interfaces:**
- `calculator.js` exports `calculateLoan(amount: number, termMonths: number)`.
- `App.test.jsx` mocks `global.fetch` rather than requiring a running Django server.

- [ ] **Step 1: Extract the calculator and write failing tests**

  Test the default loan summary, switching the language to Kazakh, rejecting an empty full name, and showing a returned application number after a successful mocked submit.

- [ ] **Step 2: Implement the extracted calculator and test hooks**

  Use stable accessible labels and buttons so tests exercise the same interactions a user performs. Keep language strings in the translation map.

- [ ] **Step 3: Run frontend tests**

  Run from `frontend/`: `npm test`.

  Expected: all frontend tests pass.

- [ ] **Step 4: Run the complete local verification**

  Run `python manage.py test` in `backend/`, `npm test` and `npm run build` in `frontend/`, and manually verify both language toggles, application creation, staff status update, mobile layout, and an offline API state.

- [ ] **Step 5: Update the handoff notes**

  Document that the staff view is deliberately unauthenticated for the first-week prototype and list the next safe production steps: authentication, permission checks, rate policy, audit trail, and deployment secrets.
