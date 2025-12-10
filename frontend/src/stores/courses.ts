import { defineStore } from 'pinia'
import { ref } from 'vue'
import { coursesApi } from '@/api'
import type { Course, Module, ModuleCreate, Lesson, LessonCreate, Question, QuestionCreate } from '@/types'
import type { AxiosError } from 'axios'

export const useCoursesStore = defineStore('courses', () => {
  const courses = ref<Course[]>([])
  const currentCourse = ref<Course | null>(null)
  const modules = ref<Module[]>([])
  const currentModule = ref<Module | null>(null)
  const lessons = ref<Lesson[]>([])
  const currentLesson = ref<Lesson | null>(null)
  const questions = ref<Question[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchMyCourses(userId: number) {
    loading.value = true
    error.value = null
    try {
      const response = await coursesApi.getMyCourses(userId)
      courses.value = response.data
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      error.value = axiosError.response?.data?.detail || 'Error al cargar cursos'
    } finally {
      loading.value = false
    }
  }

  async function fetchCourse(id: number) {
    loading.value = true
    error.value = null
    try {
      const response = await coursesApi.getById(id)
      currentCourse.value = response.data
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      error.value = axiosError.response?.data?.detail || 'Error al cargar curso'
    } finally {
      loading.value = false
    }
  }

  async function fetchModules(courseId: number) {
    loading.value = true
    try {
      const response = await coursesApi.getModules(courseId)
      modules.value = response.data
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      error.value = axiosError.response?.data?.detail || 'Error al cargar módulos'
    } finally {
      loading.value = false
    }
  }

  async function fetchModule(courseId: number, moduleId: number) {
    loading.value = true
    error.value = null
    try {
      const response = await coursesApi.getModule(courseId, moduleId)
      currentModule.value = response.data
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      error.value = axiosError.response?.data?.detail || 'Error al cargar módulo'
    } finally {
      loading.value = false
    }
  }

  async function createModule(courseId: number, data: ModuleCreate) {
    loading.value = true
    error.value = null
    try {
      const response = await coursesApi.createModule(courseId, data)
      modules.value.push(response.data)
      return response.data
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      error.value = axiosError.response?.data?.detail || 'Error al crear módulo'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateModule(courseId: number, moduleId: number, data: Partial<Module>) {
    loading.value = true
    error.value = null
    try {
      const response = await coursesApi.updateModule(courseId, moduleId, data)
      const index = modules.value.findIndex(m => m.id === moduleId)
      if (index !== -1) modules.value[index] = response.data
      if (currentModule.value?.id === moduleId) currentModule.value = response.data
      return response.data
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      error.value = axiosError.response?.data?.detail || 'Error al actualizar módulo'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteCourse(courseId: number) {
    loading.value = true
    error.value = null
    try {
      await coursesApi.delete(courseId)
      courses.value = courses.value.filter(c => c.id !== courseId)
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      error.value = axiosError.response?.data?.detail || 'Error al eliminar curso'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteModule(courseId: number, moduleId: number) {
    loading.value = true
    error.value = null
    try {
      await coursesApi.deleteModule(courseId, moduleId)
      modules.value = modules.value.filter(m => m.id !== moduleId)
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      error.value = axiosError.response?.data?.detail || 'Error al eliminar módulo'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchLessons(moduleId: number) {
    loading.value = true
    try {
      const response = await coursesApi.getLessons(moduleId)
      lessons.value = response.data
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      error.value = axiosError.response?.data?.detail || 'Error al cargar lecciones'
    } finally {
      loading.value = false
    }
  }

  async function fetchLesson(moduleId: number, lessonId: number) {
    loading.value = true
    error.value = null
    try {
      const response = await coursesApi.getLesson(moduleId, lessonId)
      currentLesson.value = response.data
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      error.value = axiosError.response?.data?.detail || 'Error al cargar lección'
    } finally {
      loading.value = false
    }
  }

  async function createLesson(moduleId: number, data: LessonCreate) {
    loading.value = true
    error.value = null
    try {
      const response = await coursesApi.createLesson(moduleId, data)
      lessons.value.push(response.data)
      return response.data
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      error.value = axiosError.response?.data?.detail || 'Error al crear lección'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateLesson(moduleId: number, lessonId: number, data: Partial<Lesson>) {
    loading.value = true
    error.value = null
    try {
      const response = await coursesApi.updateLesson(moduleId, lessonId, data)
      const index = lessons.value.findIndex(l => l.id === lessonId)
      if (index !== -1) lessons.value[index] = response.data
      if (currentLesson.value?.id === lessonId) currentLesson.value = response.data
      return response.data
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      error.value = axiosError.response?.data?.detail || 'Error al actualizar lección'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteLesson(moduleId: number, lessonId: number) {
    loading.value = true
    error.value = null
    try {
      await coursesApi.deleteLesson(moduleId, lessonId)
      lessons.value = lessons.value.filter(l => l.id !== lessonId)
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      error.value = axiosError.response?.data?.detail || 'Error al eliminar lección'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchQuestions(lessonId: number) {
    loading.value = true
    try {
      const response = await coursesApi.getQuestions(lessonId)
      questions.value = response.data
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      error.value = axiosError.response?.data?.detail || 'Error al cargar preguntas'
    } finally {
      loading.value = false
    }
  }

  async function createQuestion(lessonId: number, data: QuestionCreate) {
    loading.value = true
    error.value = null
    try {
      const response = await coursesApi.createQuestion(lessonId, data)
      questions.value.push(response.data)
      return response.data
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      error.value = axiosError.response?.data?.detail || 'Error al crear pregunta'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateQuestion(lessonId: number, questionId: number, data: Partial<Question>) {
    loading.value = true
    error.value = null
    try {
      const response = await coursesApi.updateQuestion(lessonId, questionId, data)
      const index = questions.value.findIndex(q => q.id === questionId)
      if (index !== -1) questions.value[index] = response.data
      return response.data
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      error.value = axiosError.response?.data?.detail || 'Error al actualizar pregunta'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteQuestion(lessonId: number, questionId: number) {
    loading.value = true
    error.value = null
    try {
      await coursesApi.deleteQuestion(lessonId, questionId)
      questions.value = questions.value.filter(q => q.id !== questionId)
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      error.value = axiosError.response?.data?.detail || 'Error al eliminar pregunta'
      throw err
    } finally {
      loading.value = false
    }
  }

  function clearCurrent() {
    currentCourse.value = null
    currentModule.value = null
    currentLesson.value = null
    modules.value = []
    lessons.value = []
    questions.value = []
  }

  function clearModule() {
    currentModule.value = null
    currentLesson.value = null
    lessons.value = []
    questions.value = []
  }

  function clearLesson() {
    currentLesson.value = null
    questions.value = []
  }

  return {
    courses,
    currentCourse,
    modules,
    currentModule,
    lessons,
    currentLesson,
    questions,
    loading,
    error,
    fetchMyCourses,
    fetchCourse,
    fetchModules,
    fetchModule,
    createModule,
    updateModule,
    deleteCourse,
    deleteModule,
    fetchLessons,
    fetchLesson,
    createLesson,
    updateLesson,
    deleteLesson,
    fetchQuestions,
    createQuestion,
    updateQuestion,
    deleteQuestion,
    clearCurrent,
    clearModule,
    clearLesson
  }
})
