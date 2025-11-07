<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import axios from "axios";
import { useLoadingStore } from '@/stores/loading';

const backend = import.meta.env.VITE_BACKEND_URL
const route = useRoute();
const router = useRouter();
const loading = useLoadingStore();

const orderDropdown = ref<boolean>(false);
const profileDropdown = ref<boolean>(false);
const showChangePassModal = ref<boolean>(false);

const adminEmail = ref<string>("");
const verificationCode = ref<string>("");
const codeVerified = ref<boolean>(false);

const newPassword = ref<string>("");
const confirmPassword = ref<string>("");

const sendCooldown = ref<number>(0);
let cooldownInterval: number | null = null;

// Navigation
const goTo = (path: string) => {
    orderDropdown.value = false;
    profileDropdown.value = false;
    router.push(path);
};

const isActive = (path: string): boolean => route.path === path;

const toggleOrderDropdown = (): void => {
    orderDropdown.value = !orderDropdown.value;
    profileDropdown.value = false;
};

const toggleProfileDropdown = (): void => {
    profileDropdown.value = !profileDropdown.value;
    orderDropdown.value = false;
};

// Fetch admin email from cookie
const fetchAdminEmail = async () => {
  try {
    const res = await axios.get(`${backend}/admin/me`, { withCredentials: true });
    adminEmail.value = res.data.email;
  } catch (err) {
    console.log("Not logged in or session expired");
    router.replace("/admin-login");
  } finally {
  }
};

// Logout function
const logout = async (): Promise<void> => {
  try {
    loading.show();
    await axios.post(`${backend}/admin/logout`, {}, { withCredentials: true });
    adminEmail.value = "";
    router.replace("/admin-login");
  } catch (err) {
    console.log("Logout failed", err);
    loading.hide();
  } finally {
    loading.hide();
  }
};

// Password verification & change
const sendVerification = async (): Promise<void> => {
  if (!adminEmail.value) {
    alert("Admin email missing");
    return;
  }

  if (sendCooldown.value > 0) {
    alert(`Please wait ${sendCooldown.value} seconds before resending.`);
    return;
  }

  try {
    loading.show();
    await axios.post(`${backend}/auth/send-code`, {
      email: adminEmail.value,
      role: "admin",
      purpose: "reset",
    });
    alert(`Verification code sent to ${adminEmail.value}`);

    // Start cooldown
    sendCooldown.value = 60; // 60 seconds
    cooldownInterval = window.setInterval(() => {
      if (sendCooldown.value > 0) {
        sendCooldown.value--;
      } else {
        if (cooldownInterval) clearInterval(cooldownInterval);
      }
    }, 1000);

  } catch (err: any) {
    alert(err.response?.data?.detail || "Failed to send verification code");
    loading.hide();
  } finally {
    loading.hide();
  }
};

const verifyCode = async (): Promise<void> => {
  if (!verificationCode.value) {
    alert("Enter the verification code");
    return;
  }

  try {
    loading.show();
    await axios.post(`${backend}/auth/verify-code`, {
      email: adminEmail.value,
      code: verificationCode.value,
      role: "admin"
    });
    codeVerified.value = true;
    alert("Code verified. You can now change your password.");
  } catch (err: any) {
    alert(err.response?.data?.detail || "Invalid verification code");
  } finally {
    loading.hide();
  }
};

const changePassword = async (): Promise<void> => {
  if (!newPassword.value || !confirmPassword.value) {
    alert("Fill both password fields");
    return;
  }
  if (newPassword.value !== confirmPassword.value) {
    alert("Passwords do not match");
    return;
  }

  try {
    loading.show();
    await axios.post(`${backend}/admin/change-password`, {
      new_password: newPassword.value,
    }, { withCredentials: true });
    alert("Password changed successfully!");
    showChangePassModal.value = false;
    codeVerified.value = false;
    verificationCode.value = "";
    newPassword.value = "";
    confirmPassword.value = "";
  } catch (err: any) {
    alert(err.response?.data?.detail || "Failed to change password");
  } finally {
    loading.hide();
  }
};

onMounted(() => {
  fetchAdminEmail();
});
</script>

<template>
<div class="relative h-screen w-full bg-white flex flex-col">
    <nav class="w-full h-[130px] flex flex-col border-b bg-gray-900 border-gray-700 shadow-[0_2px_5px_rgba(135,206,235,0.3)] z-30">
        <div class="flex flex-row justify-between items-center py-3 px-6">
            <div>
                <img src="@/assets/img/sdtc-logo.jpg" alt="logo" class="h-[50px] bg-gray-200 rounded-2xl" />
            </div>

            <!-- Profile icon with dropdown -->
            <div class="relative">
                <button @click="toggleProfileDropdown" class="hover:text-gray-600 transition">
                    <i class="fa-solid fa-circle-user text-3xl text-gray-200 cursor-pointer"></i>
                </button>

                <div v-if="profileDropdown" class="absolute right-0 mt-2 w-56 bg-gray-700 shadow-lg rounded-lg overflow-hidden z-50">
                    <div class="flex items-center gap-2 px-4 py-2 text-white text-sm truncate">
                        <i class="fa-solid fa-envelope text-blue-400"></i>
                        <span>{{ adminEmail }}</span>
                    </div>
                    <button @click="showChangePassModal = true; profileDropdown = false"
                        class="w-full text-left px-4 py-2 hover:bg-gray-900 text-white flex items-center gap-2">
                        <i class="fa-solid fa-key text-green-400"></i> Change Password
                    </button>
                    <button @click="logout" class="w-full text-left px-4 py-2 hover:bg-gray-900 text-red-600 flex items-center gap-2">
                        <i class="fa-solid fa-right-from-bracket text-red-500"></i> Logout
                    </button>
                </div>
            </div>
        </div>

        <!-- Nav buttons -->
        <div class="w-full h-[50px] flex items-center gap-5 shadow-sm px-6">
            <button class="px-4 py-1.5 text-sm font-medium rounded transition" :class="isActive('/admin/dashboard')
                ? 'bg-[#172554] text-white'
                : 'bg-[#1E3A8A] text-white hover:bg-[#172554]'"
                @click="goTo('/admin/dashboard')">
                Dashboard
            </button>
            <button class="px-4 py-1.5 text-sm font-medium rounded transition" :class="isActive('/admin/product-management')
                ? 'bg-[#172554] text-white'
                : 'bg-[#1E3A8A] text-white hover:bg-[#172554]'"
                @click="goTo('/admin/product-management')">
                Product Management
            </button>

            <div class="relative">
                <button class="px-4 py-1.5 text-sm font-medium rounded transition flex items-center gap-2" :class="route.path.startsWith('/admin/order-management')
                    ? 'bg-[#172554] text-white'
                    : 'bg-[#1E3A8A] text-white hover:bg-[#172554]'"
                    @click="toggleOrderDropdown">
                    Order Management <i class="fa-solid fa-caret-down"></i>
                </button>

                <div v-if="orderDropdown" class="absolute mt-1 left-0 bg-gray-700 shadow rounded w-48 py-2 z-50">
                    <button class="block w-full text-left px-4 py-2 text-sm hover:bg-gray-900" :class="isActive('/admin/order-management/approvals')
                        ? 'font-bold text-gray-400'
                        : 'text-white'"
                        @click="goTo('/admin/order-management/approvals')">
                        <i class="fa-solid fa-circle-check text-lg"></i> Approvals
                    </button>
                    <button class="block w-full text-left px-4 py-2 text-sm hover:bg-gray-900" :class="isActive('/admin/order-management/logs')
                        ? 'font-bold text-gray-400'
                        : 'text-white'"
                        @click="goTo('/admin/order-management/logs')">
                        <i class="fa-solid fa-clock-rotate-left text-lg"></i> Order Logs
                    </button>
                </div>
            </div>

            <button class="px-4 py-1.5 text-sm font-medium rounded transition" :class="isActive('/admin/user-management')
                ? 'bg-[#172554] text-white'
                : 'bg-[#1E3A8A] text-white hover:bg-[#172554]'"
                @click="goTo('/admin/user-management')">
                User Management
            </button>
                        <button class="px-4 py-1.5 text-sm font-medium rounded transition" :class="isActive('/admin/feedback')
                ? 'bg-[#172554] text-white'
                : 'bg-[#1E3A8A] text-white hover:bg-[#172554]'"
                @click="goTo('/admin/feedback')">
                Customer Feedback
            </button>
        </div>
    </nav>

    <!-- Change Password Modal -->
    <div v-if="showChangePassModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div class="bg-gray-800 p-6 rounded-lg w-96 text-gray-200">
            <h3 class="text-lg font-bold mb-4 flex items-center gap-2">
                <i class="fa-solid fa-key text-green-400"></i> Change Password
            </h3>

            <div v-if="!codeVerified">
                <div class="mb-3 flex items-center gap-2">
                    <i class="fa-solid fa-envelope text-blue-400"></i>
                    <input type="email" v-model="adminEmail" class="bg-gray-700 text-gray-200 border border-gray-600 rounded px-3 py-2 w-full" readonly />
                </div>
                <div class="mb-3 flex items-center gap-2">
                    <i class="fa-solid fa-shield-halved text-yellow-400"></i>
                    <input type="text" v-model="verificationCode" placeholder="Enter verification code" class="bg-gray-700 text-gray-200 border border-gray-600 rounded px-3 py-2 w-full" />
                </div>
                <div class="flex justify-end gap-2">
                    <button @click="sendVerification" class="bg-blue-600 px-3 py-1 rounded hover:bg-blue-700 text-white">Send Code <span v-if="sendCooldown>0">({{ sendCooldown }}s)</span></button>
                    <button @click="verifyCode" class="bg-green-600 px-3 py-1 rounded hover:bg-green-700 text-white">Verify</button>
                </div>
            </div>

            <div v-else>
                <div class="mb-3 flex items-center gap-2">
                    <i class="fa-solid fa-lock text-blue-400"></i>
                    <input type="password" v-model="newPassword" placeholder="New Password" class="bg-gray-700 text-gray-200 border border-gray-600 rounded px-3 py-2 w-full" />
                </div>
                <div class="mb-3 flex items-center gap-2">
                    <i class="fa-solid fa-lock text-blue-400"></i>
                    <input type="password" v-model="confirmPassword" placeholder="Re-enter Password" class="bg-gray-700 text-gray-200 border border-gray-600 rounded px-3 py-2 w-full" />
                </div>
            </div>

            <div class="flex justify-end gap-2 mt-4">
                <button @click="showChangePassModal=false; codeVerified=false" class="bg-gray-600 px-4 py-2 rounded hover:bg-gray-700">Cancel</button>
                <button v-if="codeVerified" @click="changePassword" class="bg-blue-600 px-4 py-2 rounded hover:bg-blue-700">Submit</button>
            </div>
        </div>
    </div>

    <div class="flex-1 overflow-auto p-6 bg-gray-900 text-gray-200">
        <router-view />
    </div>
</div>
</template>
