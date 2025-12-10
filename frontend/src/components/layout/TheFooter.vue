<template>
  <footer class="bg-bg-secondary border-t border-line mt-auto">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="flex flex-col md:flex-row justify-between items-center gap-4">
        <div class="flex items-center gap-2">
          <div class="w-6 h-6 bg-gradient-to-br from-primary to-primary-hover rounded-lg flex items-center justify-center">
            <span class="text-white font-bold text-xs">M</span>
          </div>
          <span class="text-text-secondary text-sm">
            &copy; {{ new Date().getFullYear() }} Merq
          </span>
        </div>
        <p class="text-text-secondary text-xs">
          Plataforma de aprendizaje adaptativo
        </p>
      </div>
    </div>
  </footer>
</template>
