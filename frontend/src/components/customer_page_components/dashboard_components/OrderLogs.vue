<script setup lang="ts">
import { ref, onMounted } from "vue";
import axios from "axios";

const backend = import.meta.env.VITE_BACKEND_URL;

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

const orderLogs = ref<OrderItem[]>([]);

const fetchOrderLogs = async () => {
  try {
    const res = await axios.get(`${backend}/orders/logs`, { withCredentials: true });
    // ✅ Only keep logs with status "Shipped" or "Rejected"
    orderLogs.value = res.data.filter(
      (item: OrderItem) => ["Shipped", "Rejected"].includes(item.status)
    );
  } catch (err) {
    console.error("Error fetching order logs:", err);
    orderLogs.value = [];
  }
};

const formatDelivery = (value: string | null) => {
  if (!value) return "Awaiting Admin Approval";
  const parsed = new Date(value);
  return isNaN(parsed.getTime()) ? value : parsed.toLocaleString();
};

onMounted(() => fetchOrderLogs());
</script>

<template>
  <div class="w-full max-w-4xl mx-auto p-4">
    <h1 class="text-3xl font-bold mb-6 text-gray-900 flex items-center gap-3">
      <i class="fa-solid fa-clock-rotate-left text-yellow-400"></i>
      Order Logs
    </h1>

    <div v-if="orderLogs.length === 0" class="text-gray-800 text-center py-10">
      No past orders yet.
    </div>

    <div v-for="item in orderLogs" :key="item.order_id + '-' + item.tile_name"
      class="bg-gray-300 rounded-xl shadow-lg overflow-hidden mb-5 hover:shadow-2xl transition-shadow duration-300 flex flex-col md:flex-row border border-gray-500">

      <!-- 🖼️ Product Image -->
      <div class="md:w-1/4 h-40 md:h-auto overflow-hidden">
        <img :src="item.tile_image" class="w-full h-full object-cover" alt="Tile Image" />
      </div>

      <!-- 📦 Order Info -->
      <div class="flex-1 p-5 flex flex-col justify-between">
        <div>
          <div class="flex items-center justify-between mb-2">
            <h2 class="font-semibold sm:text-xl text-gray-900">{{ item.tile_name }}</h2>
            <span class="inline-block px-3 py-1 rounded-full text-sm font-medium capitalize"
              :class="{
                'bg-orange-600 text-orange-100': item.status.toLowerCase() === 'pending',
                'bg-green-700 text-green-100': item.status.toLowerCase() === 'shipped',
                'bg-red-700 text-red-100': item.status.toLowerCase() === 'rejected'
              }">
              <i class="fa-solid fa-circle mr-1"></i> {{ item.status }}
            </span>
          </div>

          <p class="text-gray-800 text-sm mb-1">
            <i class="fa-solid fa-layer-group mr-1"></i>
            {{ item.tile_category }} - {{ item.tile_type }}
          </p>
          <p class="text-gray-800 text-sm mb-1">
            <i class="fa-solid fa-hashtag mr-1"></i> Order #: {{ item.order_id }}
          </p>
          <p class="text-gray-800 text-sm mb-2">
            <i class="fa-solid fa-calendar-day mr-1"></i>
            Placed: {{ new Date(item.created_at).toLocaleString() }}
          </p>

          <!-- 🕒 Delivery Info -->
          <div class="border-t border-gray-500 pt-2 mt-3">
            <p class="text-sm mb-2 text-gray-800">
              <i class="fa-solid fa-truck mr-1 text-yellow-400"></i>
              Estimated Delivery:
              <span :class="item.estimated_delivery ? 'text-green-400 font-semibold' : 'text-yellow-400 font-semibold'">
                {{ formatDelivery(item.estimated_delivery) }}
              </span>
            </p>

            <!-- 📍 Delivery Address -->
            <div class="bg-gray-400 rounded-lg p-3 mt-2 text-gray-900 border border-gray-700">
              <p class="text-sm font-medium mb-1 flex items-center gap-2">
                <i class="fa-solid fa-location-dot text-yellow-400"></i>
                Delivery Address
              </p>
              <p class="text-gray-900 text-sm ml-5 leading-relaxed">
                {{ item.delivery_address.house_number }},
                {{ item.delivery_address.street }},
                {{ item.delivery_address.barangay }},
                {{ item.delivery_address.city }},
                {{ item.delivery_address.province }}
              </p>
            </div>
          </div>

          <!-- 💰 Price & Quantity -->
          <div class="flex gap-6 text-gray-900 text-sm mt-4 flex-wrap">
            <span><i class="fa-solid fa-hashtag mr-1"></i> Qty: {{ item.quantity }}</span>
            <span><i class="fa-solid fa-money-bill-wave mr-1"></i> Price: ₱{{ item.tile_price }}</span>
            <span><i class="fa-solid fa-coins mr-1"></i> Total: ₱{{ item.total_price }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
