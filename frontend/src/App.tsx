import { useEffect, useState } from 'react'
import { AuthScreen } from './features/auth/AuthScreen'
import type { AuthMode, Credentials } from './features/auth/AuthScreen'
import { Catalog, Hero, Showtimes } from './features/movies/MovieCatalog'
import { SeatPicker } from './features/bookings/SeatPicker'
import { Checkout } from './features/payments/Checkout'
import type { Movie, Show } from './features/movies/types'
import type { Booking, Seat } from './features/bookings/types'
import type { CheckoutResult, Payment } from './features/payments/types'
import { openCheckout } from './features/payments/razorpay'
import { api, listAll } from './shared/api'
import './App.css'

const errorText = (error: unknown) => error instanceof Error ? error.message : 'Something went wrong. Try again.'

function App() {
  const [movies, setMovies] = useState<Movie[]>([])
  const [loading, setLoading] = useState(true)
  const [catalogError, setCatalogError] = useState('')
  const [catalogVersion, setCatalogVersion] = useState(0)
  const [movie, setMovie] = useState<Movie>()
  const [shows, setShows] = useState<Show[]>([])
  const [show, setShow] = useState<Show>()
  const [seats, setSeats] = useState<Seat[]>([])
  const [selected, setSelected] = useState<string[]>([])
  const [booking, setBooking] = useState<Booking>()
  const [payment, setPayment] = useState<Payment>()
  const [checkoutResult, setCheckoutResult] = useState<CheckoutResult>()
  const [outcome, setOutcome] = useState('')
  const [seconds, setSeconds] = useState(0)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [token, setToken] = useState('')
  const [auth, setAuth] = useState<AuthMode>()
  useEffect(() => {
    let active = true
    listAll<Movie>('/movies').then(
      (result) => { if (active) setMovies(result) },
      (reason: unknown) => { if (active) setCatalogError(errorText(reason)) },
    ).finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [catalogVersion])

  useEffect(() => {
    if (!booking) return
    const interval = window.setInterval(() => {
      const remaining = Math.max(0, Math.ceil((Date.parse(booking.expires_at) - Date.now()) / 1000))
      setSeconds(remaining)

    }, 1000)
    return () => window.clearInterval(interval)
  }, [booking])

  async function action(work: () => Promise<void>) {
    setBusy(true)
    setError('')
    try {
      await work()
    } catch (reason) {
      setError(errorText(reason))
    } finally {
      setBusy(false)
    }
  }

  function reset() {
    setMovie(undefined)
    setShow(undefined)
    setBooking(undefined)
    setPayment(undefined)
    setCheckoutResult(undefined)
    setOutcome('')
    setSelected([])
    setError('')
  }

  function selectMovie(choice: Movie) {
    void action(async () => {
      const upcoming = await listAll<Show>('/shows')
      setShows(upcoming.filter((entry) => entry.movie_id === choice.id))
      setMovie(choice)
    })
  }

  function selectShow(choice: Show) {
    void action(async () => {
      setSeats(await api<Seat[]>(`/shows/${choice.id}/seats`))
      setSelected([])
      setShow(choice)
    })
  }

  function submitAuth(credentials: Credentials) {
    void action(async () => {
      if (auth === 'register') await api('/auth/register', { body: credentials })
      const result = await api<{ access_token: string }>('/auth/login', { body: credentials })
      setToken(result.access_token)
      setAuth(undefined)
    })
  }

  function holdSeats() {
    if (!show || !selected.length) return
    if (!token) {
      setAuth('login')
      return
    }
    void action(async () => {
      const path = `/shows/${show.id}/seats`
      try {
        const held = await api<Booking>('/bookings', { token, body: { show_id: show.id, seat_ids: selected } })
        const remaining = Math.max(0, Math.ceil((Date.parse(held.expires_at) - Date.now()) / 1000))
        setSeconds(remaining)

        setBooking(held)
      } catch (reason) {
        const refreshed = await api<Seat[]>(path).catch(() => null)
        if (refreshed) {
          setSeats(refreshed)
          setSelected((current) => current.filter((id) => refreshed.some((seat) => seat.id === id && seat.is_available)))
        }
        throw reason
      }
    })
  }

  async function verify(path: string, result: CheckoutResult) {
    const verified = await api<{ payment_status: string }>(`${path}/verify`, { token, body: result })
    setOutcome(verified.payment_status)
  }

  function pay() {
    if (!booking) return
    void action(async () => {
      const path = `/bookings/${booking.id}/payments`
      if (checkoutResult && payment) {
        await verify(`${path}/${payment.id}`, checkoutResult)
        return
      }
      if (Date.parse(booking.expires_at) <= Date.now()) throw new Error('Your seat hold expired.')
      const key = import.meta.env.VITE_RAZORPAY_KEY_ID
      if (typeof key !== 'string' || !key.startsWith('rzp_test_')) {
        throw new Error('Set VITE_RAZORPAY_KEY_ID to your Razorpay test key ID to enable checkout.')
      }
      const attempt = payment ?? await api<Payment>(path, { token, body: {} })
      setPayment(attempt)
      if (!attempt.provider_order_id) throw new Error('The payment order is unavailable. Try again.')

      const result = await new Promise<CheckoutResult | undefined>((resolve, reject) => {
        void openCheckout({
          key,
          order_id: attempt.provider_order_id!,
          amount: attempt.amount_minor,
          currency: attempt.currency,
          name: 'CineBook',
          description: movie?.title ?? 'Movie tickets',
          handler: resolve,
          modal: { ondismiss: () => resolve(undefined) },
        }).catch(reject)
      })
      if (result) {
        setCheckoutResult(result)
        await verify(`${path}/${attempt.id}`, result)
      }
    })
  }

  return (
    <>
      <header className="topbar">
        <div className="shell nav">
          <button className="brand" disabled={busy} onClick={() => { reset(); setAuth(undefined) }}><span aria-hidden="true">▶</span> CineBook</button>
          {token
            ? <button className="secondary" disabled={busy} onClick={() => { setToken(''); reset() }}>Sign out</button>
            : <button className="secondary" disabled={busy} onClick={() => { setError(''); setAuth('login') }}>Sign in</button>}
        </div>
      </header>
      <main className="shell main">
        {!movie && !auth && <Hero />}

        {error && <p className="notice error" role="alert">{error}</p>}

        {auth ? (
          <AuthScreen mode={auth} busy={busy} submit={submitAuth}
            back={() => { setAuth(undefined); setError('') }}
            changeMode={(mode) => { setAuth(mode); setError('') }} />
        ) : !movie ? (
          <Catalog movies={movies} loading={loading} catalogError={catalogError} busy={busy}
            retry={() => { setLoading(true); setCatalogError(''); setCatalogVersion((version) => version + 1) }}
            selectMovie={selectMovie} />
        ) : !show ? (
          <Showtimes movie={movie} shows={shows} busy={busy} back={reset} selectShow={selectShow} />
        ) : !booking ? (
          <SeatPicker movie={movie} show={show} seats={seats} selected={selected} busy={busy} signedIn={Boolean(token)}
            back={() => { setShow(undefined); setError('') }} holdSeats={holdSeats}
            toggleSeat={(id) => setSelected((current) => current.includes(id)
              ? current.filter((selectedId) => selectedId !== id)
              : [...current, id])} />
        ) : (
          <Checkout movie={movie} show={show} seats={seats} selected={selected} booking={booking}
            payment={payment} outcome={outcome} remaining={seconds} busy={busy}
            verificationPending={Boolean(checkoutResult)} reset={reset} pay={pay} />
        )}
      </main>
    </>
  )
}

export default App
