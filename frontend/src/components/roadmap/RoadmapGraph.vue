<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { RoadmapNode, NodeConnection } from '@/api'

const NODE_WIDTH = 220
const NODE_HEIGHT = 100
const HORIZONTAL_GAP = 40
const VERTICAL_GAP = 80
const LEVEL_PADDING = 120

const props = defineProps<{
  nodes: RoadmapNode[]
  connections: NodeConnection[]
}>()

const emit = defineEmits<{
  (e: 'node-click', node: RoadmapNode): void
}>()

const containerRef = ref<HTMLElement | null>(null)
const scale = ref(0.9)
const offset = ref({ x: 80, y: 30 })
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })

const levelColors = {
  beginner: { bg: 'bg-emerald-500/15', border: 'border-emerald-500', text: 'text-emerald-400', dot: 'bg-emerald-500' },
  intermediate: { bg: 'bg-amber-500/15', border: 'border-amber-500', text: 'text-amber-400', dot: 'bg-amber-500' },
  advanced: { bg: 'bg-rose-500/15', border: 'border-rose-500', text: 'text-rose-400', dot: 'bg-rose-500' }
}

const levelLabels = {
  beginner: 'Principiante',
  intermediate: 'Intermedio',
  advanced: 'Avanzado'
}

const levelOrder = ['beginner', 'intermediate', 'advanced'] as const

const nodesByLevel = computed(() => {
  const grouped: Record<string, RoadmapNode[]> = {
    beginner: [],
    intermediate: [],
    advanced: []
  }
  props.nodes.forEach(node => {
    const level = node.level as string
    if (grouped[level]) {
      grouped[level].push(node)
    }
  })
  Object.keys(grouped).forEach(level => {
    grouped[level].sort((a, b) => (a.order_index ?? 0) - (b.order_index ?? 0))
  })
  return grouped
})

const calculatedPositions = computed(() => {
  const positions: Record<number, { x: number; y: number }> = {}
  let currentY = 0

  levelOrder.forEach((level) => {
    const nodesInLevel = nodesByLevel.value[level] ?? []
    const startX = LEVEL_PADDING

    nodesInLevel.forEach((node, index) => {
      positions[node.id] = {
        x: startX + index * (NODE_WIDTH + HORIZONTAL_GAP),
        y: currentY + 50
      }
    })

    currentY += NODE_HEIGHT + VERTICAL_GAP
  })

  return positions
})

const levelYPositions = computed(() => {
  const positions: Record<string, number> = {}
  let currentY = 0

  levelOrder.forEach((level) => {
    positions[level] = currentY + 15
    currentY += NODE_HEIGHT + VERTICAL_GAP
  })

  return positions
})

const svgPaths = computed(() => {
  return props.connections.map(conn => {
    const fromPos = calculatedPositions.value[conn.from_node_id]
    const toPos = calculatedPositions.value[conn.to_node_id]
    if (!fromPos || !toPos) return null

    const fromX = fromPos.x + NODE_WIDTH / 2
    const fromY = fromPos.y + NODE_HEIGHT
    const toX = toPos.x + NODE_WIDTH / 2
    const toY = toPos.y

    const controlOffset = Math.abs(toY - fromY) / 2
    return `M ${fromX} ${fromY} C ${fromX} ${fromY + controlOffset}, ${toX} ${toY - controlOffset}, ${toX} ${toY}`
  }).filter(Boolean)
})

function handleWheel(e: WheelEvent) {
  e.preventDefault()
  const delta = e.deltaY > 0 ? -0.1 : 0.1
  scale.value = Math.max(0.5, Math.min(2, scale.value + delta))
}

function handleMouseDown(e: MouseEvent) {
  if (e.target === containerRef.value || (e.target as HTMLElement).tagName === 'svg') {
    isDragging.value = true
    dragStart.value = { x: e.clientX - offset.value.x, y: e.clientY - offset.value.y }
  }
}

function handleMouseMove(e: MouseEvent) {
  if (isDragging.value) {
    offset.value = {
      x: e.clientX - dragStart.value.x,
      y: e.clientY - dragStart.value.y
    }
  }
}

function handleMouseUp() {
  isDragging.value = false
}

function handleNodeClick(node: RoadmapNode) {
  emit('node-click', node)
}

function resetView() {
  scale.value = 1
  offset.value = { x: 50, y: 50 }
}

onMounted(() => {
  window.addEventListener('mouseup', handleMouseUp)
  window.addEventListener('mousemove', handleMouseMove)
})
</script>

<template>
  <div class="relative w-full h-full bg-bg-secondary rounded-2xl overflow-hidden">
    <!-- Controls -->
    <div class="absolute top-4 right-4 z-10 flex gap-2">
      <button
        @click="scale = Math.min(2, scale + 0.2)"
        class="w-10 h-10 bg-card border border-line rounded-xl flex items-center justify-center text-text hover:bg-primary/10 transition-colors"
      >
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
      </button>
      <button
        @click="scale = Math.max(0.5, scale - 0.2)"
        class="w-10 h-10 bg-card border border-line rounded-xl flex items-center justify-center text-text hover:bg-primary/10 transition-colors"
      >
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
        </svg>
      </button>
      <button
        @click="resetView"
        class="w-10 h-10 bg-card border border-line rounded-xl flex items-center justify-center text-text hover:bg-primary/10 transition-colors"
      >
        <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
        </svg>
      </button>
    </div>

    <!-- Legend -->
    <div class="absolute top-4 left-4 z-10 bg-card/90 backdrop-blur border border-line rounded-xl p-3">
      <div class="text-xs font-medium text-text-secondary mb-2">Niveles</div>
      <div class="space-y-1.5">
        <div v-for="(label, level) in levelLabels" :key="level" class="flex items-center gap-2">
          <div :class="['w-3 h-3 rounded-full', levelColors[level as keyof typeof levelColors].bg, 'border', levelColors[level as keyof typeof levelColors].border]" />
          <span class="text-xs text-text-secondary">{{ label }}</span>
        </div>
      </div>
    </div>

    <!-- Graph Container -->
    <div
      ref="containerRef"
      class="w-full h-full cursor-grab"
      :class="{ 'cursor-grabbing': isDragging }"
      @wheel="handleWheel"
      @mousedown="handleMouseDown"
    >
      <div
        class="relative transition-transform duration-100"
        :style="{
          transform: `translate(${offset.x}px, ${offset.y}px) scale(${scale})`,
          transformOrigin: '0 0'
        }"
      >
        <!-- SVG Connections -->
        <svg class="absolute inset-0 w-[2000px] h-[1000px] pointer-events-none">
          <defs>
            <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
              <polygon points="0 0, 10 3.5, 0 7" fill="var(--color-primary)" opacity="0.5" />
            </marker>
          </defs>
          <path
            v-for="(path, index) in svgPaths"
            :key="index"
            :d="path || ''"
            fill="none"
            stroke="var(--color-primary)"
            stroke-width="2"
            stroke-opacity="0.3"
            marker-end="url(#arrowhead)"
          />
        </svg>

        <!-- Level Labels -->
        <div
          v-for="(label, level) in levelLabels"
          :key="`label-${level}`"
          class="absolute text-xs font-semibold px-3 py-1.5 rounded-lg border"
          :class="[levelColors[level as keyof typeof levelColors].bg, levelColors[level as keyof typeof levelColors].text, levelColors[level as keyof typeof levelColors].border]"
          :style="{
            left: '10px',
            top: `${levelYPositions[level as string] + 35}px`
          }"
        >
          {{ label }}
        </div>

        <!-- Nodes -->
        <div
          v-for="node in nodes"
          :key="node.id"
          class="absolute cursor-pointer group"
          :style="{
            left: `${calculatedPositions[node.id]?.x ?? 0}px`,
            top: `${calculatedPositions[node.id]?.y ?? 0}px`,
            width: `${NODE_WIDTH}px`
          }"
          @click="handleNodeClick(node)"
        >
          <div
            class="h-full p-4 rounded-xl border-2 transition-all duration-200 group-hover:scale-[1.02] group-hover:shadow-xl group-hover:shadow-primary/10"
            :class="[
              levelColors[node.level as keyof typeof levelColors]?.bg ?? 'bg-card',
              levelColors[node.level as keyof typeof levelColors]?.border ?? 'border-line',
              node.content ? 'ring-2 ring-emerald-500/30' : ''
            ]"
          >
            <div class="flex items-start justify-between gap-2 mb-2">
              <h4 class="font-semibold text-text text-sm leading-tight line-clamp-2">{{ node.title }}</h4>
              <div
                v-if="node.content"
                class="w-5 h-5 rounded-full bg-emerald-500 flex items-center justify-center flex-shrink-0"
              >
                <svg class="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <div
                v-else
                class="w-5 h-5 rounded-full border-2 border-text-secondary/30 flex-shrink-0"
              />
            </div>
            <p v-if="node.description" class="text-xs text-text-secondary line-clamp-3">
              {{ node.description }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
