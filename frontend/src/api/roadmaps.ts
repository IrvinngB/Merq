import apiClient from './client'

export interface RoadmapNode {
  id: number
  roadmap_id: number
  title: string
  description: string | null
  content: string | null
  level: 'beginner' | 'intermediate' | 'advanced'
  position_x: number
  position_y: number
  order_index: number
  is_completed: boolean
}

export interface NodeConnection {
  id: number
  from_node_id: number
  to_node_id: number
}

export interface Roadmap {
  id: number
  title: string
  description: string | null
  creator_id: number
  nodes?: RoadmapNode[]
}

export interface RoadmapCreate {
  title: string
  description?: string
}

export interface NodeCreate {
  title: string
  description?: string
  content?: string
  level?: 'beginner' | 'intermediate' | 'advanced'
  position_x?: number
  position_y?: number
  order_index?: number
  is_completed?: boolean
}

export const roadmapsApi = {
  getAll: (creatorId?: number) => {
    const params = creatorId ? `?creator_id=${creatorId}` : ''
    return apiClient.get<Roadmap[]>(`/roadmaps/${params}`)
  },

  getById: (id: number) => apiClient.get<Roadmap>(`/roadmaps/${id}`),

  create: (creatorId: number, data: RoadmapCreate) =>
    apiClient.post<Roadmap>(`/roadmaps/?creator_id=${creatorId}`, data),

  update: (id: number, data: Partial<RoadmapCreate>) =>
    apiClient.patch<Roadmap>(`/roadmaps/${id}`, data),

  delete: (id: number) => apiClient.delete(`/roadmaps/${id}`),

  getNodes: (roadmapId: number) =>
    apiClient.get<RoadmapNode[]>(`/roadmaps/${roadmapId}/nodes/`),

  getNode: (roadmapId: number, nodeId: number) =>
    apiClient.get<RoadmapNode>(`/roadmaps/${roadmapId}/nodes/${nodeId}`),

  createNode: (roadmapId: number, data: NodeCreate) =>
    apiClient.post<RoadmapNode>(`/roadmaps/${roadmapId}/nodes/`, data),

  updateNode: (roadmapId: number, nodeId: number, data: Partial<NodeCreate>) =>
    apiClient.patch<RoadmapNode>(`/roadmaps/${roadmapId}/nodes/${nodeId}`, data),

  deleteNode: (roadmapId: number, nodeId: number) =>
    apiClient.delete(`/roadmaps/${roadmapId}/nodes/${nodeId}`),

  toggleNodeComplete: (roadmapId: number, nodeId: number, isCompleted: boolean) =>
    apiClient.patch<RoadmapNode>(`/roadmaps/${roadmapId}/nodes/${nodeId}`, { is_completed: isCompleted }),

  getConnections: (roadmapId: number) =>
    apiClient.get<NodeConnection[]>(`/roadmaps/${roadmapId}/connections`),

  createConnection: (roadmapId: number, fromNodeId: number, toNodeId: number) =>
    apiClient.post<NodeConnection>(`/roadmaps/${roadmapId}/connections`, {
      from_node_id: fromNodeId,
      to_node_id: toNodeId
    }),

  deleteConnection: (roadmapId: number, connectionId: number) =>
    apiClient.delete(`/roadmaps/${roadmapId}/connections/${connectionId}`)
}

export const aiApi = {
  generateRoadmap: (file: File, title: string, creatorId: number) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('title', title)
    formData.append('creator_id', creatorId.toString())

    return apiClient.post<{ roadmap_id: number; title: string; nodes_count: number; message: string }>(
      '/ai/generate-roadmap',
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 120000
      }
    )
  },

  generateNodeContent: (nodeId: number) => {
    return apiClient.post<{ message: string; node_id: number }>(
      `/ai/nodes/${nodeId}/generate-content`,
      {},
      { timeout: 120000 }
    )
  },

  importRoadmap: (title: string, creatorId: number, data: {
    description?: string
    nodes: Array<{
      title: string
      description?: string | null
      level: string
      order: number
      prerequisites: number[]
    }>
  }) => {
    return apiClient.post<{ roadmap_id: number; title: string; nodes_count: number; message: string }>(
      '/ai/import-roadmap',
      {
        title,
        creator_id: creatorId,
        data
      }
    )
  },

  autoLayout: (roadmapId: number) => {
    return apiClient.post<{ message: string; roadmap_id: number; nodes_updated: number }>(
      `/ai/${roadmapId}/auto-layout`
    )
  }
}
