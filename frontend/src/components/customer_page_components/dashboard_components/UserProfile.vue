<script setup lang="ts">
import { ref, onMounted } from "vue";
import axios from "axios";
import defaultProfileImage from "@/assets/img/default_profile.png";
import { useNotifStore } from "@/stores/notif";

const notif = useNotifStore();
const backend = import.meta.env.VITE_BACKEND_URL;

interface UserAddress {
  id: number;
  house_number: string;
  street: string;
  barangay: string;
  city: string;
  province: string;
  is_active: boolean;
}

const showForm = ref(false);
const addresses = ref<UserAddress[]>([]);
const profileImage = ref(defaultProfileImage);
const email = ref("");
const fileInput = ref<HTMLInputElement | null>(null);

const newAddress = ref<Omit<UserAddress, "id" | "is_active">>({
  house_number: "",
  street: "",
  barangay: "",
  city: "",
  province: "",
});

// --- Delete modal state ---
const showConfirmModal = ref(false);
const selectedAddress = ref<UserAddress | null>(null);

// ---------------- Fetch user profile ----------------
onMounted(async () => {
  try {
    const res = await axios.get(`${backend}/users/profile`, {
      withCredentials: true,
    });
    email.value = res.data.email;
    if (res.data.profile_picture) profileImage.value = res.data.profile_picture;
    await fetchAddresses();
  } catch (err) {
    notif.show("Failed to fetch user profile", "error");
  }
});

// ---------------- Fetch addresses ----------------
const fetchAddresses = async () => {
  try {
    const res = await axios.get<UserAddress[]>(`${backend}/users/addresses`, {
      withCredentials: true,
    });
    addresses.value = res.data
      .map((addr) => ({
        ...addr,
        is_active: addr.is_active ?? false,
      }))
      .sort((a, b) => (b.is_active ? 1 : 0) - (a.is_active ? 1 : 0));
  } catch (err) {
    notif.show("Failed to fetch addresses", "error");
  }
};

// ---------------- Upload new profile image ----------------
const handleImageUpload = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = async (e) => {
    const base64Image = e.target?.result as string;
    profileImage.value = base64Image;

    try {
      const res = await axios.post(
        `${backend}/users/upload-profile-image`,
        { profile_image: base64Image },
        { withCredentials: true }
      );
      profileImage.value = res.data.image_url;
      notif.show("Profile image updated successfully!", "success");
    } catch (err) {
      notif.show("Failed to upload profile image", "error");
    }
  };
  reader.readAsDataURL(file);
};

const triggerFilePicker = () => fileInput.value?.click();

// ---------------- Address CRUD ----------------
const addAddress = async () => {
  if (
    !newAddress.value.house_number ||
    !newAddress.value.street ||
    !newAddress.value.barangay ||
    !newAddress.value.city ||
    !newAddress.value.province
  ) {
    notif.show("Please fill in all fields", "warning");
    return;
  }

  try {
    await axios.post(`${backend}/users/address/add`, newAddress.value, {
      withCredentials: true,
    });
    await fetchAddresses();
    showForm.value = false;
    newAddress.value = {
      house_number: "",
      street: "",
      barangay: "",
      city: "",
      province: "",
    };
    notif.show("Address added successfully!", "success");
  } catch (err) {
    notif.show("Failed to add address", "error");
  }
};

const activateAddress = async (id: number) => {
  try {
    await axios.put(
      `${backend}/users/address/${id}/activate`,
      { is_active: true },
      { withCredentials: true }
    );
    await fetchAddresses();
    notif.show("Address activated successfully!", "success");
  } catch (err) {
    notif.show("Failed to activate address", "error");
  }
};

// --- Delete Confirmation Modal ---
const confirmDelete = (address: UserAddress) => {
  selectedAddress.value = address;
  showConfirmModal.value = true;
};

const deleteAddress = async () => {
  if (!selectedAddress.value) return;
  try {
    await axios.delete(`${backend}/users/address/${selectedAddress.value.id}`, {
      withCredentials: true,
    });
    notif.show("Address deleted successfully!", "success");
    await fetchAddresses();
  } catch (err) {
    notif.show("Failed to delete address", "error");
  } finally {
    showConfirmModal.value = false;
    selectedAddress.value = null;
  }
};
</script>

<template>
  <div class="flex flex-col md:flex-row gap-8 sm:p-6 text-white min-h-screen">
    <!-- Left Section -->
    <div
      class="md:w-1/3 flex flex-col items-center bg-gray-900/80 p-6 rounded-2xl shadow-[0_0_20px_rgba(0,0,0,0.4)] border border-gray-700 backdrop-blur-md">
      <!-- Profile Image -->
      <div class="relative group">
        <img :src="profileImage" alt="Profile"
          class="w-32 h-32 rounded-full border-4 border-sky-500 object-cover shadow-lg cursor-pointer hover:scale-105 transition-transform duration-300"
          @click="triggerFilePicker" />
        <div @click="triggerFilePicker"
          class="absolute inset-0 bg-black/50 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition">
          <i class="fa-solid fa-camera text-white text-2xl"></i>
        </div>
        <input type="file" accept="image/*" class="hidden" ref="fileInput" @change="handleImageUpload" />
      </div>

      <p class="mt-4 text-lg font-semibold text-gray-200 text-center break-words">
        <i class="fa-solid fa-envelope mr-2 text-sky-400"></i>{{ email }}
      </p>

      <button
        class="mt-6 bg-gradient-to-r from-sky-600 to-sky-500 hover:from-sky-500 hover:to-sky-600 text-white font-medium px-6 py-2 rounded-xl transition-transform duration-200 hover:scale-105 active:scale-95 flex items-center gap-2 shadow-lg shadow-sky-900/40"
        @click="showForm = !showForm">
        <i :class="showForm ? 'fa-solid fa-xmark' : 'fa-solid fa-plus'"></i>
        {{ showForm ? "Cancel" : "Add Address" }}
      </button>

      <!-- Address Form -->
      <transition name="fade">
        <form v-if="showForm" @submit.prevent="addAddress"
          class="mt-6 w-full max-w-lg sm:max-w-2xl bg-gray-800/70 p-4 sm:p-6 rounded-2xl flex flex-col gap-4 border border-gray-700 shadow-inner mx-auto">
          <div class="space-y-3">
            <div v-for="(icon, field) in {
              house_number: 'fa-house',
              street: 'fa-road',
              barangay: 'fa-landmark',
              city: 'fa-city',
              province: 'fa-map-marker-alt'
            }" :key="field" class="flex flex-col sm:flex-row sm:items-center sm:gap-3 gap-1">
              <div class="flex items-center gap-2 sm:w-40">
                <i :class="`fa-solid ${icon} text-sky-400 text-sm sm:text-base`"></i>
                <label class="text-gray-300 capitalize text-sm sm:text-base" :for="field">
                  {{ field.replace('_', ' ') }}
                </label>
              </div>

              <input :id="field" v-model="newAddress[field]"
                :placeholder="field.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())" type="text"
                class="p-2 sm:p-3 rounded-lg bg-gray-900 text-white border border-gray-700 outline-none focus:ring-2 focus:ring-sky-500 w-full placeholder-gray-500 text-sm sm:text-base" />
            </div>
          </div>

          <button type="submit"
            class="mt-5 bg-sky-600 hover:bg-sky-700 px-4 sm:px-6 py-2 sm:py-3 rounded-xl font-semibold transition-transform duration-200 hover:scale-105 active:scale-95 flex items-center justify-center gap-2 shadow-md shadow-sky-900/40 text-sm sm:text-base">
            <i class="fa-solid fa-floppy-disk"></i>
            Save Address
          </button>
        </form>
      </transition>
    </div>

    <!-- Right Section -->
    <div
      class="flex-1 bg-gray-900/80 p-6 rounded-2xl shadow-[0_0_25px_rgba(0,0,0,0.4)] border border-gray-700 backdrop-blur-md overflow-y-auto">
      <h2 class="text-2xl font-bold mb-5 pb-3 border-b border-gray-700 flex items-center gap-2 text-sky-400">
        <i class="fa-solid fa-location-dot"></i> Delivery Addresses
      </h2>

      <div v-if="addresses.length === 0" class="text-gray-500 flex items-center gap-2">
        <i class="fa-solid fa-circle-exclamation text-yellow-400"></i> No addresses added yet.
      </div>

      <div class="flex flex-col gap-5">
        <div v-for="address in addresses" :key="address.id"
          class="p-5 rounded-2xl cursor-pointer transition-all duration-300 hover:-translate-y-1 hover:shadow-xl"
          :class="address.is_active
            ? 'bg-gradient-to-r from-green-700/80 to-green-600/60 border border-green-500/50'
            : 'bg-gray-800 border border-gray-700 hover:border-sky-600/50'" @click="activateAddress(address.id)">
          <div class="space-y-2 text-gray-200">
            <div class="flex items-start gap-2">
              <i class="fa-solid fa-house text-sky-400 w-5 text-center"></i>
              <span class="font-semibold w-28 sm:w-32">House No:</span>
              <span class="flex-1 break-words">{{ address.house_number }}</span>
            </div>

            <div class="flex items-start gap-2">
              <i class="fa-solid fa-road text-sky-400 w-5 text-center"></i>
              <span class="font-semibold w-28 sm:w-32">Street:</span>
              <span class="flex-1 break-words">{{ address.street }}</span>
            </div>

            <div class="flex items-start gap-2">
              <i class="fa-solid fa-landmark text-sky-400 w-5 text-center"></i>
              <span class="font-semibold w-28 sm:w-32">Barangay:</span>
              <span class="flex-1 break-words">{{ address.barangay }}</span>
            </div>

            <div class="flex items-start gap-2">
              <i class="fa-solid fa-city text-sky-400 w-5 text-center"></i>
              <span class="font-semibold w-28 sm:w-32">City:</span>
              <span class="flex-1 break-words">{{ address.city }}</span>
            </div>

            <div class="flex items-start gap-2">
              <i class="fa-solid fa-map-marker-alt text-sky-400 w-5 text-center"></i>
              <span class="font-semibold w-28 sm:w-32">Province:</span>
              <span class="flex-1 break-words">{{ address.province }}</span>
            </div>
          </div>

          <div class="flex justify-end gap-2 mt-4">
            <button @click.stop="activateAddress(address.id)" :disabled="address.is_active"
              class="px-4 py-1.5 rounded-lg text-sm font-medium transition-transform hover:scale-105 flex items-center gap-1 shadow-md"
              :class="address.is_active
                ? 'bg-gray-700 text-gray-400 cursor-not-allowed border border-gray-600'
                : 'bg-sky-600 hover:bg-sky-700 text-white border border-sky-500/50'">
              <i :class="address.is_active ? 'fa-solid fa-check' : 'fa-solid fa-toggle-on'"></i>
              {{ address.is_active ? "Active" : "Activate" }}
            </button>

            <button @click.stop="confirmDelete(address)"
              class="bg-red-600 hover:bg-red-700 text-white px-4 py-1.5 rounded-lg text-sm font-medium transition-transform hover:scale-105 active:scale-95 flex items-center gap-1 shadow-md border border-red-500/40">
              <i class="fa-solid fa-trash"></i> Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 🗑️ Delete Confirmation Modal -->
    <transition name="fade">
      <div v-if="showConfirmModal" class="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
        <div
          class="bg-gray-900/90 border border-gray-700 rounded-xl p-6 w-[400px] text-center shadow-2xl">
          <h3 class="text-lg font-semibold mb-4 text-cyan-300">
            <i class="fas fa-exclamation-triangle text-yellow-400 mr-2"></i>
            Confirm Delete
          </h3>
          <p class="text-gray-300 mb-6">
            Are you sure you want to delete this address?
            <br />
            <span class="font-semibold text-sky-400 block mt-2">
              {{ selectedAddress?.house_number }}, {{ selectedAddress?.street }},
              {{ selectedAddress?.barangay }}, {{ selectedAddress?.city }}
            </span>
          </p>
          <div class="flex justify-center gap-4">
            <button @click="showConfirmModal = false"
              class="bg-gray-600 hover:bg-gray-700 px-5 py-1.5 rounded-lg font-medium shadow">
              Cancel
            </button>
            <button @click="deleteAddress"
              class="bg-red-600 hover:bg-red-700 px-5 py-1.5 rounded-lg font-medium shadow">
              Delete
            </button>
          </div>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
