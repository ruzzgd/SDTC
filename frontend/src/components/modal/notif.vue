<template>
  <transition name="fade">
    <div
      v-if="notif.isNotif"
      :class="[
        'fixed top-5 right-5 z-50 px-5 py-3 rounded-lg shadow-lg flex items-center gap-3 text-white',
        typeClass
      ]"
    >
      <i :class="iconClass" class="text-xl"></i>
      <p class="font-medium">{{ notif.message }}</p>
      <button @click="notif.hide" class="ml-3 text-white/80 hover:text-white">
        <i class="fa-solid fa-xmark"></i>
      </button>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useNotifStore } from "@/stores/notif";

const notif = useNotifStore()

const typeClass = computed(() => {
  switch (notif.type) {
    case 'success':
      return 'bg-green-600'
    case 'error':
      return 'bg-red-600'
    case 'warning':
      return 'bg-yellow-500 text-black'
    default:
      return 'bg-blue-600'
  }
})

const iconClass = computed(() => {
  switch (notif.type) {
    case 'success':
      return 'fa-solid fa-circle-check'
    case 'error':
      return 'fa-solid fa-circle-xmark'
    case 'warning':
      return 'fa-solid fa-triangle-exclamation'
    default:
      return 'fa-solid fa-circle-info'
  }
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
