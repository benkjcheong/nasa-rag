<template>
  <div>
    <div v-if="loading" class="loading">
      Searching knowledge graph and documents...
    </div>
    
    <div v-if="results.length > 0" class="results">
      <div v-for="result in results" :key="result.document_id || result.item_id" class="result-card">
        <div class="result-score">Score: {{ result.score.toFixed(3) }}</div>
        <div class="result-type">{{ result.type }}</div>
        <div class="result-content">
          <div v-if="result.type === 'document'">
            <strong>Document {{ result.document_id }}</strong>
            <p>{{ result.document }}</p>
          </div>
          <div v-else>
            <strong>Knowledge Graph</strong>
            <p>{{ result.content }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <div v-if="!loading && results.length === 0 && searched" class="no-results">
      No results found. Try different search terms.
    </div>
  </div>
</template>

<script>
export default {
  name: 'SearchResults',
  props: {
    results: Array,
    loading: Boolean,
    searched: Boolean
  }
}
</script>

<style scoped>
.loading, .no-results {
  text-align: center;
  color: #666;
  padding: 20px;
}

.results {
  display: grid;
  gap: 15px;
}

.result-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  position: relative;
}

.result-score {
  position: absolute;
  top: 15px;
  right: 15px;
  background: #e3f2fd;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.result-type {
  color: #666;
  font-size: 12px;
  text-transform: uppercase;
  margin-bottom: 10px;
}

.result-content {
  line-height: 1.5;
}

.result-content p {
  margin: 10px 0 0 0;
}
</style>