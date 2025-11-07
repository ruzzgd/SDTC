<script setup lang="ts">
import { ref, onMounted } from "vue";
import axios from "axios";
const backend = import.meta.env.VITE_BACKEND_URL
interface Order {
  order_id: number;
  product_id: number;
  customer_email: string;
  tile_name: string;
  tile_price: number;
  quantity: number;
  created_at: string;
  status: string;
  estimated_delivery?: string;
}

const orders = ref<Order[]>([]);
const estimatedTimes = ref<Record<number, string>>({});
const showConfirm = ref(false);
const confirmMessage = ref("");
const confirmAction = ref<() => void>(() => { });

const fetchOrders = async () => {
  try {
    const res = await axios.get(`${backend}/admin/orders/all`);
    orders.value = res.data;
  } catch (err) {
    console.error("Error fetching orders:", err);
  }
};

const confirmModal = (message: string, action: () => void) => {
  confirmMessage.value = message;
  confirmAction.value = action;
  showConfirm.value = true;
};

// ✅ Handle main action
const handlePrimaryAction = async (order: Order) => {
  confirmModal(
    order.status === "Pending"
      ? `Approve order #${order.order_id}?`
      : order.status === "Approved"
        ? `Mark order #${order.order_id} as shipped?`
        : `Mark order #${order.order_id} as completed?`,
    async () => {
      try {
        let newStatus = "";
        if (order.status === "Pending") {
          const estimated = estimatedTimes.value[order.order_id];
          if (!estimated) {
            alert("⚠️ Please set estimated delivery before approving.");
            return;
          }
          newStatus = "Approved";
          await axios.put(
            `${backend}/admin/orders/update/${order.order_id}`,
            { status: newStatus, estimated_delivery: estimated }
          );
        } else if (order.status === "Approved") {
          newStatus = "Shipped";
          await axios.put(
            `${backend}/admin/orders/update/${order.order_id}`,
            { status: newStatus }
          );
        } else if (order.status === "Shipped") {
          newStatus = "Completed";
          await axios.put(
            `${backend}/admin/orders/update/${order.order_id}`,
            { status: newStatus }
          );
        }
        fetchOrders();
        showConfirm.value = false;
      } catch (err) {
        console.error(err);
        alert("❌ Failed to update order");
      }
    }
  );
};

// ✅ Handle reject/delete
const handleSecondaryAction = async (order: Order) => {
  confirmModal(
    order.status === "Pending"
      ? `Reject order #${order.order_id}?`
      : `Delete order #${order.order_id}?`,
    async () => {
      try {
        if (order.status === "Pending") {
          await axios.put(
            `${backend}/admin/orders/update/${order.order_id}`,
            { status: "Rejected" }
          );
        } else {
          await axios.delete(
            `${backend}/admin/orders/delete/${order.order_id}`
          );
        }
        fetchOrders();
        showConfirm.value = false;
      } catch (err) {
        console.error(err);
        alert("❌ Failed to update or delete order");
      }
    }
  );
};

onMounted(fetchOrders);
</script>

<template>
  <div class="p-8 bg-gradient-to-b from-gray-900 to-gray-800 min-h-screen text-white">
    <h2
      class="text-3xl font-bold mb-8 text-center bg-gradient-to-r from-sky-400 to-blue-500 bg-clip-text text-transparent">
      🧾 Orders Management
    </h2>

    <div class="overflow-x-auto rounded-lg shadow-lg bg-gray-900/70 backdrop-blur-md border border-gray-700">
      <table class="w-full text-sm text-gray-200">
        <thead class="bg-gray-800/80 text-cyan-400 uppercase text-xs">
          <tr>
            <th class="px-4 py-3 text-center">Order ID</th>
            <th class="px-4 py-3 text-center">Product ID</th>
            <th class="px-4 py-3">Customer</th>
            <th class="px-4 py-3">Item</th>
            <th class="px-4 py-3 text-center">Price</th>
            <th class="px-4 py-3 text-center">Qty</th>
            <th class="px-4 py-3 text-center">Order Date</th>
            <th class="px-4 py-3 text-center">Est. Delivery</th>
            <th class="px-4 py-3 text-center">Actions</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="order in orders" :key="order.order_id" class="hover:bg-gray-800/60 transition-colors">
            <td class="border-t border-gray-700 py-3 text-center">{{ order.order_id }}</td>
            <td class="border-t border-gray-700 py-3 text-center">{{ order.product_id }}</td>
            <td class="border-t border-gray-700 py-3">{{ order.customer_email }}</td>
            <td class="border-t border-gray-700 py-3">{{ order.tile_name }}</td>
            <td class="border-t border-gray-700 py-3 text-center">
              ₱{{ order.tile_price.toFixed(2) }}
            </td>
            <td class="border-t border-gray-700 py-3 text-center">{{ order.quantity }}</td>
            <td class="border-t border-gray-700 py-3 text-center">
              {{ new Date(order.created_at).toLocaleString("en-US", {
                year: "numeric",
                month: "short",
                day: "numeric",
                hour: "2-digit",
                minute: "2-digit",
              }) }}
            </td>

            <td class="border-t border-gray-700 py-3 text-center">
              <input v-if="order.status === 'Pending'" type="datetime-local" v-model="estimatedTimes[order.order_id]"
                :min="new Date().toISOString().slice(0, 16)"
                class="px-2 py-1 rounded bg-gray-700 text-white w-44 text-sm" />

              <span v-else>{{ order.estimated_delivery || "—" }}</span>
            </td>

            <!-- ✅ Buttons -->
            <td class="border-t border-gray-700 py-3 text-center">
              <div class="flex flex-col items-center gap-2">
                <!-- Left Button -->
                <button :disabled="order.status === 'Shipped' || order.status === 'Rejected'" :class="[
                  order.status === 'Pending'
                    ? 'bg-green-600 hover:bg-green-700'
                    : order.status === 'Approved'
                      ? 'bg-blue-600 hover:bg-blue-700'
                      : order.status === 'Shipped'
                        ? 'bg-purple-600 hover:bg-purple-700'
                        : order.status === 'Completed'
                          ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                          : 'bg-gray-600 text-gray-400 cursor-not-allowed',
                  'w-32 py-1.5 rounded-lg font-medium transition-all shadow-md hover:scale-[1.02] disabled:opacity-60',
                ]" @click="handlePrimaryAction(order)">
                  {{
                    order.status === "Pending"
                      ? "Approve"
                      : order.status === "Approved"
                        ? "Deliver"
                        : order.status === "Shipped"
                          ? "Complete"
                          : order.status === "Completed"
                            ? "Completed"
                            : "Rejected"
                  }}
                </button>

                <!-- Right Button -->
                <button :class="[
                  order.status === 'Pending'
                    ? 'bg-red-600 hover:bg-red-700'
                    : 'bg-gray-700 hover:bg-gray-600',
                  'w-32 py-1.5 rounded-lg font-medium text-white transition-all shadow-md hover:scale-[1.02]',
                ]" @click="handleSecondaryAction(order)">
                  {{ order.status === "Pending" ? "Reject" : "Delete" }}
                </button>
              </div>
            </td>
          </tr>

          <tr v-if="orders.length === 0">
            <td colspan="9" class="text-center py-6 text-gray-400 italic">
              No orders found.
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ✅ Confirmation Modal -->
    <div v-if="showConfirm" class="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
      <div class="bg-gray-900/90 border border-gray-700 rounded-xl p-6 text-center shadow-2xl w-80">
        <h3 class="text-lg font-semibold mb-5 text-cyan-300">
          {{ confirmMessage }}
        </h3>
        <div class="flex justify-center gap-4">
          <button @click="confirmAction()"
            class="bg-green-600 hover:bg-green-700 px-5 py-1.5 rounded-lg font-medium shadow">
            Yes
          </button>
          <button @click="showConfirm = false"
            class="bg-red-600 hover:bg-red-700 px-5 py-1.5 rounded-lg font-medium shadow">
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
