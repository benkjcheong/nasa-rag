<template>
  <div id="app">
    <header>
      <h1>🚀 NASA Bioscience Knowledge Engine</h1>
      <div class="controls">
        <input 
          v-model="searchTerm" 
          @input="searchPublications"
          placeholder="Search publications..."
          class="search-input"
        />
        <select v-model="selectedMission" @change="filterPublications" class="filter-select">
          <option value="">All Missions</option>
          <option value="Mars">Mars</option>
          <option value="Moon">Moon</option>
          <option value="ISS">ISS</option>
        </select>
        <select v-model="selectedRisk" @change="filterPublications" class="filter-select">
          <option value="">All Risk Levels</option>
          <option value="High">High Risk</option>
          <option value="Medium">Medium Risk</option>
          <option value="Low">Low Risk</option>
        </select>
      </div>
    </header>

    <main>
      <div class="dashboard-grid">
        <div class="summary-section">
          <div class="summary-cards">
            <div class="card">
              <h3>Publications</h3>
              <p>{{ summary.totalPublications }}</p>
            </div>
            <div class="card">
              <h3>Mars Relevant</h3>
              <p>{{ summary.missionRelevance?.Mars || 0 }}</p>
            </div>
            <div class="card">
              <h3>High Risk</h3>
              <p>{{ summary.riskDistribution?.High || 0 }}</p>
            </div>
          </div>
        </div>
        
        <KnowledgeGraph :graphData="knowledgeGraph" />
      </div>

      <div class="publications">
        <div 
          v-for="pub in publications" 
          :key="pub.id" 
          class="publication-card"
          @click="selectPublication(pub)"
        >
          <div class="pub-header">
            <h3>{{ pub.title }}</h3>
            <span class="risk-badge" :class="pub.riskLevel?.toLowerCase()">{{ pub.riskLevel }} Risk</span>
          </div>
          <p class="authors">{{ pub.authors.join(', ') }} ({{ pub.year }})</p>
          <p class="summary">{{ pub.summary }}</p>
          <div class="keywords">
            <span v-for="keyword in pub.keywords" :key="keyword" class="keyword">
              {{ keyword }}
            </span>
          </div>
          <div class="pub-footer">
            <div class="missions">
              <span v-for="mission in pub.missionRelevance" :key="mission" class="mission-tag">
                {{ mission }}
              </span>
            </div>
            <p class="impact">{{ pub.impact }}</p>
          </div>
        </div>
      </div>
      
      <div v-if="selectedPub" class="ai-insights">
        <h2>🤖 AI Insights: {{ selectedPub.title }}</h2>
        <div class="insights-grid">
          <div class="insight-card">
            <h4>Key Findings</h4>
            <ul>
              <li v-for="finding in aiInsights.keyFindings" :key="finding">{{ finding }}</li>
            </ul>
          </div>
          <div class="insight-card">
            <h4>Countermeasures</h4>
            <ul>
              <li v-for="measure in aiInsights.countermeasures" :key="measure">{{ measure }}</li>
            </ul>
          </div>
          <div class="insight-card">
            <h4>Related Studies</h4>
            <div v-for="related in relatedPubs" :key="related.id" class="related-item">
              {{ related.title }}
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import axios from 'axios'
import KnowledgeGraph from './components/KnowledgeGraph.vue'

export default {
  name: 'App',
  components: {
    KnowledgeGraph
  },
  data() {
    return {
      publications: [],
      summary: {},
      knowledgeGraph: null,
      searchTerm: '',
      selectedMission: '',
      selectedRisk: '',
      selectedPub: null,
      aiInsights: {},
      relatedPubs: []
    }
  },
  async mounted() {
    await this.loadData()
  },
  methods: {
    async loadData() {
      try {
        const [pubsRes, summaryRes, graphRes] = await Promise.all([
          axios.get('http://localhost:3001/api/publications'),
          axios.get('http://localhost:3001/api/summary'),
          axios.get('http://localhost:3001/api/knowledge-graph')
        ])
        this.publications = pubsRes.data
        this.summary = summaryRes.data
        this.knowledgeGraph = graphRes.data
      } catch (error) {
        console.error('Error loading data:', error)
      }
    },
    async filterPublications() {
      try {
        const params = {}
        if (this.searchTerm) params.search = this.searchTerm
        if (this.selectedMission) params.mission = this.selectedMission
        if (this.selectedRisk) params.risk = this.selectedRisk
        
        const response = await axios.get('http://localhost:3001/api/publications', { params })
        this.publications = response.data
      } catch (error) {
        console.error('Error filtering:', error)
      }
    },
    async searchPublications() {
      await this.filterPublications()
    },
    async selectPublication(pub) {
      this.selectedPub = pub
      try {
        const [insightsRes, relatedRes] = await Promise.all([
          axios.get(`http://localhost:3001/api/ai-insights/${pub.id}`),
          axios.get(`http://localhost:3001/api/related/${pub.id}`)
        ])
        this.aiInsights = insightsRes.data
        this.relatedPubs = relatedRes.data
      } catch (error) {
        console.error('Error loading insights:', error)
      }
    }
  }
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }

body { 
  font-family: Arial, sans-serif; 
  background: #0a0a0a; 
  color: #fff; 
}

#app { min-height: 100vh; }

header {
  background: linear-gradient(135deg, #1a1a2e, #16213e);
  padding: 2rem;
  text-align: center;
}

h1 { font-size: 2.5rem; margin-bottom: 1rem; }

.controls {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.search-input, .filter-select {
  padding: 0.8rem;
  border: none;
  border-radius: 25px;
  background: rgba(255,255,255,0.1);
  color: #fff;
  font-size: 1rem;
}

.search-input {
  width: 300px;
}

.filter-select {
  width: 150px;
}

.search-input::placeholder { color: #ccc; }

.filter-select option {
  background: #1a1a2e;
  color: #fff;
}

main { padding: 2rem; }

.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 2rem;
  margin-bottom: 2rem;
}

.summary-cards {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

@media (max-width: 768px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}

.card {
  background: rgba(255,255,255,0.1);
  padding: 1rem;
  border-radius: 10px;
  text-align: center;
  min-width: 120px;
  flex: 1;
}

.card h3 { color: #64b5f6; margin-bottom: 0.5rem; }
.card p { font-size: 1.2rem; font-weight: bold; }

.publications {
  display: grid;
  gap: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
}

.publication-card {
  background: rgba(255,255,255,0.05);
  padding: 1.5rem;
  border-radius: 10px;
  border-left: 4px solid #64b5f6;
  cursor: pointer;
  transition: all 0.3s ease;
}

.publication-card:hover {
  background: rgba(255,255,255,0.1);
  transform: translateY(-2px);
}

.pub-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.publication-card h3 {
  color: #64b5f6;
  margin: 0;
  flex: 1;
}

.risk-badge {
  padding: 0.3rem 0.8rem;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: bold;
}

.risk-badge.high { background: rgba(244, 67, 54, 0.3); color: #f44336; }
.risk-badge.medium { background: rgba(255, 152, 0, 0.3); color: #ff9800; }
.risk-badge.low { background: rgba(76, 175, 80, 0.3); color: #4caf50; }

.authors {
  color: #ccc;
  font-style: italic;
  margin-bottom: 1rem;
}

.summary {
  margin-bottom: 1rem;
  line-height: 1.5;
}

.keywords {
  margin-bottom: 1rem;
}

.keyword {
  background: rgba(100, 181, 246, 0.2);
  color: #64b5f6;
  padding: 0.3rem 0.8rem;
  border-radius: 15px;
  font-size: 0.8rem;
  margin-right: 0.5rem;
  display: inline-block;
  margin-bottom: 0.5rem;
}

.pub-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
}

.missions {
  display: flex;
  gap: 0.5rem;
}

.mission-tag {
  background: rgba(156, 39, 176, 0.3);
  color: #9c27b0;
  padding: 0.2rem 0.6rem;
  border-radius: 10px;
  font-size: 0.8rem;
}

.impact {
  font-weight: bold;
  color: #4caf50;
  font-size: 0.9rem;
}

.ai-insights {
  margin-top: 3rem;
  padding: 2rem;
  background: rgba(255,255,255,0.05);
  border-radius: 15px;
}

.ai-insights h2 {
  color: #64b5f6;
  margin-bottom: 1.5rem;
  text-align: center;
}

.insights-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.insight-card {
  background: rgba(255,255,255,0.1);
  padding: 1.5rem;
  border-radius: 10px;
}

.insight-card h4 {
  color: #64b5f6;
  margin-bottom: 1rem;
}

.insight-card ul {
  list-style: none;
  padding: 0;
}

.insight-card li {
  padding: 0.5rem 0;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

.related-item {
  padding: 0.5rem;
  background: rgba(100, 181, 246, 0.1);
  border-radius: 5px;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}
</style>