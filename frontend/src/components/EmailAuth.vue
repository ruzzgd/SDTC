<script setup lang="ts">
import { ref, onBeforeUnmount } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";
import { useLoadingStore } from "@/stores/loading";

const verification_code = ref<string>("");
const router = useRouter();
const loading = useLoadingStore();
const backend = import.meta.env.VITE_BACKEND_URL;

const email_error = ref(false);
const code_error = ref(false);
const api_error = ref<string>("");

const resendCooldown = ref(0);
let resendInterval: number | null = null;

onBeforeUnmount(() => {
  sessionStorage.removeItem("pending_email");
  sessionStorage.removeItem("pending_password");
  if (resendInterval) clearInterval(resendInterval);
});

const handleVerify = async () => {
  const email = sessionStorage.getItem("pending_email");
  const password = sessionStorage.getItem("pending_password");

  email_error.value = false;
  code_error.value = false;
  api_error.value = "";

  if (!email || !password) {
    api_error.value = "Session expired. Please create an account again.";
    setTimeout(() => (api_error.value = ""), 3000);
    router.replace("/register");
    return;
  }

  if (!verification_code.value.trim()) {
    code_error.value = true;
    api_error.value = "Verification code cannot be empty.";
    setTimeout(() => {
      code_error.value = false;
      api_error.value = "";
    }, 3000);
    return;
  }

  try {
    loading.show();

    await axios.post(`${backend}/auth/verify-code`, {
      email,
      code: verification_code.value,
      role: "user",
    });

    await axios.post(
      `${backend}/users/register`,
      { email, password },
      { withCredentials: true }
    );

    sessionStorage.removeItem("pending_email");
    sessionStorage.removeItem("pending_password");

    router.push("/dashboard");
  } catch (err: any) {
    api_error.value = err.response?.data?.detail || "Something went wrong, please try again.";
    setTimeout(() => (api_error.value = ""), 3000);
  } finally {
    loading.hide();
  }
};

// 🔁 Resend Verification Code
const handleResend = async () => {
  const email = sessionStorage.getItem("pending_email");
  if (!email) {
    api_error.value = "Session expired. Please create an account again.";
    setTimeout(() => (api_error.value = ""), 3000);
    router.replace("/register");
    return;
  }

  try {
    loading.show();
    await axios.post(`${backend}/auth/send-code`, {
      email,
      role: "user",
      purpose: "register",
    });

    // Start cooldown (60 seconds)
    resendCooldown.value = 60;
    resendInterval = window.setInterval(() => {
      resendCooldown.value -= 1;
      if (resendCooldown.value <= 0 && resendInterval) {
        clearInterval(resendInterval);
        resendInterval = null;
      }
    }, 1000);
  } catch (err: any) {
    api_error.value = err.response?.data?.detail || "Failed to resend code.";
    setTimeout(() => (api_error.value = ""), 3000);
  } finally {
    loading.hide();
  }
};
</script>

<template>
  <div
    class="h-screen w-full flex items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white px-6 relative overflow-hidden"
  >
    <div class="absolute inset-0 flex justify-center items-center opacity-10 blur-3xl">
      <div class="w-[600px] h-[600px] bg-sky-500/20 rounded-full animate-pulse"></div>
    </div>

    <div
      class="relative bg-gray-800/70 backdrop-blur-md rounded-2xl shadow-2xl p-8 sm:p-10 w-full max-w-md flex flex-col gap-6 border border-gray-700/50 animate-fade-in"
    >
      <h1 class="text-3xl sm:text-4xl font-extrabold text-center text-sky-400 mb-2 tracking-wide">
        Email Verification
      </h1>

      <p class="text-gray-400 text-center text-sm mb-2 leading-relaxed">
        We've sent a verification code to your registered email. <br />
        Please enter it below to complete your registration.
      </p>

      <!-- Verification Code -->
      <div class="flex flex-col gap-2">
        <label for="code" class="font-medium text-sm text-gray-300">Verification Code</label>
        <input
          type="text"
          id="code"
          v-model="verification_code"
          maxlength="6"
          :placeholder="code_error ? 'Code cannot be empty' : 'Enter your 6-digit code'"
          :class="[
            'border rounded-lg px-4 py-3 bg-gray-900/70 text-white focus:outline-none text-center font-mono tracking-widest text-lg transition-all duration-200 placeholder-gray-500',
            code_error
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

      <!-- Verify Button -->
      <button
        @click="handleVerify"
        class="bg-sky-600 hover:bg-sky-500 active:bg-sky-700 text-white font-semibold py-3 rounded-lg shadow-md shadow-sky-900/40 transition-all duration-200 transform hover:scale-105 active:scale-95"
      >
        Verify Email
      </button>

      <!-- Resend -->
      <p class="text-sm text-gray-400 text-center">
        Didn’t receive the code?
        <button
          @click="handleResend"
          :disabled="resendCooldown > 0"
          class="text-sky-400 hover:text-sky-300 font-medium cursor-pointer transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ resendCooldown > 0 ? `Resend (${resendCooldown}s)` : "Resend" }}
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
