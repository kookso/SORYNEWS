import { defineStore } from "pinia"

export const useNewsFilterStore = defineStore("newsFilter", {
  state: () => ({
    activeTab: 1,
    sortBy: "latest",
    currentPage: 1,
  }),
  actions: {
    setTab(tabId) {
      this.activeTab = tabId
      this.currentPage = 1
    },
    setSort(sort) {
      this.sortBy = sort
      this.currentPage = 1
    },
    setPage(page) {
      this.currentPage = page
    },
  },
})
