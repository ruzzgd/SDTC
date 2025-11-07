<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { useLoadingStore } from '@/stores/loading';

const loading = useLoadingStore();
const router = useRouter();
const backend = import.meta.env.VITE_BACKEND_URL

const admin_email = ref<string>('');
const admin_password = ref<string>('');

const email_error = ref(false);
const password_error = ref(false);
const error_message = ref<string>('');

const loginAdmin = async () => {
  // Reset errors
  email_error.value = false;
  password_error.value = false;
  error_message.value = '';

  // Validate inputs
  if (!admin_email.value.trim()) email_error.value = true;
  if (!admin_password.value.trim()) password_error.value = true;

  if (email_error.value || password_error.value) {
    setTimeout(() => {
      email_error.value = false;
      password_error.value = false;
    }, 3000);
    return;
  }

  try {
    loading.show(); // Show loading spinner

    const response = await axios.post(
      `${backend}/admin/login`,
      { email: admin_email.value, password: admin_password.value },
      { withCredentials: true } // Receive cookie from FastAPI
    );

    console.log('Admin login response:', response.data);
    router.replace('/admin'); // Redirect after successful login
  } catch (err: any) {
    if (err.response?.data?.detail) {
      error_message.value = err.response.data.detail;
    } else {
      error_message.value = 'Something went wrong';
    }

    setTimeout(() => {
      error_message.value = '';
    }, 3000);
  } finally {
    loading.hide(); // Hide loading spinner
  }
};
</script>

<template>
  <div class="h-screen w-full flex items-center justify-center bg-gray-900 text-white">
    <div class="bg-gray-800 rounded-2xl shadow-lg p-10 w-[350px] md:w-[400px] flex flex-col gap-6">
      <h1 class="text-2xl font-bold text-center mb-4">Admin Login</h1>

      <!-- Email -->
      <div class="flex flex-col gap-2">
        <label for="admin-email" class="font-medium">Email</label>
        <input
          type="email"
          id="admin-email"
          v-model="admin_email"
          :placeholder="email_error ? 'Email cannot be empty' : 'Enter your email'"
          :class="[
            'border rounded-lg px-4 py-2 bg-gray-700 text-white focus:outline-none transition-colors',
            email_error
              ? 'border-red-500 placeholder-red-400 focus:ring-2 focus:ring-red-400'
              : 'border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 hover:border-blue-500'
          ]"
        />
      </div>

      <!-- Password -->
      <div class="flex flex-col gap-2">
        <label for="admin-password" class="font-medium">Password</label>
        <input
          type="password"
          id="admin-password"
          v-model="admin_password"
          :placeholder="password_error ? 'Password cannot be empty' : 'Enter your password'"
          :class="[
            'border rounded-lg px-4 py-2 bg-gray-700 text-white focus:outline-none transition-colors',
            password_error
              ? 'border-red-500 placeholder-red-400 focus:ring-2 focus:ring-red-400'
              : 'border-gray-600 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 hover:border-blue-500'
          ]"
        />
      </div>

      <!-- API Error -->
      <p v-if="error_message" class="text-red-500 text-sm text-center">{{ error_message }}</p>

      <!-- Login Button -->
      <button
        @click="loginAdmin"
        class="bg-blue-700 text-white font-semibold py-2 rounded-lg hover:bg-blue-600 transition-colors cursor-pointer"
      >
        Login
      </button>
    </div>
  </div>
</template>
