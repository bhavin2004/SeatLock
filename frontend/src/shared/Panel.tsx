import type { ReactNode } from 'react'

export function Panel({ title, children, back }: { title: string; children: ReactNode; back?: () => void }) {
  return <section className="panel">
    {back && <button className="text-button" onClick={back}>← Back</button>}
    <h2>{title}</h2>
    {children}
  </section>
}
