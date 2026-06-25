<template>
  <template v-if="isPublicRoute">
    <RouterView />
  </template>
  <template v-else>
    <NavBar />
    <SideBar />
    <main class="main-content">
      <RouterView />
    </main>
    <Message />
  </template>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, RouterView } from 'vue-router'
import NavBar from '@/components/NavBar.vue'
import SideBar from '@/components/SideBar.vue'
import Message from '@/components/Message.vue'

const route = useRoute()
const isPublicRoute = computed(() => route.meta.public === true)
</script>

<style>
:root {
  --navbar-height: 56px;
  --sidebar-width: 220px;
  --sidebar-bg: #1a2236;
  --sidebar-active: #2563eb;
  --navbar-bg: #ffffff;
}

body {
  margin: 0;
  background: #f0f2f5;
}

.main-content {
  margin-left: var(--sidebar-width);
  margin-top: var(--navbar-height);
  min-height: calc(100vh - var(--navbar-height));
  padding: 24px;
}

/* 보고서 출력(window.print) 시 네비게이션/사이드바/플로팅 버튼을 숨기고 본문만 인쇄 */
@media print {
  .erp-navbar, .erp-sidebar, .messenger-fab, .messenger-window, .no-print {
    display: none !important;
  }
  .main-content {
    margin: 0 !important;
    padding: 0 !important;
  }
}
</style>
