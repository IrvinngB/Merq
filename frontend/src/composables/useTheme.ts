import { ref, watch, onMounted } from 'vue'

type Theme = 'light' | 'dark' | 'system'

const theme = ref<Theme>((localStorage.getItem('theme') as Theme) || 'system')
const isDark = ref(false)

function getSystemTheme(): boolean {
  return window.matchMedia('(prefers-color-scheme: dark)').matches
}

function applyTheme() {
  if (theme.value === 'system') {
    isDark.value = getSystemTheme()
  } else {
    isDark.value = theme.value === 'dark'
  }

  if (isDark.value) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

export function useTheme() {
  onMounted(() => {
    applyTheme()

    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
      if (theme.value === 'system') {
        applyTheme()
      }
    })
  })

  watch(theme, (newTheme) => {
    localStorage.setItem('theme', newTheme)
    applyTheme()
  })

  function setTheme(newTheme: Theme) {
    theme.value = newTheme
  }

  function toggleTheme() {
    if (isDark.value) {
      theme.value = 'light'
    } else {
      theme.value = 'dark'
    }
  }

  return {
    theme,
    isDark,
    setTheme,
    toggleTheme
  }
}
