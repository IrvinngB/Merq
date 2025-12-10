<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import type { RoadmapNode, NodeConnection } from '@/api'

const props = defineProps<{
  nodes: RoadmapNode[]
  connections: NodeConnection[]
  editMode?: boolean
}>()

const emit = defineEmits<{
  (e: 'node-click', node: RoadmapNode): void
  (e: 'node-move', nodeId: number, x: number, y: number): void
  (e: 'connection-click', connection: NodeConnection, fromNode: RoadmapNode, toNode: RoadmapNode): void
  (e: 'add-node', level: 'beginner' | 'intermediate' | 'advanced'): void
}>()

// Constantes de diseño
const NODE_WIDTH = 170
const NODE_HEIGHT = 52
const NODE_GAP_X = 16
const NODE_GAP_Y = 70
const PADDING = 60
const MAX_NODES_PER_ROW = 8 // Máximo de nodos por fila en cada nivel

const containerRef = ref<HTMLElement | null>(null)
const scale = ref(1)
const offset = ref({ x: 0, y: 0 })
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })

// Estado para drag de nodos
const draggingNode = ref<number | null>(null)
const nodeDragStart = ref({ x: 0, y: 0, nodeX: 0, nodeY: 0 })
const customNodePositions = ref<Record<number, { x: number; y: number }>>({})

// Estado para tooltip de conexiones
const hoveredConnection = ref<{ connection: NodeConnection; x: number; y: number } | null>(null)

// Configuración de niveles - Verde, Amarillo, Rojo
const levelConfig = {
  beginner: { 
    label: 'Principiante',
    labelBg: 'bg-emerald-500',
    nodeBg: 'bg-emerald-500',
    nodeText: 'text-white',
    borderColor: 'border-emerald-400'
  },
  intermediate: { 
    label: 'Intermedio',
    labelBg: 'bg-amber-500',
    nodeBg: 'bg-amber-500',
    nodeText: 'text-white',
    borderColor: 'border-amber-400'
  },
  advanced: { 
    label: 'Avanzado',
    labelBg: 'bg-rose-500',
    nodeBg: 'bg-rose-500',
    nodeText: 'text-white',
    borderColor: 'border-rose-400'
  }
}

const levelOrder = ['beginner', 'intermediate', 'advanced'] as const

// Agrupar nodos por nivel
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
  
  // Ordenar por order_index
  Object.keys(grouped).forEach(level => {
    grouped[level]?.sort((a, b) => (a.order_index ?? 0) - (b.order_index ?? 0))
  })
  
  return grouped
})

// Calcular filas por nivel (para distribuir nodos en múltiples filas)
const rowsPerLevel = computed(() => {
  const rows: Record<string, number> = {}
  levelOrder.forEach(level => {
    const count = nodesByLevel.value[level]?.length || 0
    rows[level] = Math.ceil(count / MAX_NODES_PER_ROW)
  })
  return rows
})

// Calcular altura total necesaria para cada nivel
const levelHeights = computed(() => {
  const heights: Record<string, number> = {}
  levelOrder.forEach(level => {
    const rows = rowsPerLevel.value[level] ?? 1
    heights[level] = rows * (NODE_HEIGHT + 12) + 40 // 40 para el label
  })
  return heights
})

// Ancho total del canvas
const canvasWidth = computed(() => {
  return MAX_NODES_PER_ROW * (NODE_WIDTH + NODE_GAP_X) + PADDING * 2
})

// Alto total del canvas
const canvasHeight = computed(() => {
  let totalHeight = PADDING * 2
  levelOrder.forEach(level => {
    totalHeight += (levelHeights.value[level] ?? 0) + NODE_GAP_Y
  })
  return totalHeight
})

// Centro X del canvas
const centerX = computed(() => canvasWidth.value / 2)

// Calcular posición Y de inicio de cada nivel
const levelStartY = computed(() => {
  const startY: Record<string, number> = {}
  let currentY = PADDING
  
  levelOrder.forEach(level => {
    startY[level] = currentY
    currentY += (levelHeights.value[level] ?? 0) + NODE_GAP_Y
  })
  
  return startY
})

// Calcular posiciones de nodos con distribución en filas
const nodePositions = computed(() => {
  const positions: Record<number, { x: number; y: number; row: number }> = {}
  
  levelOrder.forEach((level) => {
    const nodesInLevel = nodesByLevel.value[level] || []
    const baseY = (levelStartY.value[level] ?? 0) + 35 // Espacio para el label
    
    nodesInLevel.forEach((node, nodeIndex) => {
      // Si hay posición custom (por drag), usarla
      const customPos = customNodePositions.value[node.id]
      if (customPos) {
        positions[node.id] = { x: customPos.x, y: customPos.y, row: 0 }
        return
      }
      
      const row = Math.floor(nodeIndex / MAX_NODES_PER_ROW)
      const col = nodeIndex % MAX_NODES_PER_ROW
      const nodesInThisRow = Math.min(MAX_NODES_PER_ROW, nodesInLevel.length - row * MAX_NODES_PER_ROW)
      
      // Centrar la fila
      const rowWidth = nodesInThisRow * (NODE_WIDTH + NODE_GAP_X) - NODE_GAP_X
      const startX = (canvasWidth.value - rowWidth) / 2
      
      positions[node.id] = {
        x: startX + col * (NODE_WIDTH + NODE_GAP_X),
        y: baseY + row * (NODE_HEIGHT + 12),
        row
      }
    })
  })
  
  return positions
})

// Generar paths SVG para conexiones con mejor visualización
const connectionPaths = computed(() => {
  return props.connections.map(conn => {
    const fromPos = nodePositions.value[conn.from_node_id]
    const toPos = nodePositions.value[conn.to_node_id]
    
    if (!fromPos || !toPos) return null
    
    const fromX = fromPos.x + NODE_WIDTH / 2
    const fromY = fromPos.y + NODE_HEIGHT
    const toX = toPos.x + NODE_WIDTH / 2
    const toY = toPos.y
    
    // Punto medio para el tooltip
    const midX = (fromX + toX) / 2
    const midY = (fromY + toY) / 2
    
    // Determinar el tipo de conexión
    const horizontalDist = Math.abs(fromX - toX)
    const verticalDist = toY - fromY
    
    let path: string
    
    if (horizontalDist < 10) {
      // Conexión vertical directa
      path = `M ${fromX} ${fromY} L ${toX} ${toY}`
    } else if (verticalDist > 50) {
      // Conexión con curva suave para diferentes niveles
      const curvedMidY = fromY + verticalDist * 0.5
      path = `M ${fromX} ${fromY} 
              C ${fromX} ${curvedMidY}, ${toX} ${curvedMidY}, ${toX} ${toY}`
    } else {
      // Conexión horizontal con curva
      const curveMidX = (fromX + toX) / 2
      path = `M ${fromX} ${fromY} 
              Q ${fromX} ${fromY + 20}, ${curveMidX} ${fromY + 20}
              Q ${toX} ${fromY + 20}, ${toX} ${toY}`
    }
    
    return {
      connection: conn,
      path,
      isDashed: horizontalDist > NODE_WIDTH,
      midX,
      midY
    }
  }).filter(Boolean) as { connection: NodeConnection; path: string; isDashed: boolean; midX: number; midY: number }[]
})

// Obtener nodos por ID para tooltips
function getNodeById(id: number): RoadmapNode | undefined {
  return props.nodes.find(n => n.id === id)
}

// Controles de interacción
function handleWheel(e: WheelEvent) {
  e.preventDefault()
  const delta = e.deltaY > 0 ? -0.08 : 0.08
  scale.value = Math.max(0.4, Math.min(1.8, scale.value + delta))
}

function handleMouseDown(e: MouseEvent) {
  const target = e.target as HTMLElement
  if (target.closest('.node-card')) return
  
  isDragging.value = true
  dragStart.value = { 
    x: e.clientX - offset.value.x, 
    y: e.clientY - offset.value.y 
  }
}

function handleMouseMove(e: MouseEvent) {
  // Drag de nodo específico
  if (draggingNode.value !== null) {
    const dx = (e.clientX - nodeDragStart.value.x) / scale.value
    const dy = (e.clientY - nodeDragStart.value.y) / scale.value
    customNodePositions.value[draggingNode.value] = {
      x: nodeDragStart.value.nodeX + dx,
      y: nodeDragStart.value.nodeY + dy
    }
    return
  }
  
  if (!isDragging.value) return
  offset.value = {
    x: e.clientX - dragStart.value.x,
    y: e.clientY - dragStart.value.y
  }
}

function handleMouseUp() {
  if (draggingNode.value !== null) {
    const pos = customNodePositions.value[draggingNode.value]
    if (pos) {
      emit('node-move', draggingNode.value, pos.x, pos.y)
    }
    draggingNode.value = null
  }
  isDragging.value = false
}

// Drag de nodo
function handleNodeMouseDown(e: MouseEvent, node: RoadmapNode) {
  if (!props.editMode) return
  e.stopPropagation()
  
  draggingNode.value = node.id
  const pos = nodePositions.value[node.id]
  nodeDragStart.value = {
    x: e.clientX,
    y: e.clientY,
    nodeX: pos?.x ?? 0,
    nodeY: pos?.y ?? 0
  }
}

function handleNodeClick(node: RoadmapNode) {
  // Si estaba arrastrando, no emitir click
  if (draggingNode.value !== null) return
  emit('node-click', node)
}

// Hover en conexiones
function handleConnectionMouseEnter(_e: MouseEvent, conn: { connection: NodeConnection; midX: number; midY: number }) {
  hoveredConnection.value = {
    connection: conn.connection,
    x: conn.midX,
    y: conn.midY
  }
}

function handleConnectionMouseLeave() {
  hoveredConnection.value = null
}

function handleConnectionClick(conn: { connection: NodeConnection }) {
  const fromNode = getNodeById(conn.connection.from_node_id)
  const toNode = getNodeById(conn.connection.to_node_id)
  if (fromNode && toNode) {
    emit('connection-click', conn.connection, fromNode, toNode)
  }
}

function zoomIn() {
  scale.value = Math.min(1.8, scale.value + 0.15)
}

function zoomOut() {
  scale.value = Math.max(0.4, scale.value - 0.15)
}

function resetView() {
  scale.value = 1
  offset.value = { x: 0, y: 0 }
  customNodePositions.value = {}
}

function fitToScreen() {
  if (!containerRef.value) return
  
  const containerWidth = containerRef.value.clientWidth
  const containerHeight = containerRef.value.clientHeight
  
  const scaleX = (containerWidth - 60) / canvasWidth.value
  const scaleY = (containerHeight - 60) / canvasHeight.value
  
  scale.value = Math.min(scaleX, scaleY, 1.2)
  offset.value = {
    x: (containerWidth - canvasWidth.value * scale.value) / 2,
    y: 20
  }
}

watch(() => props.nodes.length, () => {
  setTimeout(fitToScreen, 100)
})

onMounted(() => {
  window.addEventListener('mouseup', handleMouseUp)
  window.addEventListener('mousemove', handleMouseMove)
  setTimeout(fitToScreen, 200)
})

onUnmounted(() => {
  window.removeEventListener('mouseup', handleMouseUp)
  window.removeEventListener('mousemove', handleMouseMove)
})
</script>

<template>
  <div 
    ref="containerRef"
    class="relative w-full h-full bg-slate-900 rounded-2xl overflow-hidden select-none"
  >
    <!-- Background Pattern -->
    <div 
      class="absolute inset-0 opacity-[0.02]" 
      style="background-image: radial-gradient(circle, #fff 1px, transparent 1px); background-size: 20px 20px;" 
    />
    
    <!-- Controles -->
    <div class="absolute top-4 right-4 z-20 flex items-center gap-1 bg-slate-800/95 backdrop-blur-sm rounded-lg p-1 border border-slate-700/50">
      <button
        @click="zoomIn"
        class="w-8 h-8 flex items-center justify-center text-slate-400 hover:text-white hover:bg-slate-700 rounded transition-colors"
        title="Acercar"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
        </svg>
      </button>
      <button
        @click="zoomOut"
        class="w-8 h-8 flex items-center justify-center text-slate-400 hover:text-white hover:bg-slate-700 rounded transition-colors"
        title="Alejar"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M20 12H4" />
        </svg>
      </button>
      <div class="w-px h-5 bg-slate-600/50" />
      <button
        @click="fitToScreen"
        class="w-8 h-8 flex items-center justify-center text-slate-400 hover:text-white hover:bg-slate-700 rounded transition-colors"
        title="Ajustar"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
        </svg>
      </button>
      <button
        @click="resetView"
        class="w-8 h-8 flex items-center justify-center text-slate-400 hover:text-white hover:bg-slate-700 rounded transition-colors"
        title="Resetear"
      >
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
      </button>
    </div>

    <!-- Leyenda -->
    <div class="absolute top-4 left-4 z-20 bg-slate-800/95 backdrop-blur-sm rounded-xl p-4 border border-slate-700/50 min-w-[140px] shadow-xl">
      <div class="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-3">Niveles</div>
      <div class="space-y-2.5">
        <div class="flex items-center gap-2.5">
          <div class="w-5 h-5 rounded bg-emerald-500 shadow" />
          <span class="text-sm text-slate-200 font-medium">Principiante</span>
        </div>
        <div class="flex items-center gap-2.5">
          <div class="w-5 h-5 rounded bg-amber-500 shadow" />
          <span class="text-sm text-slate-200 font-medium">Intermedio</span>
        </div>
        <div class="flex items-center gap-2.5">
          <div class="w-5 h-5 rounded bg-rose-500 shadow" />
          <span class="text-sm text-slate-200 font-medium">Avanzado</span>
        </div>
      </div>
      <div class="mt-4 pt-3 border-t border-slate-700/50 space-y-2">
        <div class="flex items-center gap-2.5">
          <div class="w-5 h-5 rounded-full bg-white flex items-center justify-center shadow">
            <svg class="w-3 h-3 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="4">
              <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <span class="text-sm text-slate-400">Completado</span>
        </div>
        <div class="flex items-center gap-2.5">
          <div class="w-5 h-5 rounded-full border-2 border-white bg-white/20 flex items-center justify-center">
            <svg class="w-2.5 h-2.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <span class="text-sm text-slate-400">Con contenido</span>
        </div>
        <div class="flex items-center gap-2.5">
          <div class="w-5 h-5 rounded-full border-2 border-slate-500 bg-slate-700/50" />
          <span class="text-sm text-slate-400">Pendiente</span>
        </div>
      </div>
    </div>

    <!-- Instrucciones -->
    <div class="absolute bottom-4 left-1/2 -translate-x-1/2 z-20">
      <div class="text-[11px] text-slate-500 bg-slate-800/80 backdrop-blur-sm px-3 py-1.5 rounded-full border border-slate-700/30">
        <template v-if="editMode">
          ✏️ Modo edición • Arrastra nodos para moverlos • Click en conexión para info
        </template>
        <template v-else>
          🖱️ Arrastra para mover • Scroll para zoom • Click en nodo para ver contenido
        </template>
      </div>
    </div>

    <!-- Canvas -->
    <div
      class="w-full h-full cursor-grab"
      :class="{ 'cursor-grabbing': isDragging }"
      @wheel.prevent="handleWheel"
      @mousedown="handleMouseDown"
    >
      <div
        class="relative origin-top-left"
        :style="{
          transform: `translate(${offset.x}px, ${offset.y}px) scale(${scale})`,
          width: `${canvasWidth}px`,
          height: `${canvasHeight}px`,
          transition: isDragging ? 'none' : 'transform 0.1s ease-out'
        }"
      >
        <!-- SVG para conexiones -->
        <svg 
          class="absolute inset-0"
          :class="editMode ? 'pointer-events-auto' : 'pointer-events-none'"
          :width="canvasWidth"
          :height="canvasHeight"
        >
          <!-- Línea central vertical punteada -->
          <line
            :x1="centerX"
            :y1="PADDING"
            :x2="centerX"
            :y2="canvasHeight - PADDING"
            stroke="#475569"
            stroke-width="2"
            stroke-dasharray="6 6"
            stroke-linecap="round"
          />
          
          <!-- Conexiones entre nodos -->
          <g v-for="(conn, index) in connectionPaths" :key="`conn-${index}`">
            <!-- Path invisible más grueso para hover -->
            <path
              :d="conn.path"
              fill="none"
              stroke="transparent"
              stroke-width="20"
              class="cursor-pointer"
              @mouseenter="(e) => handleConnectionMouseEnter(e, conn)"
              @mouseleave="handleConnectionMouseLeave"
              @click="() => handleConnectionClick(conn)"
            />
            <!-- Path visible -->
            <path
              :d="conn.path"
              fill="none"
              :stroke="hoveredConnection?.connection.id === conn.connection.id ? '#38bdf8' : '#64748b'"
              :stroke-width="hoveredConnection?.connection.id === conn.connection.id ? 3 : 2"
              :stroke-dasharray="conn.isDashed ? '5 4' : 'none'"
              stroke-linecap="round"
              class="transition-all duration-200 pointer-events-none"
            />
          </g>
        </svg>
        
        <!-- Tooltip de conexión -->
        <div
          v-if="hoveredConnection"
          class="absolute z-50 bg-slate-800 border border-slate-600 rounded-lg shadow-xl px-3 py-2 pointer-events-none"
          :style="{
            left: `${hoveredConnection.x}px`,
            top: `${hoveredConnection.y - 40}px`,
            transform: 'translateX(-50%)'
          }"
        >
          <div class="text-xs text-slate-300 whitespace-nowrap flex items-center gap-2">
            <span class="font-medium text-white">{{ getNodeById(hoveredConnection.connection.from_node_id)?.title }}</span>
            <svg class="w-4 h-4 text-sky-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
            <span class="font-medium text-white">{{ getNodeById(hoveredConnection.connection.to_node_id)?.title }}</span>
          </div>
        </div>

        <!-- Labels de nivel centrados -->
        <div
          v-for="level in levelOrder"
          :key="`label-${level}`"
          class="absolute z-10"
          :class="editMode ? 'pointer-events-auto' : 'pointer-events-none'"
          :style="{
            left: `${centerX}px`,
            top: `${(levelStartY[level] ?? 0) + 12}px`,
            transform: 'translateX(-50%)'
          }"
        >
          <div class="flex items-center gap-2">
            <div
              class="px-4 py-1.5 rounded-full text-xs font-bold text-white shadow-lg"
              :class="levelConfig[level].labelBg"
            >
              {{ levelConfig[level].label }}
            </div>
            <!-- Botón añadir nodo en modo edición -->
            <button
              v-if="editMode"
              @click.stop="emit('add-node', level)"
              class="w-6 h-6 rounded-full flex items-center justify-center transition-all
                     bg-white/20 hover:bg-white/40 text-white border border-white/30
                     hover:scale-110 shadow-lg"
              :title="`Añadir nodo ${levelConfig[level].label}`"
            >
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Nodos -->
        <div
          v-for="node in nodes"
          :key="node.id"
          class="node-card absolute group"
          :class="[
            editMode ? 'cursor-move' : 'cursor-pointer',
            draggingNode === node.id ? 'z-50' : ''
          ]"
          :style="{
            left: `${nodePositions[node.id]?.x ?? 0}px`,
            top: `${nodePositions[node.id]?.y ?? 0}px`,
            width: `${NODE_WIDTH}px`,
            height: `${NODE_HEIGHT}px`,
            transition: draggingNode === node.id ? 'none' : 'all 0.2s ease-out'
          }"
          @mousedown="(e) => handleNodeMouseDown(e, node)"
          @click="handleNodeClick(node)"
        >
          <!-- Card del nodo -->
          <div
            class="h-full px-3 rounded-lg border-2 shadow-md
                   flex items-center gap-2 transition-all duration-200"
            :class="[
              levelConfig[node.level as keyof typeof levelConfig]?.nodeBg ?? 'bg-slate-500',
              levelConfig[node.level as keyof typeof levelConfig]?.borderColor ?? 'border-slate-400',
              node.is_completed ? 'ring-2 ring-white ring-offset-2 ring-offset-slate-900' : '',
              draggingNode === node.id ? 'scale-105 shadow-2xl' : 'hover:scale-105 hover:shadow-xl hover:-translate-y-0.5'
            ]"
          >
            <!-- Título -->
            <span 
              class="flex-1 font-semibold text-sm leading-tight line-clamp-2"
              :class="levelConfig[node.level as keyof typeof levelConfig]?.nodeText ?? 'text-white'"
            >
              {{ node.title }}
            </span>
            
            <!-- Indicador de estado -->
            <div class="flex-shrink-0">
              <div
                v-if="node.is_completed"
                class="w-6 h-6 rounded-full bg-white flex items-center justify-center shadow-md"
              >
                <svg class="w-4 h-4 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <div
                v-else-if="node.content"
                class="w-6 h-6 rounded-full border-2 border-white bg-white/20 flex items-center justify-center"
              >
                <svg class="w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div
                v-else
                class="w-6 h-6 rounded-full border-2 border-white/40 bg-white/10"
              />
            </div>
          </div>
          
          <!-- Tooltip con descripción -->
          <div 
            v-if="node.description"
            class="absolute left-1/2 -translate-x-1/2 bottom-full mb-2 
                   bg-slate-800 text-white text-xs rounded-lg shadow-2xl
                   opacity-0 group-hover:opacity-100 transition-opacity duration-200
                   pointer-events-none z-30 border border-slate-600
                   px-3 py-2 max-w-[220px] text-center leading-relaxed"
          >
            {{ node.description }}
            <div class="absolute left-1/2 -translate-x-1/2 top-full w-0 h-0 
                        border-l-[6px] border-r-[6px] border-t-[6px] 
                        border-transparent border-t-slate-800" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
