import { Panel } from '../../shared/Panel'

export type AuthMode = 'login' | 'register'
export type Credentials = { email: string; password: string }

export function AuthScreen({ mode, busy, back, changeMode, submit }: {
  mode: AuthMode; busy: boolean; back: () => void
  changeMode: (mode: AuthMode) => void; submit: (credentials: Credentials) => void
}) {
  const registering = mode === 'register'
  return (
    <Panel title={registering ? 'Create your account' : 'Sign in'} back={busy ? undefined : back}>
      <p>{registering ? 'Create an account to reserve seats.' : 'Sign in to reserve your selected seats.'}</p>
      <form key={mode} className="auth-form" onSubmit={(event) => {
        event.preventDefault()
        const data = new FormData(event.currentTarget)
        submit({ email: String(data.get('email')).trim(), password: String(data.get('password')) })
      }}>
        <label>Email<input name="email" type="email" autoComplete="email" required disabled={busy} /></label>
        <label>Password<input name="password" type="password" autoComplete={registering ? 'new-password' : 'current-password'} required minLength={registering ? 8 : undefined} maxLength={registering ? 128 : undefined} disabled={busy} /></label>
        <button className="primary" disabled={busy}>{busy ? 'Please wait…' : registering ? 'Create account' : 'Sign in'}</button>
        <button className="text-button" type="button" disabled={busy} onClick={() => changeMode(registering ? 'login' : 'register')}>
          {registering ? 'Already have an account? Sign in' : 'Create an account'}
        </button>
      </form>
    </Panel>
  )
}
