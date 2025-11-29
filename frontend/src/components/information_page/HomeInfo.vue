<template>
  <div
    class="w-full flex flex-col items-center justify-center px-6 py-16 md:py-24 bg-gradient-to-b from-gray-100 via-gray-200 to-gray-300 text-white">
    <!-- Hero Section -->
    <section class="text-center max-w-3xl animate-fade-in">
      <h1
        class="text-4xl md:text-6xl font-extrabold mb-4 bg-gradient-to-r from-sky-400 to-blue-600 bg-clip-text text-transparent drop-shadow-lg">
        Welcome to SDTC
      </h1>
      <p class="text-base sm:text-lg md:text-xl text-gray-900 mb-8 leading-relaxed">
        Your web-based solution for ordering and managing inventory efficiently at
        <span class="text-sky-600 font-semibold">Sorsogon Depot and Tile Center</span>.
      </p>

      <div class="flex flex-wrap justify-center gap-4">
        <button @click="$router.push('/login')"
          class="px-6 py-3 bg-sky-600 hover:bg-sky-700 rounded-xl font-semibold text-white transition-all duration-300 transform hover:scale-105 active:scale-95 shadow-md hover:shadow-sky-600/40">
          Start Ordering
        </button>
        <button @click="$router.push('/login')"
          class="px-6 py-3 bg-emerald-600 hover:bg-emerald-700 rounded-xl font-semibold text-gray-900 transition-all duration-300 transform hover:scale-105 active:scale-95 shadow-md hover:shadow-emerald-600/40">
          View Products
        </button>
      </div>
    </section>

    <!-- Feature Cards -->
    <section class="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl text-center px-4">
      <div v-for="(card, i) in cards" :key="i" class="relative bg-gray-400/70 backdrop-blur-lg p-8 rounded-2xl shadow-lg border border-gray-100/60
           transition-all duration-700 hover:shadow-[0_0_40px_rgba(255,255,255,0.35)] hover:scale-105 group
           animate-slide-up" :style="{ animationDelay: `${i * 0.2}s` }">
        <!-- ✨ MORE VISIBLE SHINE EFFECT -->
        <div
          class="absolute inset-0 bg-gradient-to-r from-transparent via-white/60 to-transparent
             opacity-0 group-hover:opacity-100
             -translate-x-full group-hover:translate-x-full transition-all duration-[1200ms] ease-in-out pointer-events-none">
        </div>

        <div class="flex flex-col items-center relative z-10">
          <div class="w-12 h-12 mb-4 flex items-center justify-center bg-sky-600/20 rounded-full">
            <i :class="`fa-solid ${card.icon} text-sky-400 text-2xl`"></i>
          </div>
          <h2 class="text-2xl font-semibold mb-2 text-gray-900">{{ card.title }}</h2>
          <p class="text-gray-700 leading-relaxed">{{ card.text }}</p>
        </div>
      </div>
    </section>

  </div>
</template>

<script setup>
const cards = [
  {
    title: "Easy Ordering",
    text: "Place orders quickly without paperwork, directly through your web browser.",
    icon: "fa-cart-shopping",
  },
  {
    title: "Inventory Tracking",
    text: "Check stock levels in real time and avoid running out of tiles or materials.",
    icon: "fa-boxes-stacked",
  },
  {
    title: "Secure Transactions",
    text: "Safe and reliable order management for your team and customers.",
    icon: "fa-shield-halved",
  },
];
</script>

<style scoped>
@keyframes slideUp {
  0% {
    transform: translateY(50px);
    opacity: 0;
  }

  100% {
    transform: translateY(0);
    opacity: 1;
  }
}

.animate-slide-up {
  animation: slideUp 0.8s ease-out forwards;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fadeIn 1s ease-out forwards;
}
</style>


<style scoped>
@keyframes slideDown {
  0% {
    transform: translateY(-50px);
    opacity: 0;
  }

  100% {
    transform: translateY(0);
    opacity: 1;
  }
}

.animate-slide-down {
  animation: slideDown 0.8s ease-out forwards;
}

.delay-200 {
  animation-delay: 0.2s;
}

.delay-500 {
  animation-delay: 0.5s;
}
</style>
