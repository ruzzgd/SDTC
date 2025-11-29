<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import axios from "axios";
import { useLoadingStore } from "@/stores/loading";

const router = useRouter();
const loading = useLoadingStore();
const backend = import.meta.env.VITE_BACKEND_URL;

const email_input = ref<string>("");
const password_input = ref<string>("");

const email_error = ref(false);
const password_error = ref(false);
const error_message = ref<string>("");

// Forgot Password Modal
const showForgotModal = ref(false);
const forgotEmail = ref("");
const forgotError = ref(false);
const forgotMsg = ref("");

// Verify Code Modal
const showVerifyModal = ref(false);
const verifyCode = ref("");
const verifyMsg = ref("");
const verifyError = ref(false);

// Change Password Modal
const showChangePassModal = ref(false);
const newPassword = ref("");
const confirmPassword = ref("");
const changeMsg = ref("");
const changeError = ref(false);

const login = async () => {
  email_error.value = false;
  password_error.value = false;
  error_message.value = "";

  if (!email_input.value.trim()) email_error.value = true;
  if (!password_input.value.trim()) password_error.value = true;

  if (email_error.value || password_error.value) {
    setTimeout(() => {
      email_error.value = false;
      password_error.value = false;
    }, 3000);
    return;
  }

  try {
    loading.show();
    const response = await axios.post(
      `${backend}/users/login`,
      { email: email_input.value, password: password_input.value },
      { withCredentials: true }
    );
    console.log("Login response:", response.data);
    router.replace("/dashboard");
  } catch (err: any) {
    if (err.response?.data?.detail) {
      error_message.value = err.response.data.detail;
    } else {
      error_message.value = "Something went wrong";
    }
    setTimeout(() => {
      error_message.value = "";
    }, 3000);
  } finally {
    loading.hide();
  }
};

const goToRegister = () => {
  router.replace("/register");
};

// Handle Forgot Password
const sendForgotCode = async () => {
  forgotError.value = false;
  forgotMsg.value = "";

  if (!forgotEmail.value.trim()) {
    forgotError.value = true;
    forgotMsg.value = "Email cannot be empty.";
    setTimeout(() => (forgotError.value = false), 3000);
    return;
  }

  try {
    loading.show();

    await axios.post(`${backend}/auth/send-code`, {
      email: forgotEmail.value,
      role: "user",
      purpose: "reset",
    });

    // Save email for next step
    sessionStorage.setItem("pending_email", forgotEmail.value);
    showForgotModal.value = false;
    showVerifyModal.value = true; // Open verify modal automatically
  } catch (err: any) {
    forgotMsg.value = err.response?.data?.detail || "Something went wrong. Try again.";
    setTimeout(() => (forgotMsg.value = ""), 3000);
  } finally {
    loading.hide();
  }
};

// Verify the code sent to email
const verifyForgotCode = async () => {
  verifyError.value = false;
  verifyMsg.value = "";

  if (!verifyCode.value.trim()) {
    verifyError.value = true;
    verifyMsg.value = "Code cannot be empty.";
    setTimeout(() => (verifyError.value = false), 3000);
    return;
  }

  try {
    loading.show();
    const email = sessionStorage.getItem("pending_email");
    await axios.post(`${backend}/auth/verify-code`, {
      email,
      role: "user",
      code: verifyCode.value,
    });

    showVerifyModal.value = false;
    showChangePassModal.value = true;
  } catch (err: any) {
    verifyMsg.value = err.response?.data?.detail || "Invalid or expired code.";
    setTimeout(() => (verifyMsg.value = ""), 3000);
  } finally {
    loading.hide();
  }
};

// Change Password
const changePassword = async () => {
  changeError.value = false;
  changeMsg.value = "";

  if (!newPassword.value.trim() || !confirmPassword.value.trim()) {
    changeError.value = true;
    changeMsg.value = "Fields cannot be empty.";
    return;
  }

  if (newPassword.value !== confirmPassword.value) {
    changeError.value = true;
    changeMsg.value = "Passwords do not match.";
    return;
  }

  try {
    loading.show();
    const email = sessionStorage.getItem("pending_email");
    await axios.post(`${backend}/users/change-password`, {
      email,
      new_password: newPassword.value,
    });

    changeMsg.value = "Password changed successfully. You can now log in.";
    setTimeout(() => {
      showChangePassModal.value = false;
    }, 2000);
  } catch (err: any) {
    changeMsg.value = err.response?.data?.detail || "Something went wrong.";
  } finally {
    loading.hide();
  }
};
</script>

<template>
  <div
    class="h-screen w-full flex items-center justify-center bg-gradient-to-br from-gray-100 via-gray-200 to-gray-300 text-white px-6 relative overflow-hidden">
    <!-- Background glow -->
    <div class="absolute inset-0 flex justify-center items-center opacity-10 blur-3xl">
      <div class="w-[600px] h-[600px] bg-sky-500/20 rounded-full animate-pulse"></div>
    </div>

    <!-- Login Card -->
    <div
      class="relative bg-gray-300/70 backdrop-blur-md rounded-2xl shadow-2xl p-8 sm:p-10 w-full max-w-md flex flex-col gap-6 border border-gray-700/50 animate-fade-in">
      <h1 class="text-3xl sm:text-4xl font-extrabold text-center text-sky-400 mb-2 tracking-wide">
        Welcome Back
      </h1>
      <p class="text-center text-gray-700 text-sm mb-4">Log in to continue to your dashboard</p>

      <!-- Email -->
      <div class="flex flex-col gap-2">
        <label for="email" class="font-medium text-sm text-gray-900">Email</label>
        <input type="email" id="email" v-model="email_input"
          :placeholder="email_error ? 'Email cannot be empty' : 'Enter your email'" :class="[
            'border rounded-lg px-4 py-3 bg-gray-200/70 text-gray-900 focus:outline-none transition-all duration-200 placeholder-gray-700',
            email_error
              ? 'border-red-500 focus:ring-2 focus:ring-red-400 placeholder-red-400'
              : 'border-gray-700 focus:ring-2 focus:ring-sky-500 focus:border-sky-500 hover:border-sky-400'
          ]" />
      </div>

      <!-- Password -->
      <div class="flex flex-col gap-2">
        <label for="password" class="font-medium text-sm text-gray-900">Password</label>
        <input type="password" id="password" v-model="password_input"
          :placeholder="password_error ? 'Password cannot be empty' : 'Enter your password'" :class="[
            'border rounded-lg px-4 py-3 bg-gray-200/70 text-gray-900 focus:outline-none transition-all duration-200 placeholder-gray-700',
            password_error
              ? 'border-red-500 focus:ring-2 focus:ring-red-400 placeholder-red-400'
              : 'border-gray-700 focus:ring-2 focus:ring-sky-500 focus:border-sky-500 hover:border-sky-400'
          ]" />

        <!-- Forgot Password -->
        <button type="button" @click="showForgotModal = true"
          class="text-sm text-sky-400 hover:text-sky-300 mt-1 text-right transition-colors">
          Forgot Password?
        </button>
      </div>

      <!-- Error -->
      <transition name="fade">
        <p v-if="error_message"
          class="text-red-400 text-sm text-center bg-red-500/10 p-2 rounded-md border border-red-500/40">
          {{ error_message }}
        </p>
      </transition>

      <!-- Login Button -->
      <button @click="login"
        class="bg-sky-600 hover:bg-sky-500 active:bg-sky-700 text-white font-semibold py-3 rounded-lg shadow-md shadow-sky-900/40 transition-all duration-200 transform hover:scale-105 active:scale-95">
        Login
      </button>

      <!-- Register -->
      <p class="text-sm text-gray-700 text-center">
        Don’t have an account?
        <button @click="goToRegister" class="text-sky-400 hover:text-sky-300 font-medium transition-colors">
          Create Account
        </button>
      </p>
    </div>

    <!-- Forgot Password Modal -->
    <transition name="fade">
      <div v-if="showForgotModal"
        class="absolute inset-0 flex items-center justify-center bg-black/20 backdrop-blur-sm z-50">
        <div
          class="bg-white border border-gray-300 rounded-2xl shadow-xl p-8 w-[90%] max-w-md flex flex-col gap-5 animate-fade-in">
          <h2 class="text-2xl font-bold text-center text-sky-600">Reset Password</h2>
          <p class="text-gray-600 text-sm text-center">
            Enter your email to receive a verification code.
          </p>

          <input type="email" v-model="forgotEmail" placeholder="Enter your email" :class="[
            'border rounded-lg px-4 py-3 bg-gray-100 text-gray-900 focus:outline-none placeholder-gray-400',
            forgotError
              ? 'border-red-500 focus:ring-2 focus:ring-red-300 placeholder-red-400'
              : 'border-gray-400 focus:ring-2 focus:ring-sky-400'
          ]" />

          <p v-if="forgotMsg" class="text-center text-sm text-red-500">{{ forgotMsg }}</p>

          <div class="flex gap-3 mt-2">
            <button @click="sendForgotCode"
              class="flex-1 bg-sky-600 hover:bg-sky-500 text-white font-semibold py-2 rounded-lg transition-all duration-200">
              Submit
            </button>
            <button @click="showForgotModal = false"
              class="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold py-2 rounded-lg transition-all duration-200">
              Cancel
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- Verify Code Modal -->
    <transition name="fade">
      <div v-if="showVerifyModal"
        class="absolute inset-0 flex items-center justify-center bg-black/20 backdrop-blur-sm z-50">
        <div
          class="bg-white border border-gray-300 rounded-2xl shadow-xl p-8 w-[90%] max-w-md flex flex-col gap-5 animate-fade-in">
          <h2 class="text-2xl font-bold text-center text-sky-600">Verify Code</h2>
          <p class="text-gray-600 text-sm text-center">
            Enter the code sent to your email.
          </p>

          <input type="text" v-model="verifyCode" placeholder="Enter verification code" :class="[
            'border rounded-lg px-4 py-3 bg-gray-100 text-gray-900 focus:outline-none placeholder-gray-400',
            verifyError
              ? 'border-red-500 focus:ring-2 focus:ring-red-300 placeholder-red-400'
              : 'border-gray-400 focus:ring-2 focus:ring-sky-400'
          ]" />

          <p v-if="verifyMsg" class="text-center text-sm text-red-500">{{ verifyMsg }}</p>

          <div class="flex gap-3 mt-2">
            <button @click="verifyForgotCode"
              class="flex-1 bg-sky-600 hover:bg-sky-500 text-white font-semibold py-2 rounded-lg transition-all duration-200">
              Verify
            </button>
            <button @click="showVerifyModal = false"
              class="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold py-2 rounded-lg transition-all duration-200">
              Cancel
            </button>
          </div>
        </div>
      </div>
    </transition>


    <!-- Change Password Modal -->
    <transition name="fade">
      <div v-if="showChangePassModal"
        class="absolute inset-0 flex items-center justify-center bg-black/20 backdrop-blur-sm z-50">
        <div
          class="bg-white border border-gray-300 rounded-2xl shadow-xl p-8 w-[90%] max-w-md flex flex-col gap-5 animate-fade-in">
          <h2 class="text-2xl font-bold text-center text-sky-600">Change Password</h2>
          <p class="text-gray-600 text-sm text-center">
            Enter your new password below.
          </p>

          <input type="password" v-model="newPassword" placeholder="New password"
            class="border rounded-lg px-4 py-3 bg-gray-100 text-gray-900 focus:outline-none placeholder-gray-400 border-gray-400 focus:ring-2 focus:ring-sky-400" />

          <input type="password" v-model="confirmPassword" placeholder="Confirm new password"
            class="border rounded-lg px-4 py-3 bg-gray-100 text-gray-900 focus:outline-none placeholder-gray-400 border-gray-400 focus:ring-2 focus:ring-sky-400" />

          <p v-if="changeMsg" class="text-center text-sm text-red-500">{{ changeMsg }}</p>

          <div class="flex gap-3 mt-2">
            <button @click="changePassword"
              class="flex-1 bg-sky-600 hover:bg-sky-500 text-white font-semibold py-2 rounded-lg transition-all duration-200">
              Submit
            </button>
            <button @click="showChangePassModal = false"
              class="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-700 font-semibold py-2 rounded-lg transition-all duration-200">
              Cancel
            </button>
          </div>
        </div>
      </div>
    </transition>

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
  animation: fadeIn 0.5s ease-out forwards;
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
