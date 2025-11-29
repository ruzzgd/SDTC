<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import { useNotifStore } from '@/stores/notif'

const backend = import.meta.env.VITE_BACKEND_URL
const notif = useNotifStore() // ✅ use notification store

// Backend expects product_id and quantity
interface CartItem {
  cartId: number
  product_id: number
  tile_name: string
  tile_image: string
  tile_category: string
  tile_type: string
  tile_price: number
  tile_stock: number
  quantity: number
}

const cartItems = ref<CartItem[]>([])
const selectedCartItems = ref<number[]>([])
const selectAllCart = ref(false)

// Fetch cart
const fetchCart = async () => {
  try {
    const res = await axios.get(`${backend}/cart`, { withCredentials: true })
    cartItems.value = res.data.map((c: any) => ({
      cartId: c.id,
      product_id: c.product_id,
      tile_name: c.tile_name,
      tile_image: c.tile_image || '',
      tile_category: c.tile_category || '',
      tile_type: c.tile_type || '',
      tile_price: c.tile_price,
      tile_stock: c.tile_stock,
      quantity: 1
    }))

    // Auto-sync quantity updates
    cartItems.value.forEach(item => {
      watch(
        () => item.quantity,
        (newQty, oldQty) => {
          if (newQty !== oldQty && newQty > 0 && newQty <= item.tile_stock) {
            updateCartBackend(item)
          }
        }
      )
    })
  } catch (err) {
    console.error('Error fetching cart:', err)
    notif.show('Failed to fetch cart items.', 'error')
  }
}

// Update backend cart quantity
const updateCartBackend = async (item: CartItem) => {
  try {
    await axios.post(
      `${backend}/cart/add`,
      { product_id: item.product_id, quantity: item.quantity },
      { withCredentials: true }
    )
  } catch (err) {
    console.error('Error updating cart:', err)
    notif.show('Failed to update cart.', 'error')
  }
}

// Place order for a single item
const placeOrder = async (item: CartItem, index: number) => {
  try {
    await axios.post(
      `${backend}/orders/add-order`,
      { product_id: item.product_id, quantity: item.quantity },
      { withCredentials: true }
    )

    // Delete from cart
    await axios.delete(`${backend}/cart/delete/${item.product_id}`, { withCredentials: true })
    cartItems.value.splice(index, 1)
    selectedCartItems.value = selectedCartItems.value.filter(id => id !== item.product_id)

    // ✅ Show success notification
    notif.show(`Order placed for ${item.tile_name} ×${item.quantity}!`, 'success')
  } catch (err: any) {
    console.error('Error placing order:', err)
    let message = 'Failed to place order.'
    if (err.response?.data?.detail) message = err.response.data.detail
    else if (err.message) message = err.message

    // ❌ Show error notification
    notif.show(message, 'error')
  }
}

// Place order for multiple selected items
const placeBulkOrder = async () => {
  const selected = cartItems.value.filter(item =>
    selectedCartItems.value.includes(item.product_id)
  )

  if (selected.length === 0) {
    notif.show('No items selected for checkout.', 'warning')
    return
  }

  for (const item of selected) {
    const index = cartItems.value.findIndex(c => c.product_id === item.product_id)
    await placeOrder(item, index)
  }

  selectAllCart.value = false
  notif.show('All selected orders placed successfully!', 'success')
}

// Remove item from cart
const removeItem = async (index: number) => {
  const item = cartItems.value[index]
  if (!item) return

  try {
    await axios.delete(`${backend}/cart/delete/${item.product_id}`, { withCredentials: true })
    cartItems.value.splice(index, 1)
    selectedCartItems.value = selectedCartItems.value.filter(id => id !== item.product_id)

    notif.show(`${item.tile_name} removed from cart.`, 'info')
  } catch (err) {
    console.error('Error removing item:', err)
    notif.show('Failed to remove item from cart.', 'error')
  }
}

// Compute total
const totalPrice = computed(() =>
  cartItems.value.reduce((sum, item) => sum + item.tile_price * item.quantity, 0)
)

// Select all checkbox
watch(selectAllCart, val => {
  selectedCartItems.value = val
    ? cartItems.value.map(item => item.product_id)
    : []
})

onMounted(fetchCart)
</script>

<template>
  <div class="w-full max-w-4xl mx-auto p-4">
    <h1 class="text-3xl font-bold mb-6 text-gray-900 flex items-center gap-3">
      <i class="fa-solid fa-cart-shopping text-yellow-400"></i>
      Your Cart
    </h1>

    <div v-if="cartItems.length === 0" class="text-gray-600 text-center py-10">
      Your cart is empty.
    </div>

    <!-- Select All & Bulk Order -->
    <div v-if="cartItems.length > 0" class="flex items-center justify-between mb-4">
      <label class="flex items-center gap-2 text-gray-600 cursor-pointer">
        <input type="checkbox" v-model="selectAllCart" class="w-5 h-5 accent-blue-500">
        Select All
      </label>

      <button @click="placeBulkOrder" :disabled="selectedCartItems.length === 0"
        class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2">
        <i class="fa-solid fa-credit-card"></i> Place Order Selected
      </button>
    </div>

    <!-- Cart Items -->
    <div v-for="(item, index) in cartItems" :key="item.cartId"
      class="bg-gray-300 rounded-xl shadow-lg overflow-hidden mb-5 hover:shadow-2xl transition-shadow duration-300 flex flex-col md:flex-row"
      style="min-height: 140px;">

      <!-- Image -->
      <div class=" relative md:w-1/4 h-40 md:h-auto overflow-hidden">
        <!-- Selection Checkbox -->
        <div class=" absolute m-2">
          <input type="checkbox" v-model="selectedCartItems" :value="item.product_id" class="w-4 h-4 accent-blue-500">
        </div>
        <img :src="item.tile_image" class="w-full h-full object-cover" alt="Tile Image" />
      </div>

      <!-- Info -->
      <div class="flex-1 p-4 flex flex-col justify-between">
        <div>
          <h2 class="font-semibold text-gray-600 mb-2 sm:text-xl">{{ item.tile_name }}</h2>
          <p class="text-gray-900 text-sm mb-1">
            <i class="fa-solid fa-layer-group mr-1"></i>
            {{ item.tile_category }} - {{ item.tile_type }}
          </p>
          <p class="text-gray-900 text-sm mb-1">
            <i class="fa-solid fa-boxes-stacked mr-1"></i> Stock:
            <span :class="item.tile_stock > 0 ? 'text-green-400 font-semibold' : 'text-red-500 font-semibold'">
              {{ item.tile_stock > 0 ? item.tile_stock : 'Out of Stock' }}
            </span>
          </p>

          <!-- Quantity & Price -->
          <div class="flex gap-4 text-gray-600 text-sm mt-2 flex-wrap items-center">
            <div class="flex items-center gap-2">
              <label class="text-gray-600">Qty:</label>
              <div class="flex items-center bg-gray-700 rounded-lg overflow-hidden border border-gray-600">
                <button @click="item.quantity = Math.max(1, item.quantity - 1)"
                  class="px-3 py-1 hover:bg-gray-600 text-gray-600 text-lg" :disabled="item.quantity <= 1">
                  <i class="fa-solid fa-minus"></i>
                </button>
                <input type="number" v-model.number="item.quantity" min="1" :max="item.tile_stock" @input="() => {
                  if (item.quantity > item.tile_stock) item.quantity = item.tile_stock;
                  if (item.quantity < 1) item.quantity = 1;
                }" class="w-16 text-center bg-gray-800 text-white outline-none border-x border-gray-600" />
                <button @click="item.quantity = Math.min(item.tile_stock, item.quantity + 1)"
                  class="px-3 py-1 hover:bg-gray-600 text-gray-300 text-lg"
                  :disabled="item.quantity >= item.tile_stock">
                  <i class="fa-solid fa-plus"></i>
                </button>
              </div>
            </div>

            <span>
              <i class="fa-solid fa-money-bill-wave mr-1"></i> Price: ₱{{ item.tile_price }}
            </span>
            <span>
              <i class="fa-solid fa-coins mr-1"></i> Total: ₱{{ item.tile_price * item.quantity }}
            </span>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex justify-end gap-3 mt-4">
          <button @click="placeOrder(item, index)" :disabled="item.tile_stock === 0"
            class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed">
            <i class="fa-solid fa-credit-card"></i> Place Order
          </button>

          <button @click="removeItem(index)"
            class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition flex items-center gap-2">
            <i class="fa-solid fa-trash"></i> Remove
          </button>
        </div>
      </div>
    </div>

    <!-- Total Price -->
    <div v-if="cartItems.length > 0"
      class="mt-6 text-right text-2xl font-bold text-gray-100 border-t border-gray-700 pt-4">
      <i class="fa-solid fa-wallet mr-2 text-yellow-400"></i>
      Total: <span class="text-green-400">₱{{ totalPrice }}</span>
    </div>
  </div>
</template>

<style scoped>
input::-webkit-inner-spin-button,
input::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
</style>
