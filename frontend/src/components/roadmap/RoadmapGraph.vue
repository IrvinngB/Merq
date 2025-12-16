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

// Constantes de diseño - Nodos estilo grafo
const NODE_WIDTH = 160
const NODE_HEIGHT = 56
const NODE_GAP_X = 50
const NODE_GAP_Y = 100
const PADDING = 80
const MAX_NODES_PER_ROW = 6

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
const hoveredNode = ref<number | null>(null)

// Configuración de niveles con colores vibrantes y efectos glow
const levelConfig = {
  beginner: { 
    label: 'Principiante',
    color: '#10b981',
    colorRgb: '16, 185, 129',
    gradient: 'from-emerald-500 to-emerald-600',
    glow: 'shadow-emerald-500/50',
    border: 'border-emerald-400/60'
  },
  intermediate: { 
    label: 'Intermedio',
    color: '#f59e0b',
    colorRgb: '245, 158, 11',
    gradient: 'from-amber-500 to-orange-500',
    glow: 'shadow-amber-500/50',
    border: 'border-amber-400/60'
  },
  advanced: { 
    label: 'Avanzado',
    color: '#f43f5e',
    colorRgb: '244, 63, 94',
    gradient: 'from-rose-500 to-pink-600',
    glow: 'shadow-rose-500/50',
    border: 'border-rose-400/60'
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

// Calcular filas por nivel
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
    heights[level] = rows * (NODE_HEIGHT + NODE_GAP_Y) + 60
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
    const baseY = (levelStartY.value[level] ?? 0) + 50
    
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
        y: baseY + row * (NODE_HEIGHT + NODE_GAP_Y),
        row
      }
    })
  })
  
  return positions
})

// Generar paths SVG para conexiones con curvas bezier mejoradas
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
    
    // Calcular curva bezier suave
    const verticalDist = toY - fromY
    const horizontalDist = Math.abs(fromX - toX)
    
    let path: string
    let controlOffset = Math.min(verticalDist * 0.5, 60)
    
    if (horizontalDist < 15) {
      // Conexión casi vertical - curva suave
      path = `M ${fromX} ${fromY} 
              C ${fromX} ${fromY + controlOffset}, 
                ${toX} ${toY - controlOffset}, 
                ${toX} ${toY}`
    } else {
      // Conexión diagonal - curva S elegante
      const cp1Y = fromY + controlOffset
      const cp2Y = toY - controlOffset
      path = `M ${fromX} ${fromY} 
              C ${fromX} ${cp1Y}, 
                ${toX} ${cp2Y}, 
                ${toX} ${toY}`
    }
    
    // Obtener color del nodo origen para el gradiente
    const fromNode = props.nodes.find(n => n.id === conn.from_node_id)
    const toNode = props.nodes.find(n => n.id === conn.to_node_id)
    const fromLevel = fromNode?.level || 'beginner'
    const toLevel = toNode?.level || 'beginner'
    
    return {
      connection: conn,
      path,
      midX,
      midY,
      fromColor: levelConfig[fromLevel as keyof typeof levelConfig]?.color || '#6366f1',
      toColor: levelConfig[toLevel as keyof typeof levelConfig]?.color || '#8b5cf6',
      gradientId: `gradient-${conn.id}`
    }
  }).filter(Boolean) as { 
    connection: NodeConnection
    path: string
    midX: number
    midY: number
    fromColor: string
    toColor: string
    gradientId: string
  }[]
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
    class="relative w-full h-full bg-slate-950 rounded-2xl overflow-hidden select-none"
  >
    <!-- Animated Background Pattern -->
    <div class="absolute inset-0">
      <!-- Grid pattern - Increased opacity -->
      <div 
        class="absolute inset-0 opacity-10" 
        style="background-image: radial-gradient(circle, #fff 1.5px, transparent 1.5px); background-size: 24px 24px;" 
      />
      <!-- Gradient overlay - More vibrant -->
      <div class="absolute inset-0 bg-gradient-to-br from-indigo-950/40 via-slate-900/50 to-purple-950/40" />
      
      <!-- Animated glow orbs - Increased visibility -->
      <div class="absolute top-1/4 left-1/4 w-96 h-96 bg-emerald-500/10 rounded-full blur-[100px] animate-pulse" />
      <div class="absolute bottom-1/3 right-1/4 w-80 h-80 bg-rose-500/10 rounded-full blur-[100px] animate-pulse" style="animation-delay: 1s" />
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-slate-800/10 rounded-full blur-[120px]" />
    </div>

    <!-- ... (controls omitted) ... -->

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
          transition: isDragging ? 'none' : 'transform 0.15s ease-out'
        }"
      >
        <!-- SVG para conexiones -->
        <svg 
          class="absolute inset-0"
          :class="editMode ? 'pointer-events-auto' : 'pointer-events-none'"
          :width="canvasWidth"
          :height="canvasHeight"
        >
          <!-- Definiciones de gradientes y markers -->
          <defs>
            <!-- Gradientes dinámicos para cada conexión -->
            <linearGradient
              v-for="conn in connectionPaths"
              :key="`grad-${conn.gradientId}`"
              :id="conn.gradientId"
              gradientUnits="userSpaceOnUse"
              :x1="(nodePositions[conn.connection.from_node_id]?.x ?? 0) + 80"
              :y1="(nodePositions[conn.connection.from_node_id]?.y ?? 0) + 56"
              :x2="(nodePositions[conn.connection.to_node_id]?.x ?? 0) + 80"
              :y2="(nodePositions[conn.connection.to_node_id]?.y ?? 0)"
            >
              <stop offset="0%" :stop-color="conn.fromColor" stop-opacity="1" />
              <stop offset="100%" :stop-color="conn.toColor" stop-opacity="1" />
            </linearGradient>
            
            <!-- Arrow marker -->
            <marker
              id="arrow"
              viewBox="0 0 10 10"
              refX="8"
              refY="5"
              markerWidth="5"
              markerHeight="5"
              orient="auto"
            >
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#94a3b8" />
            </marker>
            
            <marker
              id="arrow-active"
              viewBox="0 0 10 10"
              refX="8"
              refY="5"
              markerWidth="6"
              markerHeight="6"
              orient="auto"
            >
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#38bdf8" />
            </marker>
            
            <!-- Glow filter -->
            <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
              <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>
          
          <!-- Línea central vertical decorativa -->
          <line
            :x1="centerX"
            :y1="PADDING"
            :x2="centerX"
            :y2="canvasHeight - PADDING"
            stroke="#334155"
            stroke-width="1"
            stroke-dasharray="6 6"
            stroke-linecap="round"
            opacity="0.2"
          />
          
          <!-- Conexiones entre nodos -->
          <g v-for="(conn, index) in connectionPaths" :key="`conn-${index}`">
            <!-- Back line (shadow/glow) -->
             <path
              :d="conn.path"
              fill="none"
              :stroke="conn.fromColor"
              stroke-width="4"
              opacity="0.1"
              stroke-linecap="round"
            />

            <!-- Main line -->
            <path
              :d="conn.path"
              fill="none"
              :stroke="`url(#${conn.gradientId})`"
              stroke-width="2.5"
              stroke-linecap="round"
              class="transition-all duration-300 pointer-events-none"
              :marker-end="hoveredConnection?.connection.id === conn.connection.id ? 'url(#arrow-active)' : 'url(#arrow)'"
            />
            
            <!-- Hit area (invisible, thicker) -->
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
            
            <!-- Active state highlight -->
             <path
              v-if="hoveredConnection?.connection.id === conn.connection.id"
              :d="conn.path"
              fill="none"
              stroke="#38bdf8"
              stroke-width="3"
              stroke-linecap="round"
              filter="url(#glow)"
              class="pointer-events-none"
            />
            
            <!-- Moving dot (Always visible but subtle, brighter when hovered) -->
            <circle
              r="3"
              fill="white"
              :filter="hoveredConnection?.connection.id === conn.connection.id ? 'url(#glow)' : ''"
              opacity="0.8"
            >
              <animateMotion
                :path="conn.path"
                :dur="hoveredConnection?.connection.id === conn.connection.id ? '1.5s' : '4s'"
                repeatCount="indefinite"
              />
            </circle>
          </g>
        </svg>
        
        <!-- Tooltip de conexión -->
        <Transition
          enter-active-class="transition-all duration-200 ease-out"
          enter-from-class="opacity-0 scale-95"
          enter-to-class="opacity-100 scale-100"
          leave-active-class="transition-all duration-150 ease-in"
          leave-from-class="opacity-100 scale-100"
          leave-to-class="opacity-0 scale-95"
        >
          <div
            v-if="hoveredConnection"
            class="absolute z-50 bg-slate-800/95 backdrop-blur-xl border border-slate-600/50 rounded-xl shadow-2xl px-4 py-3 pointer-events-none"
            :style="{
              left: `${hoveredConnection.x}px`,
              top: `${hoveredConnection.y - 50}px`,
              transform: 'translateX(-50%)'
            }"
          >
            <div class="text-xs text-slate-300 whitespace-nowrap flex items-center gap-3">
              <span class="font-semibold text-white">{{ getNodeById(hoveredConnection.connection.from_node_id)?.title }}</span>
              <div class="flex items-center">
                <div class="w-6 h-0.5 bg-gradient-to-r from-sky-400 to-indigo-400 rounded-full" />
                <svg class="w-4 h-4 text-sky-400 -ml-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </div>
              <span class="font-semibold text-white">{{ getNodeById(hoveredConnection.connection.to_node_id)?.title }}</span>
            </div>
          </div>
        </Transition>

        <!-- Labels de nivel con diseño mejorado -->
        <div
          v-for="level in levelOrder"
          :key="`label-${level}`"
          class="absolute z-10"
          :class="editMode ? 'pointer-events-auto' : 'pointer-events-none'"
          :style="{
            left: `${centerX}px`,
            top: `${(levelStartY[level] ?? 0) + 8}px`,
            transform: 'translateX(-50%)'
          }"
        >
          <div class="flex items-center gap-3">
            <div
              class="px-5 py-2 rounded-full text-xs font-bold text-white shadow-xl border border-white/10 backdrop-blur-sm"
              :class="`bg-gradient-to-r ${levelConfig[level].gradient} ${levelConfig[level].glow}`"
              :style="`box-shadow: 0 0 20px rgba(${levelConfig[level].colorRgb}, 0.3)`"
            >
              {{ levelConfig[level].label }}
            </div>
            <!-- Botón añadir nodo en modo edición -->
            <button
              v-if="editMode"
              @click.stop="emit('add-node', level)"
              class="w-7 h-7 rounded-full flex items-center justify-center transition-all duration-200
                     bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-white 
                     border border-slate-600/50 hover:border-slate-500
                     hover:scale-110 shadow-lg backdrop-blur-sm"
              :title="`Añadir nodo ${levelConfig[level].label}`"
            >
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Nodos con diseño de grafo -->
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
            transition: draggingNode === node.id ? 'none' : 'all 0.25s cubic-bezier(0.4, 0, 0.2, 1)'
          }"
          @mousedown="(e) => handleNodeMouseDown(e, node)"
          @click="handleNodeClick(node)"
          @mouseenter="hoveredNode = node.id"
          @mouseleave="hoveredNode = null"
        >
          <!-- Card del nodo con efecto glassmorphism -->
          <div
            class="h-full px-4 rounded-2xl border-2 backdrop-blur-sm
                   flex items-center gap-3 transition-all duration-300 relative overflow-hidden"
            :class="[
              node.is_completed 
                ? 'bg-slate-800/90 border-emerald-400/50' 
                : 'bg-slate-800/80 border-opacity-60',
              levelConfig[node.level as keyof typeof levelConfig]?.border ?? 'border-slate-500',
              draggingNode === node.id 
                ? 'scale-105 shadow-2xl' 
                : 'hover:scale-105 hover:-translate-y-1',
              hoveredNode === node.id ? 'shadow-xl' : 'shadow-lg'
            ]"
            :style="{
              boxShadow: hoveredNode === node.id || draggingNode === node.id
                ? `0 0 30px rgba(${levelConfig[node.level as keyof typeof levelConfig]?.colorRgb || '99, 102, 241'}, 0.3), 0 8px 32px rgba(0,0,0,0.4)`
                : `0 0 15px rgba(${levelConfig[node.level as keyof typeof levelConfig]?.colorRgb || '99, 102, 241'}, 0.15), 0 4px 16px rgba(0,0,0,0.3)`
            }"
          >
            <!-- Gradient accent line at top -->
            <div
              class="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r"
              :class="levelConfig[node.level as keyof typeof levelConfig]?.gradient || 'from-indigo-500 to-purple-500'"
            />
            
            <!-- Título -->
            <span 
              class="flex-1 font-semibold text-sm leading-tight line-clamp-2 text-white"
            >
              {{ node.title }}
            </span>
            
            <!-- Indicador de estado con diseño mejorado -->
            <div class="flex-shrink-0">
              <!-- Completado -->
              <div
                v-if="node.is_completed"
                class="w-7 h-7 rounded-full bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center shadow-lg ring-2 ring-emerald-400/30 ring-offset-2 ring-offset-slate-800"
              >
                <svg class="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <!-- Con contenido pero no completado -->
              <div
                v-else-if="node.content"
                class="w-7 h-7 rounded-full border-2 border-dashed flex items-center justify-center"
                :class="`${levelConfig[node.level as keyof typeof levelConfig]?.border || 'border-slate-500'} bg-slate-700/50`"
              >
                <svg class="w-3.5 h-3.5 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <!-- Pendiente - con animación de pulso -->
              <div
                v-else
                class="w-7 h-7 rounded-full border-2 border-slate-600 bg-slate-700/30 relative"
              >
                <div 
                  class="absolute inset-0 rounded-full animate-ping opacity-20"
                  :class="`bg-${node.level === 'beginner' ? 'emerald' : node.level === 'intermediate' ? 'amber' : 'rose'}-500`"
                  style="animation-duration: 2s"
                />
              </div>
            </div>
          </div>
          
          <!-- Tooltip con descripción -->
          <Transition
            enter-active-class="transition-all duration-200 ease-out"
            enter-from-class="opacity-0 translate-y-1"
            enter-to-class="opacity-100 translate-y-0"
            leave-active-class="transition-all duration-150 ease-in"
            leave-from-class="opacity-100 translate-y-0"
            leave-to-class="opacity-0 translate-y-1"
          >
            <div 
              v-if="node.description && hoveredNode === node.id"
              class="absolute left-1/2 -translate-x-1/2 bottom-full mb-3 
                     bg-slate-800/95 backdrop-blur-xl text-white text-xs rounded-xl shadow-2xl
                     pointer-events-none z-30 border border-slate-600/50
                     px-4 py-3 max-w-[240px] text-center leading-relaxed"
            >
              {{ node.description }}
              <div class="absolute left-1/2 -translate-x-1/2 top-full w-0 h-0 
                          border-l-[8px] border-r-[8px] border-t-[8px] 
                          border-transparent border-t-slate-800/95" />
            </div>
          </Transition>
          
          <!-- Connection points (visible in edit mode) -->
          <template v-if="editMode">
            <!-- Output point (bottom) -->
            <div 
              class="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-1/2 
                     w-3 h-3 rounded-full bg-slate-600 border-2 border-slate-400
                     opacity-0 group-hover:opacity-100 transition-opacity duration-200
                     hover:bg-sky-500 hover:border-sky-300 hover:scale-125"
            />
            <!-- Input point (top) -->
            <div 
              class="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 
                     w-3 h-3 rounded-full bg-slate-600 border-2 border-slate-400
                     opacity-0 group-hover:opacity-100 transition-opacity duration-200
                     hover:bg-sky-500 hover:border-sky-300 hover:scale-125"
            />
          </template>
        </div>
      </div>
    </div>
  </div>
</template>
