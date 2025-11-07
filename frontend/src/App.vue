<script setup lang="ts">
import { useLoadingStore } from '@/stores/loading';
import Notif from '@/components/modal/notif.vue';
const loading = useLoadingStore()
</script>

<template>
  <!-- Loading overlay -->
  <div
    v-if="loading.isLoading"
    class="absolute z-100 inset-0 flex items-center justify-center bg-black/50 text-white"
  >
    <i class="fa-solid fa-spinner fa-spin-pulse text-4xl"></i>
  </div>

  <!-- Main app content -->
  <div class="h-full w-full relative custom-scrollbar">
    <router-view />
    <!-- ✅ Add notification component here -->
    <Notif />
  </div>
</template>
