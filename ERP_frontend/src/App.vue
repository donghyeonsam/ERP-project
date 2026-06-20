<template>
  
  <div>
    <NavBar />
    <SideBar />
    <Message />
  </div>
  
  <RouterView />

</template>

<script setup>
  
  import { RouterView } from 'vue-router'
  import NavBar from '@/components/NavBar.vue'
  import SideBar from '@/components/SideBar.vue'
  import Message from '@/components/Message.vue'

</script>

<style scoped>

</style>