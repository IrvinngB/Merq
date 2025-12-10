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

interface GenerateRoadmapResponse {
  roadmap_id: number
  title: string
  nodes_count: number
  message: string
}

interface ImportNodeData {
  title: string
  description?: string
  level: 'beginner' | 'intermediate' | 'advanced'
  order: number
  prerequisites: number[]
}

interface ImportRoadmapData {
  description?: string
  nodes: ImportNodeData[]
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
  },

  generateRoadmap: (file: File, title: string, creatorId: number) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('title', title)
    formData.append('creator_id', creatorId.toString())

    return apiClient.post<GenerateRoadmapResponse>('/ai/generate-roadmap', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      timeout: 120000
    })
  },

  generateNodeContent: (nodeId: number) => {
    return apiClient.post<{ message: string; node_id: number }>(
      `/ai/nodes/${nodeId}/generate-content`,
      {},
      { timeout: 120000 }
    )
  },

  importRoadmap: (title: string, creatorId: number, data: ImportRoadmapData) => {
    return apiClient.post<GenerateRoadmapResponse>('/ai/import-roadmap', {
      title,
      creator_id: creatorId,
      data
    })
  }
}
