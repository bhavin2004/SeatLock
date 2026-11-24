import { Panel } from '../../shared/Panel'
import type { Movie, Show } from '../movies/types'
import type { Seat } from './types'
import { formatMoney, formatShow, SEAT_PRICE_MINOR } from '../../shared/format'

export function SeatPicker({ movie, show, seats, selected, busy, signedIn, back, holdSeats, toggleSeat }: {
  movie: Movie; show: Show; seats: Seat[]; selected: string[]; busy: boolean; signedIn: boolean
  back: () => void; holdSeats: () => void; toggleSeat: (id: string) => void
}) {
  const rows = new Map<string, Seat[]>()
  for (const seat of seats) {
    const row = rows.get(seat.row_label)
    if (row) row.push(seat)
    else rows.set(seat.row_label, [seat])
  }

  return (<Panel title="Choose your seats" back={busy ? undefined : back}>
    <p>{movie.title} · {formatShow.format(new Date(show.starts_at))}</p>
    <div className="seat-map">
      <div className="screen">Screen</div>
      {!seats.length && <p>No seats are listed for this show.</p>}
      {[...rows].map(([label, row]) => <div className="seat-row" key={label}>
        <span>{label}</span>
        {row.map((seat) => <button
          className="seat"
          key={seat.id}
          aria-label={`Seat ${label}${seat.seat_number}`}
          aria-pressed={selected.includes(seat.id)}
          disabled={!seat.is_available || busy}
          onClick={() => toggleSeat(seat.id)}
        >{seat.seat_number}</button>)}
      </div>)}
    </div>
    <div className="legend"><span>Available</span><span>Selected</span><span>Unavailable</span></div>
    <div className="panel-actions"><p>{selected.length} selected · {formatMoney(selected.length * SEAT_PRICE_MINOR)} estimated</p><button className="primary" disabled={!selected.length || busy} onClick={holdSeats}>{signedIn ? 'Hold seats' : 'Sign in to book'}</button></div>
  </Panel>)
}
