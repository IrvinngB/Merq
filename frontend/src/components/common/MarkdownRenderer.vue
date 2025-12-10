<script setup lang="ts">
import { computed } from 'vue'
import { marked, type MarkedOptions } from 'marked'
import hljs from 'highlight.js'

const props = defineProps<{
  content: string
}>()

const renderer = new marked.Renderer()

renderer.code = function(code: string, language: string | undefined) {
  const lang = language || ''
  if (lang && hljs.getLanguage(lang)) {
    const highlighted = hljs.highlight(code, { language: lang }).value
    return `<pre><code class="hljs language-${lang}">${highlighted}</code></pre>`
  }
  const highlighted = hljs.highlightAuto(code).value
  return `<pre><code class="hljs">${highlighted}</code></pre>`
}

const markedOptions: MarkedOptions = {
  renderer,
  breaks: true,
  gfm: true
}

const renderedContent = computed(() => {
  if (!props.content) return ''
  return marked(props.content, markedOptions) as string
})
</script>

<template>
  <div class="markdown-content" v-html="renderedContent" />
</template>

<style scoped>
.markdown-content {
  color: var(--color-text);
  line-height: 1.7;
}

.markdown-content :deep(h1) {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text);
  margin-top: 1.5rem;
  margin-bottom: 1rem;
}

.markdown-content :deep(h2) {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-text);
  margin-top: 1.25rem;
  margin-bottom: 0.75rem;
}

.markdown-content :deep(h3) {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text);
  margin-top: 1rem;
  margin-bottom: 0.5rem;
}

.markdown-content :deep(p) {
  margin-bottom: 1rem;
  color: var(--color-text-secondary);
}

.markdown-content :deep(strong) {
  color: var(--color-text);
  font-weight: 600;
}

.markdown-content :deep(em) {
  font-style: italic;
  color: var(--color-text-secondary);
}

.markdown-content :deep(ul) {
  list-style-type: disc;
  list-style-position: inside;
  margin-bottom: 1rem;
  color: var(--color-text-secondary);
}

.markdown-content :deep(ol) {
  list-style-type: decimal;
  list-style-position: inside;
  margin-bottom: 1rem;
  color: var(--color-text-secondary);
}

.markdown-content :deep(li) {
  color: var(--color-text-secondary);
  margin-bottom: 0.25rem;
}

.markdown-content :deep(code:not(pre code)) {
  background: rgba(99, 102, 241, 0.1);
  color: var(--color-primary);
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  font-size: 0.875rem;
  font-family: monospace;
}

.markdown-content :deep(pre) {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-line);
  border-radius: 0.75rem;
  padding: 1rem;
  margin-bottom: 1rem;
  overflow-x: auto;
}

.markdown-content :deep(pre code) {
  font-size: 0.875rem;
  font-family: monospace;
  color: var(--color-text-secondary);
  background: transparent;
  padding: 0;
}

.markdown-content :deep(blockquote) {
  border-left: 4px solid var(--color-primary);
  padding-left: 1rem;
  font-style: italic;
  color: var(--color-text-secondary);
  margin: 1rem 0;
}

.markdown-content :deep(a) {
  color: var(--color-primary);
}

.markdown-content :deep(a:hover) {
  text-decoration: underline;
}

.markdown-content :deep(hr) {
  border-color: var(--color-line);
  margin: 1.5rem 0;
}

.markdown-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1rem;
}

.markdown-content :deep(th) {
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-line);
  padding: 0.5rem 1rem;
  text-align: left;
  font-weight: 600;
  color: var(--color-text);
}

.markdown-content :deep(td) {
  border: 1px solid var(--color-line);
  padding: 0.5rem 1rem;
  color: var(--color-text-secondary);
}

/* Highlight.js */
.markdown-content :deep(.hljs-keyword) { color: #a78bfa; }
.markdown-content :deep(.hljs-string) { color: #4ade80; }
.markdown-content :deep(.hljs-number) { color: #fb923c; }
.markdown-content :deep(.hljs-function) { color: #60a5fa; }
.markdown-content :deep(.hljs-comment) { color: #6b7280; font-style: italic; }
.markdown-content :deep(.hljs-variable) { color: #f87171; }
.markdown-content :deep(.hljs-built_in) { color: #22d3ee; }
</style>
