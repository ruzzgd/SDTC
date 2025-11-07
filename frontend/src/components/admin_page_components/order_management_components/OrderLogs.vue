<script setup lang="ts">
import { ref, computed, onMounted } from "vue";

const backend = import.meta.env.VITE_BACKEND_URL;

// Interfaces
interface OrderItem {
  name: string;
  price: number;
  quantity: number;
}

type OrderStatus = "Shipped" | "Rejected" | "Deleted";

interface OrderLog {
  orderId: number;
  customer: string;
  items: OrderItem[];
  dateOrdered: string;
  status: OrderStatus;
}

// Search query
const searchQuery = ref("");

// Order logs state
const orderLogs = ref<OrderLog[]>([]);

// Compute total price per item
const itemTotal = (item: OrderItem): number => item.price * item.quantity;

// Function to get status color
const statusColor = (status: OrderStatus): string => {
  if (status === "Shipped") return "text-green-400 font-bold";
  if (status === "Rejected") return "text-red-500 font-bold";
  if (status === "Deleted") return "text-gray-400 font-bold";
  return "";
};

// Filter orders by Order ID
const filteredOrders = computed((): OrderLog[] => {
  if (!searchQuery.value) return orderLogs.value;
  return orderLogs.value.filter(order =>
    order.orderId.toString().includes(searchQuery.value)
  );
});

// Fetch order logs from backend
const fetchOrderLogs = async () => {
  try {
    const res = await fetch(`${backend}/admin/orderlogs`);
    const data = await res.json();

    // Convert each log into OrderLog format grouped by orderId
    const logsMap = new Map<number, OrderLog>();

    data.order_logs.forEach((log: any) => {
      if (!logsMap.has(log.order_id)) {
        logsMap.set(log.order_id, {
          orderId: log.order_id,
          customer: log.customer,
          items: [],
          dateOrdered: log.date_ordered,
          status: log.status,
        });
      }
      logsMap.get(log.order_id)?.items.push({
        name: log.item_name,
        price: log.item_price,
        quantity: log.quantity,
      });
    });

    orderLogs.value = Array.from(logsMap.values());
  } catch (err) {
    console.error("Failed to fetch order logs:", err);
  }
};

// Fetch on mount
onMounted(fetchOrderLogs);
</script>

<template>
  <div class="p-8 bg-gradient-to-b from-gray-900 to-gray-800 min-h-screen text-white">
    <!-- Header -->
    <div class="flex justify-between items-center mb-8">
      <h2
        class="text-3xl font-bold bg-gradient-to-r from-sky-400 to-blue-500 bg-clip-text text-transparent"
      >
        📜 Order Logs
      </h2>

      <!-- Search Bar -->
      <div class="relative w-64">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search by Order ID..."
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
            <th class="px-4 py-3 text-center">Order ID</th>
            <th class="px-4 py-3 text-center">Customer</th>
            <th class="px-4 py-3 text-left">Item</th>
            <th class="px-4 py-3 text-center">Price</th>
            <th class="px-4 py-3 text-center">Qty</th>
            <th class="px-4 py-3 text-center">Total</th>
            <th class="px-4 py-3 text-center">Date Ordered</th>
            <th class="px-4 py-3 text-center">Status</th>
          </tr>
        </thead>

        <tbody>
          <tr
            v-for="order in filteredOrders"
            :key="order.orderId"
            class="hover:bg-gray-800/60 transition-colors"
          >
            <td class="border-t border-gray-700 py-3 text-center font-medium">
              {{ order.orderId }}
            </td>
            <td class="border-t border-gray-700 py-3 text-center">
              {{ order.customer }}
            </td>
            <td class="border-t border-gray-700 py-3">
              <ul>
                <li v-for="(item, i) in order.items" :key="i">
                  {{ item.name }}
                </li>
              </ul>
            </td>
            <td class="border-t border-gray-700 py-3 text-center">
              <ul>
                <li v-for="(item, i) in order.items" :key="i">
                  ₱{{ item.price.toFixed(2) }}
                </li>
              </ul>
            </td>
            <td class="border-t border-gray-700 py-3 text-center">
              <ul>
                <li v-for="(item, i) in order.items" :key="i">
                  {{ item.quantity }}
                </li>
              </ul>
            </td>
            <td class="border-t border-gray-700 py-3 text-center">
              <ul>
                <li v-for="(item, i) in order.items" :key="i">
                  ₱{{ itemTotal(item).toFixed(2) }}
                </li>
              </ul>
            </td>
            <td class="border-t border-gray-700 py-3 text-center">
              {{ order.dateOrdered }}
            </td>
            <td
              class="border-t border-gray-700 py-3 text-center font-semibold"
              :class="statusColor(order.status)"
            >
              {{ order.status }}
            </td>
          </tr>

          <tr v-if="filteredOrders.length === 0">
            <td colspan="8" class="text-center py-6 text-gray-400 italic">
              No order logs found.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
