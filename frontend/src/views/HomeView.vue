<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { BaseButton, BaseCard } from '@/components/common'
</script>

<template>
  <div>
    <!-- Hero Section -->
    <section class="relative overflow-hidden min-h-[90vh] flex items-center">
      <div class="absolute inset-0 bg-gradient-to-br from-bg-secondary via-bg to-primary/5" />
      <div class="absolute top-20 left-10 w-72 h-72 bg-primary/10 rounded-full blur-3xl animate-pulse" />
      <div class="absolute bottom-20 right-10 w-96 h-96 bg-primary-hover/10 rounded-full blur-3xl animate-pulse" style="animation-delay: 1s" />
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-primary/5 rounded-full blur-3xl" />
      
      <div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div class="grid lg:grid-cols-2 gap-12 items-center">
          <div class="text-center lg:text-left">
            <div class="inline-flex items-center gap-2 bg-primary/10 text-primary px-4 py-2 rounded-full text-sm font-medium mb-8 border border-primary/20">
              <span class="relative flex h-2 w-2">
                <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75"></span>
                <span class="relative inline-flex rounded-full h-2 w-2 bg-primary"></span>
              </span>
              Potenciado por Inteligencia Artificial
            </div>
            
            <h1 class="text-4xl md:text-5xl lg:text-6xl font-bold text-text mb-6 leading-tight">
              Transforma cualquier contenido en
              <span class="text-transparent bg-clip-text bg-gradient-to-r from-primary to-primary-hover"> roadmaps interactivos</span>
            </h1>
            <p class="text-lg md:text-xl text-text-secondary mb-10 leading-relaxed max-w-xl mx-auto lg:mx-0">
              Sube un PDF o pega texto y nuestra IA generará un roadmap visual con nodos conectados, organizado por niveles de dificultad.
            </p>
            <div class="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
              <RouterLink to="/auth/register">
                <BaseButton size="lg" class="w-full sm:w-auto group">
                  <span>Comenzar gratis</span>
                  <svg class="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </BaseButton>
              </RouterLink>
              <RouterLink to="/auth/login">
                <BaseButton size="lg" variant="secondary" class="w-full sm:w-auto">
                  Ya tengo cuenta
                </BaseButton>
              </RouterLink>
            </div>
            
            <div class="mt-12 flex items-center gap-8 justify-center lg:justify-start">
              <div class="text-center">
                <p class="text-2xl font-bold text-text">100%</p>
                <p class="text-sm text-text-secondary">Gratis</p>
              </div>
              <div class="w-px h-10 bg-line" />
              <div class="text-center">
                <p class="text-2xl font-bold text-text">IA</p>
                <p class="text-sm text-text-secondary">Adaptativa</p>
              </div>
              <div class="w-px h-10 bg-line" />
              <div class="text-center">
                <p class="text-2xl font-bold text-text">24/7</p>
                <p class="text-sm text-text-secondary">Disponible</p>
              </div>
            </div>
          </div>
          
          <!-- Hero Visual -->
          <div class="hidden lg:block relative">
            <div class="relative">
              <div class="absolute -inset-4 bg-gradient-to-r from-primary/20 to-primary-hover/20 rounded-3xl blur-2xl" />
              <div class="relative bg-card border border-line rounded-2xl p-6 shadow-2xl">
                <div class="flex items-center gap-3 mb-4 pb-4 border-b border-line">
                  <div class="flex gap-1.5">
                    <div class="w-3 h-3 rounded-full bg-danger/60" />
                    <div class="w-3 h-3 rounded-full bg-warning/60" />
                    <div class="w-3 h-3 rounded-full bg-success/60" />
                  </div>
                  <span class="text-sm text-text-secondary">Roadmap: Machine Learning</span>
                </div>
                
                <div class="space-y-3">
                  <div class="flex items-center gap-3 p-3 bg-success/10 rounded-xl border border-success/30">
                    <div class="w-10 h-10 bg-success/20 rounded-lg flex items-center justify-center">
                      <span class="text-success text-xs font-bold">P</span>
                    </div>
                    <div class="flex-1">
                      <p class="text-sm font-medium text-text">¿Qué es ML?</p>
                      <p class="text-xs text-success">Principiante</p>
                    </div>
                    <svg class="w-5 h-5 text-success" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                    </svg>
                  </div>
                  
                  <div class="flex items-center gap-3 p-3 bg-primary/10 rounded-xl border border-primary/30">
                    <div class="w-10 h-10 bg-primary/20 rounded-lg flex items-center justify-center">
                      <span class="text-primary text-xs font-bold">I</span>
                    </div>
                    <div class="flex-1">
                      <p class="text-sm font-medium text-text">Regresión lineal</p>
                      <p class="text-xs text-primary">Intermedio</p>
                    </div>
                    <span class="text-xs text-primary font-medium bg-primary/10 px-2 py-0.5 rounded">En progreso</span>
                  </div>
                  
                  <div class="flex items-center gap-3 p-3 bg-bg-secondary rounded-xl opacity-60">
                    <div class="w-10 h-10 bg-warning/20 rounded-lg flex items-center justify-center">
                      <span class="text-warning text-xs font-bold">A</span>
                    </div>
                    <div class="flex-1">
                      <p class="text-sm font-medium text-text-secondary">Redes neuronales</p>
                      <p class="text-xs text-text-secondary">Avanzado</p>
                    </div>
                    <svg class="w-5 h-5 text-text-secondary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                  </div>
                </div>
                
                <div class="mt-4 pt-4 border-t border-line flex items-center justify-between">
                  <div class="flex items-center gap-2">
                    <div class="w-8 h-8 bg-gradient-to-br from-primary to-primary-hover rounded-full flex items-center justify-center">
                      <span class="text-white text-xs font-bold">JD</span>
                    </div>
                    <span class="text-sm text-text-secondary">Juan D.</span>
                  </div>
                  <span class="text-xs text-success font-medium bg-success/10 px-2 py-1 rounded-full">+15% esta semana</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- How it works -->
    <section class="py-24 bg-bg-secondary">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="text-center mb-16">
          <span class="text-primary font-medium text-sm uppercase tracking-wider">Proceso simple</span>
          <h2 class="text-3xl md:text-4xl font-bold text-text mt-3 mb-4">
            ¿Cómo funciona?
          </h2>
          <p class="text-text-secondary text-lg max-w-2xl mx-auto">
            En 3 simples pasos, convierte cualquier documento en un roadmap visual e interactivo
          </p>
        </div>

        <div class="grid md:grid-cols-3 gap-8 relative">
          <div class="hidden md:block absolute top-24 left-1/4 right-1/4 h-0.5 bg-gradient-to-r from-primary/50 via-primary-hover/50 to-success/50" />
          
          <div class="relative">
            <div class="bg-card border border-line rounded-2xl p-8 text-center shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-2 group">
              <div class="w-16 h-16 bg-gradient-to-br from-primary to-primary/70 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg shadow-primary/25 group-hover:scale-110 transition-transform">
                <svg class="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
              <span class="inline-block text-xs font-bold text-primary bg-primary/10 px-3 py-1 rounded-full mb-4">PASO 1</span>
              <h3 class="text-xl font-semibold text-text mb-3">Sube un PDF o texto</h3>
              <p class="text-text-secondary leading-relaxed">
                Carga cualquier documento PDF o pega texto directamente sobre el tema que quieras aprender.
              </p>
            </div>
          </div>

          <div class="relative">
            <div class="bg-card border border-line rounded-2xl p-8 text-center shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-2 group">
              <div class="w-16 h-16 bg-gradient-to-br from-primary-hover to-primary-hover/70 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg shadow-primary-hover/25 group-hover:scale-110 transition-transform">
                <svg class="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <span class="inline-block text-xs font-bold text-primary-hover bg-primary-hover/10 px-3 py-1 rounded-full mb-4">PASO 2</span>
              <h3 class="text-xl font-semibold text-text mb-3">La IA genera el roadmap</h3>
              <p class="text-text-secondary leading-relaxed">
                Nuestra IA analiza el contenido y crea un grafo visual con nodos conectados por niveles.
              </p>
            </div>
          </div>

          <div class="relative">
            <div class="bg-card border border-line rounded-2xl p-8 text-center shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-2 group">
              <div class="w-16 h-16 bg-gradient-to-br from-success to-success/70 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg shadow-success/25 group-hover:scale-110 transition-transform">
                <svg class="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                </svg>
              </div>
              <span class="inline-block text-xs font-bold text-success bg-success/10 px-3 py-1 rounded-full mb-4">PASO 3</span>
              <h3 class="text-xl font-semibold text-text mb-3">Explora y aprende</h3>
              <p class="text-text-secondary leading-relaxed">
                Navega por el grafo interactivo y genera contenido detallado bajo demanda para cada nodo.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features -->
    <section class="py-24 bg-bg">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid lg:grid-cols-2 gap-16 items-center">
          <div>
            <span class="text-primary font-medium text-sm uppercase tracking-wider">Características</span>
            <h2 class="text-3xl md:text-4xl font-bold text-text mt-3 mb-6">
              Roadmaps inteligentes para cualquier tema
            </h2>
            <p class="text-text-secondary text-lg mb-10">
              Merq usa IA local (Ollama) para transformar cualquier contenido en grafos de aprendizaje interactivos.
            </p>
            
            <div class="space-y-6">
              <div class="flex gap-4">
                <div class="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center flex-shrink-0">
                  <svg class="w-6 h-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <div>
                  <h3 class="font-semibold text-text mb-1">Grafo interactivo</h3>
                  <p class="text-text-secondary text-sm">Visualiza tu roadmap con nodos conectados, zoom y navegación intuitiva.</p>
                </div>
              </div>
              
              <div class="flex gap-4">
                <div class="w-12 h-12 bg-primary-hover/10 rounded-xl flex items-center justify-center flex-shrink-0">
                  <svg class="w-6 h-6 text-primary-hover" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <div>
                  <h3 class="font-semibold text-text mb-1">Tres niveles de dificultad</h3>
                  <p class="text-text-secondary text-sm">Principiante, Intermedio y Avanzado con prerequisitos claros.</p>
                </div>
              </div>
              
              <div class="flex gap-4">
                <div class="w-12 h-12 bg-success/10 rounded-xl flex items-center justify-center flex-shrink-0">
                  <svg class="w-6 h-6 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
                  </svg>
                </div>
                <div>
                  <h3 class="font-semibold text-text mb-1">Contenido bajo demanda</h3>
                  <p class="text-text-secondary text-sm">Haz click en cualquier nodo para generar contenido detallado con Markdown.</p>
                </div>
              </div>
              
              <div class="flex gap-4">
                <div class="w-12 h-12 bg-warning/10 rounded-xl flex items-center justify-center flex-shrink-0">
                  <svg class="w-6 h-6 text-warning" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
                  </svg>
                </div>
                <div>
                  <h3 class="font-semibold text-text mb-1">IA 100% local</h3>
                  <p class="text-text-secondary text-sm">Usa Ollama con Gemma 2, sin APIs externas ni costos adicionales.</p>
                </div>
              </div>
            </div>
          </div>
          
          <div class="relative">
            <div class="absolute -inset-4 bg-gradient-to-r from-primary/10 to-success/10 rounded-3xl blur-2xl" />
            <div class="relative grid grid-cols-2 gap-4">
              <BaseCard class="p-5">
                <div class="text-3xl font-bold text-primary mb-1">3</div>
                <p class="text-sm text-text-secondary">Niveles por roadmap</p>
              </BaseCard>
              <BaseCard class="p-5">
                <div class="text-3xl font-bold text-success mb-1">~2min</div>
                <p class="text-sm text-text-secondary">Tiempo de generación</p>
              </BaseCard>
              <BaseCard class="p-5">
                <div class="text-3xl font-bold text-primary-hover mb-1">∞</div>
                <p class="text-sm text-text-secondary">Roadmaps ilimitados</p>
              </BaseCard>
              <BaseCard class="p-5">
                <div class="text-3xl font-bold text-warning mb-1">Local</div>
                <p class="text-sm text-text-secondary">IA privada</p>
              </BaseCard>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="py-24 bg-gradient-to-br from-primary to-primary-hover relative overflow-hidden">
      <div class="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4xIj48cGF0aCBkPSJNMzYgMzRjMC0yLjIxLTEuNzktNC00LTRzLTQgMS43OS00IDQgMS43OSA0IDQgNCA0LTEuNzkgNC00eiIvPjwvZz48L2c+PC9zdmc+')] opacity-30" />
      <div class="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 class="text-3xl md:text-4xl font-bold text-white mb-6">
          ¿Listo para crear tu primer roadmap?
        </h2>
        <p class="text-white/80 text-lg mb-10 max-w-2xl mx-auto">
          Transforma cualquier documento en un grafo de aprendizaje interactivo en minutos.
        </p>
        <RouterLink to="/auth/register">
          <button class="bg-white text-primary hover:bg-white/90 px-8 py-4 rounded-xl text-lg font-semibold transition-all shadow-xl hover:shadow-2xl hover:-translate-y-1">
            Crear cuenta gratis
          </button>
        </RouterLink>
        <p class="text-white/60 text-sm mt-6">Sin tarjeta de crédito • IA 100% local</p>
      </div>
    </section>
  </div>
</template>
