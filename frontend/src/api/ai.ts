import apiClient from './client'

interface GenerateCourseResponse {
  course_id: number
  title: string
  modules_count: number
  message: string
}

interface GenerateModuleContentResponse {
  message: string
  module_id: number
  lessons_count?: number
}

export const aiApi = {
  generateCourse: (file: File, title: string, teacherId: number) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('title', title)
    formData.append('teacher_id', teacherId.toString())

    return apiClient.post<GenerateCourseResponse>('/ai/generate-course', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 120000
    })
  },

  generateModuleContent: (moduleId: number) => {
    return apiClient.post<GenerateModuleContentResponse>(
      `/ai/modules/${moduleId}/generate-content`,
      {},
      { timeout: 120000 }
    )
  }
}
