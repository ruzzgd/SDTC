<script setup lang="ts">
import { ref, onMounted } from "vue";
import axios from "axios";
import { useNotifStore } from "@/stores/notif";

const notif = useNotifStore(); // ✅ use notif store
const backend = import.meta.env.VITE_BACKEND_URL;

// ✅ Backend response types
interface DeliveryAddress {
  house_number: string;
  street: string;
  barangay: string;
  city: string;
  province: string;
}

interface OrderItem {
  order_id: number;
  tile_image: string;
  tile_category: string;
  tile_type: string;
  tile_name: string;
  tile_price: number;
  quantity: number;
  total_price: number;
  status: string;
  created_at: string;
  estimated_delivery: string | null;
  delivery_address: DeliveryAddress;
}

interface OrderGrouped {
  id: number;
  created_at: string;
  status: string;
  estimated_delivery: string | null;
  items: OrderItem[];
  delivery_address: DeliveryAddress;
}

const ordersFlat = ref<OrderItem[]>([]);
const orders = ref<OrderGrouped[]>([]);

// ✅ Fetch orders
const fetchOrders = async () => {
  try {
    const res = await axios.get(`${backend}/orders`, {
      withCredentials: true,
    });

    ordersFlat.value = res.data;

    const grouped: Record<number, OrderGrouped> = {};
    ordersFlat.value.forEach((item) => {
      const orderId = item.order_id;
      if (!grouped[orderId]) {
        grouped[orderId] = {
          id: orderId,
          created_at: item.created_at,
          status: item.status ?? "pending",
          estimated_delivery: item.estimated_delivery ?? null,
          items: [],
          delivery_address: item.delivery_address,
        };
      }
      grouped[orderId].items.push(item);
    });

    orders.value = Object.values(grouped);
  } catch (err) {
    console.error("Error fetching orders:", err);
    notif.show("Failed to fetch orders", "error");
  }
};

// ✅ Cancel an order (with notif)
const cancelOrder = async (orderId: number) => {
  try {
    await axios.delete(`${backend}/orders/${orderId}`, {
      withCredentials: true,
    });

    ordersFlat.value = ordersFlat.value.filter((item) => item.order_id !== orderId);
    orders.value = orders.value.filter((o) => o.id !== orderId);

    notif.show(`Order #${orderId} has been cancelled`, "success"); // ✅ success notif
  } catch (err) {
    console.error("Error cancelling order:", err);
    notif.show("Failed to cancel order", "error"); // ✅ error notif
  }
};

// ✅ Format delivery date safely
const formatDelivery = (value: string | null) => {
  if (!value) return "Awaiting Admin Approval";
  const parsed = new Date(value);
  return isNaN(parsed.getTime()) ? value : parsed.toLocaleString();
};

onMounted(() => fetchOrders());
</script>


<template>
  <div class="w-full max-w-4xl mx-auto p-4">
    <h1 class="text-3xl font-bold mb-6 text-gray-100 flex items-center gap-3">
      <i class="fa-solid fa-box-open text-yellow-400"></i>
      Your Orders
    </h1>

    <div v-if="ordersFlat.length === 0" class="text-gray-400 text-center py-10">
      You have no orders yet.
    </div>

    <div v-for="item in ordersFlat" :key="item.order_id + '-' + item.tile_name"
      class="bg-gray-800 rounded-xl shadow-lg overflow-hidden mb-5 hover:shadow-2xl transition-shadow duration-300 flex flex-col md:flex-row border border-gray-700">
      <!-- 🖼️ Product Image -->
      <div class="md:w-1/4 h-40 md:h-auto overflow-hidden">
        <img :src="item.tile_image" class="w-full h-full object-cover" alt="Tile Image" />
      </div>

      <!-- 📦 Order Info -->
      <div class="flex-1 p-5 flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between mb-2">
            <h2 class="font-semibold sm:text-xl text-gray-100">{{ item.tile_name }}</h2>
            <span class="inline-block px-3 py-1 rounded-full text-sm font-medium capitalize" :class="{
              'bg-orange-600 text-orange-100': item.status.toLowerCase() === 'pending',
              'bg-green-700 text-green-100': ['approved', 'shipped', 'completed'].includes(item.status.toLowerCase()),
              'bg-red-700 text-red-100': item.status.toLowerCase() === 'rejected',
              'bg-gray-600 text-gray-100': !['pending', 'approved', 'shipped', 'completed', 'rejected'].includes(item.status.toLowerCase())
            }">
              <i class="fa-solid fa-circle mr-1"></i> {{ item.status }}
            </span>

          </div>

          <p class="text-gray-400 text-sm mb-1">
            <i class="fa-solid fa-layer-group mr-1"></i>
            {{ item.tile_category }} - {{ item.tile_type }}
          </p>
          <p class="text-gray-400 text-sm mb-1">
            <i class="fa-solid fa-hashtag mr-1"></i> Order #: {{ item.order_id }}
          </p>
          <p class="text-gray-400 text-sm mb-2">
            <i class="fa-solid fa-calendar-day mr-1"></i>
            Placed: {{ new Date(item.created_at).toLocaleString() }}
          </p>

          <!-- 🕒 Delivery Info -->
          <div class="border-t border-gray-700 pt-2 mt-3">
            <p class="text-sm mb-2 text-gray-300">
              <i class="fa-solid fa-truck mr-1 text-yellow-400"></i>
              Estimated Delivery:
              <span :class="item.estimated_delivery ? 'text-green-400 font-semibold' : 'text-yellow-400 font-semibold'">
                {{ formatDelivery(item.estimated_delivery) }}
              </span>
            </p>

            <!-- 📍 Delivery Address -->
            <div class="bg-gray-900 rounded-lg p-3 mt-2 text-gray-300 border border-gray-700">
              <p class="text-sm font-medium mb-1 flex items-center gap-2">
                <i class="fa-solid fa-location-dot text-yellow-400"></i>
                Delivery Address
              </p>
              <p class="text-gray-400 text-sm ml-5 leading-relaxed">
                {{ item.delivery_address.house_number }},
                {{ item.delivery_address.street }},
                {{ item.delivery_address.barangay }},
                {{ item.delivery_address.city }},
                {{ item.delivery_address.province }}
              </p>
            </div>
          </div>

          <!-- 💰 Price & Quantity -->
          <div class="flex gap-6 text-gray-300 text-sm mt-4 flex-wrap">
            <span><i class="fa-solid fa-hashtag mr-1"></i> Qty: {{ item.quantity }}</span>
            <span><i class="fa-solid fa-money-bill-wave mr-1"></i> Price: ₱{{ item.tile_price }}</span>
            <span><i class="fa-solid fa-coins mr-1"></i> Total: ₱{{ item.total_price }}</span>
          </div>
        </div>

        <!-- ❌ Cancel / Locked -->
        <div class="flex justify-end items-center mt-5">
          <button v-if="item.status === 'Pending'" @click="cancelOrder(item.order_id)"
            class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors duration-200 flex items-center gap-2">
            <i class="fa-solid fa-xmark"></i> Cancel
          </button>
        </div>
      </div>
    </div>

    <!-- 💸 Total Spent -->
    <div v-if="ordersFlat.length > 0"
      class="mt-6 text-right text-2xl font-bold text-gray-100 border-t border-gray-700 pt-4">
      <i class="fa-solid fa-wallet mr-2 text-yellow-400"></i>
      Total Spent: ₱{{ordersFlat.reduce((sum, i) => sum + (i.total_price ?? 0), 0)}}
    </div>
  </div>
</template>
