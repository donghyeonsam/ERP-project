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
</style>
