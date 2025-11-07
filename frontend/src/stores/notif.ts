import { defineStore } from 'pinia'

type NotifType = 'success' | 'error' | 'warning' | 'info'

export const useNotifStore = defineStore('notif', {
  state: () => ({
    isNotif: false as boolean,
    message: '' as string,
    type: 'info' as NotifType
  }),

  actions: {
    show(message: string, type: NotifType = 'info') {
      this.message = message
      this.type = type
      this.isNotif = true

      // Auto-hide after 3 seconds
      setTimeout(() => {
        this.hide()
      }, 3000)
    },

    hide() {
      this.isNotif = false
      this.message = ''
    }
  }
})
