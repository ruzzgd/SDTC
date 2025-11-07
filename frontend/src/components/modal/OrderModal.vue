<script setup lang="ts">
import { ref, computed } from "vue"
import axios from "axios"
import { useOrderStore } from "@/stores/order"
import { useLoadingStore } from "@/stores/loading"
import { useNotifStore } from "@/stores/notif"

const loading = useLoadingStore()
const notif = useNotifStore()
const orderStore = useOrderStore()

const quantity = ref(1)
const backend = import.meta.env.VITE_BACKEND_URL

const maxStock = computed(() => orderStore.selectedItem?.tile_stock ?? 1)

const increaseQuantity = () => {
  if (quantity.value < maxStock.value) quantity.value++
}
const decreaseQuantity = () => {
  if (quantity.value > 1) quantity.value--
}

// ---------------- ADD TO CART ----------------
const addToCart = async () => {
  if (!orderStore.selectedItem) return

  try {
    loading.show()

    await axios.post(
      `${backend}/cart/add`,
      {
        product_id: orderStore.selectedItem.id,
        quantity: quantity.value
      },
      { withCredentials: true }
    )

    loading.hide()
    notif.show(`${orderStore.selectedItem.tile_name} added to cart!`, 'success')
  } catch (error: any) {
    loading.hide()
    notif.show('Failed to add item to cart.', 'error')
  }
}

// ---------------- PLACE ORDER ----------------
const placeOrder = async () => {
  if (!orderStore.selectedItem) return

  try {
    loading.show()

    await axios.post(
      `${backend}/orders/add-order`,
      {
        product_id: orderStore.selectedItem.id,
        quantity: quantity.value
      },
      { withCredentials: true }
    )

    loading.hide()
    notif.show('Order placed successfully!', 'success')
    orderStore.closeModal()
  } catch (error: any) {
    loading.hide()
    notif.show('Failed to place order. Please try again.', 'error')
  }
}
</script>


<template>
    <div v-if="orderStore.showModal" class="absolute inset-0 z-50 bg-black/60 flex items-center justify-center p-4">
        <div
            class="bg-gray-800 w-full max-w-4xl rounded-2xl shadow-lg overflow-hidden flex flex-col md:flex-row h-full sm:max-h-[400px] relative max-h-[540px]">

            <!-- Left: Image -->
            <div class="md:w-1/2 flex items-center justify-center bg-gray-900 p-4">
                <img :src="orderStore.selectedItem?.tile_image" alt=""
                    class="rounded-xl object-cover w-full h-full shadow-lg" />
            </div>

            <!-- Right: Details -->
            <div class="md:w-1/2 p-6 flex flex-col justify-between overflow-y-scroll custom-scrollbar">
                <div class="space-y-2">
                    <h2 class="text-2xl font-bold mb-2 flex items-center gap-2 text-white">
                        <i class="fa-solid fa-box-open text-sky-500"></i>
                        {{ orderStore.selectedItem?.tile_name }}
                    </h2>

                    <p class="text-gray-400 flex items-center gap-2">
                        <i class="fa-solid fa-tags text-gray-300"></i>
                        Category: {{ orderStore.selectedItem?.tile_category }}
                    </p>

                    <p class="text-gray-400 flex items-center gap-2">
                        <i class="fa-solid fa-layer-group text-gray-300"></i>
                        Type: {{ orderStore.selectedItem?.tile_type }}
                    </p>

                    <p class="text-gray-300 flex items-start gap-2">
                        <i class="fa-solid fa-align-left text-gray-400 mt-1"></i>
                        {{ orderStore.selectedItem?.tile_description }}
                    </p>

                    <p class="text-green-400 font-bold text-lg flex items-center gap-2">
                        <i class="fa-solid fa-money-bill-wave text-green-400"></i>
                        ₱{{ orderStore.selectedItem?.tile_price }}
                    </p>

                    <p class="text-gray-400 flex items-center gap-2">
                        <i class="fa-solid fa-boxes-stacked text-gray-300"></i>
                        Stock: {{ orderStore.selectedItem?.tile_stock }}
                    </p>
                </div>

                <!-- Bottom: Quantity + Buttons -->
                <div class="mt-4 flex flex-col gap-4">
                    <!-- Quantity -->
                    <div class="flex items-center gap-3">
                        <button @click="decreaseQuantity"
                            class="bg-gray-600 hover:bg-gray-700 text-white w-10 h-10 flex items-center justify-center rounded-lg text-xl font-bold">
                            -
                        </button>
                        <input type="number" v-model.number="quantity" :max="maxStock" :min="1" @input="() => {
                            if (quantity > maxStock) quantity = maxStock;
                            if (quantity < 1) quantity = 1;
                        }" class="w-16 text-center rounded-lg bg-gray-700 text-white outline-none text-lg py-1" />
                        <button @click="increaseQuantity"
                            class="bg-gray-600 hover:bg-gray-700 text-white w-10 h-10 flex items-center justify-center rounded-lg text-xl font-bold">
                            +
                        </button>
                        <span class="text-gray-400 ml-2">Max: {{ maxStock }}</span>
                    </div>

                    <!-- Buttons -->
                    <div class="flex gap-3">
                        <button @click="addToCart"
                            class="flex-1 bg-sky-600 hover:bg-sky-700 text-white font-semibold py-3 rounded-xl transition hover:scale-105 flex items-center justify-center gap-2">
                            <i class="fa-solid fa-cart-plus"></i> Add to Cart
                        </button>
                        <button @click="placeOrder"
                            class="flex-1 bg-green-600 hover:bg-green-700 text-white font-semibold py-3 rounded-xl transition hover:scale-105 flex items-center justify-center gap-2">
                            <i class="fa-solid fa-credit-card"></i> Order Now
                        </button>
                    </div>
                </div>
            </div>

            <!-- Close button -->
            <button @click="orderStore.closeModal()"
                class="absolute top-0 right-0 text-gray-300 hover:text-white text-2xl m-5">
                <i class="fa-solid fa-xmark"></i>
            </button>
        </div>
    </div>
</template>
