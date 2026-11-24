export type Movie = {
  id: string
  title: string
  duration_minutes: number
  certification: string | null
  poster_url: string | null
  description: string | null
}

export type Show = { id: string; movie_id: string; screen_id: string; starts_at: string }
