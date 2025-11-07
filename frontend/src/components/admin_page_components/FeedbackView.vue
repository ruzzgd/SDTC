<template>
    <div
        class="summary-card mb-6 p-6 rounded-xl shadow-lg bg-gradient-to-r from-gray-800 to-gray-900 text-white flex flex-col items-center">
        <h2 class="text-2xl font-bold mb-2">Customer Feedback</h2>
        <p class="text-gray-400 mb-2">Total Feedbacks: <span class="font-semibold">{{ feedbackList.length }}</span></p>
        <div class="flex items-center">
            <div class="flex text-yellow-400 text-3xl">
                <span v-for="i in 5" :key="i">
                    {{ i <= Math.round(avgRating) ? '★' : '☆' }} </span>
            </div>
            <span class="ml-2 text-gray-400 text-lg">{{ avgRating.toFixed(1) }}</span>
        </div>
    </div>

    <div v-if="feedbackList.length">
        <h3 class="text-xl font-bold mb-3 text-gray-200">All Feedback</h3>
        <ul class="space-y-4">
            <li v-for="item in feedbackList" :key="item.id"
                class="p-4 bg-gray-800 rounded-xl shadow hover:shadow-lg transition-shadow flex justify-between items-start">
                <div class="flex-1">
                    <p class="font-semibold text-gray-100">{{ item.email }}</p>
                    <p class="text-sm text-gray-400">{{ formatDate(item.created_at) }}</p>
                    <p class="mt-2 text-gray-200">{{ item.description }}</p>
                </div>
                <div class="flex flex-col justify-start ml-4">
                    <div class="flex text-yellow-400 text-xl">
                        <span v-for="i in 5" :key="i">{{ i <= item.rating ? '★' : '☆' }}</span>
                    </div>
                </div>
            </li>
        </ul>
    </div>
</template>

<script setup>
import { reactive, ref, onMounted, computed } from 'vue'
import axios from 'axios'

const backend = import.meta.env.VITE_BACKEND_URL
const form = reactive({
    description: '',
    rating: 0
})

const successMessage = ref('')
const errorMessage = ref('')
const feedbackList = ref([])

// Compute average rating
const avgRating = computed(() => {
    if (feedbackList.value.length === 0) return 0
    const total = feedbackList.value.reduce((sum, f) => sum + f.rating, 0)
    return total / feedbackList.value.length
})

// Fetch all feedback
const getFeedback = async () => {
    try {
        const { data } = await axios.get(`${backend}/users/feedback`, { withCredentials: true })
        feedbackList.value = data
    } catch (err) {
        console.error(err)
    }
}

// Format datetime in Philippine Time
const formatDate = (dateString) => {
    const date = new Date(dateString)
    return date.toLocaleString("en-PH", {
        timeZone: "Asia/Manila",
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hour12: false
    })
}

onMounted(() => getFeedback())
</script>
