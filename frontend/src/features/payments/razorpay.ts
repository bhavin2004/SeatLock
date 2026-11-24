import type { CheckoutResult } from './types'

type CheckoutOptions = {
  key: string
  order_id: string
  amount: number
  currency: string
  name: string
  description: string
  handler: (result: CheckoutResult) => void
  modal: { ondismiss: () => void }
}

declare global {
  interface Window {
    Razorpay?: new (options: CheckoutOptions) => { open: () => void }
  }
}

let checkoutScript: Promise<void> | undefined

export async function openCheckout(options: CheckoutOptions) {
  if (!window.Razorpay) {
    checkoutScript ??= new Promise<void>((resolve, reject) => {
      const script = document.createElement('script')
      script.src = 'https://checkout.razorpay.com/v1/checkout.js'
      script.onload = () => resolve()
      script.onerror = () => {
        script.remove()
        reject(new Error('Razorpay could not load. Try again.'))
      }
      document.head.append(script)
    }).catch((error: unknown) => {
      checkoutScript = undefined
      throw error
    })
    await checkoutScript
  }
  if (!window.Razorpay) throw new Error('Razorpay Checkout is unavailable.')
  new window.Razorpay(options).open()
}
