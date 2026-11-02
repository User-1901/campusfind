/**
 * CampusFind: Centralized Campus Document Search Engine
 * Frontend Client Application
 * Compatible with local Python server (http://localhost:5000) and Vercel Serverless.
 */

// Application State
const state = {
  documents: [],
  categories: [],
  categoryCounts: {},
  docTypes: [],
  invertedIndex: {},
  sortedVocabulary: [],
  unsortedVocabulary: [],
  activeView: 'dashboard',
  benchmarkCharts: {}
};

// 35 Viva Questions Knowledge Base
const VIVA_QUESTIONS = [
  {
    q: "1. What is a search engine?",
    a: "A search engine is an information retrieval software system designed to search, locate, and retrieve relevant documents or records from an indexed collection of text or data based on user-supplied query keywords."
  },
  {
    q: "2. What is the fundamental difference between Linear Search and Binary Search?",
    a: "Linear Search examines items sequentially one by one from beginning to end without requiring any data ordering (O(n) time). Binary Search is a divide-and-conquer algorithm that operates strictly on sorted collections, repeatedly halving the search space by checking the midpoint (O(log n) time)."
  },
  {
    q: "3. Why does Binary Search strictly require the dataset to be sorted?",
    a: "Binary Search relies on the mathematical invariant that if target < data[mid], all elements at indices greater than mid are guaranteed to be greater than target and can be safely eliminated. In an unsorted array, this deduction fails because smaller elements could reside in the pruned partition, causing false negative search results."
  },
  {
    q: "4. Can Binary Search be implemented on a singly linked list with O(log n) time?",
    a: "No. A singly linked list does not support O(1) random access by index. Finding the middle element requires traversing n/2 nodes sequentially, which takes O(n) time. Therefore, the total time complexity remains O(n)."
  },
  {
    q: "5. What is the best-case, average-case, and worst-case time complexity of Linear Search?",
    a: "Best Case: O(1) when target is at index 0. Average Case: O(n) when target is around n/2. Worst Case: O(n) when target is at index n-1 or absent from the dataset."
  },
  {
    q: "6. What is the best-case, average-case, and worst-case time complexity of Binary Search?",
    a: "Best Case: O(1) when target matches initial midpoint. Average Case: O(log2 n). Worst Case: O(log2 n) when target is at the leaf level or absent (max comparisons = floor(log2 n) + 1)."
  },
  {
    q: "7. What is the auxiliary space complexity of iterative Binary Search?",
    a: "O(1) auxiliary space, because it operates in-place using only three integer pointer variables (left, right, and mid) regardless of dataset size n."
  },
  {
    q: "8. How is the midpoint calculated in Binary Search to prevent integer overflow?",
    a: "mid = left + (right - left) // 2. This prevents integer overflow that can occur when computing (left + right) / 2 if the sum exceeds maximum integer capacity."
  },
  {
    q: "9. What is an Inverted Index and why is it used?",
    a: "An Inverted Index maps unique vocabulary words to posting lists recording which documents contain each word, term frequencies, and word offsets. It enables instantaneous lookups without sequentially scanning raw files."
  },
  {
    q: "10. What is the difference between a Forward Index and an Inverted Index?",
    a: "A Forward Index maps a Document to the list of words it contains: Document -> [words]. An Inverted Index inverts this mapping by associating each Word with documents: Word -> [documents, positions]."
  },
  {
    q: "11. What is the difference between an Inverted Index and a Sorted Vocabulary?",
    a: "The Inverted Index is a hash map mapping terms to document postings and offsets. The Sorted Vocabulary is an alphabetically sorted array of unique keys enabling Binary Search in O(log n) time."
  },
  {
    q: "12. What is text normalization and why is it necessary?",
    a: "Text normalization transforms text into a standardized format by converting characters to lowercase and stripping punctuation, ensuring 'Exam', 'EXAM', and 'exam.' match the same token."
  },
  {
    q: "13. What is the difference between indexing and searching?",
    a: "Indexing is an offline precomputation phase where documents are tokenized and organized into an inverted index. Searching is an online interactive phase where user queries are resolved in the vocabulary."
  },
  {
    q: "14. What is Big O notation?",
    a: "Big O notation describes the asymptotic upper bound of an algorithm's growth rate in terms of time or memory as input size n tends toward infinity."
  },
  {
    q: "15. What does O(n) mean geometrically and practically?",
    a: "O(n) represents linear growth forming a straight line. If dataset size doubles from 5,000 to 10,000, operations double from 5,000 to 10,000."
  },
  {
    q: "16. What does O(log n) mean geometrically and practically?",
    a: "O(log n) represents logarithmic growth that flattens rapidly. If dataset size increases from 1,000 to 1,000,000, operations only increase from ~10 to ~20."
  },
  {
    q: "17. Derive the recurrence relation for Binary Search.",
    a: "T(n) = T(n/2) + O(1). Unfolding k times gives T(n) = T(n/2^k) + k*c. Halting at n/2^k = 1 gives k = log2 n, yielding T(n) = O(log2 n)."
  },
  {
    q: "18. How many comparisons does Binary Search take for N = 10,000?",
    a: "At most 14 comparisons, because ceil(log2 10001) = 14 (2^13 = 8,192 < 10,000 <= 2^14 = 16,384)."
  },
  {
    q: "19. Why did we avoid built-in shortcuts like bisect or list.index()?",
    a: "Built-in routines are opaque C functions that hide key comparisons and pointer movements. Manual implementation allows precise tracking and educational visualization."
  },
  {
    q: "20. Why did we use Python 3 and modern web architecture?",
    a: "Python provides clean algorithmic expression for data structures, and the web app architecture allows instant deployment and accessible interactive exploration."
  },
  {
    q: "21. Why did we measure time using high-resolution monotonic timers?",
    a: "Monotonic timers provide sub-microsecond resolution unaffected by system clock adjustments, daylight saving changes, or NTP synchronization."
  },
  {
    q: "22. Why do we test multiple iterations per dataset size during benchmarking?",
    a: "Preemptive operating systems experience CPU context switching and background jitter. Taking the average over multiple iterations yields stable, representative timings."
  },
  {
    q: "23. Why is comparison count superior to wall-clock time in theory?",
    a: "Wall-clock time varies with hardware, CPU load, and interpreter overhead. Comparison count is an absolute mathematical metric invariant across all machines."
  },
  {
    q: "24. When is Linear Search practically preferred over Binary Search?",
    a: "On very small datasets (N < 20), on unsorted streams searched only once, or on non-random-access structures like singly linked lists."
  },
  {
    q: "25. When is Binary Search practically mandatory?",
    a: "On large, static or infrequently modified datasets searched repeatedly (e.g. database indexes and inverted index vocabularies)."
  },
  {
    q: "26. What is the cost of sorting a dataset before searching?",
    a: "Efficient comparison sorts take O(n log n) time. Sorting is economical when multiple queries amortize the initial sorting overhead."
  },
  {
    q: "27. What happens when duplicate words exist in a document?",
    a: "The inverted index records the document ID once and appends each sequential word offset to that document's position array."
  },
  {
    q: "28. What constitutes a 'Key Comparison' in search algorithms?",
    a: "A key comparison is an evaluation of the query target against an element of the dataset (target == data[i] or target < data[mid])."
  },
  {
    q: "29. What are the key architectural limitations of CampusFind?",
    a: "In-memory index storage, single-word queries without full boolean operators (AND/OR/NOT), and lack of linguistic stemmers (e.g. Porter Stemmer)."
  },
  {
    q: "30. How would you extend the engine to support multi-word phrase queries?",
    a: "Search each word independently, retrieve posting lists, and perform positional intersection checking that word positions are adjacent (pos2 = pos1 + 1)."
  },
  {
    q: "31. What is the time complexity of building the inverted index?",
    a: "O(M + V log V), where M is total words parsed and V is unique terms sorted for Binary Search."
  },
  {
    q: "32. How does the system handle empty search queries or special characters?",
    a: "Empty queries return early, and punctuation is stripped using regex character classes ([^\\w\\s])."
  },
  {
    q: "33. What is the purpose of the 'Unsorted Failure' demonstration?",
    a: "It visually proves why sorted data is mandatory by showing Binary Search pruning the wrong partition on unsorted data, leading to false negatives."
  },
  {
    q: "34. How does Chart.js visualize asymptotic behavior in this project?",
    a: "It plots empirical measurements of execution time and comparison counts across N=100 to 10,000, illustrating linear slope vs. logarithmic flattening."
  },
  {
    q: "35. Summarize CampusFind in 60 seconds.",
    a: "CampusFind is a centralized campus document search engine powered by an Inverted Index over 21 institutional documents. It implements Linear Search O(n) and Binary Search O(log n) from scratch, empirically demonstrating that Binary Search reduces 10,000 comparisons down to just 14 comparisons while providing rich search result cards, category filtering, and dry-run tracing."
  }
];

// Initialize on DOM Ready
document.addEventListener('DOMContentLoaded', () => {
  setupNavigation();
  setupSearchActions();
  setupDocumentLibrary();
  setupAlgorithmLab();
  setupBenchmarking();
  setupEducationalMode();
  setupViva();
  loadRepositoryData();
});

// ==============================================================================
// DATA INGESTION & REPOSITORY INITIALIZATION
// ==============================================================================
async function loadRepositoryData() {
  try {
    const res = await fetch('/api/documents');
    if (res.ok) {
      const data = await res.json();
      state.documents = data.documents || [];
      state.categories = data.statistics.categories || [];
      state.categoryCounts = data.statistics.category_counts || {};
      state.docTypes = data.statistics.doc_types || [];
      
      buildClientInvertedIndex();
      updateDashboardUI(data.statistics);
      populateLibraryUI();
      document.getElementById('repo-status-text').innerText = 'Online (21 Docs)';
      return;
    }
  } catch (err) {
    console.log('Using embedded fallback data...');
  }

  // Fallback to embedded index if API unavailable
  loadEmbeddedFallback();
}

function updateDashboardUI(stats) {
  document.getElementById('kpi-docs').innerText = stats.total_documents || state.documents.length;
  document.getElementById('kpi-vocab').innerText = (stats.unique_words || state.sortedVocabulary.length).toLocaleString();
  document.getElementById('kpi-terms').innerText = (stats.total_terms || 2038).toLocaleString();

  // Categories list
  const catContainer = document.getElementById('categories-list');
  catContainer.innerHTML = '';
  for (const [cat, count] of Object.entries(stats.category_counts || state.categoryCounts)) {
    const row = document.createElement('div');
    row.className = 'cat-row';
    row.innerHTML = `<span>📁 ${cat}</span><span class="badge">${count} documents</span>`;
    row.style.cursor = 'pointer';
    row.onclick = () => {
      document.getElementById('filter-category').value = cat;
      switchView('search');
    };
    catContainer.appendChild(row);
  }

  // Recent notices
  const recentContainer = document.getElementById('recent-notices-list');
  recentContainer.innerHTML = '';
  const recent = [...state.documents].sort((a,b) => b.date.localeCompare(a.date)).slice(0, 5);
  for (const doc of recent) {
    const item = document.createElement('div');
    item.className = 'recent-item';
    item.innerHTML = `
      <div class="recent-meta">
        <span>${doc.category}</span>
        <span>📅 ${doc.date}</span>
      </div>
      <div class="recent-title">${doc.title}</div>
    `;
    item.style.cursor = 'pointer';
    item.onclick = () => openDocModal(doc);
    recentContainer.appendChild(item);
  }
}

// Client-side Inverted Index Builder
function buildClientInvertedIndex() {
  state.invertedIndex = {};
  const vocabSet = new Set();

  for (const doc of state.documents) {
    const words = cleanText(doc.body).split(/\s+/).filter(w => w);
    words.forEach((word, idx) => {
      vocabSet.add(word);
      if (!state.invertedIndex[word]) state.invertedIndex[word] = {};
      if (!state.invertedIndex[word][doc.doc_id]) state.invertedIndex[word][doc.doc_id] = [];
      state.invertedIndex[word][doc.doc_id].push(idx + 1);
    });
  }

  state.unsortedVocabulary = Array.from(vocabSet);
  state.sortedVocabulary = [...state.unsortedVocabulary].sort();
}

function cleanText(text) {
  if (!text) return '';
  return text.toLowerCase().replace(/[^\w\s]/g, ' ');
}

// ==============================================================================
// SEARCH IMPLEMENTATION
// ==============================================================================
function setupSearchActions() {
  const searchInput = document.getElementById('global-search-input');
  const searchBtn = document.getElementById('search-action-btn');

  searchBtn.addEventListener('click', () => executeSearch(searchInput.value));
  searchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') executeSearch(searchInput.value);
  });

  // Suggestion Pills
  document.querySelectorAll('.pill-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const q = btn.getAttribute('data-query');
      searchInput.value = q;
      executeSearch(q);
    });
  });

  // Toggle Traces Button
  document.getElementById('toggle-traces-btn').addEventListener('click', () => {
    const details = document.getElementById('traces-content');
    details.classList.toggle('hidden');
  });
}

function executeSearch(rawQuery) {
  const query = cleanText(rawQuery).trim();
  if (!query) return;

  const algo = document.getElementById('filter-algorithm').value;
  const category = document.getElementById('filter-category').value;
  const docType = document.getElementById('filter-doc-type').value;

  // Make results container visible
  const resultsSec = document.getElementById('search-results-section');
  resultsSec.classList.remove('hidden');

  // Try API first, fallback to client evaluation
  fetch(`/api/search?q=${encodeURIComponent(query)}&algo=${algo}&category=${encodeURIComponent(category)}&doc_type=${encodeURIComponent(docType)}`)
    .then(r => r.json())
    .then(data => renderSearchResultsUI(data))
    .catch(() => {
      const clientRes = performClientSearch(query, algo, category, docType);
      renderSearchResultsUI(clientRes);
    });

  // Scroll smoothly to results
  resultsSec.scrollIntoView({ behavior: 'smooth' });
}

// Client-side search algorithm execution
function performClientSearch(query, algo, category, docType) {
  let linRes = null;
  let binRes = null;

  if (algo === 'linear' || algo === 'compare_both') {
    linRes = runLinearSearch(state.sortedVocabulary, query);
  }
  if (algo === 'binary' || algo === 'compare_both') {
    binRes = runBinarySearch(state.sortedVocabulary, query);
  }

  const postings = state.invertedIndex[query] || {};
  const items = [];
  let totalOccurrences = 0;

  for (const [docId, positions] of Object.entries(postings)) {
    const doc = state.documents.find(d => d.doc_id === docId);
    if (!doc) continue;

    if (category !== 'All Categories' && doc.category !== category) continue;
    if (docType !== 'All Types' && doc.doc_type !== docType) continue;

    totalOccurrences += positions.length;
    items.push({
      doc_id: doc.doc_id,
      title: doc.title,
      category: doc.category,
      doc_type: doc.doc_type,
      department: doc.department,
      date: doc.date,
      occurrences_count: positions.length,
      positions: positions,
      snippet: extractSnippet(doc.body, query)
    });
  }

  items.sort((a,b) => b.occurrences_count - a.occurrences_count);

  return {
    query: query,
    found: items.length > 0,
    algorithm_mode: algo,
    total_matching_documents: items.length,
    total_occurrences: totalOccurrences,
    linear_metrics: linRes,
    binary_metrics: binRes,
    items: items
  };
}

function extractSnippet(text, target, len = 160) {
  if (!text || !target) return '';
  const lower = text.toLowerCase();
  const pos = lower.indexOf(target.toLowerCase());
  if (pos === -1) return text.slice(0, len).trim() + '...';

  const start = Math.max(0, pos - Math.floor(len / 2));
  const end = Math.min(text.length, pos + target.length + Math.floor(len / 2));
  let snip = text.slice(start, end).trim();
  if (start > 0) snip = '...' + snip;
  if (end < text.length) snip = snip + '...';
  return snip;
}

// Manual Linear Search
function runLinearSearch(arr, target) {
  const t0 = performance.now();
  let comparisons = 0;
  let found = false;
  let index = -1;
  const trace = [];

  for (let i = 0; i < arr.length; i++) {
    comparisons++;
    const isMatch = (arr[i] === target);
    if (trace.length < 50) {
      trace.push({
        step: comparisons,
        index: i,
        term: arr[i],
        match: isMatch
      });
    }
    if (isMatch) {
      found = true;
      index = i;
      break;
    }
  }

  const elapsed = performance.now() - t0;
  return {
    found: found,
    index: index,
    comparisons: comparisons,
    execution_time_ms: elapsed,
    trace: trace
  };
}

// Manual Iterative Binary Search
function runBinarySearch(sortedArr, target) {
  const t0 = performance.now();
  let comparisons = 0;
  let found = false;
  let index = -1;
  const trace = [];

  let left = 0;
  let right = sortedArr.length - 1;
  let step = 0;

  while (left <= right) {
    step++;
    const mid = left + Math.floor((right - left) / 2);
    const midVal = sortedArr[mid];
    comparisons++;

    if (midVal === target) {
      found = true;
      index = mid;
      trace.push({
        step: step, left: left, right: right, mid: mid,
        term: midVal, action: 'Match Found! Terminate.'
      });
      break;
    } else if (target < midVal) {
      trace.push({
        step: step, left: left, right: right, mid: mid,
        term: midVal, action: `Prune right half -> right = ${mid - 1}`
      });
      right = mid - 1;
    } else {
      trace.push({
        step: step, left: left, right: right, mid: mid,
        term: midVal, action: `Prune left half -> left = ${mid + 1}`
      });
      left = mid + 1;
    }
  }

  const elapsed = performance.now() - t0;
  return {
    found: found,
    index: index,
    comparisons: comparisons,
    execution_time_ms: elapsed,
    trace: trace
  };
}

function renderSearchResultsUI(data) {
  document.getElementById('results-title').innerText = `Search Results for "${data.query}"`;
  document.getElementById('results-count-badge').innerText = `${data.total_matching_documents} Document(s)`;

  // Algorithm comparison metrics
  const algoBar = document.getElementById('algo-comparison-bar');
  const insightBanner = document.getElementById('algo-insight-banner');

  if (data.linear_metrics && data.binary_metrics) {
    algoBar.classList.remove('hidden');
    document.getElementById('lin-comps').innerText = data.linear_metrics.comparisons;
    document.getElementById('lin-time').innerText = `${data.linear_metrics.execution_time_ms.toFixed(4)} ms`;
    document.getElementById('bin-comps').innerText = data.binary_metrics.comparisons;
    document.getElementById('bin-time').innerText = `${data.binary_metrics.execution_time_ms.toFixed(4)} ms`;

    if (data.linear_metrics.comparisons > data.binary_metrics.comparisons) {
      insightBanner.classList.remove('hidden');
      const diff = data.linear_metrics.comparisons - data.binary_metrics.comparisons;
      const ratio = (data.linear_metrics.comparisons / Math.max(1, data.binary_metrics.comparisons)).toFixed(1);
      insightBanner.innerHTML = `⚡ <b>Algorithmic Efficiency:</b> Binary Search took <b>${diff} fewer comparisons</b> (${ratio}x reduction in operations) than Linear Search to locate "${data.query}"!`;
    } else {
      insightBanner.classList.add('hidden');
    }
  } else {
    algoBar.classList.add('hidden');
    insightBanner.classList.add('hidden');
  }

  // Cards List
  const cardsContainer = document.getElementById('results-cards-list');
  cardsContainer.innerHTML = '';

  if (!data.items || data.items.length === 0) {
    cardsContainer.innerHTML = `
      <div class="result-card">
        <p style="color: #94A3B8;">No campus documents matched keyword <b>"${data.query}"</b> with the selected filters.</p>
        <p style="font-size: 0.85rem; color: #64748B; margin-top: 6px;">Try broader terms: examination, syllabus, attendance, placement, hackathon, library.</p>
      </div>
    `;
    document.getElementById('traces-container').classList.add('hidden');
    return;
  }

  data.items.forEach((item, idx) => {
    const card = document.createElement('div');
    card.className = 'result-card';
    card.innerHTML = `
      <div class="result-header">
        <span class="result-title">${idx + 1}. ${item.title}</span>
        <span class="badge">${item.category}</span>
      </div>
      <div class="result-meta-row">
        <span><b>File:</b> ${item.doc_id}</span>
        <span><b>Department:</b> ${item.department}</span>
        <span><b>Type:</b> ${item.doc_type}</span>
        <span><b>Date:</b> ${item.date}</span>
        <span style="color: #FBBF24;"><b>Occurrences:</b> ${item.occurrences_count}</span>
      </div>
      <div class="result-snippet">"${item.snippet}"</div>
      <div class="result-actions">
        <button class="link-btn" onclick="openDocModalById('${item.doc_id}')">📄 Read Full Document</button>
        <span style="font-size: 0.8rem; color: #64748B;">Word Offsets: [${item.positions.slice(0, 8).join(', ')}${item.positions.length > 8 ? '...' : ''}]</span>
      </div>
    `;
    cardsContainer.appendChild(card);
  });

  // Populate Traces
  renderTracesUI(data.linear_metrics, data.binary_metrics);
}

function renderTracesUI(lin, bin) {
  const container = document.getElementById('traces-container');
  if (!lin && !bin) {
    container.classList.add('hidden');
    return;
  }
  container.classList.remove('hidden');

  // Binary trace table
  const binContainer = document.getElementById('bin-trace-table-container');
  if (bin && bin.trace && bin.trace.length > 0) {
    let html = '<div class="trace-scroll-box">';
    bin.trace.forEach(step => {
      html += `<div class="trace-item">Step ${step.step}: L=${step.left}, R=${step.right}, Mid=${step.mid} (${step.term}) &rarr; ${step.action}</div>`;
    });
    html += '</div>';
    binContainer.innerHTML = html;
  } else {
    binContainer.innerHTML = '<p class="section-desc">No trace available.</p>';
  }

  // Linear trace table
  const linContainer = document.getElementById('lin-trace-table-container');
  if (lin && lin.trace && lin.trace.length > 0) {
    let html = '<div class="trace-scroll-box">';
    lin.trace.forEach(step => {
      html += `<div class="trace-item">Step ${step.step}: Index ${step.index} (${step.term}) &rarr; ${step.match ? 'MATCH FOUND' : 'Mismatch'}</div>`;
    });
    html += '</div>';
    linContainer.innerHTML = html;
  } else {
    linContainer.innerHTML = '<p class="section-desc">No trace available.</p>';
  }
}

// ==============================================================================
// DOCUMENT LIBRARY & UPLOAD
// ==============================================================================
function setupDocumentLibrary() {
  const searchInput = document.getElementById('library-filter-input');
  const catFilter = document.getElementById('library-cat-filter');

  searchInput.addEventListener('input', populateLibraryUI);
  catFilter.addEventListener('change', populateLibraryUI);

  // Upload Modal handling
  const modal = document.getElementById('upload-modal');
  document.getElementById('open-upload-btn').addEventListener('click', () => modal.classList.remove('hidden'));
  document.querySelectorAll('.close-modal-btn, #cancel-upload-btn').forEach(btn => {
    btn.addEventListener('click', () => modal.classList.add('hidden'));
  });

  const fileInput = document.getElementById('upload-file-input');
  fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (evt) => {
        document.getElementById('upload-doc-body').value = evt.target.result;
        if (!document.getElementById('upload-doc-title').value) {
          document.getElementById('upload-doc-title').value = file.name.replace('.txt', '');
        }
      };
      reader.readAsText(file);
    }
  });

  document.getElementById('submit-upload-btn').addEventListener('click', () => {
    const title = document.getElementById('upload-doc-title').value.trim() || 'Custom Document';
    const cat = document.getElementById('upload-doc-cat').value;
    const body = document.getElementById('upload-doc-body').value.trim();

    if (!body) {
      alert('Please provide document text to index.');
      return;
    }

    const filename = `uploaded_${Date.now()}.txt`;
    const newDoc = {
      doc_id: filename,
      filename: filename,
      title: title,
      category: cat,
      doc_type: 'Custom Upload',
      department: 'Campus Administration',
      date: new Date().toISOString().split('T')[0],
      total_words: body.split(/\s+/).length,
      unique_words: new Set(cleanText(body).split(/\s+/)).size,
      body: body
    };

    state.documents.push(newDoc);
    buildClientInvertedIndex();
    populateLibraryUI();
    modal.classList.add('hidden');
    alert(`Successfully indexed "${title}"! You can now search for its contents.`);
  });
}

function populateLibraryUI() {
  const grid = document.getElementById('library-grid');
  const query = document.getElementById('library-filter-input').value.toLowerCase();
  const cat = document.getElementById('library-cat-filter').value;

  // Update cat select options if empty
  const catFilter = document.getElementById('library-cat-filter');
  if (catFilter.options.length <= 1) {
    state.categories.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c;
      opt.innerText = c;
      catFilter.appendChild(opt);
    });
  }

  const filtered = state.documents.filter(doc => {
    const matchCat = (cat === 'All' || doc.category === cat);
    const matchQ = (!query || doc.title.toLowerCase().includes(query) || doc.body.toLowerCase().includes(query));
    return matchCat && matchQ;
  });

  grid.innerHTML = '';
  filtered.forEach(doc => {
    const card = document.createElement('div');
    card.className = 'library-card';
    card.innerHTML = `
      <div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 6px;">
          <span class="badge">${doc.category}</span>
          <span style="font-size: 0.78rem; color: #64748B;">📅 ${doc.date}</span>
        </div>
        <h4>${doc.title}</h4>
        <div class="library-card-meta">
          <span><b>File:</b> ${doc.filename}</span> &bull; 
          <span>${doc.total_words} words</span>
        </div>
      </div>
      <div>
        <button class="secondary-btn" style="width: 100%;" onclick="openDocModalById('${doc.doc_id}')">Read Full Document</button>
      </div>
    `;
    grid.appendChild(card);
  });
}

// Modal Viewers
window.openDocModalById = function(docId) {
  const doc = state.documents.find(d => d.doc_id === docId);
  if (doc) openDocModal(doc);
};

function openDocModal(doc) {
  const modal = document.getElementById('doc-modal');
  document.getElementById('modal-doc-title').innerText = doc.title;
  document.getElementById('modal-doc-meta').innerHTML = `
    <span><b>Category:</b> ${doc.category}</span> &nbsp;|&nbsp;
    <span><b>Type:</b> ${doc.doc_type}</span> &nbsp;|&nbsp;
    <span><b>Department:</b> ${doc.department}</span> &nbsp;|&nbsp;
    <span><b>Date:</b> ${doc.date}</span>
  `;
  document.getElementById('modal-doc-content').innerText = doc.body;
  modal.classList.remove('hidden');
}

// ==============================================================================
// ALGORITHM LAB
// ==============================================================================
function setupAlgorithmLab() {
  const runBtn = document.getElementById('run-lab-btn');
  const targetInput = document.getElementById('lab-target-input');

  runBtn.addEventListener('click', () => {
    const target = cleanText(targetInput.value).trim();
    if (!target) return;

    const lin = runLinearSearch(state.sortedVocabulary, target);
    const bin = runBinarySearch(state.sortedVocabulary, target);

    document.getElementById('lab-lin-status').innerText = lin.found ? 'Found ✅' : 'Not Found ❌';
    document.getElementById('lab-lin-comps').innerText = lin.comparisons;
    document.getElementById('lab-lin-time').innerText = `${lin.execution_time_ms.toFixed(4)} ms`;

    document.getElementById('lab-bin-status').innerText = bin.found ? 'Found ✅' : 'Not Found ❌';
    document.getElementById('lab-bin-comps').innerText = bin.comparisons;
    document.getElementById('lab-bin-time').innerText = `${bin.execution_time_ms.toFixed(4)} ms`;

    // Linear steps
    let linHtml = '';
    lin.trace.forEach(s => {
      linHtml += `<div class="trace-item">Step ${s.step}: Index ${s.index} &rarr; "${s.term}" (${s.match ? 'MATCH' : 'Mismatch'})</div>`;
    });
    document.getElementById('lab-lin-trace-box').innerHTML = linHtml || 'No steps.';

    // Binary steps
    let binHtml = '';
    bin.trace.forEach(s => {
      binHtml += `<div class="trace-item">Step ${s.step}: [${s.left}..${s.right}], mid=${s.mid} ("${s.term}") &rarr; ${s.action}</div>`;
    });
    document.getElementById('lab-bin-trace-box').innerHTML = binHtml || 'No steps.';
  });

  // Unsorted Failure Demo
  document.getElementById('run-unsorted-experiment-btn').addEventListener('click', () => {
    const box = document.getElementById('unsorted-exp-result');
    box.classList.remove('hidden');

    const sampleWord = state.unsortedVocabulary[15] || 'examination';
    const lRes = runLinearSearch(state.unsortedVocabulary, sampleWord);
    const bRes = runBinarySearch(state.unsortedVocabulary, sampleWord);

    box.innerHTML = `
      <p><b>Target Word:</b> <code>"${sampleWord}"</code> (Guaranteed to exist in vocabulary)</p>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 10px;">
        <div style="background: #0B1120; padding: 10px; border-radius: 6px;">
          <b style="color: #F43F5E;">Linear Search on Unsorted:</b><br>
          Result: ${lRes.found ? 'Found ✅' : 'Not Found ❌'} (${lRes.comparisons} comparisons)<br>
          <small style="color: #10B981;">Succeeded because it checks every item sequentially without ordering assumptions.</small>
        </div>
        <div style="background: #0B1120; padding: 10px; border-radius: 6px;">
          <b style="color: #38BDF8;">Binary Search on Unsorted:</b><br>
          Result: ${bRes.found ? 'Found ✅' : 'FAILED / MISSED ❌'} (${bRes.comparisons} comparisons)<br>
          <small style="color: #EF4444;">${bRes.found ? 'Stumbled by coincidence.' : 'Failed because unsorted array caused it to prune the wrong partition!'}</small>
        </div>
      </div>
    `;
  });
}

// ==============================================================================
// BENCHMARKING SUITE & CHART.JS
// ==============================================================================
function setupBenchmarking() {
  document.getElementById('run-benchmark-btn').addEventListener('click', runBenchmarkSuite);
}

function runBenchmarkSuite() {
  const scenario = document.getElementById('bench-scenario').value;
  const iterations = parseInt(document.getElementById('bench-iterations').value);
  const sizes = [100, 500, 1000, 5000, 10000];

  const tbody = document.getElementById('bench-table-body');
  tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;">Executing live empirical tests...</td></tr>';

  // Run synthetic benchmark
  setTimeout(() => {
    const points = [];

    sizes.forEach(n => {
      const vocab = generateSyntheticVocab(n, state.sortedVocabulary);
      let totalLinTime = 0, totalBinTime = 0;
      let totalLinComps = 0, totalBinComps = 0;

      for (let iter = 0; iter < iterations; iter++) {
        let target;
        if (scenario === 'best_case') target = vocab[Math.floor((n - 1) / 2)];
        else if (scenario === 'worst_case') target = vocab[n - 1];
        else if (scenario === 'unsuccessful') target = 'zz_missing_term_9999';
        else target = vocab[Math.floor(Math.random() * n)];

        const l = runLinearSearch(vocab, target);
        const b = runBinarySearch(vocab, target);

        totalLinTime += l.execution_time_ms;
        totalBinTime += b.execution_time_ms;
        totalLinComps += l.comparisons;
        totalBinComps += b.comparisons;
      }

      const theoLin = (scenario === 'worst_case' || scenario === 'unsuccessful') ? n : Math.floor(n / 2);
      const theoBin = Math.ceil(Math.log2(n + 1));

      points.push({
        size: n,
        linTime: totalLinTime / iterations,
        binTime: totalBinTime / iterations,
        linComps: Math.round(totalLinComps / iterations),
        binComps: Math.round(totalBinComps / iterations),
        theoLin: theoLin,
        theoBin: theoBin
      });
    });

    renderBenchmarkTable(points);
    renderBenchmarkCharts(points);
  }, 50);
}

function generateSyntheticVocab(size, seeds) {
  const base = seeds.length > 0 ? seeds : ['campus', 'exam', 'syllabus', 'notice', 'library'];
  const set = new Set(base.slice(0, size));
  let count = 1;
  while (set.size < size) {
    const w = base[(count - 1) % base.length];
    set.add(`${w}_${String(count).padStart(5, '0')}`);
    count++;
  }
  return Array.from(set).sort();
}

function renderBenchmarkTable(points) {
  const tbody = document.getElementById('bench-table-body');
  tbody.innerHTML = '';

  points.forEach(p => {
    const tr = document.createElement('tr');
    const ratio = (p.linComps / Math.max(1, p.binComps)).toFixed(1);
    tr.innerHTML = `
      <td><b>${p.size.toLocaleString()}</b></td>
      <td>${p.linTime.toFixed(4)} ms</td>
      <td>${p.binTime.toFixed(4)} ms</td>
      <td style="color: #F43F5E;">${p.linComps.toLocaleString()}</td>
      <td style="color: #38BDF8;">${p.binComps.toLocaleString()}</td>
      <td style="color: #10B981; font-weight:700;">${ratio}x</td>
      <td>${p.theoLin.toLocaleString()}</td>
      <td>${p.theoBin}</td>
    `;
    tbody.appendChild(tr);
  });
}

function renderBenchmarkCharts(points) {
  const labels = points.map(p => p.size.toLocaleString());
  const linTimes = points.map(p => p.linTime);
  const binTimes = points.map(p => p.binTime);
  const linComps = points.map(p => p.linComps);
  const binComps = points.map(p => p.binComps);
  const theoBin = points.map(p => p.theoBin);

  // Destroy previous charts if existing
  Object.values(state.benchmarkCharts).forEach(c => c.destroy());
  state.benchmarkCharts = {};

  const commonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { labels: { color: '#F8FAFC', font: { family: 'Inter' } } }
    },
    scales: {
      x: { ticks: { color: '#94A3B8' }, grid: { color: '#334155' } },
      y: { ticks: { color: '#94A3B8' }, grid: { color: '#334155' } }
    }
  };

  // Chart 1: Time Comparison
  state.benchmarkCharts.c1 = new Chart(document.getElementById('chart-exec-time'), {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        { label: 'Linear Search O(n)', data: linTimes, borderColor: '#F43F5E', backgroundColor: 'rgba(244, 63, 94, 0.2)', borderWidth: 2.5, tension: 0.2 },
        { label: 'Binary Search O(log n)', data: binTimes, borderColor: '#38BDF8', backgroundColor: 'rgba(56, 189, 248, 0.2)', borderWidth: 2.5, tension: 0.2 }
      ]
    },
    options: commonOptions
  });

  // Chart 2: Comparison Counts
  state.benchmarkCharts.c2 = new Chart(document.getElementById('chart-comps'), {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        { label: 'Linear Comparisons O(n)', data: linComps, borderColor: '#F43F5E', backgroundColor: 'rgba(244, 63, 94, 0.2)', borderWidth: 2.5, tension: 0.2 },
        { label: 'Binary Comparisons O(log n)', data: binComps, borderColor: '#10B981', backgroundColor: 'rgba(16, 185, 129, 0.2)', borderWidth: 2.5, tension: 0.2 }
      ]
    },
    options: commonOptions
  });

  // Chart 3: Grouped Bar Times
  state.benchmarkCharts.c3 = new Chart(document.getElementById('chart-grouped-time'), {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        { label: 'Linear Time (ms)', data: linTimes, backgroundColor: '#F43F5E' },
        { label: 'Binary Time (ms)', data: binTimes, backgroundColor: '#38BDF8' }
      ]
    },
    options: commonOptions
  });

  // Chart 4: Log Curve vs Theoretical
  state.benchmarkCharts.c4 = new Chart(document.getElementById('chart-log-curve'), {
    type: 'line',
    data: {
      labels: labels,
      datasets: [
        { label: 'Empirical Binary Comps', data: binComps, borderColor: '#10B981', borderWidth: 2.5, tension: 0.1 },
        { label: 'Theoretical ceil(log2 N)', data: theoBin, borderColor: '#FBBF24', borderDash: [5, 5], borderWidth: 2, tension: 0.1 }
      ]
    },
    options: commonOptions
  });
}

// ==============================================================================
// EDUCATIONAL SIMULATOR
// ==============================================================================
function setupEducationalMode() {
  const btn = document.getElementById('run-dry-btn');
  btn.addEventListener('click', runDryRunSimulator);
  runDryRunSimulator();
}

function runDryRunSimulator() {
  const rawArr = document.getElementById('dry-array-input').value;
  const target = document.getElementById('dry-target-input').value.trim();
  const tbody = document.getElementById('dry-run-table-body');
  tbody.innerHTML = '';

  const arr = rawArr.split(',').map(s => s.trim()).filter(s => s);
  const isNums = arr.every(s => !isNaN(Number(s)));
  const typedArr = isNums ? arr.map(Number) : arr;
  const typedTarget = isNums ? Number(target) : target;

  let left = 0;
  let right = typedArr.length - 1;
  let step = 0;

  while (left <= right) {
    step++;
    const mid = left + Math.floor((right - left) / 2);
    const val = typedArr[mid];
    const tr = document.createElement('tr');

    let action = '';
    let comp = '';

    if (val === typedTarget) {
      comp = `${typedTarget} == ${val}`;
      action = '<span style="color:#10B981; font-weight:700;">Exact Match Found! Halt.</span>';
      tr.innerHTML = `<td>${step}</td><td>${left}</td><td>${right}</td><td>${mid}</td><td><b>${val}</b></td><td>${comp}</td><td>${action}</td>`;
      tbody.appendChild(tr);
      break;
    } else if (typedTarget < val) {
      comp = `${typedTarget} < ${val}`;
      action = `Prune right half &rarr; right = ${mid - 1}`;
      right = mid - 1;
    } else {
      comp = `${typedTarget} > ${val}`;
      action = `Prune left half &rarr; left = ${mid + 1}`;
      left = mid + 1;
    }

    tr.innerHTML = `<td>${step}</td><td>${left}</td><td>${right}</td><td>${mid}</td><td><b>${val}</b></td><td>${comp}</td><td>${action}</td>`;
    tbody.appendChild(tr);
  }
}

// ==============================================================================
// VIVA PREP ACCORDIONS
// ==============================================================================
function setupViva() {
  const list = document.getElementById('viva-accordion-list');
  const search = document.getElementById('viva-search-input');

  function render(filter = '') {
    list.innerHTML = '';
    const qFilt = filter.toLowerCase();

    VIVA_QUESTIONS.forEach((item, idx) => {
      if (qFilt && !item.q.toLowerCase().includes(qFilt) && !item.a.toLowerCase().includes(qFilt)) return;

      const card = document.createElement('div');
      card.className = 'viva-card';
      card.innerHTML = `
        <div class="viva-q">
          <span>${item.q}</span>
          <span style="color: #38BDF8;">+</span>
        </div>
        <div class="viva-a hidden">${item.a}</div>
      `;

      card.querySelector('.viva-q').addEventListener('click', () => {
        const a = card.querySelector('.viva-a');
        const isHidden = a.classList.toggle('hidden');
        card.querySelector('.viva-q span:last-child').innerText = isHidden ? '+' : '&minus;';
      });

      list.appendChild(card);
    });
  }

  search.addEventListener('input', (e) => render(e.target.value));
  render();
}

// ==============================================================================
// NAVIGATION
// ==============================================================================
function setupNavigation() {
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const view = btn.getAttribute('data-view');
      switchView(view);
    });
  });
}

function switchView(viewName) {
  state.activeView = viewName;
  document.querySelectorAll('.nav-btn').forEach(b => {
    b.classList.toggle('active', b.getAttribute('data-view') === viewName);
  });

  document.querySelectorAll('.content-view').forEach(v => {
    v.classList.add('hidden');
  });

  const targetView = document.getElementById(`view-${viewName}`);
  if (targetView) targetView.classList.remove('hidden');

  if (viewName === 'benchmark' && Object.keys(state.benchmarkCharts).length === 0) {
    runBenchmarkSuite();
  }
}

// ==============================================================================
// EMBEDDED FALLBACK DATA
// ==============================================================================
function loadEmbeddedFallback() {
  const defaultDocs = [
    {
      doc_id: "doc_01_exam_schedule.txt",
      filename: "doc_01_exam_schedule.txt",
      title: "End-Term Theory Examination Schedule Autumn 2026",
      category: "Examination Notices",
      doc_type: "Schedule",
      department: "Examination Cell",
      date: "2026-10-15",
      body: "All undergraduate and postgraduate students are hereby notified that the End-Term Theory Examinations for the Autumn Semester 2026 will commence on November 25, 2026. Students must carry valid admit card."
    },
    {
      doc_id: "doc_02_admit_card_circular.txt",
      filename: "doc_02_admit_card_circular.txt",
      title: "Hall Ticket and Admit Card Distribution Guidelines",
      category: "Examination Notices",
      doc_type: "Circular",
      department: "Examination Cell",
      date: "2026-10-20",
      body: "The Controller of Examinations announces that digital Hall Tickets and Admit Cards for upcoming semester examinations are available. Minimum 75 percent attendance is mandatory."
    },
    {
      doc_id: "doc_05_attendance_policy.txt",
      filename: "doc_05_attendance_policy.txt",
      title: "Mandatory 75 Percent Minimum Attendance Policy",
      category: "Academic Circulars",
      doc_type: "Regulation",
      department: "Dean of Academic Affairs",
      date: "2026-08-10",
      body: "Maintaining minimum attendance of 75 percent in each enrolled lecture and practical laboratory course is mandatory for all students on CampusFind."
    },
    {
      doc_id: "doc_07_daa_syllabus.txt",
      filename: "doc_07_daa_syllabus.txt",
      title: "Course Syllabus: Design and Analysis of Algorithms",
      category: "Course Syllabus",
      doc_type: "Syllabus",
      department: "Computer Science and Engineering",
      date: "2026-08-01",
      body: "Module 1 introduces algorithm analysis, asymptotic notation Big O, Big Omega, Master Theorem. Module 2 covers Divide and Conquer strategies, analyzing Linear Search and Binary Search."
    },
    {
      doc_id: "doc_14_hackathon_announcement.txt",
      filename: "doc_14_hackathon_announcement.txt",
      title: "Smart Campus Annual 36-Hour Hackathon 2026",
      category: "Event Announcements",
      doc_type: "Announcement",
      department: "Innovation and Incubation Center",
      date: "2026-09-01",
      body: "The flagship Smart Campus 36-Hour Hackathon 2026 takes place in October. Themes include Smart Campus Automation, Intelligent Information Retrieval, and Search Engines."
    },
    {
      doc_id: "doc_17_campus_placement_policy.txt",
      filename: "doc_17_campus_placement_policy.txt",
      title: "Campus Recruitment Guidelines and Eligibility Policy",
      category: "Placement Notifications",
      doc_type: "Policy",
      department: "Training and Placement Cell",
      date: "2026-08-20",
      body: "Guidelines governing the Campus Placement Season. Eligibility criteria require minimum aggregate CGPA of 6.5 across completed semesters with no active backlogs."
    },
    {
      doc_id: "doc_19_library_guidelines.txt",
      filename: "doc_19_library_guidelines.txt",
      title: "Central Library Borrowing Rules and Digital Access Policy",
      category: "Student Guidelines",
      doc_type: "Guidelines",
      department: "Central Library",
      date: "2026-08-01",
      body: "The Central Library provides textbooks, monographs, and digital academic subscriptions. Students may borrow four physical volumes for fourteen days."
    }
  ];

  state.documents = defaultDocs;
  const cats = {};
  defaultDocs.forEach(d => {
    cats[d.category] = (cats[d.category] || 0) + 1;
  });
  state.categoryCounts = cats;
  state.categories = Object.keys(cats);

  buildClientInvertedIndex();
  updateDashboardUI({
    total_documents: defaultDocs.length,
    unique_words: state.sortedVocabulary.length,
    total_terms: 2038,
    category_counts: cats
  });
  populateLibraryUI();
  document.getElementById('repo-status-text').innerText = 'Online (Standby Mode)';
}

