<template>
  <div class="p-8 bg-gray-300 min-h-screen text-gray-900">
    <h2
      class="text-3xl font-bold mb-8 text-center bg-gradient-to-r from-blue-500 to-sky-400 bg-clip-text text-transparent">
      <i class="fas fa-box-open mr-2"></i>
      Product Management
    </h2>

    <!-- Add Product & Bulk Stock -->
    <div class="flex flex-col md:flex-row md:justify-between items-center gap-4 mb-6">
      <div class="flex flex-row gap-5">
        <button
          class="bg-blue-500 hover:bg-blue-600 text-white px-5 py-2.5 rounded-lg font-medium transition-all shadow-sm hover:scale-[1.03] flex items-center gap-2"
          @click="openAddModal">
          <i class="fas fa-plus"></i>
          Add New Product
        </button>

        <button @click="showArchived = !showArchived"
          class="bg-gray-500 hover:bg-gray-400 text-gray-800 px-5 py-2.5 rounded-lg font-medium transition-all shadow-sm hover:scale-[1.03] flex items-center gap-2">
          <i class="fas fa-archive"></i>
          {{ showArchived ? 'Hide Archived' : 'Show Archived' }}
        </button>

        <button @click="openStockRecordModal"
          class="bg-indigo-500 hover:bg-indigo-600 text-white px-5 py-2.5 rounded-lg font-medium transition-all shadow-sm hover:scale-[1.03] flex items-center gap-2">
          <i class="fas fa-history"></i>
          Stock Records
        </button>
      </div>

      <div class="flex items-center gap-3">
        <div v-if="selectAllMode && selectedProducts.length > 0" class="flex items-center gap-3">
          <input type="number" min="0" v-model.number="bulkStock"
            class="w-24 px-3 py-2 rounded-lg text-gray-800 border border-gray-300 bg-white" placeholder="Stock" />

          <button @click="addSelectedStock"
            class="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg font-medium transition-all shadow flex items-center gap-2">
            <i class="fas fa-plus-circle"></i>
            Add Stock
          </button>

          <button @click="updateSelectedStock"
            class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg font-medium transition-all shadow flex items-center gap-2">
            <i class="fas fa-sync-alt"></i>
            Update Stock
          </button>
        </div>

        <button
          class="bg-gray-200 hover:bg-gray-300 text-gray-700 px-4 py-2 rounded-lg flex items-center justify-center gap-2"
          @click="toggleSelectAllMode" title="Select All Products">
          <span>Stock-In</span>
          <i class="fas fa-check-double" :class="selectAllMode ? 'text-blue-600' : 'text-gray-600'"></i>
        </button>
      </div>
    </div>

    <!-- Product Table -->
    <div class="overflow-x-auto rounded-lg shadow bg-white border border-gray-300">
      <table class="w-full text-sm text-gray-700">
        <thead class="bg-gray-200 text-blue-600 uppercase text-xs">
          <tr>
            <th class="px-4 py-3 text-left">
              <input v-if="selectAllMode" type="checkbox" v-model="selectAll" />
            </th>
            <th class="px-4 py-3 text-center">Image</th>
            <th class="px-4 py-3">Category</th>
            <th class="px-4 py-3">Type</th>
            <th class="px-4 py-3">Name</th>
            <th class="px-4 py-3">Description</th>
            <th class="px-4 py-3 text-center">Price</th>
            <th class="px-4 py-3 text-center">Stock</th>
            <th class="px-4 py-3 text-center">Actions</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="product in products.filter(p => showArchived ? p.is_archived : !p.is_archived)" :key="product.id"
            :class="[
              'hover:bg-gray-50 transition-colors',
              product.is_archived ? 'bg-gray-200 line-through text-gray-500' : ''
            ]">
            <td class="border-t border-gray-200 py-3 px-4">
              <input v-if="selectAllMode" type="checkbox" v-model="selectedProducts" :value="product.id" />
            </td>

            <td class="border-t border-gray-200 py-3 px-4 text-center">
              <img v-if="product.tile_image" :src="product.tile_image" alt="Tile"
                class="w-16 h-16 object-cover rounded-lg border border-gray-300 shadow-sm mx-auto" />
              <span v-else class="text-gray-400 italic">No image</span>
            </td>

            <td class="border-t border-gray-200 py-3 px-4">{{ product.tile_category }}</td>
            <td class="border-t border-gray-200 py-3 px-4">{{ product.tile_type }}</td>
            <td class="border-t border-gray-200 py-3 px-4 font-medium text-gray-900">{{ product.tile_name }}</td>

            <td class="border-t border-gray-200 py-3 px-4 text-gray-600 truncate max-w-[200px]">
              {{ product.tile_description }}
            </td>

            <td class="border-t border-gray-200 py-3 px-4 text-center font-semibold text-green-600">
              ₱{{ product.tile_price?.toFixed(2) }}
            </td>

            <td class="border-t border-gray-200 py-3 px-4 text-center" :class="stockColor(product.tile_stock)">
              {{ product.tile_stock }}
            </td>

            <td class="border-t border-gray-200 py-3 text-center">
              <div class="flex flex-col items-center gap-2">
                <button @click="openEditModal(product)" :disabled="product.is_archived"
                  class="bg-blue-500 hover:bg-blue-600 text-white w-32 py-1.5 rounded-lg font-medium transition-all shadow flex items-center justify-center gap-2 disabled:opacity-40">
                  <i class="fas fa-edit"></i> Edit
                </button>

                <button @click="toggleArchive(product)"
                  :class="product.is_archived ? 'bg-yellow-500 hover:bg-yellow-600' : 'bg-gray-300 hover:bg-gray-400'"
                  class="w-32 py-1.5 rounded-lg font-medium transition-all shadow flex items-center justify-center gap-2 text-gray-800">
                  <i class="fas" :class="product.is_archived ? 'fa-box-open' : 'fa-archive'"></i>
                  {{ product.is_archived ? 'Unarchive' : 'Archive' }}
                </button>

                <button @click="confirmDelete(product)" :disabled="product.is_archived"
                  class="bg-red-500 hover:bg-red-600 text-white w-32 py-1.5 rounded-lg font-medium transition-all shadow flex items-center justify-center gap-2 disabled:opacity-40">
                  <i class="fas fa-trash"></i> Delete
                </button>
              </div>
            </td>
          </tr>

          <tr v-if="products.length === 0">
            <td colspan="10" class="text-center py-6 text-gray-500 italic">
              No products found.
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Stock Records Modal -->
    <transition name="fade">
      <div v-if="showStockModal" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
        <div
          class="bg-white border border-gray-300 rounded-xl p-6 w-[800px] text-gray-900 shadow-xl max-h-[80vh] overflow-y-auto">
          <h3 class="text-2xl font-bold mb-5 text-indigo-600 border-b border-gray-200 pb-2 flex items-center gap-2">
            <i class="fas fa-history"></i>
            Stock Records
          </h3>

          <table class="w-full text-sm text-gray-700 border border-gray-300 rounded-lg">
            <thead class="bg-gray-100 text-indigo-600 uppercase text-xs">
              <tr>
                <th class="px-3 py-2 text-left">Product ID</th>
                <th class="px-3 py-2 text-left">Change Type</th>
                <th class="px-3 py-2 text-center">Quantity</th>
                <th class="px-3 py-2 text-center">Prev Stock</th>
                <th class="px-3 py-2 text-center">New Stock</th>
                <th class="px-3 py-2 text-center">Date</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="record in stockRecords" :key="record.id" class="border-t border-gray-200 hover:bg-gray-50">
                <td class="px-3 py-2">{{ record.product_id }}</td>
                <td class="px-3 py-2 capitalize">{{ record.change_type }}</td>
                <td class="px-3 py-2 text-center">{{ record.quantity_changed }}</td>
                <td class="px-3 py-2 text-center">{{ record.previous_stock }}</td>
                <td class="px-3 py-2 text-center">{{ record.new_stock }}</td>
                <td class="px-3 py-2 text-center">{{ new Date(record.created_at).toLocaleString() }}</td>
              </tr>

              <tr v-if="stockRecords.length === 0">
                <td colspan="7" class="text-center py-5 text-gray-500 italic">
                  No stock records found.
                </td>
              </tr>
            </tbody>
          </table>

          <div class="mt-5 flex justify-end">
            <button @click="closeStockRecordModal"
              class="bg-gray-300 hover:bg-gray-400 text-gray-800 px-5 py-2 rounded-lg font-medium transition-all">
              Close
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- Add/Edit Product Modal -->
    <transition name="fade">
      <div v-if="showModal" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
        <div class="bg-white border border-gray-300 rounded-xl p-6 w-[700px] text-gray-900 shadow-xl">
          <h3 class="text-2xl font-bold mb-5 text-blue-600 border-b border-gray-200 pb-2 flex items-center gap-2">
            <i :class="isEditing ? 'fas fa-edit text-blue-500' : 'fas fa-plus text-green-500'"></i>
            {{ isEditing ? 'Edit Product' : 'Add Product' }}
          </h3>

          <div class="grid grid-cols-2 gap-5">
            <div>
              <label class="block text-gray-700 font-medium">Category</label>
              <select v-model="form.tile_category"
                class="w-full border border-gray-300 bg-white rounded-lg px-3 py-2 mt-1 text-gray-900 focus:ring-2 focus:ring-blue-400">
                <option value="" disabled>Select Category</option>
                <option value="Tiles">Tiles</option>
                <option value="Others">Others</option>
              </select>

              <label class="block text-gray-700 font-medium mt-3">Type</label>
              <select v-if="form.tile_category === 'Tiles'" v-model="form.tile_type"
                class="w-full border border-gray-300 bg-white rounded-lg px-3 py-2 mt-1 text-gray-900 focus:ring-2 focus:ring-blue-400">
                <option value="" disabled>Select Type</option>
                <option value="Floor">Floor Tile</option>
                <option value="Wall">Wall Tile</option>
                <option value="Ceiling">Ceiling Tile</option>
                <option value="Paving">Paving Tile</option>
                <option value="Pool">Pool Tile</option>
              </select>

              <input v-else type="text" v-model="form.tile_type" placeholder="Enter product type"
                class="w-full border border-gray-300 bg-white rounded-lg px-3 py-2 mt-1 text-gray-900 focus:ring-2 focus:ring-blue-400" />

              <label class="block text-gray-700 font-medium mt-3">Name</label>
              <input v-model="form.tile_name" type="text"
                class="w-full border border-gray-300 bg-white rounded-lg px-3 py-2 mt-1 text-gray-900 focus:ring-2 focus:ring-blue-400" />

              <label class="block text-gray-700 font-medium mt-3">Description</label>
              <textarea v-model="form.tile_description" rows="4"
                class="w-full border border-gray-300 bg-white rounded-lg px-3 py-2 mt-1 resize-none text-gray-900 focus:ring-2 focus:ring-blue-400"></textarea>
            </div>

            <div>
              <label class="block text-gray-700 font-medium">Price (₱)</label>
              <input v-model.number="form.tile_price" type="number" min="0" step="0.01"
                class="w-full border border-gray-300 bg-white rounded-lg px-3 py-2 mt-1 text-gray-900 focus:ring-2 focus:ring-blue-400" />

              <label class="block text-gray-700 font-medium mt-3">Tile Image</label>
              <input ref="fileInput" type="file" accept="image/*" @change="handleFileUpload"
                class="w-full text-gray-700 file:bg-gray-300 file:text-gray-900 file:px-3 file:py-2 file:rounded-lg file:border-0 file:mr-3 mt-1" />

              <div v-if="form.tile_image" class="mt-3">
                <img :src="form.tile_image"
                  class="w-28 h-28 rounded-lg object-cover border border-gray-300 shadow-md" />
              </div>
            </div>
          </div>

          <div class="mt-6 flex justify-end space-x-3">
            <button @click="closeModal"
              class="bg-gray-300 hover:bg-gray-400 text-gray-800 px-4 py-2 rounded-lg font-medium transition-all shadow">
              Cancel
            </button>

            <button @click="saveProduct"
              class="bg-green-500 hover:bg-green-600 text-white px-5 py-2 rounded-lg font-medium transition-all shadow flex items-center gap-2">
              <i :class="isEditing ? 'fas fa-save' : 'fas fa-check'"></i>
              {{ isEditing ? 'Update Product' : 'Save Product' }}
            </button>
          </div>
        </div>
      </div>
    </transition>

    <!-- Confirmation Modal -->
    <transition name="fade">
      <div v-if="showConfirmModal" class="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
        <div class="bg-white border border-gray-300 rounded-xl p-6 w-[400px] text-center shadow-xl">
          <h3 class="text-lg font-semibold mb-4 text-blue-600">
            <i class="fas fa-exclamation-triangle text-yellow-500 mr-2"></i>
            Confirm Delete
          </h3>

          <p class="text-gray-700 mb-6">
            Are you sure you want to delete
            <span class="font-semibold text-blue-600">{{ selectedProduct?.tile_name }}</span>?
          </p>

          <div class="flex justify-center gap-4">
            <button @click="showConfirmModal = false"
              class="bg-gray-300 hover:bg-gray-400 text-gray-800 px-5 py-1.5 rounded-lg font-medium shadow">
              Cancel
            </button>
            <button @click="deleteProduct"
              class="bg-red-500 hover:bg-red-600 text-white px-5 py-1.5 rounded-lg font-medium shadow">
              Delete
            </button>
          </div>
        </div>
      </div>
    </transition>

  </div>
</template>


<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import axios from "axios";

const backend = import.meta.env.VITE_BACKEND_URL;
const showArchived = ref(false);

interface Product {
  id: number;
  tile_image?: string | null;
  tile_category: string;
  tile_type: string;
  tile_name: string;
  tile_description: string;
  tile_price: number;
  tile_stock: number;
  is_archived: boolean;
}

const products = ref<Product[]>([]);
const selectedProducts = ref<number[]>([]);
const selectAll = ref(false);
const bulkStock = ref<number | null>(null);

// New ref to control Select All icon mode
const selectAllMode = ref(false);

const showModal = ref(false);
const showConfirmModal = ref(false);
const isEditing = ref(false);
const editingId = ref<number | null>(null);
const selectedProduct = ref<Product | null>(null);
const fileInput = ref<HTMLInputElement | null>(null);

const form = ref<Product>({
  id: 0,
  tile_image: "",
  tile_category: "",
  tile_type: "",
  tile_name: "",
  tile_description: "",
  tile_price: 0,
  tile_stock: 0,
  is_archived: false,
});

const api = `${backend}/product`;

const stockRecords = ref<any[]>([]);
const showStockModal = ref(false);

// Fetch stock records from backend
const getStockRecords = async () => {
  try {
    const res = await axios.get(`${backend}/admin/product/stock-records`, {
      withCredentials: true, // important to send admin cookie
    });
    // ✅ FIX: Access the "records" array from the response
    stockRecords.value = res.data.records || [];
  } catch (err) {
    console.error("Failed to fetch stock records:", err);
    stockRecords.value = [];
  }
};

// Open stock record modal
const openStockRecordModal = async () => {
  await getStockRecords();
  showStockModal.value = true;
};

// Close stock record modal
const closeStockRecordModal = () => {
  showStockModal.value = false;
};
const getProducts = async () => {
  const res = await axios.get<Product[]>(`${api}/admin`);
  products.value = res.data;
};

const stockColor = (stock: number): string => {
  if (stock < 10) return "text-red-500 font-bold";
  if (stock < 20) return "text-orange-400 font-bold";
  return "text-green-400 font-bold";
};

// Watch selectAll
watch(selectAll, val => {
  if (val) selectedProducts.value = products.value.map(p => p.id);
  else selectedProducts.value = [];
});

// ✅ Replace stock (update stock value directly)
const updateSelectedStock = async () => {
  if (!bulkStock.value || selectedProducts.value.length === 0) return;

  await Promise.all(
    selectedProducts.value.map(id =>
      axios.put(`${backend}/admin/product/${id}/update-stock`, { tile_stock: bulkStock.value })
    )
  );

  bulkStock.value = null;
  selectAll.value = false;
  selectedProducts.value = [];
  await getProducts();
};

// ✅ Add stock (adds to existing stock)
const addSelectedStock = async () => {
  if (!bulkStock.value || selectedProducts.value.length === 0) return;

  await Promise.all(
    selectedProducts.value.map(id =>
      axios.put(`${backend}/admin/product/${id}/add-stock`, { tile_stock: bulkStock.value })
    )
  );

  bulkStock.value = null;
  selectAll.value = false;
  selectedProducts.value = [];
  await getProducts();
};

const toggleArchive = async (product: Product) => {
  try {
    const res = await axios.patch(`${api}/toggle-archive/${product.id}`);
    // Update product in local list
    const index = products.value.findIndex(p => p.id === product.id);
    if (index !== -1) products.value[index] = res.data;
  } catch (err) {
    console.error(err);
  }
};

// Toggle Select All icon mode
const toggleSelectAllMode = () => {
  selectAllMode.value = !selectAllMode.value;
  if (!selectAllMode.value) {
    selectedProducts.value = [];
    selectAll.value = false;
  }
};

// Rest of modal functions (no changes)
const handleFileUpload = (event: Event) => {
  const target = event.target as HTMLInputElement;
  const file = target.files?.[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      form.value.tile_image = e.target?.result as string;
    };
    reader.readAsDataURL(file);
  }
};

const openAddModal = () => {
  isEditing.value = false;
  showModal.value = true;
  Object.assign(form.value, {
    id: 0,
    tile_image: "",
    tile_category: "",
    tile_type: "",
    tile_name: "",
    tile_description: "",
    tile_price: 0,
    tile_stock: 0,
    is_archived: false,
  });
};

const openEditModal = (product: Product) => {
  isEditing.value = true;
  showModal.value = true;
  editingId.value = product.id;
  Object.assign(form.value, product);
};

const confirmDelete = (product: Product) => {
  selectedProduct.value = product;
  showConfirmModal.value = true;
};

const deleteProduct = async () => {
  if (!selectedProduct.value) return;
  await axios.delete(`${api}/${selectedProduct.value.id}`);
  showConfirmModal.value = false;
  getProducts();
};

const saveProduct = async () => {
  if (isEditing.value && editingId.value) {
    await axios.put(`${api}/${editingId.value}`, form.value);
  } else {
    await axios.post(`${api}/add-product`, form.value);
  }
  closeModal();
  getProducts();
};

const closeModal = () => {
  showModal.value = false;
};

onMounted(getProducts);
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
