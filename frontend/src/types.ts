export type FieldType = 'text' | 'number' | 'email' | 'textarea' | 'file' | 'checkbox' | 'radio' | 'yes_no' | 'datetime'

export interface FormField {
  id: string
  label: string
  type: FieldType
  options?: string[]
  validation?: { required?: boolean; min_length?: number; max_length?: number }
}

export interface Form {
  id: string
  title: string
  organization_id: string
  created_by_user_id: string | null
  is_active: boolean
  structure: FormField[]
  created_at: string
}

export interface Submission {
  id: string
  form_id: string
  answers: Record<string, unknown>
  created_at: string
}

export interface SubmissionResponse {
  total: number
  skip: number
  limit: number
  data: Submission[]
}

export interface CurrentUser {
  id: string
  email: string
  organization_id: string
  role: 'owner' | 'admin' | 'member'
}
