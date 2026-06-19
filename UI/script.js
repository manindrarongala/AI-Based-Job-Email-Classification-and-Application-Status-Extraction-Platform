// API configuration
const BACKEND_URL = 'https://career-radar.onrender.com';
const API_URL = `${BACKEND_URL}/api/scan-emails`;

// Global State
let currentJobEmails = [];

// DOM Elements
const emailForm = document.getElementById('emailForm');
const emailInput = document.getElementById('email');
const appPasswordInput = document.getElementById('appPassword');
const scanBtn = document.getElementById('scanBtn');
const btnText = scanBtn.querySelector('.btn-text');
const btnLoaderText = scanBtn.querySelector('.btn-loader-text');
const togglePasswordBtn = document.getElementById('togglePassword');

const helpCard = document.querySelector('.help-card');
const helpAccordionHeader = document.getElementById('helpAccordionHeader');

const initialState = document.getElementById('initialState');
const loadingIndicator = document.getElementById('loadingIndicator');
const errorMessage = document.getElementById('errorMessage');
const errorText = document.getElementById('errorText');
const resultsSection = document.getElementById('resultsSection');
const totalEmailsSpan = document.getElementById('totalEmails');
const jobEmailCountSpan = document.getElementById('jobEmailCount');
const jobEmailsList = document.getElementById('jobEmailsList');

// Modal Elements
const emailModal = document.getElementById('emailModal');
const modalCloseBtn = document.getElementById('modalClose');
const btnCopyBody = document.getElementById('btnCopyBody');

/* -------------------------------------------------------------
   INITIALIZATION & STATUS CHECKS
   ------------------------------------------------------------- */
document.addEventListener('DOMContentLoaded', () => {
    // 1. Initial Status check of local backend API
    checkBackendStatus();
    // Poll the backend status every 12 seconds
    setInterval(checkBackendStatus, 12000);
});

async function checkBackendStatus() {
    const statusPill = document.getElementById('backendStatus');
    const statusText = statusPill.querySelector('.status-text');
    
    try {
        const response = await fetch(BACKEND_URL, {
            method: 'GET',
            headers: { 'Accept': 'application/json' }
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.status === 'running') {
                statusPill.className = 'status-indicator online';
                statusText.textContent = 'Backend Connected';
                return;
            }
        }
        throw new Error('Unhealthy status');
    } catch (e) {
        statusPill.className = 'status-indicator offline';
        statusText.textContent = 'Backend Offline';
    }
}

/* -------------------------------------------------------------
   INTERACTIVE COMPONENT CONTROLS
   ------------------------------------------------------------- */
// Toggle Password Visibility
togglePasswordBtn.addEventListener('click', () => {
    const isPassword = appPasswordInput.type === 'password';
    appPasswordInput.type = isPassword ? 'text' : 'password';
    
    const icon = togglePasswordBtn.querySelector('i');
    if (isPassword) {
        icon.className = 'fa-regular fa-eye-slash';
    } else {
        icon.className = 'fa-regular fa-eye';
    }
});

// App Password Guide Accordion Toggle
helpAccordionHeader.addEventListener('click', () => {
    helpCard.classList.toggle('active');
});

/* -------------------------------------------------------------
   MODAL EMAIL DRAWER CONTROLS
   ------------------------------------------------------------- */
function openEmailModal(index) {
    const email = currentJobEmails[index];
    if (!email) return;
    
    // Set text elements
    document.getElementById('modalSubject').textContent = email.subject || '[No Subject]';
    document.getElementById('modalCompany').textContent = email.company || 'Not Identified';
    document.getElementById('modalRole').textContent = email.role || 'Not Identified';
    
    // Configure badge details
    const statusBadge = document.getElementById('modalStatus');
    const status = email.status ? email.status.toLowerCase().replace(/\s+/g, '_') : 'unknown';
    statusBadge.className = `status-badge ${status}`;
    statusBadge.textContent = email.status || 'Unknown';
    
    // Set main scrollable text content
    const bodyContent = email.body && email.body.trim() ? email.body : '[No body content available]';
    document.getElementById('modalBody').textContent = bodyContent;
    
    // Modal action listener setup
    btnCopyBody.onclick = () => {
        navigator.clipboard.writeText(bodyContent).then(() => {
            const originalHTML = btnCopyBody.innerHTML;
            btnCopyBody.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
            setTimeout(() => {
                btnCopyBody.innerHTML = originalHTML;
            }, 2000);
        });
    };
    
    // Add display classes
    emailModal.classList.add('open');
    document.body.style.overflow = 'hidden'; // Stop viewport scroll
}

function closeModal() {
    emailModal.classList.remove('open');
    document.body.style.overflow = ''; // Restore viewport scroll
}

// Attach listeners to close modal
modalCloseBtn.addEventListener('click', closeModal);
emailModal.addEventListener('click', (e) => {
    if (e.target === emailModal) {
        closeModal();
    }
});

// Expose open function globally to connect with dynamically appended tags
window.openEmail = function(index) {
    openEmailModal(index);
}

// Copy single email subject to clipboard helper
window.copySubjectToClipboard = function(text, index, event) {
    event.stopPropagation(); // Avoid triggering open card click if we extend card clicks
    navigator.clipboard.writeText(text).then(() => {
        const btn = event.target.closest('.btn-action');
        const originalHTML = btn.innerHTML;
        btn.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
        setTimeout(() => {
            btn.innerHTML = originalHTML;
        }, 2000);
    });
}

/* -------------------------------------------------------------
   SCAN EMAILS REQUEST FLOW
   ------------------------------------------------------------- */
emailForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = emailInput.value.trim();
    const appPassword = appPasswordInput.value.trim();
    
    if (!email || !appPassword) {
        showError('Please enter both Gmail address and password.');
        return;
    }
    
    await scanEmails(email, appPassword);
});

async function scanEmails(email, appPassword) {
    // Reset views
    hideError();
    hideResults();
    initialState.style.display = 'none';
    showLoading();
    
    // Set button loading state
    btnText.style.display = 'none';
    btnLoaderText.style.display = 'inline-block';
    scanBtn.disabled = true;
    
    try {
        console.log('[UI] Sending scan query...');
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                app_password: appPassword
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            const errorMsg = errorData.detail || `Server error: ${response.status}`;
            throw new Error(errorMsg);
        }
        
        const data = await response.json();
        console.log('[UI] Scan results received successfully:', data);
        
        // Cache response locally
        currentJobEmails = data.job_emails || [];
        
        hideLoading();
        displayResults(data);
        
    } catch (error) {
        console.error('[UI] Scan error:', error);
        hideLoading();
        showError(error.message || 'Failed to scan emails. Make sure your Gmail settings and App password are correct.');
    } finally {
        // Reset button loading state
        btnText.style.display = 'inline-block';
        btnLoaderText.style.display = 'none';
        scanBtn.disabled = false;
    }
}

/* -------------------------------------------------------------
   RESULTS VIEW BINDINGS
   ------------------------------------------------------------- */
function displayResults(data) {
    totalEmailsSpan.textContent = data.total_emails || 0;
    jobEmailCountSpan.textContent = data.job_related_count || 0;
    
    if (currentJobEmails.length > 0) {
        jobEmailsList.innerHTML = currentJobEmails.map((email, index) => {
            const companyText = email.company ? escapeHtml(email.company) : 'Not Identified';
            const roleText = email.role ? escapeHtml(email.role) : 'Not Identified';
            const statusLabel = email.status ? escapeHtml(email.status) : 'Unknown';
            const statusClass = email.status ? email.status.toLowerCase().replace(/\s+/g, '_') : 'unknown';
            
            const bodyPreview = email.body && email.body.trim() 
                ? escapeHtml(email.body) 
                : '[No email message details present]';
            
            return `
                <div class="glass-card job-email-card" onclick="openEmail(${index})">
                    <div class="email-header">
                        <div class="email-title">
                            <span class="email-number">#${index + 1}</span>
                            <span class="email-subject">${escapeHtml(email.subject || '[No Subject]')}</span>
                        </div>
                        <span class="email-badge"><i class="fa-solid fa-wand-magic-sparkles"></i> Job Related</span>
                    </div>
                    
                    <div class="email-meta">
                        <div class="meta-item">
                            <span class="meta-icon"><i class="fa-solid fa-building"></i></span>
                            <span class="meta-label">Company:</span>
                            <span class="meta-value">${companyText}</span>
                        </div>
                        <div class="meta-item">
                            <span class="meta-icon"><i class="fa-solid fa-id-badge"></i></span>
                            <span class="meta-label">Role:</span>
                            <span class="meta-value">${roleText}</span>
                        </div>
                        <div class="meta-item">
                            <span class="meta-icon"><i class="fa-solid fa-chart-line"></i></span>
                            <span class="meta-label">Status:</span>
                            <span class="status-badge ${statusClass}">
                                ${statusLabel}
                            </span>
                        </div>
                    </div>

                    <div class="email-body-section">
                        <div class="email-body-label">Email Message Snippet:</div>
                        <div class="email-body">
                            ${bodyPreview}
                        </div>
                    </div>

                    <div class="email-actions">
                        <button class="btn-action" onclick="copySubjectToClipboard('${escapeHtml(email.subject || '').replace(/'/g, "\\'")}', '${index}', event)">
                            <i class="fa-regular fa-copy"></i> Copy Subject
                        </button>
                        <button class="btn-action btn-action-primary" onclick="event.stopPropagation(); openEmail(${index})">
                            <i class="fa-solid fa-up-right-and-down-left-from-center"></i> View Full
                        </button>
                    </div>
                </div>
            `;
        }).join('');
    } else {
        jobEmailsList.innerHTML = `
            <div class="glass-card empty-state">
                <div class="empty-state-icon"><i class="fa-solid fa-folder-open"></i></div>
                <p>No job-related emails detected in the last 24 hours.</p>
                <p style="font-size: 0.82rem; color: var(--text-muted);">Ensure you have received candidate emails in the selected Gmail inbox during this timeframe.</p>
            </div>
        `;
    }
    
    showResults();
}

/* -------------------------------------------------------------
   UTILITY HELPER FUNCTIONS
   ------------------------------------------------------------- */
function showLoading() {
    loadingIndicator.style.display = 'flex';
}

function hideLoading() {
    loadingIndicator.style.display = 'none';
}

function showError(message) {
    errorText.textContent = message;
    errorMessage.style.display = 'flex';
}

function hideError() {
    errorMessage.style.display = 'none';
}

function showResults() {
    resultsSection.style.display = 'block';
}

function hideResults() {
    resultsSection.style.display = 'none';
}

function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}
