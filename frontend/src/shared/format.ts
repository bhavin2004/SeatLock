export const SEAT_PRICE_MINOR = 25_000

export const formatShow = new Intl.DateTimeFormat('en-IN', { dateStyle: 'medium', timeStyle: 'short' })
export const formatMoney = (amount: number, currency = 'INR') =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency }).format(amount / 100)
