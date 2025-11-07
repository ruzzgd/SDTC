import { defineStore } from 'pinia';

interface OrderItem {
  id: number;
  tile_category: string;
  tile_type: string;
  tile_name: string;
  tile_image: string;
  tile_description: string;
  tile_price: number;
  tile_stock: number;
}

export const useOrderStore = defineStore('order', {
  state: () => ({
    selectedItem: null as OrderItem | null,
    showModal: false,
  }),
  actions: {
    openModal(item: OrderItem) {
      this.selectedItem = item;
      this.showModal = true;
    },
    closeModal() {
      this.selectedItem = null;
      this.showModal = false;
    },
  },
});
