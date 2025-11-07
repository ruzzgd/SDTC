<template>
  <div class="h-screen flex items-center justify-center flex-col">
    <h1 class="text-4xl font-bold mb-4">404</h1>
    <p class="text-xl">Page Not Found</p>
    <button @click="$router.push('/')" class="mt-4 px-4 py-2 bg-blue-500 text-white rounded">
      Go Home
    </button>
  </div>
</template>
