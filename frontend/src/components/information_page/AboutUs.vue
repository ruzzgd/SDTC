<template>
  <div class="w-full flex flex-col items-center justify-center px-6 py-16 bg-gray-300 text-white overflow-hidden">
    <!-- About Us Section -->
    <section class="max-w-3xl text-center animate-slide-down">
      <h1 class="text-4xl md:text-5xl font-bold mb-4 text-sky-400 drop-shadow-md">
        About SDTC
      </h1>
      <p class="text-lg md:text-xl mb-6 text-gray-900 leading-relaxed">
        <span class="font-semibold">Sorsogon Depot and Tile Center (SDTC)</span> is a
        web-based platform designed to simplify ordering and streamline inventory management
        for staff, managers, and customers.
      </p>
    </section>

    <!-- Mission / Vision Section -->
    <section class="mt-16 max-w-4xl text-center animate-slide-up">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div
          class="bg-gray-400/70 border border-gray-100/60 rounded-2xl p-8 shadow-lg hover:shadow-[0_0_30px_rgba(255,255,255,0.3)] transition-all duration-700 group relative overflow-hidden"
        >
          <div
            class="absolute inset-0 bg-gradient-to-r from-transparent via-white/60 to-transparent
                   opacity-0 group-hover:opacity-100 -translate-x-full group-hover:translate-x-full
                   transition-all duration-[1200ms] ease-in-out pointer-events-none"
          ></div>
          <i class="fa-solid fa-bullseye text-sky-400 text-3xl mb-4"></i>
          <h2 class="text-2xl font-semibold mb-3 text-gray-900">Our Mission</h2>
          <p class="text-gray-700 leading-relaxed">
            To simplify the ordering process and improve inventory tracking, saving time and reducing
            errors for both staff and customers.
          </p>
        </div>

        <div
          class="bg-gray-400/70 border border-gray-100/60 rounded-2xl p-8 shadow-lg hover:shadow-[0_0_30px_rgba(255,255,255,0.3)] transition-all duration-700 group relative overflow-hidden"
        >
          <div
            class="absolute inset-0 bg-gradient-to-r from-transparent via-white/60 to-transparent
                   opacity-0 group-hover:opacity-100 -translate-x-full group-hover:translate-x-full
                   transition-all duration-[1200ms] ease-in-out pointer-events-none"
          ></div>
          <i class="fa-solid fa-eye text-sky-400 text-3xl mb-4"></i>
          <h2 class="text-2xl font-semibold mb-3 text-gray-900">Our Vision</h2>
          <p class="text-gray-700 leading-relaxed">
            To provide a reliable, user-friendly, and future-ready platform that enhances
            order processing, stock accuracy, and the customer experience.
          </p>
        </div>
      </div>
    </section>

    <!-- How it Helps Section -->
    <section class="mt-20 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl text-center px-4">
      <div
        v-for="(card, i) in cards"
        :key="i"
        class="relative bg-gray-400/70 backdrop-blur-md p-8 rounded-2xl shadow-lg border border-gray-100/60
               transition-all duration-700 hover:shadow-[0_0_35px_rgba(255,255,255,0.35)] hover:scale-105 group
               animate-slide-up"
        :style="{ animationDelay: `${i * 0.25}s` }"
      >
        <div
          class="absolute inset-0 bg-gradient-to-r from-transparent via-white/60 to-transparent
                 opacity-0 group-hover:opacity-100 -translate-x-full group-hover:translate-x-full
                 transition-all duration-[1200ms] ease-in-out pointer-events-none"
        ></div>

        <div class="relative z-10 flex flex-col items-center">
          <div class="w-12 h-12 mb-4 flex items-center justify-center bg-sky-600/20 rounded-full">
            <i :class="`fa-solid ${card.icon} text-sky-400 text-2xl`"></i>
          </div>
          <h3 class="text-xl font-semibold mb-2 text-gray-900">{{ card.title }}</h3>
          <p class="text-gray-700 leading-relaxed">{{ card.text }}</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
const cards = [
  { icon: "fa-warehouse", title: "For Staff", text: "Manage inventory easily and track orders in real-time." },
  { icon: "fa-briefcase", title: "For Managers", text: "Monitor stock levels and streamline workflows efficiently." },
  { icon: "fa-users", title: "For Customers", text: "Place orders quickly and check availability anytime." }
];
</script>

<style scoped>
@keyframes slideDown {
  0% { transform: translateY(-40px); opacity: 0; }
  100% { transform: translateY(0); opacity: 1; }
}

@keyframes slideUp {
  0% { transform: translateY(40px); opacity: 0; }
  100% { transform: translateY(0); opacity: 1; }
}

.animate-slide-down {
  animation: slideDown 0.9s ease-out forwards;
}

.animate-slide-up {
  animation: slideUp 0.9s ease-out forwards;
}
</style>
