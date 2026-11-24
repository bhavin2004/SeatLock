import { Panel } from '../../shared/Panel'
import type { Booking, Seat } from '../bookings/types'
import type { Movie, Show } from '../movies/types'
import type { Payment } from './types'
import { formatMoney, formatShow, SEAT_PRICE_MINOR } from '../../shared/format'

export function Checkout({ movie, show, seats, selected, booking, payment, outcome, remaining, busy, verificationPending, reset, pay }: {
  movie: Movie; show: Show; seats: Seat[]; selected: string[]; booking: Booking; payment?: Payment
  outcome: string; remaining: number; busy: boolean; verificationPending: boolean
  reset: () => void; pay: () => void
}) {
  const expired = remaining === 0
  return (<Panel title={outcome === 'completed' ? 'Booking confirmed' : outcome ? 'Payment update' : 'Checkout'}>
    <p>{movie.title} · {formatShow.format(new Date(show.starts_at))}</p>
    <dl className="details">
      <div><dt>Booking reference</dt><dd>{booking.id}</dd></div>
      <div><dt>Seats</dt><dd>{seats.filter((seat) => selected.includes(seat.id)).map((seat) => `${seat.row_label}${seat.seat_number}`).join(', ')}</dd></div>
      <div><dt>{payment ? 'Total' : 'Estimated total'}</dt><dd>{formatMoney(payment?.amount_minor ?? selected.length * SEAT_PRICE_MINOR, payment?.currency)}</dd></div>
      {!outcome && <div><dt>Seat hold</dt><dd>{expired ? 'Expired' : `${Math.floor(remaining / 60)}:${String(remaining % 60).padStart(2, '0')}`}</dd></div>}
    </dl>
    {outcome && outcome !== 'completed' && <p role="status">Payment status: {outcome.replaceAll('_', ' ')}.</p>}
    <div className="panel-actions">
      {((expired && !verificationPending) || outcome)
        ? <button className="primary" disabled={busy} onClick={reset}>Browse movies</button>
        : <button className="primary" disabled={busy} onClick={pay}>{busy ? 'Please wait…' : verificationPending ? 'Retry verification' : 'Pay with Razorpay (test)'}</button>}
    </div>
  </Panel>)
}
