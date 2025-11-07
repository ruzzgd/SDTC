<template>
  <div class="w-full flex flex-col items-center justify-center px-6 py-16 bg-gray-900 text-white">
    <!-- Header -->
    <section class="max-w-3xl text-center animate-slide-down">
      <h1 class="text-4xl sm:text-5xl font-extrabold mb-4">Contact Us</h1>
      <p class="text-base sm:text-lg md:text-xl text-gray-300 mb-6">
        Have questions or need assistance? Reach out to us — we’ll get back to you as soon as possible.
      </p>
    </section>

    <!-- Contact Info -->
    <section class="mt-12 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 sm:gap-8 w-full max-w-5xl text-center">
      <div class="relative bg-gray-800/90 p-6 rounded-2xl shadow-lg overflow-hidden
                  transition-all duration-700 hover:shadow-[0_0_30px_rgba(56,189,248,0.4)] hover:scale-105 group animate-slide-down">
        <div class="absolute inset-0 bg-gradient-to-r from-transparent via-sky-400/20 to-transparent
                    -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-in-out pointer-events-none"></div>
        <h3 class="text-xl font-semibold mb-2 text-sky-400">Email</h3>
        <p class="text-gray-300 break-words">support@sdtc.com</p>
      </div>

      <div class="relative bg-gray-800/90 p-6 rounded-2xl shadow-lg overflow-hidden
                  transition-all duration-700 hover:shadow-[0_0_30px_rgba(56,189,248,0.4)] hover:scale-105 group animate-slide-down delay-200">
        <div class="absolute inset-0 bg-gradient-to-r from-transparent via-sky-400/20 to-transparent
                    -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-in-out pointer-events-none"></div>
        <h3 class="text-xl font-semibold mb-2 text-sky-400">Phone</h3>
        <p class="text-gray-300">+63 912 345 6789</p>
      </div>

      <div class="relative bg-gray-800/90 p-6 rounded-2xl shadow-lg overflow-hidden
                  transition-all duration-700 hover:shadow-[0_0_30px_rgba(56,189,248,0.4)] hover:scale-105 group animate-slide-down delay-500">
        <div class="absolute inset-0 bg-gradient-to-r from-transparent via-sky-400/20 to-transparent
                    -translate-x-full group-hover:translate-x-full transition-transform duration-1000 ease-in-out pointer-events-none"></div>
        <h3 class="text-xl font-semibold mb-2 text-sky-400">Address</h3>
        <p class="text-gray-300 leading-relaxed">
          Sorsogon Depot and Tile Center, <br />
          Bulan, Sorsogon, Philippines
        </p>
      </div>
    </section>

    <!-- Contact Form -->
    <section class="mt-16 w-full max-w-2xl animate-slide-down delay-700 px-2 sm:px-0">
      <form
        ref="form"
        @submit.prevent="sendEmail"
        class="flex flex-col gap-5 bg-gray-800/90 p-8 rounded-2xl shadow-lg border border-gray-700"
      >
        <input
          v-model="name"
          type="text"
          name="user_name"
          placeholder="Your Name"
          class="p-3 sm:p-4 rounded-lg bg-gray-900 text-white border border-gray-700 focus:outline-none focus:ring-2 focus:ring-sky-500 placeholder-gray-500"
          required
        />
        <input
          v-model="email"
          type="email"
          name="user_email"
          placeholder="Your Email"
          class="p-3 sm:p-4 rounded-lg bg-gray-900 text-white border border-gray-700 focus:outline-none focus:ring-2 focus:ring-sky-500 placeholder-gray-500"
          required
        />
        <textarea
          v-model="message"
          name="message"
          placeholder="Your Message"
          rows="5"
          class="p-3 sm:p-4 rounded-lg bg-gray-900 text-white border border-gray-700 focus:outline-none focus:ring-2 focus:ring-sky-500 placeholder-gray-500 resize-none"
          required
        ></textarea>

        <button
          type="submit"
          class="px-6 py-3 bg-sky-600 hover:bg-sky-700 active:bg-sky-800 rounded-xl font-semibold transition-all duration-300 transform hover:scale-105 active:scale-95 shadow-md shadow-sky-900/40"
        >
          Send Message
        </button>

        <!-- Success & Error Messages -->
        <p v-if="successMessage" class="text-green-400 text-center">{{ successMessage }}</p>
        <p v-if="errorMessage" class="text-red-400 text-center">{{ errorMessage }}</p>
      </form>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import emailjs from '@emailjs/browser'

const form = ref(null)
const name = ref('')
const email = ref('')
const message = ref('')
const successMessage = ref('')
const errorMessage = ref('')

// Replace with your own EmailJS credentials
const serviceID = 'service_xxxxxx'
const templateID = 'template_xxxxxx'
const publicKey = 'hHh-xxxxx123'

const sendEmail = () => {
  successMessage.value = ''
  errorMessage.value = ''

  emailjs
    .sendForm(serviceID, templateID, form.value, publicKey)
    .then(() => {
      successMessage.value = 'Your message has been sent successfully!'
      name.value = ''
      email.value = ''
      message.value = ''
    })
    .catch(() => {
      errorMessage.value = 'Failed to send message. Please try again later.'
    })
}
</script>

<style scoped>
@keyframes slideDown {
  0% {
    transform: translateY(-40px);
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

.delay-700 {
  animation-delay: 0.7s;
}
</style>
