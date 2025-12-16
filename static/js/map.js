/**
 * Map Interaction JavaScript
 * Handles SVG map clicks, hovers, and tooltips
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeMap();
});

/**
 * Initialize the interactive SVG map
 */
function initializeMap() {
    const svgMap = document.getElementById('svg-map');
    if (!svgMap) return;
    
    const states = svgMap.querySelectorAll('.state');
    const statesData = window.statesData || {};
    
    // Create tooltip element
    const tooltip = createTooltip();
    
    states.forEach(stateElement => {
        const stateAbbr = stateElement.getAttribute('data-state');
        const stateData = statesData[stateAbbr];
        
        if (!stateData) return;
        
        // Apply status class to SVG path
        stateElement.classList.add(stateData.status_class);
        
        // Click handler
        stateElement.addEventListener('click', function(e) {
            e.preventDefault();
            handleStateClick(stateAbbr);
        });
        
        // Hover handlers for tooltip
        stateElement.addEventListener('mouseenter', function(e) {
            showTooltip(e, stateData, tooltip);
        });
        
        stateElement.addEventListener('mousemove', function(e) {
            updateTooltipPosition(e, tooltip);
        });
        
        stateElement.addEventListener('mouseleave', function() {
            hideTooltip(tooltip);
        });
    });
}

/**
 * Create tooltip element
 */
function createTooltip() {
    const tooltip = document.createElement('div');
    tooltip.className = 'map-tooltip';
    tooltip.id = 'mapTooltip';
    document.body.appendChild(tooltip);
    return tooltip;
}

/**
 * Show tooltip with state information
 */
function showTooltip(event, stateData, tooltip) {
    let content = `<strong>${stateData.name}</strong>`;
    content += `<div>${stateData.badge_text}</div>`;
    
    if (stateData.expires_on && stateData.status === 'licensed') {
        const daysRemaining = stateData.days_remaining;
        if (daysRemaining !== null) {
            if (daysRemaining < 0) {
                content += `<div class="text-danger">OVERDUE by ${Math.abs(daysRemaining)} days</div>`;
            } else if (daysRemaining <= 90) {
                content += `<div>${daysRemaining} days until renewal</div>`;
            } else {
                content += `<div>Expires ${formatDateShort(stateData.expires_on)}</div>`;
            }
        }
    }
    
    if (stateData.coverage_level === 'draft') {
        content += `<div class="small text-muted">Draft - Verify with board</div>`;
    }
    
    tooltip.innerHTML = content;
    tooltip.classList.add('visible');
    updateTooltipPosition(event, tooltip);
}

/**
 * Update tooltip position
 */
function updateTooltipPosition(event, tooltip) {
    const offset = 15;
    const tooltipWidth = tooltip.offsetWidth;
    const tooltipHeight = tooltip.offsetHeight;
    
    let left = event.pageX + offset;
    let top = event.pageY + offset;
    
    // Prevent tooltip from going off-screen
    if (left + tooltipWidth > window.innerWidth) {
        left = event.pageX - tooltipWidth - offset;
    }
    
    if (top + tooltipHeight > window.innerHeight) {
        top = event.pageY - tooltipHeight - offset;
    }
    
    tooltip.style.left = left + 'px';
    tooltip.style.top = top + 'px';
}

/**
 * Hide tooltip
 */
function hideTooltip(tooltip) {
    tooltip.classList.remove('visible');
}

/**
 * Format date in short format for tooltip
 */
function formatDateShort(isoString) {
    if (!isoString) return '';
    
    try {
        const date = new Date(isoString);
        return date.toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric',
            year: 'numeric'
        });
    } catch (e) {
        return isoString;
    }
}
