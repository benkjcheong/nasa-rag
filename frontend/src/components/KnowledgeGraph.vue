<template>
  <div class="knowledge-graph">
    <h3>🕸️ Knowledge Graph</h3>
    <div ref="graphContainer" class="graph-container"></div>
  </div>
</template>

<script>
export default {
  name: 'KnowledgeGraph',
  props: ['graphData'],
  mounted() {
    this.renderGraph()
  },
  watch: {
    graphData() {
      this.renderGraph()
    }
  },
  methods: {
    async renderGraph() {
      if (!this.graphData) return
      
      const d3 = await import('d3')
      const container = this.$refs.graphContainer
      d3.select(container).selectAll("*").remove()
      
      const width = 400
      const height = 300
      
      const svg = d3.select(container)
        .append('svg')
        .attr('width', width)
        .attr('height', height)
      
      const simulation = d3.forceSimulation(this.graphData.nodes)
        .force('link', d3.forceLink(this.graphData.edges).id(d => d.id))
        .force('charge', d3.forceManyBody().strength(-100))
        .force('center', d3.forceCenter(width / 2, height / 2))
      
      const link = svg.append('g')
        .selectAll('line')
        .data(this.graphData.edges)
        .enter().append('line')
        .attr('stroke', '#64b5f6')
        .attr('stroke-width', 2)
      
      const node = svg.append('g')
        .selectAll('circle')
        .data(this.graphData.nodes)
        .enter().append('circle')
        .attr('r', 8)
        .attr('fill', d => d.risk === 'High' ? '#f44336' : d.risk === 'Medium' ? '#ff9800' : '#4caf50')
      
      node.append('title').text(d => d.title)
      
      simulation.on('tick', () => {
        link
          .attr('x1', d => d.source.x)
          .attr('y1', d => d.source.y)
          .attr('x2', d => d.target.x)
          .attr('y2', d => d.target.y)
        
        node
          .attr('cx', d => d.x)
          .attr('cy', d => d.y)
      })
    }
  }
}
</script>

<style scoped>
.knowledge-graph {
  background: rgba(255,255,255,0.05);
  padding: 1rem;
  border-radius: 10px;
  margin-bottom: 2rem;
}

.graph-container {
  display: flex;
  justify-content: center;
}

h3 {
  color: #64b5f6;
  margin-bottom: 1rem;
  text-align: center;
}
</style>