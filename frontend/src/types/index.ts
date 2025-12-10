export interface User {
  id: number
  email: string
  username: string
  full_name: string
  role: 'student' | 'teacher' | 'admin'
  is_active: boolean
  created_at: string
  updated_at: string | null
}

export interface UserCreate {
  email: string
  username: string
  password: string
  full_name: string
  role?: 'student' | 'teacher'
}

export interface UserUpdate {
  email?: string
  username?: string
  password?: string
  full_name?: string
}

export interface Course {
  id: number
  title: string
  description: string | null
  is_published: boolean
  teacher_id: number
  created_at: string
  updated_at: string
}

export interface CourseCreate {
  title: string
  description?: string
  content: string
}

export interface Module {
  id: number
  title: string
  description: string | null
  position: number
  course_id: number
  created_at: string
}

export interface ModuleCreate {
  title: string
  description?: string
}

export interface Lesson {
  id: number
  title: string
  content: string | null
  position: number
  module_id: number
}

export interface LessonCreate {
  title: string
  content?: string
}

export interface Question {
  id: number
  text: string
  question_type: 'multiple_choice' | 'true_false' | 'open'
  difficulty: 'easy' | 'medium' | 'hard'
  lesson_id: number
  options?: QuestionOption[]
}

export interface QuestionCreate {
  text: string
  question_type: 'multiple_choice' | 'true_false' | 'open'
  difficulty: 'easy' | 'medium' | 'hard'
  options?: { text: string; is_correct: boolean }[]
}

export interface QuestionOption {
  id: number
  text: string
  is_correct: boolean
}

export interface Attempt {
  id: number
  student_id: number
  question_id: number
  selected_option_id: number | null
  is_correct: boolean
  response_time_seconds: number | null
  created_at: string
}

export interface StudentStats {
  total_attempts: number
  correct_attempts: number
  accuracy_rate: number
}
