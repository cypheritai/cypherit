// CypherIt Chrome Extension - Popup Logic

const CYPHERIT_URL = 'https://cypherit.ai';

document.addEventListener('DOMContentLoaded', async () => {
  const contentEl = document.getElementById('content');
  
  // Get current tab
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const url = tab.url || '';
  
  // Check if we're on YouTube
  if (!isYouTubeVideo(url)) {
    showNotYouTube(contentEl);
    return;
  }
  
  // Extract video info
  const videoId = extractVideoId(url);
  const title = tab.title?.replace(' - YouTube', '').trim() || 'YouTube Video';
  
  showVideoInfo(contentEl, { url, videoId, title });
});

function isYouTubeVideo(url) {
  return url.includes('youtube.com/watch') || url.includes('youtu.be/');
}

function extractVideoId(url) {
  const patterns = [
    /[?&]v=([^&]+)/,           // youtube.com/watch?v=ID
    /youtu\.be\/([^?&]+)/,     // youtu.be/ID
    /embed\/([^?&]+)/,         // youtube.com/embed/ID
  ];
  
  for (const pattern of patterns) {
    const match = url.match(pattern);
    if (match) return match[1];
  }
  return null;
}

function showNotYouTube(container) {
  container.innerHTML = `
    <div class="not-youtube">
      <div class="not-youtube-icon">📺</div>
      <p>Navigate to a YouTube video to extract the steps!</p>
      <button class="open-site-btn" id="openSiteBtn">Open CypherIt</button>
    </div>
  `;
  
  document.getElementById('openSiteBtn').addEventListener('click', () => {
    chrome.tabs.create({ url: CYPHERIT_URL });
  });
}

function showVideoInfo(container, { url, videoId, title }) {
  container.innerHTML = `
    <div class="video-info">
      <div class="video-title">${escapeHtml(title)}</div>
      <div class="video-url">${escapeHtml(url.substring(0, 50))}...</div>
    </div>
    <button class="extract-btn" id="extractBtn">
      🔧 Extract Steps
    </button>
    <button class="open-site-btn" id="openWithUrlBtn">
      Open in CypherIt
    </button>
    <div class="status" id="status"></div>
  `;
  
  const extractBtn = document.getElementById('extractBtn');
  const openWithUrlBtn = document.getElementById('openWithUrlBtn');
  const statusEl = document.getElementById('status');
  
  // Extract steps via API
  extractBtn.addEventListener('click', async () => {
    extractBtn.disabled = true;
    extractBtn.classList.add('loading');
    extractBtn.innerHTML = '<span class="spinner"></span> Extracting...';
    statusEl.textContent = '';
    statusEl.className = 'status';
    
    try {
      // Call CypherIt API directly
      const response = await fetch(`${CYPHERIT_URL}/extract`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });
      
      if (!response.ok) {
        throw new Error('Extraction failed');
      }
      
      const data = await response.json();
      
      // Open CypherIt with the video ID to show cached result
      const resultUrl = `${CYPHERIT_URL}?v=${videoId}`;
      chrome.tabs.create({ url: resultUrl });
      
      statusEl.textContent = '✅ Steps extracted!';
      statusEl.className = 'status success';
      
    } catch (error) {
      console.error('Extraction error:', error);
      statusEl.textContent = '❌ Failed. Try opening in CypherIt.';
      statusEl.className = 'status error';
    } finally {
      extractBtn.disabled = false;
      extractBtn.classList.remove('loading');
      extractBtn.innerHTML = '🔧 Extract Steps';
    }
  });
  
  // Open CypherIt with URL pre-filled
  openWithUrlBtn.addEventListener('click', () => {
    const cypheritUrl = `${CYPHERIT_URL}?url=${encodeURIComponent(url)}`;
    chrome.tabs.create({ url: cypheritUrl });
  });
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
