import type { CurrentUser, Form, FormField, Submission, SubmissionResponse } from './types'
import { tokenStore } from './lib/tokenStore'
const API_URL = import.meta.env.VITE_API_URL

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = tokenStore.get()
  console.log('Token exists:', !!token)        
  console.log('Calling:', path)             

  const response = await fetch(`${API_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
    ...options,
  })

  if (!response.ok) {
    if (response.status === 401) {
      tokenStore.clear()
    }
    const body = await response.json().catch(() => ({})) as {
      detail?: string | Array<{ msg?: string }>
    }
    const message = Array.isArray(body.detail)
      ? body.detail.map(error => error.msg ?? 'Invalid value').join(' ')
      : body.detail
    throw new Error(message ?? 'Something went wrong. Please try again.')
  }

  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

export const api = {
  login: async (email: string, password: string) => {
    const data = await request<{ access_token: string; message: string }>(
      '/auth/login',
      { method: 'POST', body: JSON.stringify({ email, password }) }
    )
    tokenStore.set(data.access_token)  // save token immediately after login
    return data
  },

  signup: (
    email: string,
    password: string,
    organization_name?: string,
    invite_code?: string
  ) =>
    request<{ message: string }>('/auth/signup', {
      method: 'POST',
      body: JSON.stringify({
        email,
        password,
        organization_name: organization_name || undefined,
        invite_code: invite_code || undefined,
      }),
    }),
  logout: async () => {
    const data = await request<{ message: string }>('/auth/logout', {
      method: 'POST',
    })
    tokenStore.clear()  
    return data
  },
  createInvite: (role: 'admin' | 'member' = 'member') =>
    request<{ invite_code: string; role: string }>('/auth/invites', {
      method: 'POST',
      body: JSON.stringify({ role }),
    }),
  me: () => request<CurrentUser>('/auth/me'),
  forms: () => request<Form[]>('/forms/'),
  deleteForm: (formId: string) => request<void>(`/forms/${formId}`, { method: 'DELETE' }),
  createForm: (title: string, structure: FormField[]) => request<Form>('/forms/', { method: 'POST', body: JSON.stringify({ title, structure, organization_id: crypto.randomUUID(), is_active: true }) }),
  submissions: (formId: string, skip = 0) => request<SubmissionResponse>(`/analytics/submissions/${formId}?skip=${skip}`),
  submissionStatus: (formId: string) => request<{ has_submitted: boolean; is_active: boolean }>(`/submissions/forms/${formId}/my-status`),
  subscribeToFormUpdates: (formId: string, onUpdate: () => void) => {
    const stream = new EventSource(`${API_URL}/analytics/forms/${formId}/events`, { withCredentials: true })
    stream.addEventListener('new_submission', onUpdate)
    stream.addEventListener('submission_updated', onUpdate)
    return () => stream.close()
  },
  downloadCsv: async (formId: string) => {
    const response = await fetch(`${API_URL}/exports/forms/${formId}.csv`, { credentials: 'include' })
    if (!response.ok) throw new Error((await response.json().catch(() => ({}))).detail ?? 'Could not export submissions.')
    const url = URL.createObjectURL(await response.blob())
    const link = document.createElement('a')
    link.href = url
    link.download = `form-${formId}-submissions.csv`
    link.click()
    URL.revokeObjectURL(url)
  },
  submit: (form_id: string, answers: Record<string, unknown>) => request<Submission>('/submissions/', { method: 'POST', body: JSON.stringify({ form_id, answers }) }),
  upload: async (submissionId: string, fieldId: string | File, maybeFile?: File) => {
    const file = fieldId instanceof File ? fieldId : maybeFile!
    const resolvedFieldId = typeof fieldId === 'string' ? fieldId : 'attachment'
    const body = new FormData(); body.append('file', file); body.append('field_id', resolvedFieldId)
    const response = await fetch(`${API_URL}/files/upload/${submissionId}`, { method: 'POST', credentials: 'include', body })
    if (!response.ok) throw new Error((await response.json().catch(() => ({}))).detail ?? 'Upload failed.')
    return response.json() as Promise<{ message: string; file_id: string }>
  },
}
