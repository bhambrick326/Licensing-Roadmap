/**
 * Main JavaScript - Enhanced Offcanvas Content
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeBootstrapComponents();
    
    const searchInput = document.getElementById('stateSearch');
    if (searchInput) {
        initializeSearch();
    }
});

function initializeBootstrapComponents() {
    const tooltipTriggerList = [].slice.call(
        document.querySelectorAll('[data-bs-toggle="tooltip"]')
    );
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function initializeSearch() {
    const searchInput = document.getElementById('stateSearch');
    const searchResults = document.getElementById('searchResults');
    
    if (!searchInput || !searchResults) return;
    
    searchInput.addEventListener('input', function(e) {
        const query = e.target.value.toLowerCase().trim();
        
        if (query.length === 0) {
            searchResults.classList.remove('active');
            searchResults.innerHTML = '';
            document.querySelectorAll('.state').forEach(state => {
                state.style.opacity = '';
            });
            return;
        }
        
        const matches = [];
        for (const [abbr, stateData] of Object.entries(window.statesData || {})) {
            if (
                stateData.name.toLowerCase().includes(query) ||
                abbr.toLowerCase().includes(query)
            ) {
                matches.push({ abbr, ...stateData });
            }
        }
        
        if (matches.length > 0) {
            searchResults.innerHTML = matches.map(state => `
                <div class="search-result-item" data-state="${state.abbr}">
                    <strong>${state.name}</strong> (${state.abbr})
                    <span class="badge bg-secondary ms-2">${state.badge_text}</span>
                </div>
            `).join('');
            searchResults.classList.add('active');
            
            searchResults.querySelectorAll('.search-result-item').forEach(item => {
                item.addEventListener('click', function() {
                    const stateAbbr = this.getAttribute('data-state');
                    handleStateClick(stateAbbr);
                    searchInput.value = '';
                    searchResults.classList.remove('active');
                    searchResults.innerHTML = '';
                });
            });
        } else {
            searchResults.innerHTML = '<div class="search-result-item">No states found</div>';
            searchResults.classList.add('active');
        }
    });
    
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.classList.remove('active');
        }
    });
}

function handleStateClick(stateAbbr) {
    const stateData = window.statesData[stateAbbr];
    if (!stateData) return;
    
    populateOffcanvas(stateAbbr, stateData);
    
    const offcanvas = new bootstrap.Offcanvas(document.getElementById('stateOffcanvas'));
    offcanvas.show();
}

function populateOffcanvas(stateAbbr, stateData) {

    // Check if we're in training roadmap view
    const isTrainingView = document.querySelector('.view-tab[data-view="training"]')?.classList.contains('active');
    const trainingRoadmap = window.trainingRoadmap;
    
    if (isTrainingView && trainingRoadmap && trainingRoadmap.path) {
        const trainingStep = trainingRoadmap.path.find(step => step.state === stateAbbr);
        if (trainingStep) {
            populateTrainingRoadmapOffcanvas(stateAbbr, stateData, trainingStep, trainingRoadmap);
            return;
        }
    }
    
    const offcanvasTitle = document.getElementById('stateOffcanvasLabel');
    const offcanvasContent = document.getElementById('offcanvasContent');
    
    offcanvasTitle.textContent = stateData.name;
    
    // Build gorgeous content
    let html = `
        <div class="offcanvas-state-content">
            <!-- Status Badge -->
            <div class="status-badge-container">
                <span class="status-badge-large status-${stateData.status_class}">
                    ${getStatusIcon(stateData.status_class)} ${stateData.badge_text}
                </span>
            </div>
    `;
    
    // License Information Card
    if (stateData.status === 'licensed') {
        html += `
            <div class="info-card-pro">
                <div class="info-card-header">
                    <span class="info-card-icon">📜</span>
                    <span class="info-card-title">License Details</span>
                </div>
                <div class="info-card-body">
                    <div class="info-row">
                        <span class="info-label">Type</span>
                        <span class="info-value">${stateData.license_type || 'Master Plumber'}</span>
                    </div>
                    ${stateData.license_number ? `
                    <div class="info-row">
                        <span class="info-label">License #</span>
                        <span class="info-value"><code>${stateData.license_number}</code></span>
                    </div>
                    ` : ''}
                </div>
            </div>
        `;
        
        // Expiration Card with Progress Bar
        if (stateData.expires_on) {
            const daysRemaining = stateData.days_remaining;
            let progressPercent = 0;
            let progressClass = 'success';
            let expiryText = '';
            
            if (daysRemaining < 0) {
                progressPercent = 100;
                progressClass = 'danger';
                expiryText = `OVERDUE by ${Math.abs(daysRemaining)} days`;
            } else if (daysRemaining <= 90) {
                progressPercent = 100 - ((daysRemaining / 90) * 100);
                progressClass = 'warning';
                expiryText = `${daysRemaining} days remaining`;
            } else {
                progressPercent = 20;
                progressClass = 'success';
                expiryText = `${daysRemaining} days remaining`;
            }
            
            html += `
                <div class="info-card-pro expiry-card">
                    <div class="info-card-header">
                        <span class="info-card-icon">📅</span>
                        <span class="info-card-title">Expiration</span>
                    </div>
                    <div class="info-card-body">
                        <div class="expiry-date">${formatDate(stateData.expires_on)}</div>
                        <div class="expiry-countdown ${progressClass}">${expiryText}</div>
                        <div class="progress-bar-container">
                            <div class="progress-bar-fill progress-${progressClass}" style="width: ${progressPercent}%"></div>
                        </div>
                    </div>
                </div>
            `;
        }
    }
    
    // Board Information Card
    html += `
        <div class="info-card-pro">
            <div class="info-card-header">
                <span class="info-card-icon">🏛️</span>
                <span class="info-card-title">Licensing Board</span>
            </div>
            <div class="info-card-body">
                <div class="board-name">${stateData.board_name}</div>
                ${stateData.board_phone ? `
                <div class="board-contact">
                    <span class="contact-icon">📞</span>
                    <span>${stateData.board_phone}</span>
                </div>
                ` : ''}
            </div>
        </div>
    `;
    
    // Summary
    if (stateData.summary) {
        html += `
            <div class="info-card-pro">
                <div class="info-card-header">
                    <span class="info-card-icon">ℹ️</span>
                    <span class="info-card-title">Summary</span>
                </div>
                <div class="info-card-body">
                    <p class="summary-text">${stateData.summary}</p>
                </div>
            </div>
        `;
    }
    
    // Coverage Warning
    if (stateData.coverage_level === 'draft' || stateData.coverage_level === 'partial') {
        html += `
            <div class="alert-card ${stateData.coverage_level === 'draft' ? 'alert-warning' : 'alert-info'}">
                <strong>⚠️ Note:</strong> State roadmap ${stateData.coverage_level === 'draft' ? 'in progress' : 'partially complete'}. 
                Verify details with the state board.
            </div>
        `;
    }
    
    // Action Buttons
    html += `
        <div class="action-buttons">
            <a href="/licensing/${stateAbbr.toLowerCase()}" class="btn-action btn-primary-action">
                <span>📋</span> View Full Roadmap
            </a>
            <a href="${stateData.board_url}" target="_blank" class="btn-action btn-secondary-action">
                <span>🔗</span> Visit Board Website
            </a>
        </div>
    `;
    
    html += '</div>';
    
    offcanvasContent.innerHTML = html;
}

function getStatusIcon(statusClass) {
    const icons = {
        'licensed': '✓',
        'in_progress': '⟳',
        'due-soon': '⚠',
        'overdue': '!',
        'not_licensed': '○'
    };
    return icons[statusClass] || '○';
}

function formatDate(isoString) {
    if (!isoString) return 'N/A';
    
    try {
        const date = new Date(isoString);
        return date.toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
    } catch (e) {
        return isoString;
    }
}


function populateTrainingRoadmapOffcanvas(stateAbbr, stateData, trainingStep, roadmap) {
    const offcanvasTitle = document.getElementById('stateOffcanvasLabel');
    const offcanvasContent = document.getElementById('offcanvasContent');
    
    offcanvasTitle.textContent = stateData.name;
    
    // Build training-specific content
    let html = `
        <div class="offcanvas-state-content">
            <!-- Training Step Badge -->
            <div class="training-step-badge">
                <div class="step-number">Step ${trainingStep.step}</div>
                <div class="step-priority priority-${trainingStep.priority}">${trainingStep.priority.toUpperCase()}</div>
            </div>
            
            <!-- Training Info Card -->
            <div class="info-card-pro training-card">
                <div class="info-card-header">
                    <span class="info-card-icon">🎓</span>
                    <span class="info-card-title">Training Path Details</span>
                </div>
                <div class="info-card-body">
                    <div class="info-row">
                        <span class="info-label">License Type</span>
                        <span class="info-value">${trainingStep.license_type}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Timeline</span>
                        <span class="info-value">${trainingStep.estimated_timeline}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">Cost Estimate</span>
                        <span class="info-value"><strong>${trainingStep.cost_estimate}</strong></span>
                    </div>
                </div>
            </div>
            
            <!-- Why This State -->
            <div class="info-card-pro">
                <div class="info-card-header">
                    <span class="info-card-icon">💡</span>
                    <span class="info-card-title">Strategic Rationale</span>
                </div>
                <div class="info-card-body">
                    <p class="summary-text">${trainingStep.reason}</p>
                </div>
            </div>
            
            <!-- Prerequisites -->
            ${trainingStep.prerequisites && trainingStep.prerequisites.length > 0 ? `
            <div class="info-card-pro">
                <div class="info-card-header">
                    <span class="info-card-icon">✅</span>
                    <span class="info-card-title">Prerequisites</span>
                </div>
                <div class="info-card-body">
                    <ul class="prerequisites-list">
                        ${trainingStep.prerequisites.map(req => `<li>${req}</li>`).join('')}
                    </ul>
                </div>
            </div>
            ` : ''}
            
            <!-- Roadmap Overview -->
            <div class="info-card-pro">
                <div class="info-card-header">
                    <span class="info-card-icon">🗺️</span>
                    <span class="info-card-title">Full Roadmap</span>
                </div>
                <div class="info-card-body">
                    <div class="roadmap-summary">
                        <div class="roadmap-stat">
                            <strong>${roadmap.path.length}</strong> Total Steps
                        </div>
                        <div class="roadmap-stat">
                            <strong>${roadmap.estimated_duration}</strong> Duration
                        </div>
                        <div class="roadmap-stat">
                            <strong>${roadmap.total_cost_estimate}</strong> Total Cost
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Board Information -->
            ${stateData.board_name ? `
            <div class="info-card-pro">
                <div class="info-card-header">
                    <span class="info-card-icon">🏛️</span>
                    <span class="info-card-title">Licensing Board</span>
                </div>
                <div class="info-card-body">
                    <div class="board-name">${stateData.board_name}</div>
                    ${stateData.board_phone ? `
                    <div class="board-contact">
                        <span class="contact-icon">��</span>
                        <span>${stateData.board_phone}</span>
                    </div>
                    ` : ''}
                </div>
            </div>
            ` : ''}
            
            <!-- Action Button -->
            <div class="action-buttons">
                <a href="${stateData.board_url || '#'}" target="_blank" class="btn-action btn-primary-action">
                    <span>🔗</span> Visit Licensing Board
                </a>
            </div>
        </div>
    `;
    
    offcanvasContent.innerHTML = html;
}


window.handleStateClick = handleStateClick;
