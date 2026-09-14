# Несие — Microcredit System Design

## Goal

Build a small, understandable microcredit web application for a first-week
demo. A borrower can calculate a loan, send an application, and check its
status. A staff member can open the review view and change the status of
applications.

The product should look like a real student project: clear labels, practical
spacing, restrained colors, and useful empty/error states. It should not look
like a generic AI-generated fintech landing page.

## Product scope

### Borrower flow

1. Open the dashboard.
2. Choose a loan amount between 50,000 and 500,000 ₸.
3. Choose a term between 1 and 12 months.
4. Review the calculated monthly payment and total repayment.
5. Enter full name, phone, and IIN.
6. Submit an application.
7. See the application number and current status.

### Staff flow

1. Open the staff review view using the small header link.
2. See applications returned by the API.
3. Filter by all, new, approved, and rejected.
4. Open an application row to see the applicant details.
5. Change status to approved, rejected, or new.

This is a first-week prototype. It does not include real authentication,
credit-bureau integrations, payments, SMS, document uploads, or a production
credit decision. The lack of authentication is explicit in the setup notes so
the next iteration can replace the demo staff link with proper accounts.

## Architecture

The project is split into two small applications:

```text
IS/
├── frontend/       React + Vite single-page app
├── backend/        Django project + JSON API + SQLite
└── docs/           design and setup notes
```

The React app owns interface state, language selection, form validation,
calculator display, and the staff table. Django owns persistence and the
application status transitions. The browser calls the API at `/api`; Vite
proxies that path to Django during local development.

### API contract

`GET /api/health/`

Returns `{ "status": "ok" }`.

`GET /api/applications/?status=new`

Returns an array of application summaries. The status filter is optional.

`POST /api/applications/`

Accepts:

```json
{
  "full_name": "Алия Сейтова",
  "phone": "+7 700 123 45 67",
  "iin": "000000000000",
  "amount": 150000,
  "term_months": 6
}
```

The server validates the range and required fields, recalculates the payment,
sets `status` to `new`, and returns the saved application.

`PATCH /api/applications/<id>/status/`

Accepts `{ "status": "approved" }`, `{ "status": "rejected" }`, or
`{ "status": "new" }`. Invalid transitions return a 400 response with a
human-readable error.

## Data model

The Django `LoanApplication` model contains:

- `full_name` — required string
- `phone` — required string
- `iin` — required 12-digit string
- `amount` — integer tenge amount
- `term_months` — integer from 1 to 12
- `monthly_payment` — calculated integer tenge amount
- `total_payment` — calculated integer tenge amount
- `status` — `new`, `approved`, or `rejected`
- `created_at` — server timestamp

The demo uses a fixed 24% annual rate for an easy-to-explain annuity estimate.
The exact calculation is kept in one backend utility and mirrored by the
frontend for immediate feedback. Backend values are authoritative on submit.

## UI and visual direction

### Palette

- Ink navy `#1e293b` — headings and navigation
- Paper `#f6f7f5` — page background
- White `#ffffff` — working surfaces
- Muted green `#2f6b57` — positive/status accent
- Warm orange `#d97745` — primary action
- Line gray `#d9dedb` — borders and dividers

### Layout

The desktop view has a narrow left navigation rail and a main content column.
The borrower dashboard opens with a plain title and one working loan planner,
not a marketing hero. The planner places the amount/term controls beside a
single dark result panel. Under that is a compact applications list.

The staff view replaces the planner with a simple filter row and table. On
mobile, the rail becomes a top bar and the planner stacks vertically.

The UI uses one readable sans-serif stack with Cyrillic support, sentence case
labels, and modest 10px/14px corner radii. Cards are used for grouping real
content only; there are no decorative gradients, floating blobs, fake metrics,
or excessive animations.

### Copy style

The interface speaks plainly. Actions use verbs such as `Подать заявку` and
`Өтінім беру`; statuses are `Новая` / `Жаңа`, `Одобрена` / `Мақұлданды`, and
`Отклонена` / `Қабылданбады`. Empty states explain the next useful action.

The language toggle is visible in the header and stores the choice in
`localStorage`. Every user-visible label is read from a translation object;
there are no mixed Russian/English placeholders in the interface.

## Errors and empty states

- API unavailable: show a small inline message explaining that the server is
  not responding and let the user continue to adjust the calculator.
- Invalid form: show field-level messages near the field.
- Submit failure: keep the entered values and show the server error above the
  form.
- No applications: show one sentence and a button that returns to the planner.
- Empty staff filter: show `Заявок нет` / `Өтінімдер жоқ` instead of a blank
  table.

## Testing and verification

Backend tests cover the payment calculation, application validation, creation
through the API, status filtering, and status updates. Frontend tests cover
the calculator output, language switch, form validation, and successful
submission using a mocked API response.

Manual verification checks both languages at desktop and mobile widths, a
server-offline state, a new application appearing in the staff view, and a
status update surviving a page refresh.

## Out of scope for this week

- Real customer accounts and staff permissions
- Real interest/risk policy or legal compliance review
- Credit-history checks
- Payment processing and repayment schedule events
- Notifications, file uploads, and production deployment
