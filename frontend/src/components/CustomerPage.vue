<script setup lang="ts">
import { ref } from 'vue'
import HomeInfo from './information_page/HomeInfo.vue'
import AboutUs from './information_page/AboutUs.vue'
import ContactUs from './information_page/ContactUs.vue'

// Refs for each section
const homeRef = ref<HTMLElement | null>(null)
const aboutRef = ref<HTMLElement | null>(null)
const contactRef = ref<HTMLElement | null>(null)

// Toggle mobile menu modal
const isMenuOpen = ref(false)

const scrollToSection = (section: HTMLElement | null) => {
  if (section) {
    section.scrollIntoView({ behavior: 'smooth', block: 'start' })
    isMenuOpen.value = false // close modal after clicking
  }
}
</script>

<template>
  <div class="min-h-screen w-full flex flex-col bg-gray-200 text-gray-900 relative">
    <!-- Header / Navbar -->
    <header class="flex h-[80px] w-full bg-gray-100 sticky top-0 px-6 justify-between items-center shadow-lg z-50">
      <!-- Logo -->
      <div class="flex items-center gap-3">
        <img src="@/assets/img/sdtc-logo.jpg" alt="SDTC Logo" class="h-[50px] rounded-2xl" />
      </div>

      <!-- Desktop Navigation -->
      <nav class="hidden md:flex items-center gap-8">
        <button @click="scrollToSection(homeRef)" class="hover:text-blue-400 transition-colors">Home</button>
        <button @click="scrollToSection(aboutRef)" class="hover:text-blue-400 transition-colors">About Us</button>
        <button @click="scrollToSection(contactRef)" class="hover:text-blue-400 transition-colors">Contact Us</button>
      </nav>

      <!-- Auth Buttons (Desktop only) -->
      <div class="hidden md:flex items-center gap-3">
        <button class="px-4 py-2 bg-blue-600 rounded-lg hover:bg-blue-700 transition" @click="$router.push('/login')">Login</button>
        <button class="px-4 py-2 bg-green-600 rounded-lg hover:bg-green-700 transition" @click="$router.push('/register')">Register</button>
      </div>

      <!-- Mobile Menu Button -->
      <button class="md:hidden text-2xl" @click="isMenuOpen = !isMenuOpen">
        <i class="fa-solid fa-bars"></i>
      </button>
    </header>

    <!-- Mobile Menu Modal -->
    <div
      v-if="isMenuOpen"
      class="fixed inset-0 bg-black/70 flex justify-center items-center z-50"
    >
      <div class="bg-gray-200 w-3/4 max-w-xs p-6 rounded-lg flex flex-col gap-4 relative">
        <!-- Close Button -->
        <button class="absolute top-4 right-4 text-xl" @click="isMenuOpen = false">
          <i class="fa-solid fa-xmark"></i>
        </button>

        <button @click="scrollToSection(homeRef)" class="hover:text-blue-400 transition-colors text-left">Home</button>
        <button @click="scrollToSection(aboutRef)" class="hover:text-blue-400 transition-colors text-left">About Us</button>
        <button @click="scrollToSection(contactRef)" class="hover:text-blue-400 transition-colors text-left">Contact Us</button>
        <hr class="border-gray-600" />
        <button class="px-4 py-2 bg-blue-600 rounded-lg hover:bg-blue-700 transition" @click="$router.push('/login')">Login</button>
        <button class="px-4 py-2 bg-green-600 rounded-lg hover:bg-green-700 transition" @click="$router.push('/register')">Register</button>
      </div>
    </div>

    <!-- Main Sections -->
    <main class="flex-1">
      <section ref="homeRef" class="min-h-screen flex items-center justify-center">
        <HomeInfo />
      </section>

      <section ref="aboutRef" class="min-h-screen flex items-center justify-center bg-gray-800">
        <AboutUs />
      </section>

      <section ref="contactRef" class="min-h-screen flex items-center justify-center">
        <ContactUs />
      </section>
    </main>

    <!-- Footer -->
    <footer class="bg-gray-200 py-6 px-6 text-center mt-auto">
      <div class="flex flex-col md:flex-row justify-between items-center gap-4">
        <p class="text-sm text-gray-900">&copy; 2025 SDTC. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>
