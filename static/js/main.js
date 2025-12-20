/**
 * Main JavaScript - Enhanced Offcanvas Content with 4 Different Views
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
    
    // Determine which view is active
    const activeView = document.querySelector('.view-tab.active')?.getAttribute('data-view') || 'status';
    
    // Populate offcanvas based on active view
    populateOffcanvasForView(stateAbbr, stateData, activeView);
    
    const offcanvas = new bootstrap.Offcanvas(document.getElementById('stateOffcanvas'));
    offcanvas.show();
}

function populateOffcanvasForView(stateAbbr, stateData, view) {
    switch(view) {
        case 'status':
            populateLicenseStatusView(stateAbbr, stateData);
            break;
        case 'expiration':
            populateExpirationTrackerView(stateAbbr, stateData);
            break;
        case 'leadership':
            populateLeadershipView(stateAbbr, stateData);
            break;
        case 'training':
            populateTrainingRoadmapView(stateAbbr, stateData);
            break;
        default:
            populateLicenseStatusView(stateAbbr, stateData);
    }
}

// CLEAN, COMPACT SIDE PANEL - NO SCROLLING
// Each view shows only essential summary info with prominent "View Full Details" button

// ============================================================================
// VIEW 1: LICENSE STATUS VIEW - COMPACT
// ============================================================================
function populateLicenseStatusView(stateAbbr, stateData) {
    const offcanvasTitle = document.getElementById('stateOffcanvasLabel');
    const offcanvasContent = document.getElementById('offcanvasContent');
    
    offcanvasTitle.textContent = stateData.name;
    
    let html = `
        <div class="offcanvas-state-content-clean">
            <!-- Status Badge -->
            <div class="status-badge-container-clean">
                <span class="status-badge-xl status-${stateData.status_class}">
                    ${getStatusIcon(stateData.status_class)} ${stateData.badge_text}
                </span>
            </div>
    `;
    
    if (stateData.status === 'licensed') {
        html += `
            <!-- Quick Info Grid -->
            <div class="quick-info-grid">
                <div class="quick-info-item">
                    <div class="quick-info-label">License Type</div>
                    <div class="quick-info-value">${stateData.license_type || 'Master Plumber'}</div>
                </div>
                ${stateData.license_number ? `
                <div class="quick-info-item">
                    <div class="quick-info-label">License #</div>
                    <div class="quick-info-value"><code>${stateData.license_number}</code></div>
                </div>
                ` : ''}
                ${stateData.expires_on ? `
                <div class="quick-info-item">
                    <div class="quick-info-label">Expires</div>
                    <div class="quick-info-value">${formatDate(stateData.expires_on)}</div>
                </div>
                ` : ''}
                <div class="quick-info-item">
                    <div class="quick-info-label">Designation</div>
                    <div class="quick-info-value">
                        ${stateData.designated_role === 'master_of_record' ? 
                            '<span class="badge-sm badge-primary">Master of Record</span>' : 
                            '<span class="badge-sm badge-secondary">Standard</span>'
                        }
                    </div>
                </div>
            </div>
        `;
    } else {
        html += `
            <div class="empty-state">
                <p class="empty-state-text">Not licensed in ${stateData.name}</p>
                <p class="empty-state-subtext">View full details to see requirements and costs</p>
            </div>
        `;
    }
    
    // Board Contact - Compact
    html += `
        <div class="board-contact-compact">
            <div class="board-name-sm">${stateData.board_name || stateData.name + ' State Board'}</div>
            ${stateData.board_phone ? `<div class="board-phone-sm">📞 ${stateData.board_phone}</div>` : ''}
        </div>
    `;
    
    // Big Action Button
    html += `
        <div class="action-button-clean">
            <a href="/state/${stateAbbr}" class="btn-full-details">
                <span class="btn-icon">📖</span>
                <span class="btn-text">View Full Licensing Guide</span>
                <span class="btn-arrow">→</span>
            </a>
        </div>
    `;
    
    html += '</div>';
    offcanvasContent.innerHTML = html;
}

// ============================================================================
// VIEW 2: EXPIRATION TRACKER VIEW - COMPACT
// ============================================================================
function populateExpirationTrackerView(stateAbbr, stateData) {
    const offcanvasTitle = document.getElementById('stateOffcanvasLabel');
    const offcanvasContent = document.getElementById('offcanvasContent');
    
    offcanvasTitle.textContent = stateData.name;
    
    let html = `<div class="offcanvas-state-content-clean">`;
    
    if (stateData.status === 'licensed' && stateData.expires_on) {
        const daysRemaining = stateData.days_remaining;
        let urgencyClass = 'good';
        let urgencyText = '';
        
        if (daysRemaining < 0) {
            urgencyClass = 'overdue';
            urgencyText = `OVERDUE by ${Math.abs(daysRemaining)} days`;
        } else if (daysRemaining <= 30) {
            urgencyClass = 'critical';
            urgencyText = `${daysRemaining} days remaining`;
        } else if (daysRemaining <= 90) {
            urgencyClass = 'warning';
            urgencyText = `${daysRemaining} days remaining`;
        } else {
            urgencyClass = 'good';
            urgencyText = `${daysRemaining} days remaining`;
        }
        
        html += `
            <!-- Expiration Status -->
            <div class="expiration-display urgency-${urgencyClass}">
                <div class="expiration-date-xl">${formatDate(stateData.expires_on)}</div>
                <div class="expiration-countdown-xl">${urgencyText}</div>
                ${urgencyClass === 'critical' || urgencyClass === 'overdue' ? 
                    '<div class="urgency-alert">⚠️ Renewal needed immediately</div>' : ''}
            </div>
            
            <!-- Quick Stats -->
            <div class="quick-info-grid">
                <div class="quick-info-item">
                    <div class="quick-info-label">Renewal Fee</div>
                    <div class="quick-info-value">TBD</div>
                </div>
                <div class="quick-info-item">
                    <div class="quick-info-label">CE Required</div>
                    <div class="quick-info-value">TBD hours</div>
                </div>
            </div>
        `;
    } else {
        html += `
            <div class="status-badge-container-clean">
                <span class="status-badge-xl status-${stateData.status_class}">
                    ${getStatusIcon(stateData.status_class)} ${stateData.badge_text}
                </span>
            </div>
            <div class="empty-state">
                <p class="empty-state-text">No active license to track</p>
                <p class="empty-state-subtext">View full details for licensing requirements</p>
            </div>
        `;
    }
    
    // Big Action Button
    html += `
        <div class="action-button-clean">
            <a href="/state/${stateAbbr}" class="btn-full-details">
                <span class="btn-icon">📖</span>
                <span class="btn-text">View Full Licensing Guide</span>
                <span class="btn-arrow">→</span>
            </a>
        </div>
    </div>`;
    
    offcanvasContent.innerHTML = html;
}

// ============================================================================
// VIEW 3: LEADERSHIP VIEW - COMPACT
// ============================================================================
function populateLeadershipView(stateAbbr, stateData) {
    const offcanvasTitle = document.getElementById('stateOffcanvasLabel');
    const offcanvasContent = document.getElementById('offcanvasContent');
    
    offcanvasTitle.textContent = stateData.name;
    
    let html = `
        <div class="offcanvas-state-content-clean">
            <div class="status-badge-container-clean">
                <span class="status-badge-xl status-${stateData.status_class}">
                    ${getStatusIcon(stateData.status_class)} ${stateData.badge_text}
                </span>
            </div>
    `;
    
    if (stateData.status === 'licensed') {
        html += `
            <!-- Coverage Stats -->
            <div class="quick-info-grid">
                <div class="quick-info-item">
                    <div class="quick-info-label">Coverage Status</div>
                    <div class="quick-info-value">
                        <span class="badge-sm badge-success">Active</span>
                    </div>
                </div>
                <div class="quick-info-item">
                    <div class="quick-info-label">License Health</div>
                    <div class="quick-info-value">
                        ${stateData.days_remaining && stateData.days_remaining > 90 ?
                            '<span class="badge-sm badge-success">Healthy</span>' :
                            '<span class="badge-sm badge-warning">Attention Needed</span>'
                        }
                    </div>
                </div>
                <div class="quick-info-item">
                    <div class="quick-info-label">Team Coverage</div>
                    <div class="quick-info-value">1 license holder</div>
                </div>
                <div class="quick-info-item">
                    <div class="quick-info-label">Revenue Tracking</div>
                    <div class="quick-info-value text-muted">Coming soon</div>
                </div>
            </div>
        `;
    } else {
        html += `
            <div class="empty-state">
                <p class="empty-state-text">No coverage in ${stateData.name}</p>
                <p class="empty-state-subtext">View full details for expansion analysis</p>
            </div>
        `;
    }
    
    // Big Action Button
    html += `
        <div class="action-button-clean">
            <a href="/state/${stateAbbr}" class="btn-full-details">
                <span class="btn-icon">📖</span>
                <span class="btn-text">View Full Licensing Guide</span>
                <span class="btn-arrow">→</span>
            </a>
        </div>
    </div>`;
    
    offcanvasContent.innerHTML = html;
}

// ============================================================================
// VIEW 4: TRAINING ROADMAP VIEW - COMPACT
// ============================================================================
function populateTrainingRoadmapView(stateAbbr, stateData) {
    const offcanvasTitle = document.getElementById('stateOffcanvasLabel');
    const offcanvasContent = document.getElementById('offcanvasContent');
    
    offcanvasTitle.textContent = stateData.name;
    
    const trainingRoadmap = window.trainingRoadmap;
    const trainingStep = trainingRoadmap && trainingRoadmap.path ? 
        trainingRoadmap.path.find(step => step.state === stateAbbr) : null;
    
    let html = `<div class="offcanvas-state-content-clean">`;
    
    if (trainingStep) {
        html += `
            <!-- Training Badge -->
            <div class="training-badge-clean">
                <div class="training-step">Step ${trainingStep.step}</div>
                <div class="training-priority priority-${trainingStep.priority}">${trainingStep.priority.toUpperCase()}</div>
            </div>
            
            <!-- Quick Info -->
            <div class="quick-info-grid">
                <div class="quick-info-item">
                    <div class="quick-info-label">Target License</div>
                    <div class="quick-info-value">${trainingStep.license_type}</div>
                </div>
                <div class="quick-info-item">
                    <div class="quick-info-label">Timeline</div>
                    <div class="quick-info-value">${trainingStep.estimated_timeline}</div>
                </div>
                <div class="quick-info-item">
                    <div class="quick-info-label">Est. Cost</div>
                    <div class="quick-info-value">${trainingStep.cost_estimate}</div>
                </div>
            </div>
            
            <div class="training-reason">
                <strong>Why ${stateData.name}:</strong> ${trainingStep.reason}
            </div>
        `;
    } else {
        html += `
            <div class="status-badge-container-clean">
                <span class="status-badge-xl status-${stateData.status_class}">
                    ${getStatusIcon(stateData.status_class)} ${stateData.badge_text}
                </span>
            </div>
            <div class="empty-state">
                <p class="empty-state-text">Not in training roadmap</p>
                <p class="empty-state-subtext">View full details for exam prep and requirements</p>
            </div>
        `;
    }
    
    // Big Action Button
    html += `
        <div class="action-button-clean">
            <a href="/state/${stateAbbr}" class="btn-full-details">
                <span class="btn-icon">📖</span>
                <span class="btn-text">View Full Licensing Guide</span>
                <span class="btn-arrow">→</span>
            </a>
        </div>
    </div>`;
    
    offcanvasContent.innerHTML = html;
}

// Utility functions
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


// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================
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

window.handleStateClick = handleStateClick;
