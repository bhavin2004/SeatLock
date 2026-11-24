export type Payment = {
  id: string
  amount_minor: number
  currency: string
  provider_order_id: string | null
}
export type CheckoutResult = {
  razorpay_order_id: string
  razorpay_payment_id: string
  razorpay_signature: string
}
