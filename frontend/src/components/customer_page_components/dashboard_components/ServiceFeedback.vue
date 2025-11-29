<template>
  <div class="feedback-container p-6 max-w-xl mx-auto">
    <!-- Feedback Summary -->
    <div
      class="summary-card mb-6 p-6 rounded-xl shadow-lg bg-gradient-to-r from-gray-300 to-gray-400 flex flex-col items-center"
    >
      <h2 class="text-2xl font-bold mb-2 text-gray-900">Customer Feedback</h2>
      <p class="text-gray-700 mb-2">
        Total Feedbacks: <span class="font-semibold">{{ feedbackList.length }}</span>
      </p>
      <div class="flex items-center">
        <div class="flex text-yellow-400 text-3xl">
          <span v-for="i in 5" :key="i">
            {{ i <= Math.round(avgRating) ? '★' : '☆' }}
          </span>
        </div>
        <span class="ml-2 text-gray-900 text-lg">{{ avgRating.toFixed(1) }}</span>
      </div>
    </div>

    <!-- Feedback Form -->
    <form @submit.prevent="submitFeedback" class="mb-6 p-6 bg-gradient-to-r from-gray-300 to-gray-400 rounded-xl shadow-md">
      <div class="mb-4">
        <label for="description" class="block font-semibold mb-1 text-gray-900">Your Feedback</label>
        <textarea
          id="description"
          v-model="form.description"
          rows="4"
          required
          placeholder="Write your thoughts..."
          class="w-full p-3 rounded-lg bg-gray-300 border border-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
        ></textarea>
      </div>

      <div class="mb-4">
        <label class="block font-semibold mb-1 text-gray-900">Rating</label>
        <div class="flex space-x-2">
          <button
            v-for="n in 5"
            :key="n"
            type="button"
            @click="form.rating = n"
            class="text-yellow-400 text-3xl transform hover:scale-125 transition-transform"
          >
            <span v-if="n <= form.rating">★</span>
            <span v-else>☆</span>
          </button>
        </div>
      </div>

      <button
        type="submit"
        class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 rounded-lg transition-colors"
      >
        Submit Feedback
      </button>
    </form>

    <!-- Feedback List -->
    <div v-if="feedbackList.length">
      <h3 class="text-xl font-bold mb-3 text-gray-200">All Feedback</h3>
      <ul class="space-y-4">
        <li
          v-for="item in feedbackList"
          :key="item.id"
          class="p-4 bg-gradient-to-r from-gray-300 to-gray-400 rounded-xl shadow hover:shadow-lg transition-shadow flex justify-between items-start"
        >
          <div class="flex-1">
            <p class="font-semibold text-gray-900">{{ item.email }}</p>
            <p class="text-sm text-gray-700">{{ formatDate(item.created_at) }}</p>
            <p class="mt-2 text-gray-900">{{ item.description }}</p>
          </div>
          <div class="flex flex-col justify-start ml-4">
            <div class="flex text-yellow-400 text-xl">
              <span v-for="i in 5" :key="i">{{ i <= item.rating ? '★' : '☆' }}</span>
            </div>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted, computed } from 'vue'
import axios from 'axios'
import { useNotifStore } from '@/stores/notif'

const notif = useNotifStore()
const backend = import.meta.env.VITE_BACKEND_URL

interface Feedback {
  id: number
  email: string
  description: string
  rating: number
  created_at: string
}

const form = reactive({
  description: '',
  rating: 0,
})

const feedbackList = ref<Feedback[]>([])

const avgRating = computed(() => {
  if (feedbackList.value.length === 0) return 0
  const total = feedbackList.value.reduce((sum, f) => sum + f.rating, 0)
  return total / feedbackList.value.length
})

// ---------------- Fetch Feedback ----------------
const getFeedback = async () => {
  try {
    const { data } = await axios.get(`${backend}/users/feedback`, { withCredentials: true })
    feedbackList.value = data
  } catch (err) {
    notif.show('Failed to fetch feedback', 'error')
  }
}

// ---------------- Submit Feedback ----------------
const submitFeedback = async () => {
  if (!form.description.trim() || form.rating === 0) {
    notif.show('Please provide feedback and rating', 'warning')
    return
  }

  try {
    await axios.post(`${backend}/users/feedback`, form, { withCredentials: true })
    notif.show('Thank you for your feedback!', 'success')

    form.description = ''
    form.rating = 0

    getFeedback()
  } catch (err) {
    notif.show('Failed to submit feedback', 'error')
  }
}

// ---------------- Format Date ----------------
const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('en-PH', {
    timeZone: 'Asia/Manila',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  })
}

onMounted(() => getFeedback())
</script>

<style scoped>
.feedback-container {
  font-family: 'Inter', sans-serif;
}
button:focus {
  outline: none;
}
</style>
