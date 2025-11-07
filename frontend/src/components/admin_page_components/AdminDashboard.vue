<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import VueApexCharts from "vue3-apexcharts";
import type { ApexOptions } from "apexcharts";
import axios from "axios";
import { useRouter } from "vue-router";
import { useLoadingStore } from "@/stores/loading";
import jsPDF from "jspdf";

const backend = import.meta.env.VITE_BACKEND_URL;
const loading = useLoadingStore();
const router = useRouter();
const admin_email = ref<string | null>(null);
const recentActivity = ref<string[]>([]);
const showModal = ref(false);

// --------------------- Date Range ---------------------
const startDate = ref<string>("");
const endDate = ref<string>("");

// --------------------- Sales Chart ---------------------
const series = ref([{ name: "Sales", data: [] }]);
const chartOptions = ref<ApexOptions>({
  chart: { id: "sales-performance", toolbar: { show: false } },
  xaxis: { categories: [], labels: { style: { colors: "#ffffff" } } },
  yaxis: {
    title: { text: "PHP (thousands)", style: { color: "#ffffff" } },
    labels: { style: { colors: "#ffffff" } },
  },
  colors: ["#3b82f6"],
  dataLabels: { enabled: false },
  grid: { borderColor: "#374151" },
  tooltip: { theme: "dark" },
});

// --------------------- Fetch Admin ---------------------
const fetchAdminEmail = async () => {
  try {
    const res = await axios.get(`${backend}/admin/me`, { withCredentials: true });
    admin_email.value = res.data.email;
  } catch {
    router.replace("/");
  }
};

// --------------------- Logout ---------------------
const logoutAdmin = async () => {
  try {
    loading.show();
    await axios.post(`${backend}/admin/logout`, {}, { withCredentials: true });
    admin_email.value = null;
    router.replace("/");
  } finally {
    loading.hide();
  }
};

// --------------------- Dashboard Stats ---------------------
const lowStockCount = ref(0);
const totalOrdersToday = ref(0);
const totalSalesToday = ref(0);
const totalItemsSoldToday = ref(0);
const totalSalesOverall = ref(0);

const fetchDashboardStats = async () => {
  try {
    const res = await axios.get(`${backend}/admin/dashboard/stats`, { withCredentials: true });
    totalSalesToday.value = res.data.total_sales_today;
    totalOrdersToday.value = res.data.total_orders_today;
    totalItemsSoldToday.value = res.data.total_items_today;
    lowStockCount.value = res.data.low_stock_count;
    totalSalesOverall.value = res.data.total_sales_overall;
  } catch (error) {
    console.error("Failed to fetch dashboard stats:", error);
  }
};

// --------------------- Dynamic Stats List ---------------------
const stats = ref([
  { title: "Total Orders Today", value: totalOrdersToday },
  { title: "Sales Today", value: totalSalesToday },
  { title: "Items Sold Today", value: totalItemsSoldToday },
  { title: "Stock Alerts", value: lowStockCount },
  { title: "Total Sales Overall", value: totalSalesOverall },
]);

watch(
  [totalOrdersToday, totalSalesToday, totalItemsSoldToday, lowStockCount, totalSalesOverall],
  () => {
    stats.value = [
      { title: "Total Orders Today", value: totalOrdersToday.value },
      { title: "Sales Today", value: totalSalesToday.value },
      { title: "Items Sold Today", value: totalItemsSoldToday.value },
      { title: "Stock Alerts", value: lowStockCount.value },
      { title: "Total Sales Overall", value: totalSalesOverall.value },
    ];
  }
);

// --------------------- Sales Chart ---------------------
const fetchSalesChart = async () => {
  try {
    const res = await axios.get(`${backend}/admin/sales/performance`, { withCredentials: true });
    chartOptions.value.xaxis!.categories = res.data.categories;
    series.value = [{ name: "Sales", data: res.data.data }];
  } catch (error) {
    console.error("Failed to fetch weekly sales:", error);
  }
};

// --------------------- Recent Activity ---------------------
const fetchRecentActivities = async () => {
  try {
    const res = await axios.get(`${backend}/admin/customer_recent_activity`, { withCredentials: true });
    recentActivity.value = res.data.map((act: { activity: string }) => act.activity || "");
  } catch (error) {
    console.error("Failed to fetch recent activities:", error);
  }
};

// --------------------- PDF Report ---------------------
const generateReport = async () => {
  if (!startDate.value || !endDate.value) {
    alert("Please select both start and end dates.");
    return;
  }

  try {
    loading.show();
    const res = await axios.get(`${backend}/admin/sales/report`, {
      params: { start_date: startDate.value, end_date: endDate.value },
      withCredentials: true,
    });

    const data = res.data;
    const doc = new jsPDF({ orientation: "portrait", unit: "pt", format: "a4" });

    // Header
    doc.setFillColor(33, 150, 243);
    doc.rect(0, 0, doc.internal.pageSize.getWidth(), 70, "F");
    doc.setTextColor(255, 255, 255);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(22);
    doc.text("SALES PERFORMANCE REPORT", doc.internal.pageSize.getWidth() / 2, 40, { align: "center" });
    doc.setFontSize(11);
    doc.text(`Period: ${data.start_date} to ${data.end_date}`, doc.internal.pageSize.getWidth() / 2, 60, { align: "center" });

    // Summary
    doc.setTextColor(0, 0, 0);
    doc.setFontSize(14);
    let y = 110;
    doc.text("Report Summary", 40, y);
    doc.setDrawColor(59, 130, 246);
    doc.line(40, y + 5, 550, y + 5);

    const totalSales = data.total_sales ?? 0;
    const totalOrders = data.total_orders ?? 0;
    const totalItems = data.total_items ?? 0;

    doc.setFontSize(12);
    doc.text(`Total Sales: PHP ${totalSales.toLocaleString()}`, 60, (y += 25));
    doc.text(`Total Orders: ${totalOrders}`, 60, (y += 20));
    doc.text(`Total Items Sold: ${totalItems}`, 60, (y += 20));

    // Best Sellers
    if (data.best_sellers && Array.isArray(data.best_sellers) && data.best_sellers.length > 0) {
      y += 40;
      doc.setFontSize(14);
      doc.text("Top-Selling Products", 40, y);
      doc.setDrawColor(59, 130, 246);
      doc.line(40, y + 5, 550, y + 5);
      doc.setFontSize(12);

      let tableY = y + 25;
      data.best_sellers.slice(0, 5).forEach((p: any, i: number) => {
        const name = p.tile_name || "Unknown Product";
        const sold = p.total_sold ?? 0;
        const revenue = p.total_revenue ?? 0;
        doc.text(`${i + 1}. ${name} — ${sold} sold — PHP ${revenue.toLocaleString()}`, 60, tableY);
        tableY += 20;
      });
    } else {
      y += 40;
      doc.setFontSize(12);
      doc.text("No best-selling product data available for this period.", 60, y);
    }

    // Footer
    const now = new Date();
    doc.setFontSize(10);
    doc.setTextColor(100);
    doc.text(`Generated by: ${admin_email.value || "Admin"}`, 40, doc.internal.pageSize.getHeight() - 40);
    doc.text(`Date: ${now.toLocaleString()}`, 400, doc.internal.pageSize.getHeight() - 40);

    doc.save(`Sales_Report_${data.start_date}_to_${data.end_date}.pdf`);
  } catch (error) {
    console.error(error);
    alert("Failed to generate report. Please try again.");
  } finally {
    loading.hide();
  }
};

// --------------------- Mounted ---------------------
onMounted(() => {
  fetchAdminEmail();
  fetchDashboardStats(); // ✅ Only one call now
  fetchSalesChart();
  fetchRecentActivities();
});
</script>


<template>
  <div class="flex gap-4 p-4 bg-gray-900 text-gray-200">
    <div class="flex flex-col gap-4 w-1/3">
      <!-- Admin Info -->
      <div class="p-4 bg-gray-800 rounded shadow flex justify-between items-center">
        <p class="font-semibold">Logged in as:</p>
        <p class="text-blue-400 font-medium">{{ admin_email || "Loading..." }}</p>
        <button @click="logoutAdmin" class="ml-2 text-red-500 hover:text-red-400 font-medium">Logout</button>
      </div>

      <!-- Stats -->
      <div class="grid grid-cols-2 gap-4">
        <div v-for="(stat, index) in stats" :key="index" class="p-4 bg-gray-800 rounded shadow">
          <p class="text-sm text-gray-400">{{ stat.title }}</p>
          <p class="text-xl font-bold" :class="stat.title === 'Stock Alerts' ? 'text-red-500' : 'text-green-500'">
            {{ stat.value }}
          </p>
        </div>
      </div>

      <!-- Report Generation -->
      <div class="mt-4 space-y-2">
        <label class="block text-sm text-gray-300">Select Date Range:</label>
        <div class="flex gap-4">
          <div class="flex flex-col">
            <label class="text-sm text-gray-300 mb-1">Start Date:</label>
            <input type="date" v-model="startDate"
              class="p-2 rounded bg-gray-700 text-white border border-gray-600 focus:border-blue-500 outline-none" />
          </div>

          <div class="flex flex-col">
            <label class="text-sm text-gray-300 mb-1">End Date:</label>
            <input type="date" v-model="endDate"
              class="p-2 rounded bg-gray-700 text-white border border-gray-600 focus:border-blue-500 outline-none" />
          </div>
        </div>


        <button @click="generateReport"
          class="px-4 py-2 bg-blue-500 hover:bg-blue-400 rounded text-white font-semibold mt-2">
          Generate Report (PDF)
        </button>
      </div>

      <!-- Recent Activity -->
      <div @click="showModal = true"
        class="flex-1 p-4 bg-gray-800 rounded shadow overflow-auto cursor-pointer hover:bg-gray-700 transition mt-4">
        <h3 class="font-semibold mb-2">Recent Activity</h3>
        <ul class="space-y-1 text-gray-300">
          <li v-for="(activity, index) in recentActivity.slice(0, 3)" :key="index">• {{ activity }}</li>
        </ul>
      </div>

      <!-- Modal -->
      <div v-if="showModal" class="fixed inset-0 bg-black/50 flex justify-center items-center z-50">
        <div class="bg-gray-800 rounded shadow p-6 max-h-[80%] overflow-auto w-1/2">
          <h3 class="text-lg font-semibold mb-4">All Recent Activities</h3>
          <ul class="space-y-1 text-gray-300">
            <li v-for="(activity, index) in recentActivity" :key="index">• {{ activity }}</li>
          </ul>
          <button @click="showModal = false" class="mt-4 px-4 py-2 bg-blue-500 rounded hover:bg-blue-400">Close</button>
        </div>
      </div>
    </div>

    <!-- Sales Chart -->
    <div class="flex-1 p-4 bg-gray-800 rounded shadow">
      <h3 class="font-semibold mb-2">Sales Performance</h3>
      <VueApexCharts type="bar" :options="chartOptions" :series="series" height="100%" />
    </div>
  </div>
</template>
