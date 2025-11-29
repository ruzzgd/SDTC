<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";
import { useLoadingStore } from "@/stores/loading";

const loading = useLoadingStore();
const router = useRouter();

const email_input = ref<string>("");
const password_input = ref<string>("");

const email_error = ref(false);
const password_error = ref(false);
const api_error = ref<string>("");

const isValidEmail = (email: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

const handleCreateAccount = async () => {
  email_error.value = !email_input.value.trim() || !isValidEmail(email_input.value);
  password_error.value = !password_input.value.trim();

  if (email_error.value || password_error.value) {
    setTimeout(() => {
      email_error.value = false;
      password_error.value = false;
    }, 3000);
    return;
  }

  try {
    loading.show();

    await axios.post("http://localhost:8000/auth/send-code", {
      email: email_input.value,
      role: "user",
      purpose: "register",
    });

    sessionStorage.setItem("pending_email", email_input.value);
    sessionStorage.setItem("pending_password", password_input.value);

    router.push("/email-auth");
  } catch (err: any) {
    api_error.value = err.response?.data?.detail || "Something went wrong, please try again.";

    setTimeout(() => {
      api_error.value = "";
    }, 3000);
  } finally {
    loading.hide();
  }
};
</script>

<template>
  <div
    class="h-screen w-full flex items-center justify-center bg-gradient-to-br from-gray-100 via-gray-200 to-gray-300 text-white px-6 relative overflow-hidden"
  >
    <!-- Background glow -->
    <div class="absolute inset-0 flex justify-center items-center opacity-10 blur-3xl">
      <div class="w-[600px] h-[600px] bg-sky-500/20 rounded-full animate-pulse"></div>
    </div>

    <!-- Register Card -->
    <div
      class="relative bg-gray-300/70 backdrop-blur-md rounded-2xl shadow-2xl p-8 sm:p-10 w-full max-w-md flex flex-col gap-6 border border-gray-700/50 animate-fade-in"
    >
      <h1 class="text-3xl sm:text-4xl font-extrabold text-center text-sky-400 mb-2 tracking-wide">
        Create Account
      </h1>

      <p class="text-center text-gray-700 text-sm mb-4">
        Start managing your orders and inventory with SDTC.
      </p>

      <!-- Email -->
      <div class="flex flex-col gap-2">
        <label for="email" class="font-medium text-sm text-gray-900">Email</label>
        <input
          type="email"
          id="email"
          v-model="email_input"
          :placeholder="email_error ? 'Enter a valid email address' : 'Enter your email'"
          :class="[
            'border rounded-lg px-4 py-3 bg-gray-200/70 text-gray-900 focus:outline-none transition-all duration-200 placeholder-gray-700',
            email_error
              ? 'border-red-500 focus:ring-2 focus:ring-red-400 placeholder-red-400'
              : 'border-gray-700 focus:ring-2 focus:ring-sky-500 focus:border-sky-500 hover:border-sky-400'
          ]"
        />
      </div>

      <!-- Password -->
      <div class="flex flex-col gap-2">
        <label for="password" class="font-medium text-sm text-gray-900">Password</label>
        <input
          type="password"
          id="password"
          v-model="password_input"
          :placeholder="password_error ? 'Password is required' : 'Enter your password'"
          :class="[
            'border rounded-lg px-4 py-3 bg-gray-200/70 text-gray-900 focus:outline-none transition-all duration-200 placeholder-gray-700',
            password_error
              ? 'border-red-500 focus:ring-2 focus:ring-red-400 placeholder-red-400'
              : 'border-gray-700 focus:ring-2 focus:ring-sky-500 focus:border-sky-500 hover:border-sky-400'
          ]"
        />
      </div>

      <!-- API Error -->
      <transition name="fade">
        <p
          v-if="api_error"
          class="text-red-400 text-sm text-center bg-red-500/10 p-2 rounded-md border border-red-500/40"
        >
          {{ api_error }}
        </p>
      </transition>

      <!-- Register Button -->
      <button
        @click="handleCreateAccount"
        class="bg-sky-600 hover:bg-sky-500 active:bg-sky-700 text-white font-semibold py-3 rounded-lg shadow-md shadow-sky-900/40 transition-all duration-200 transform hover:scale-105 active:scale-95"
      >
        Create Account
      </button>

      <!-- Already Have Account -->
      <p class="text-sm text-gray-700 text-center">
        Already have an account?
        <button
          @click="$router.replace('/login')"
          class="text-sky-400 hover:text-sky-300 font-medium transition-colors"
        >
          Login
        </button>
      </p>
    </div>
  </div>
</template>

<style scoped>
@keyframes fadeIn {
  0% {
    opacity: 0;
    transform: translateY(15px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fadeIn 0.6s ease-out forwards;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
