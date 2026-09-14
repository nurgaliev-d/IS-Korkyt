import { fireEvent, render, screen, waitFor } from "@testing-library/react";

import App from "./App";

function jsonResponse(body, ok = true) {
  return Promise.resolve({
    ok,
    json: async () => body,
  });
}

describe("microcredit app", () => {
  beforeEach(() => {
    window.localStorage.clear();
    global.fetch = vi.fn((url, options = {}) => {
      if (options.method === "POST") return jsonResponse({});
      return jsonResponse([]);
    });
  });

  it("shows the default monthly payment from the calculator", async () => {
    render(<App />);

    await waitFor(() => expect(global.fetch).toHaveBeenCalled());

    expect(screen.getByTestId("monthly-payment").textContent.replace(/\s/g, "")).toContain(
      "26779",
    );
  });

  it("switches the main copy to Kazakh", async () => {
    render(<App />);

    await screen.findByText("Заявок пока нет. Начните с расчёта выше.");
    fireEvent.click(screen.getByRole("button", { name: "Переключить на казахский" }));

    expect(screen.getByRole("heading", { name: "Несиеңізді есептеңіз" })).toBeInTheDocument();
    expect(window.localStorage.getItem("nesie-language")).toBe("kk");
  });

  it("shows a validation message for an empty application", async () => {
    render(<App />);

    fireEvent.click(screen.getByRole("button", { name: "Подать заявку" }));

    expect(await screen.findByText("Введите имя и фамилию.")).toBeInTheDocument();
    expect(global.fetch).toHaveBeenCalledTimes(1);
  });

  it("shows the application number after a successful submit", async () => {
    const created = {
      id: 17,
      full_name: "Алия Сейтова",
      phone: "+7 700 123 45 67",
      iin: "000000000000",
      amount: 150000,
      term_months: 6,
      monthly_payment: 26779,
      total_payment: 160674,
      status: "new",
      created_at: "2026-09-14T09:00:00Z",
    };

    global.fetch = vi.fn((url, options = {}) => {
      if (options.method === "POST") return jsonResponse(created);
      return jsonResponse([]);
    });

    render(<App />);
    fireEvent.change(screen.getByLabelText("Имя и фамилия"), {
      target: { value: "Алия Сейтова" },
    });
    fireEvent.change(screen.getByLabelText("Телефон"), {
      target: { value: "+7 700 123 45 67" },
    });
    fireEvent.change(screen.getByLabelText("ИИН"), {
      target: { value: "000000000000" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Подать заявку" }));

    expect(await screen.findByText("Заявка отправлена")).toBeInTheDocument();
    expect(screen.getAllByText("№ 17").length).toBeGreaterThanOrEqual(1);
    expect(global.fetch).toHaveBeenCalledWith(
      "/api/applications/",
      expect.objectContaining({ method: "POST" }),
    );
  });
});
