import { defineStore } from 'pinia'
import { ref } from 'vue'
import { roadmapsApi } from '@/api'
import type { Roadmap, RoadmapNode, NodeConnection, RoadmapCreate, NodeCreate } from '@/api'
import type { AxiosError } from 'axios'

export const useRoadmapsStore = defineStore('roadmaps', () => {
  const roadmaps = ref<Roadmap[]>([])
  const currentRoadmap = ref<Roadmap | null>(null)
  const nodes = ref<RoadmapNode[]>([])
  const connections = ref<NodeConnection[]>([])
  const currentNode = ref<RoadmapNode | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  async function fetchMyRoadmaps(userId: number) {
    loading.value = true
    error.value = null
    try {
      const response = await roadmapsApi.getAll(userId)
      roadmaps.value = response.data
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      error.value = axiosError.response?.data?.detail || 'Error al cargar roadmaps'
    } finally {
      loading.value = false
    }
  }

  async function fetchRoadmap(id: number) {
    loading.value = true
    error.value = null
    try {
      const response = await roadmapsApi.getById(id)
      currentRoadmap.value = response.data
      nodes.value = response.data.nodes || []
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      error.value = axiosError.response?.data?.detail || 'Error al cargar roadmap'
    } finally {
      loading.value = false
    }
  }

  async function fetchConnections(roadmapId: number) {
    try {
      const response = await roadmapsApi.getConnections(roadmapId)
      connections.value = response.data
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      error.value = axiosError.response?.data?.detail || 'Error al cargar conexiones'
    }
  }

  async function createRoadmap(userId: number, data: RoadmapCreate) {
    loading.value = true
    error.value = null
    try {
      const response = await roadmapsApi.create(userId, data)
      roadmaps.value.unshift(response.data)
      return response.data
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      error.value = axiosError.response?.data?.detail || 'Error al crear roadmap'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteRoadmap(roadmapId: number) {
    loading.value = true
    error.value = null
    try {
      await roadmapsApi.delete(roadmapId)
      roadmaps.value = roadmaps.value.filter(r => r.id !== roadmapId)
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      error.value = axiosError.response?.data?.detail || 'Error al eliminar roadmap'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchNode(roadmapId: number, nodeId: number) {
    loading.value = true
    error.value = null
    try {
      const response = await roadmapsApi.getNode(roadmapId, nodeId)
      currentNode.value = response.data
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      error.value = axiosError.response?.data?.detail || 'Error al cargar nodo'
    } finally {
      loading.value = false
    }
  }

  async function createNode(roadmapId: number, data: NodeCreate) {
    loading.value = true
    error.value = null
    try {
      const response = await roadmapsApi.createNode(roadmapId, data)
      nodes.value.push(response.data)
      return response.data
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      error.value = axiosError.response?.data?.detail || 'Error al crear nodo'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function updateNode(roadmapId: number, nodeId: number, data: Partial<NodeCreate>) {
    loading.value = true
    error.value = null
    try {
      const response = await roadmapsApi.updateNode(roadmapId, nodeId, data)
      const index = nodes.value.findIndex(n => n.id === nodeId)
      if (index !== -1) nodes.value[index] = response.data
      if (currentNode.value?.id === nodeId) currentNode.value = response.data
      return response.data
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      error.value = axiosError.response?.data?.detail || 'Error al actualizar nodo'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function deleteNode(roadmapId: number, nodeId: number) {
    loading.value = true
    error.value = null
    try {
      await roadmapsApi.deleteNode(roadmapId, nodeId)
      nodes.value = nodes.value.filter(n => n.id !== nodeId)
    } catch (err) {
      const axiosError = err as AxiosError<{ detail?: string }>
      error.value = axiosError.response?.data?.detail || 'Error al eliminar nodo'
      throw err
    } finally {
      loading.value = false
    }
  }

  function clearCurrent() {
    currentRoadmap.value = null
    currentNode.value = null
    nodes.value = []
    connections.value = []
  }

  function clearNode() {
    currentNode.value = null
  }

  return {
    roadmaps,
    currentRoadmap,
    nodes,
    connections,
    currentNode,
    loading,
    error,
    fetchMyRoadmaps,
    fetchRoadmap,
    fetchConnections,
    createRoadmap,
    deleteRoadmap,
    fetchNode,
    createNode,
    updateNode,
    deleteNode,
    clearCurrent,
    clearNode
  }
})
