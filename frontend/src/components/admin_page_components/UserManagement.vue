<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import axios from "axios";
import { useLoadingStore } from "@/stores/loading";

const loading = useLoadingStore();
const backend = import.meta.env.VITE_BACKEND_URL
interface User {
  id: number;
  email: string;
  deliveryLocation: string;
  status: "Active" | "Banned";
}

const users = ref<User[]>([]);
const searchQuery = ref<string>("");

// Fetch all users from backend
const fetchUsers = async () => {
  try {
    const { data } = await axios.get(`${backend}/admin/users`, {
      withCredentials: true,
    });
    users.value = data.users.map((u: any) => ({
      id: u.id,
      email: u.email,
      deliveryLocation: u.deliveryLocation || "",
      status: u.status === "Banned" ? "Banned" : "Active",
    }));
  } catch (err) {
    console.error("Failed to fetch users:", err);
  }
};

// Filter users by ID or Email
const filteredUsers = computed<User[]>(() => {
  if (!searchQuery.value) return users.value;
  return users.value.filter(
    (user) =>
      user.id.toString().includes(searchQuery.value) ||
      user.email.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
});

// Toggle user status via backend
const toggleBan = async (user: User) => {
  try {
    loading.show();
    await axios.post(
      `${backend}/admin/users/${user.id}/ban`,
      {},
      { withCredentials: true }
    );
    await fetchUsers();
  } catch (err) {
    console.error("Failed to toggle ban:", err);
  } finally {
    loading.hide();
  }
};

onMounted(fetchUsers);
</script>

<template>
  <div class="p-8 bg-gradient-to-b from-gray-900 to-gray-800 min-h-screen text-white">
    <!-- Header -->
    <div class="flex justify-between items-center mb-8">
      <h2
        class="text-3xl font-bold bg-gradient-to-r from-sky-400 to-blue-500 bg-clip-text text-transparent"
      >
        👥 User Management
      </h2>

      <!-- Search Bar -->
      <div class="relative w-64">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search by ID or Email..."
          class="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-gray-200 focus:outline-none focus:ring-2 focus:ring-sky-500 placeholder-gray-500"
        />
        <i
          class="fas fa-search absolute right-3 top-1/2 -translate-y-1/2 text-gray-400"
        ></i>
      </div>
    </div>

    <!-- Table Container -->
    <div
      class="overflow-x-auto rounded-lg shadow-lg bg-gray-900/70 backdrop-blur-md border border-gray-700"
    >
      <table class="w-full text-sm text-gray-200">
        <thead class="bg-gray-800/80 text-cyan-400 uppercase text-xs">
          <tr>
            <th class="px-4 py-3 text-center">User ID</th>
            <th class="px-4 py-3 text-center">Email</th>
            <th class="px-4 py-3 text-center">Delivery Location</th>
            <th class="px-4 py-3 text-center">Status</th>
            <th class="px-4 py-3 text-center">Actions</th>
          </tr>
        </thead>

        <tbody>
          <tr
            v-for="user in filteredUsers"
            :key="user.id"
            class="hover:bg-gray-800/60 transition-colors"
          >
            <td class="border-t border-gray-700 py-3 text-center font-medium">
              {{ user.id }}
            </td>
            <td class="border-t border-gray-700 py-3 text-center">
              {{ user.email }}
            </td>
            <td class="border-t border-gray-700 py-3 text-center">
              {{ user.deliveryLocation }}
            </td>
            <td
              class="border-t border-gray-700 py-3 text-center font-semibold"
              :class="user.status === 'Active' ? 'text-green-400' : 'text-red-400'"
            >
              {{ user.status }}
            </td>
            <td class="border-t border-gray-700 py-3 text-center">
              <button
                @click="toggleBan(user)"
                :class="user.status === 'Active'
                  ? 'bg-red-600 hover:bg-red-700'
                  : 'bg-green-600 hover:bg-green-700'"
                class="text-white px-4 py-1.5 rounded-lg shadow-md flex items-center justify-center gap-2 mx-auto transition-all duration-200"
              >
                <i
                  :class="user.status === 'Active' ? 'fa-solid fa-user-slash' : 'fa-solid fa-user-check'"
                ></i>
                {{ user.status === 'Active' ? 'Ban' : 'Unban' }}
              </button>
            </td>
          </tr>

          <tr v-if="filteredUsers.length === 0">
            <td colspan="5" class="text-center py-6 text-gray-400 italic">
              No users found.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
