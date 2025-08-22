const express = require('express');
const cors = require('cors');
const axios = require('axios');
const natural = require('natural');

const app = express();
const PORT = 3001;

app.use(cors());
app.use(express.json());

// Enhanced NASA bioscience data with knowledge graph connections
const mockPublications = [
  {
    id: 1,
    title: "Effects of Microgravity on Plant Growth",
    authors: ["Smith, J.", "Johnson, A."],
    year: 2023,
    summary: "Study shows altered root development in microgravity conditions affecting nutrient uptake.",
    fullText: "Microgravity environments significantly alter plant morphology and physiology. Root systems show reduced gravitropic response, leading to altered nutrient and water uptake patterns. Cell wall composition changes, affecting structural integrity. These findings are crucial for developing sustainable food production systems for long-duration space missions to Mars.",
    keywords: ["microgravity", "plant biology", "space agriculture", "root development", "nutrient uptake"],
    impact: "High - Critical for Mars missions",
    missionRelevance: ["Mars", "Moon", "ISS"],
    relatedExperiments: [2, 4],
    experimentType: "Biological",
    riskLevel: "Medium",
    countermeasures: ["Artificial gravity", "Nutrient supplementation"]
  },
  {
    id: 2,
    title: "Bone Density Changes in Long-Duration Spaceflight",
    authors: ["Brown, K.", "Davis, M."],
    year: 2022,
    summary: "Astronauts experience 1-2% bone loss per month during extended missions.",
    fullText: "Extended exposure to microgravity results in significant bone demineralization, particularly in weight-bearing bones. Osteoblast activity decreases while osteoclast activity increases, leading to net bone loss. Exercise countermeasures show partial effectiveness but cannot completely prevent bone loss during missions longer than 6 months.",
    keywords: ["bone density", "astronaut health", "countermeasures", "osteoblast", "microgravity"],
    impact: "Critical - Crew safety concern",
    missionRelevance: ["Mars", "Moon", "Deep Space"],
    relatedExperiments: [3, 5],
    experimentType: "Medical",
    riskLevel: "High",
    countermeasures: ["Exercise protocols", "Bisphosphonates", "Vibration therapy"]
  },
  {
    id: 3,
    title: "Cellular Response to Radiation in Space Environment",
    authors: ["Wilson, R.", "Taylor, S."],
    year: 2023,
    summary: "DNA repair mechanisms show enhanced activity under space radiation exposure.",
    fullText: "Cosmic radiation and solar particle events pose significant risks to crew health. Cellular studies show upregulation of DNA repair pathways, particularly homologous recombination and non-homologous end joining. However, chronic exposure leads to increased mutation rates and potential cancer risk.",
    keywords: ["radiation", "cellular biology", "DNA repair", "cosmic rays", "cancer risk"],
    impact: "Medium - Protective mechanisms research",
    missionRelevance: ["Mars", "Deep Space"],
    relatedExperiments: [2, 6],
    experimentType: "Cellular",
    riskLevel: "High",
    countermeasures: ["Radiation shielding", "Pharmacological protection", "Antioxidants"]
  },
  {
    id: 4,
    title: "Muscle Atrophy in Microgravity Conditions",
    authors: ["Garcia, L.", "Chen, W."],
    year: 2023,
    summary: "Skeletal muscle mass decreases by 20% during 6-month missions despite exercise protocols.",
    fullText: "Microgravity-induced muscle atrophy affects both slow and fast-twitch muscle fibers. Protein synthesis decreases while protein degradation increases. Myosin heavy chain composition shifts toward faster isoforms. Current exercise countermeasures partially mitigate but cannot prevent muscle loss.",
    keywords: ["muscle atrophy", "microgravity", "exercise", "protein synthesis", "myosin"],
    impact: "High - Crew performance",
    missionRelevance: ["Mars", "Moon", "ISS"],
    relatedExperiments: [1, 2],
    experimentType: "Physiological",
    riskLevel: "Medium",
    countermeasures: ["Resistance exercise", "Electrical stimulation", "Protein supplementation"]
  },
  {
    id: 5,
    title: "Cardiovascular Deconditioning in Space",
    authors: ["Martinez, P.", "Kim, S."],
    year: 2022,
    summary: "Heart muscle weakens and blood volume decreases during spaceflight, affecting crew readiness.",
    fullText: "Cardiovascular deconditioning occurs rapidly in microgravity. Cardiac output decreases, blood volume reduces by 10-15%, and orthostatic intolerance develops. These changes impair crew ability to perform tasks upon landing and pose risks during emergency situations.",
    keywords: ["cardiovascular", "deconditioning", "blood volume", "orthostatic intolerance"],
    impact: "Critical - Mission safety",
    missionRelevance: ["Mars", "Moon", "ISS"],
    relatedExperiments: [2, 4],
    experimentType: "Medical",
    riskLevel: "High",
    countermeasures: ["Lower body negative pressure", "Fluid loading", "Exercise protocols"]
  },
  {
    id: 6,
    title: "Sleep Disruption and Circadian Rhythms in Space",
    authors: ["Thompson, A.", "Lee, J."],
    year: 2023,
    summary: "Altered light-dark cycles in space disrupt circadian rhythms, affecting crew performance and health.",
    fullText: "The 90-minute orbital period creates 16 sunrise-sunset cycles daily, disrupting natural circadian rhythms. Melatonin production becomes irregular, sleep quality decreases, and cognitive performance suffers. Light therapy and scheduled sleep periods show promise as countermeasures.",
    keywords: ["circadian rhythms", "sleep", "melatonin", "cognitive performance", "light therapy"],
    impact: "Medium - Crew wellbeing",
    missionRelevance: ["Mars", "Moon", "ISS"],
    relatedExperiments: [3, 5],
    experimentType: "Behavioral",
    riskLevel: "Medium",
    countermeasures: ["Light therapy", "Melatonin supplementation", "Sleep scheduling"]
  }
];

// Knowledge graph connections
const knowledgeGraph = {
  nodes: mockPublications.map(pub => ({
    id: pub.id,
    title: pub.title,
    type: pub.experimentType,
    risk: pub.riskLevel
  })),
  edges: mockPublications.flatMap(pub => 
    pub.relatedExperiments.map(relId => ({
      source: pub.id,
      target: relId,
      relationship: 'related'
    }))
  )
};

// AI-powered text analysis
function extractKeyInsights(text) {
  const sentenceTokenizer = new natural.SentenceTokenizer();
  const wordTokenizer = new natural.WordTokenizer();
  
  const sentences = sentenceTokenizer.tokenize(text);
  const keywords = wordTokenizer.tokenize(text.toLowerCase())
    .filter(word => word.length > 4 && !natural.stopwords.includes(word));
  
  return {
    keyFindings: sentences.slice(0, 2),
    criticalTerms: [...new Set(keywords)].slice(0, 5)
  };
}

// API Routes
app.get('/api/publications', (req, res) => {
  const { search, year, mission, risk } = req.query;
  let filtered = mockPublications;
  
  if (search) {
    filtered = filtered.filter(pub => 
      pub.title.toLowerCase().includes(search.toLowerCase()) ||
      pub.keywords.some(k => k.toLowerCase().includes(search.toLowerCase())) ||
      pub.fullText.toLowerCase().includes(search.toLowerCase())
    );
  }
  
  if (year) {
    filtered = filtered.filter(pub => pub.year.toString() === year);
  }
  
  if (mission) {
    filtered = filtered.filter(pub => pub.missionRelevance.includes(mission));
  }
  
  if (risk) {
    filtered = filtered.filter(pub => pub.riskLevel === risk);
  }
  
  res.json(filtered);
});

app.get('/api/publications/:id', (req, res) => {
  const pub = mockPublications.find(p => p.id === parseInt(req.params.id));
  if (!pub) return res.status(404).json({ error: 'Publication not found' });
  res.json(pub);
});

app.get('/api/summary', (req, res) => {
  const allKeywords = mockPublications.flatMap(p => p.keywords);
  const keywordCounts = {};
  allKeywords.forEach(k => keywordCounts[k] = (keywordCounts[k] || 0) + 1);
  const topKeywords = Object.entries(keywordCounts)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 8)
    .map(([keyword]) => keyword);
  
  res.json({
    totalPublications: mockPublications.length,
    years: [...new Set(mockPublications.map(p => p.year))],
    topKeywords,
    riskDistribution: {
      High: mockPublications.filter(p => p.riskLevel === 'High').length,
      Medium: mockPublications.filter(p => p.riskLevel === 'Medium').length,
      Low: mockPublications.filter(p => p.riskLevel === 'Low').length
    },
    missionRelevance: {
      Mars: mockPublications.filter(p => p.missionRelevance.includes('Mars')).length,
      Moon: mockPublications.filter(p => p.missionRelevance.includes('Moon')).length,
      ISS: mockPublications.filter(p => p.missionRelevance.includes('ISS')).length
    }
  });
});

app.get('/api/knowledge-graph', (req, res) => {
  res.json(knowledgeGraph);
});

app.get('/api/ai-insights/:id', (req, res) => {
  const pub = mockPublications.find(p => p.id === parseInt(req.params.id));
  if (!pub) return res.status(404).json({ error: 'Publication not found' });
  
  const insights = extractKeyInsights(pub.fullText);
  res.json({
    ...insights,
    riskAssessment: pub.riskLevel,
    countermeasures: pub.countermeasures,
    missionImpact: pub.missionRelevance
  });
});

app.get('/api/related/:id', (req, res) => {
  const pub = mockPublications.find(p => p.id === parseInt(req.params.id));
  if (!pub) return res.status(404).json({ error: 'Publication not found' });
  
  const related = mockPublications.filter(p => pub.relatedExperiments.includes(p.id));
  res.json(related);
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});