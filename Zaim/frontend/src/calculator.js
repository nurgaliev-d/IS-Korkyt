export const MIN_AMOUNT = 50000;
export const MAX_AMOUNT = 500000;
export const MIN_TERM_MONTHS = 1;
export const MAX_TERM_MONTHS = 12;
export const ANNUAL_RATE = 0.24;

export function calculateLoan(amount, termMonths) {
  const monthlyRate = ANNUAL_RATE / 12;
  const factor = (1 + monthlyRate) ** termMonths;
  const monthlyPayment = Math.round(
    (amount * monthlyRate * factor) / (factor - 1),
  );

  return {
    monthlyPayment,
    totalPayment: monthlyPayment * termMonths,
  };
}
