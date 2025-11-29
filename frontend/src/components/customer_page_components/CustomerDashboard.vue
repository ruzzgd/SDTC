<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from "vue";
import axios from "axios";
import { useRouter } from "vue-router";
import OrderModal from "@/components/modal/OrderModal.vue";
import { useOrderStore } from "@/stores/order";

const order = useOrderStore();
const router = useRouter();
const backend = import.meta.env.VITE_BACKEND_URL;

const sidebarOpen = ref(false);
const showProfileDropdown = ref(false);
const user = ref<{ email?: string; name?: string }>({});

// Toggle dropdown visibility
const toggleProfileDropdown = () => {
  showProfileDropdown.value = !showProfileDropdown.value;
};

// Close dropdown when clicking outside
const handleClickOutside = (e: MouseEvent) => {
  const target = e.target as HTMLElement;
  if (!target.closest(".profile-area")) showProfileDropdown.value = false;
};

onMounted(() => {
  document.addEventListener("click", handleClickOutside);
  fetchUser();
});

onBeforeUnmount(() => {
  document.removeEventListener("click", handleClickOutside);
});

const handleLogout = async () => {
  try {
    await axios.post(`${backend}/users/logout`, {}, { withCredentials: true });
  } catch {
    // ignore errors on logout
  }
  router.replace("/login");
};

const fetchUser = async () => {
  try {
    const res = await axios.get(`${backend}/users/profile`, { withCredentials: true });
    user.value = res.data;
  } catch {
    user.value = { name: "Unknown User", email: "Not Available" };
    router.replace("/login");
  }
};
</script>

<template>
  <div class="h-screen w-screen flex flex-col text-gray-900">
    <OrderModal v-if="order.showModal" />

    <!-- Sidebar -->
    <aside
      class="fixed top-0 left-0 h-full w-64 bg-gray-100 text-gray-900 transform transition-transform duration-300 z-50"
      :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full'">
      <!-- Sidebar Header -->
      <header class="h-[70px] flex items-center justify-between px-4 border-b border-gray-700">
        <img src="@/assets/img/sdtc-logo.jpg" class="h-[45px] rounded-2xl" alt="logo" />
        <i @click="sidebarOpen = false"
          class="fa-solid fa-arrow-left text-xl cursor-pointer hover:text-sky-400 transition"></i>
      </header>

      <!-- Sidebar Menu -->
      <nav class="p-4 flex flex-col gap-2">
        <button @click="$router.push('/dashboard/home')"
          class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-sky-700/40 transition">
          <i class="fa-solid fa-house"></i> Home
        </button>
        <button @click="$router.push('/dashboard/add-to-cart')"
          class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-sky-700/40 transition">
          <i class="fa-solid fa-cart-shopping"></i> Add to Cart
        </button>
        <button @click="$router.push('/dashboard/place-order')"
          class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-sky-700/40 transition">
          <i class="fa-solid fa-box-open"></i> Place Order
        </button>
        <button @click="$router.push('/dashboard/order-logs')"
          class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-sky-700/40 transition">
          <i class="fa-solid fa-clock-rotate-left"></i> Order logs
        </button>
        <button @click="$router.push('/dashboard/feedback')"
          class="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-sky-700/40 transition">
          <i class="fa-solid fa-comment-dots"></i> Service Feedback
        </button>
      </nav>
    </aside>

    <!-- Overlay -->
    <div v-if="sidebarOpen" class="fixed inset-0 bg-black/40 backdrop-blur-sm z-40" @click="sidebarOpen = false"></div>

    <!-- Navbar -->
    <nav
      class="w-full h-[80px] flex items-center justify-between px-6 bg-gray-100 border-b border-gray-300 shadow-[0_2px_5px_rgba(135,206,235,0.3)] z-30">
      <!-- Left Section -->
      <div class="flex items-center gap-4">
        <i class="fa-solid fa-bars text-2xl text-gray-900 cursor-pointer hover:text-sky-400 transition"
          @click="sidebarOpen = true"></i>
        <img src="@/assets/img/sdtc-logo.jpg" @click="$router.push('/dashboard/home')"
          class="h-[45px] rounded-2xl cursor-pointer hover:opacity-80 transition" alt="logo" />
      </div>

      <!-- Right Section (Profile) -->
      <div class="relative profile-area flex items-center gap-3">
        <div class="text-right hidden sm:block">
          <p class="font-semibold text-sm text-sky-400">{{ user.name || 'User' }}</p>
          <p class="text-xs text-gray-600 truncate w-40">{{ user.email || 'No email' }}</p>
        </div>

        <i class="fa-solid fa-circle-user text-3xl cursor-pointer text-gray-900 hover:text-sky-400 transition"
          @click="toggleProfileDropdown"></i>

        <!-- Dropdown -->
        <transition name="fade">
          <div v-if="showProfileDropdown"
            class="absolute right-0 top-[60px] w-48 bg-gray-800 text-white rounded-lg shadow-xl border border-gray-700 z-50 overflow-hidden">
            <button @click="$router.push('/dashboard/user-profile'); showProfileDropdown = false"
              class="w-full text-left px-4 py-2 hover:bg-gray-700 transition text-sm flex items-center gap-2">
              <i class="fa-solid fa-user"></i> View Profile
            </button>
            <button @click="handleLogout"
              class="w-full text-left px-4 py-2 hover:bg-red-700 transition text-sm flex items-center gap-2 text-red-400">
              <i class="fa-solid fa-right-from-bracket"></i> Logout
            </button>
          </div>
        </transition>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="flex-1 overflow-y-auto p-6 bg-gradient-to-br from-gray-100 via-gray-200 to-gray-300 text-gray-900 custom-scrollbar">
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
