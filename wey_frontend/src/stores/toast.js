import { definestore } from 'pinia'

export const useToastStore = definestore({
  id: 'toast',

  state: () => ({
    ms: 0,
    message: '',
    classes: '',
    isVisbile: false
  }),

  actions: {
    showToast(ms, message, classes) {
      ;(this.ms = parseInt(ms)),
        (this.message = message),
        (this.classes = classes),
        (this.isVisbile = true)

      setTimeout(() => {
        this.classes += ' -translage-y-28'
      }, 10)

      setTimeout(() => {
        this.classes += this.classes.replace('-translate-y-28')
      }, this.ms - 500)

      setTimeout(() => {
        this.isVisbile = false
      }, this.ms)
    }
  }
})
