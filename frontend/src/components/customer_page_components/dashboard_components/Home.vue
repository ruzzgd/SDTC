<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import axios from "axios"; 
import { useOrderStore } from "@/stores/order";

const orderStore = useOrderStore();
const backend = import.meta.env.VITE_BACKEND_URL;

interface Item {
  id: number;
  tile_category: string;
  tile_type: string;
  tile_name: string;
  tile_image: string;
  tile_description: string;
  tile_price: number;
  tile_stock: number;
  tile_sold?: number; // ✅ Added sold field
}

const items = ref<Item[]>([]);
const search = ref("");
const selectedCategory = ref("Tiles");
const selectedType = ref("");

const types = ["Floor", "Wall", "Ceiling", "Paving", "Pool"];

// ✅ Fetch products
const fetchProducts = async () => {
  try {
    const res = await axios.get(`${backend}/product`);
    const products = res.data;

    // Add tile_sold = 0 initially
    items.value = products.map((item: Item) => ({
      ...item,
      tile_sold: 0,
    }));

    // After fetching products, fetch sold count for each
    for (const item of items.value) {
      try {
        const soldRes = await axios.get(`${backend}/product/sold/${item.id}`);
        item.tile_sold = soldRes.data.total_sold || 0;
      } catch (soldErr) {
        console.warn(`Failed to fetch sold count for product ${item.id}`);
        item.tile_sold = 0;
      }
    }
  } catch (err) {
    console.warn("Backend not running — using temporary data for preview.");
    items.value = [
      {
        id: 1,
        tile_category: "Tiles",
        tile_type: "Floor",
        tile_name: "Marble White",
        tile_image: "https://via.placeholder.com/400x300",
        tile_description: "Elegant white marble for floors.",
        tile_price: 950,
        tile_stock: 120,
        tile_sold: 20,
      },
    ];
  }
};

// ✅ Filtered items
const filteredItems = computed(() => {
  return items.value.filter((item) => {
    const matchCategory =
      !selectedCategory.value ||
      item.tile_category.toLowerCase() === selectedCategory.value.toLowerCase();

    const matchType =
      !selectedType.value ||
      item.tile_type.toLowerCase() === selectedType.value.toLowerCase();

    const matchSearch =
      !search.value ||
      item.tile_name.toLowerCase().includes(search.value.toLowerCase());

    return matchCategory && matchType && matchSearch;
  });
});

onMounted(fetchProducts);
</script>

<template>
  <div class="w-full flex flex-col items-center gap-12 text-white pb-16">
    <!-- Hero Section -->
    <section class="text-center mt-12">
      <h1
        class="text-5xl md:text-6xl font-extrabold bg-gradient-to-r from-sky-400 via-blue-500 to-indigo-500 bg-clip-text text-transparent drop-shadow-lg animate-pulse">
        Welcome to SDTC Tiles 🏡
      </h1>
      <p class="text-gray-300 mt-4 text-lg max-w-2xl mx-auto leading-relaxed">
        Discover stunning tiles to elevate your space — from sleek modern styles
        to timeless classics. Explore, customize, and order effortlessly.
      </p>
    </section>

    <!-- Filters Section -->
    <div class="flex flex-col items-center gap-6 w-full max-w-5xl px-4 mt-4">
      <!-- Search Bar -->
      <div
        class="flex items-center gap-3 bg-gray-900/60 border border-gray-700 p-3 rounded-2xl w-full max-w-md shadow-lg focus-within:ring-2 focus-within:ring-sky-500 transition">
        <i class="fa-solid fa-magnifying-glass text-gray-400 text-xl"></i>
        <input
          type="text"
          placeholder="Search tiles..."
          v-model="search"
          class="bg-transparent outline-none w-full text-white placeholder-gray-400"
        />
      </div>

      <!-- Category Toggle -->
      <div class="flex gap-4">
        <button
          @click="selectedCategory = 'Tiles'; selectedType = ''"
          :class="selectedCategory === 'Tiles'
            ? 'bg-sky-600 text-white shadow-lg scale-105'
            : 'bg-gray-800 text-gray-300 hover:bg-gray-700'"
          class="px-5 py-2 rounded-xl font-semibold transition-all transform hover:scale-105">
          Tiles
        </button>
        <button
          @click="selectedCategory = 'Others'; selectedType = ''"
          :class="selectedCategory === 'Others'
            ? 'bg-green-600 text-white shadow-lg scale-105'
            : 'bg-gray-800 text-gray-300 hover:bg-gray-700'"
          class="px-5 py-2 rounded-xl font-semibold transition-all transform hover:scale-105">
          Others
        </button>
      </div>

      <!-- Type Buttons -->
      <div v-if="selectedCategory === 'Tiles'" class="flex flex-wrap gap-3 mt-3 justify-center">
        <button
          v-for="type in types"
          :key="type"
          @click="selectedType = selectedType === type ? '' : type"
          :class="selectedType === type
            ? 'bg-blue-500 text-white shadow-lg scale-105'
            : 'bg-gray-800 text-gray-300 hover:bg-gray-700'"
          class="px-4 py-2 rounded-xl font-semibold transition-all transform hover:scale-105">
          {{ type }}
        </button>
      </div>
    </div>

    <!-- Product Grid -->
    <div
      class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8 w-full max-w-7xl px-4 mt-8">
      <div
        v-for="item in filteredItems"
        :key="item.id"
        class="relative group bg-gray-900/70 border border-gray-800 backdrop-blur-md p-5 rounded-2xl shadow-lg hover:shadow-[0_0_25px_rgba(56,189,248,0.25)] hover:-translate-y-2 transition-all duration-300 flex flex-col overflow-hidden">
        
        <!-- Tile Image -->
        <div class="relative overflow-hidden rounded-xl mb-4">
          <img
            :src="item.tile_image"
            alt="tile image"
            class="w-full h-52 object-cover rounded-xl transition-transform duration-500 group-hover:scale-110" />
          
          <!-- Stock + Sold Badge -->
          <div
            class="absolute top-3 left-3 bg-sky-600/80 text-white text-xs font-semibold px-3 py-1 rounded-full backdrop-blur-md flex items-center gap-3">
            <span>In Stock: {{ item.tile_stock }}</span>
            <span class="bg-gray-800/70 px-2 py-0.5 rounded-full text-[11px] text-gray-300">
              Sold: {{ item.tile_sold }}
            </span>
          </div>
        </div>

        <!-- Tile Info -->
        <h3 class="font-semibold text-lg text-sky-400 group-hover:text-sky-300 transition-colors">
          {{ item.tile_name }}
        </h3>
        <p class="text-sm text-gray-400 mb-2">
          {{ item.tile_category }} • {{ item.tile_type }}
        </p>
        <p class="text-gray-300 text-sm line-clamp-2 mb-3">
          {{ item.tile_description || "No description available." }}
        </p>

        <!-- Price & Order Button -->
        <div class="flex items-center justify-between mt-auto border-t border-gray-700 pt-3">
          <p class="text-green-400 font-bold text-lg">
            ₱{{ item.tile_price.toLocaleString() }}
          </p>
          <button
            @click="orderStore.openModal(item)"
            class="bg-gradient-to-r from-sky-600 to-blue-600 hover:from-sky-500 hover:to-blue-500 text-white font-semibold px-4 py-2 rounded-xl flex items-center gap-2 transition-transform duration-200 hover:scale-105 active:scale-95">
            <i class="fa-solid fa-cart-shopping"></i>
            Order
          </button>
        </div>

        <!-- Glow Border -->
        <div
          class="absolute inset-0 rounded-2xl border-2 border-transparent group-hover:border-sky-500/40 transition-all duration-500 pointer-events-none"></div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-if="filteredItems.length === 0" class="text-gray-400 text-center mt-10">
      <i class="fa-solid fa-box-open text-4xl mb-3"></i>
      <p>No products found. Try adjusting your filters or search.</p>
    </div>
  </div>
</template>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
