// CypherIt Chrome Extension - Content Script
// Injects "Extract Steps" button on YouTube video pages

const CYPHERIT_URL = 'https://cypherit.ai';

let buttonInjected = false;

function injectCypherItButton() {
  // Don't inject twice
  if (buttonInjected || document.getElementById('cypherit-extract-btn')) return;
  
  // Find the YouTube actions area (below video, next to like/share)
  const actionsContainer = document.querySelector('#top-level-buttons-computed');
  if (!actionsContainer) return;
  
  // Create our button
  const btn = document.createElement('button');
  btn.id = 'cypherit-extract-btn';
  btn.className = 'cypherit-btn';
  btn.innerHTML = `
    <span class="cypherit-icon">🔧</span>
    <span class="cypherit-text">Get Steps</span>
  `;
  
  btn.addEventListener('click', handleExtract);
  
  // Insert at the end of actions
  actionsContainer.appendChild(btn);
  buttonInjected = true;
  
  console.log('[CypherIt] Button injected');
}

async function handleExtract() {
  const btn = document.getElementById('cypherit-extract-btn');
  const videoUrl = window.location.href;
  
  // Get video ID
  const videoId = new URLSearchParams(window.location.search).get('v');
  if (!videoId) {
    alert('Could not detect video ID');
    return;
  }
  
  // Update button state
  btn.classList.add('loading');
  btn.innerHTML = `
    <span class="cypherit-spinner"></span>
    <span class="cypherit-text">Extracting...</span>
  `;
  
  try {
    // Call CypherIt API
    const response = await fetch(`${CYPHERIT_URL}/extract`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url: videoUrl })
    });
    
    if (!response.ok) throw new Error('Failed');
    
    // Open result in new tab
    window.open(`${CYPHERIT_URL}?v=${videoId}`, '_blank');
    
    btn.innerHTML = `
      <span class="cypherit-icon">✅</span>
      <span class="cypherit-text">Done!</span>
    `;
    
    setTimeout(() => {
      btn.innerHTML = `
        <span class="cypherit-icon">🔧</span>
        <span class="cypherit-text">Get Steps</span>
      `;
      btn.classList.remove('loading');
    }, 2000);
    
  } catch (error) {
    console.error('[CypherIt] Error:', error);
    
    // Fallback: open CypherIt with URL
    window.open(`${CYPHERIT_URL}?url=${encodeURIComponent(videoUrl)}`, '_blank');
    
    btn.innerHTML = `
      <span class="cypherit-icon">🔧</span>
      <span class="cypherit-text">Get Steps</span>
    `;
    btn.classList.remove('loading');
  }
}

// YouTube is a SPA, so we need to watch for navigation
function watchForNavigation() {
  let lastUrl = location.href;
  
  const observer = new MutationObserver(() => {
    if (location.href !== lastUrl) {
      lastUrl = location.href;
      buttonInjected = false;
      
      // Remove old button if exists
      const oldBtn = document.getElementById('cypherit-extract-btn');
      if (oldBtn) oldBtn.remove();
      
      // Try to inject on new page
      setTimeout(tryInject, 1000);
    }
  });
  
  observer.observe(document.body, { childList: true, subtree: true });
}

function tryInject() {
  // Only on watch pages
  if (!window.location.pathname.includes('/watch')) return;
  
  // Try multiple times (YouTube loads dynamically)
  let attempts = 0;
  const maxAttempts = 10;
  
  const interval = setInterval(() => {
    attempts++;
    injectCypherItButton();
    
    if (buttonInjected || attempts >= maxAttempts) {
      clearInterval(interval);
    }
  }, 500);
}

// Initialize
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    tryInject();
    watchForNavigation();
  });
} else {
  tryInject();
  watchForNavigation();
}
