<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { BaseButton } from '@/components/common'
</script>

<template>
  <div class="min-h-[calc(100vh-180px)] flex items-center justify-center px-4 relative overflow-hidden">
    <!-- Background decorations -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute -top-40 -right-40 w-96 h-96 bg-primary/5 rounded-full blur-3xl" />
      <div class="absolute -bottom-40 -left-40 w-96 h-96 bg-primary-hover/5 rounded-full blur-3xl" />
    </div>
    
    <div class="text-center relative z-10">
      <div class="relative inline-block mb-8">
        <div class="text-[180px] md:text-[220px] font-black text-transparent bg-clip-text bg-gradient-to-br from-primary via-primary-hover to-primary leading-none select-none">
          404
        </div>
        <div class="absolute inset-0 text-[180px] md:text-[220px] font-black text-primary/10 blur-2xl leading-none select-none">
          404
        </div>
      </div>
      
      <div class="w-20 h-20 bg-gradient-to-br from-primary/20 to-primary-hover/20 rounded-3xl flex items-center justify-center mx-auto mb-6">
        <svg class="w-10 h-10 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      
      <h1 class="text-2xl md:text-3xl font-bold text-text mb-3">Página no encontrada</h1>
      <p class="text-text-secondary mb-8 max-w-md mx-auto leading-relaxed">
        La página que buscas no existe, fue movida o quizás nunca existió. No te preocupes, puedes volver al inicio.
      </p>
      
      <div class="flex flex-col sm:flex-row gap-4 justify-center">
        <RouterLink to="/">
          <BaseButton size="lg" class="group w-full sm:w-auto">
            <svg class="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            Ir al inicio
          </BaseButton>
        </RouterLink>
        <button 
          @click="$router.back()" 
          class="px-6 py-3 text-text-secondary hover:text-text font-medium transition-colors"
        >
          ← Volver atrás
        </button>
      </div>
    </div>
  </div>
</template>
