<template>
  <div class="app">
    <header class="header">
      <h1>🚀 NASA Space Biology Knowledge Engine</h1>
      <p>Search through NASA bioscience publications and experiments</p>
    </header>
    
    <SearchBox @search="handleSearch" :loading="loading" />
    
    <SearchResults :results="results" :loading="loading" :searched="searched" />
  </div>
</template>

<script>
import SearchBox from './components/SearchBox.vue'
import SearchResults from './components/SearchResults.vue'
import { searchAPI } from './api'

export default {
  name: 'App',
  components: {
    SearchBox,
    SearchResults
  },
  data() {
    return {
      results: [],
      loading: false,
      searched: false
    }
  },
  methods: {
    async handleSearch(query) {
      this.loading = true
      this.searched = true
      
      try {
        const data = await searchAPI(query)
        this.results = data.results || []
      } catch (error) {
        console.error('Search error:', error)
        this.results = []
      }
      
      this.loading = false
    }
  }
}
</script>

<style>
.app {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.header h1 {
  color: #1a365d;
  margin-bottom: 10px;
}

.header p {
  color: #666;
  font-size: 16px;
}
</style>