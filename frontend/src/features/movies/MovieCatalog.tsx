import { useState } from 'react'
import { Panel } from '../../shared/Panel'
import type { Movie, Show } from './types'
import { formatShow } from '../../shared/format'

function Poster({ movie }: { movie: Movie }) {
  const [failed, setFailed] = useState(false)
  const source = movie.poster_url
  return (
    <div className="poster">
      <span className="poster-letter" aria-hidden="true">{movie.title.charAt(0)}</span>
      {source && !source.startsWith('https://example.com') && !failed &&
        <img src={source} alt="" loading="lazy" onError={() => setFailed(true)} />}
    </div>
  )
}

export function Hero() {
  return (
    <section className="hero">
      <div className="hero-copy">
        <h1>Find your next<br />movie night.</h1>
        <p>Pick a film, choose your seats, and book your tickets.</p>
        <a className="primary" href="#movies">Browse movies ↓</a>
      </div>
      <div className="hero-screen" aria-hidden="true"><span>▶</span></div>
    </section>
  )
}

type CatalogProps = {
  movies: Movie[]; loading: boolean; catalogError: string; busy: boolean
  retry: () => void; selectMovie: (movie: Movie) => void
}

export function Catalog({ movies, loading, catalogError, busy, retry, selectMovie }: CatalogProps) {
  return (<section className="catalog" id="movies">
    <h2>Now Showing</h2>
    {loading && <p role="status">Loading movies…</p>}
    {catalogError && <div className="notice"><p role="alert">{catalogError}</p><button className="secondary" onClick={retry}>Retry</button></div>}
    {!loading && !catalogError && !movies.length && <p className="notice">No movies are showing right now.</p>}
    <div className="movie-grid">
      {movies.map((entry) => <article className="movie-card" key={entry.id}>
        <Poster movie={entry} />
        <div className="movie-info">
          <h3>{entry.title}</h3>
          <p>{entry.duration_minutes} min{entry.certification && ` · Rated ${entry.certification}`}</p>
          <button className="secondary" disabled={busy} onClick={() => selectMovie(entry)}>View shows <span aria-hidden="true">→</span></button>
        </div>
      </article>)}
    </div>
  </section>)
}

export function Showtimes({ movie, shows, busy, back, selectShow }: {
  movie: Movie; shows: Show[]; busy: boolean; back: () => void; selectShow: (show: Show) => void
}) {
  return (<Panel title={movie.title} back={busy ? undefined : back}>
    {movie.description && movie.description !== 'string' && <p>{movie.description}</p>}
    <h3>Upcoming shows</h3>
    {!shows.length && <p className="notice">No upcoming showtimes for this movie.</p>}
    <div className="show-list">{shows.map((entry) =>
      <button className="secondary" key={entry.id} disabled={busy} onClick={() => selectShow(entry)}>{formatShow.format(new Date(entry.starts_at))}</button>
    )}</div>
  </Panel>)
}
