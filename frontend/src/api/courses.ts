import apiClient from './client'
import type { Course, CourseCreate, Module, ModuleCreate, Lesson, LessonCreate, Question, QuestionCreate } from '@/types'

export const coursesApi = {
  getAll: () => apiClient.get<Course[]>('/courses/'),
  getMyCourses: (userId: number) => apiClient.get<Course[]>(`/courses/?teacher_id=${userId}`),
  getById: (id: number) => apiClient.get<Course>(`/courses/${id}`),
  create: (userId: number, data: CourseCreate) => apiClient.post<Course>(`/courses/?teacher_id=${userId}`, data),
  update: (id: number, data: Partial<Course>) => apiClient.patch<Course>(`/courses/${id}`, data),
  delete: (id: number) => apiClient.delete(`/courses/${id}`),

  getModules: (courseId: number) => apiClient.get<Module[]>(`/courses/${courseId}/modules/`),
  getModule: (courseId: number, moduleId: number) => apiClient.get<Module>(`/courses/${courseId}/modules/${moduleId}`),
  createModule: (courseId: number, data: ModuleCreate) => apiClient.post<Module>(`/courses/${courseId}/modules/`, data),
  updateModule: (courseId: number, moduleId: number, data: Partial<Module>) => apiClient.patch<Module>(`/courses/${courseId}/modules/${moduleId}`, data),
  deleteModule: (courseId: number, moduleId: number) => apiClient.delete(`/courses/${courseId}/modules/${moduleId}`),

  getLessons: (moduleId: number) => apiClient.get<Lesson[]>(`/modules/${moduleId}/lessons/`),
  getLesson: (moduleId: number, lessonId: number) => apiClient.get<Lesson>(`/modules/${moduleId}/lessons/${lessonId}`),
  createLesson: (moduleId: number, data: LessonCreate) => apiClient.post<Lesson>(`/modules/${moduleId}/lessons/`, data),
  updateLesson: (moduleId: number, lessonId: number, data: Partial<Lesson>) => apiClient.patch<Lesson>(`/modules/${moduleId}/lessons/${lessonId}`, data),
  deleteLesson: (moduleId: number, lessonId: number) => apiClient.delete(`/modules/${moduleId}/lessons/${lessonId}`),

  getQuestions: (lessonId: number) => apiClient.get<Question[]>(`/lessons/${lessonId}/questions/`),
  getQuestion: (lessonId: number, questionId: number) => apiClient.get<Question>(`/lessons/${lessonId}/questions/${questionId}`),
  createQuestion: (lessonId: number, data: QuestionCreate) => apiClient.post<Question>(`/lessons/${lessonId}/questions/`, data),
  updateQuestion: (lessonId: number, questionId: number, data: Partial<Question>) => apiClient.patch<Question>(`/lessons/${lessonId}/questions/${questionId}`, data),
  deleteQuestion: (lessonId: number, questionId: number) => apiClient.delete(`/lessons/${lessonId}/questions/${questionId}`)
}
