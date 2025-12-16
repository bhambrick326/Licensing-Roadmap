/**
 * Mapbox GL JS - Interactive US State Map with Multiple Views
 */

let map;
let currentView = 'status'; // status, expiration, leadership, training

const fipsToAbbr = {
    '01': 'AL', '02': 'AK', '04': 'AZ', '05': 'AR', '06': 'CA', '08': 'CO', '09': 'CT', '10': 'DE',
    '12': 'FL', '13': 'GA', '15': 'HI', '16': 'ID', '17': 'IL', '18': 'IN', '19': 'IA', '20': 'KS',
    '21': 'KY', '22': 'LA', '23': 'ME', '24': 'MD', '25': 'MA', '26': 'MI', '27': 'MN', '28': 'MS',
    '29': 'MO', '30': 'MT', '31': 'NE', '32': 'NV', '33': 'NH', '34': 'NJ', '35': 'NM', '36': 'NY',
    '37': 'NC', '38': 'ND', '39': 'OH', '40': 'OK', '41': 'OR', '42': 'PA', '44': 'RI', '45': 'SC',
    '46': 'SD', '47': 'TN', '48': 'TX', '49': 'UT', '50': 'VT', '51': 'VA', '53': 'WA', '54': 'WV',
    '55': 'WI', '56': 'WY'
};

function initializeMapboxMap() {
    if (!window.mapboxToken) {
        console.error('Mapbox token not found');
        return;
    }

    mapboxgl.accessToken = window.mapboxToken;
    
    map = new mapboxgl.Map({
        container: 'mapbox-map',
        style: 'mapbox://styles/mapbox/light-v11',
        center: [-98.5795, 39.8283],
        zoom: 3.5,
        minZoom: 3,
        maxZoom: 8
    });

    map.addControl(new mapboxgl.NavigationControl(), 'top-right');

    map.on('load', function() {
        addStateLayer();
        initializeViewSelector();
    });
}

function addStateLayer() {
    map.addSource('states', {
        type: 'vector',
        url: 'mapbox://mapbox.us_census_states_2015'
    });

    map.addLayer({
        id: 'state-fills',
        type: 'fill',
        source: 'states',
        'source-layer': 'states',
        paint: {
            'fill-color': '#e5e7eb',
            'fill-opacity': 0.75
        }
    });

    map.addLayer({
        id: 'state-borders',
        type: 'line',
        source: 'states',
        'source-layer': 'states',
        paint: {
            'line-color': '#2d3748',
            'line-width': 1
        }
    });

    map.addLayer({
        id: 'state-hover',
        type: 'line',
        source: 'states',
        'source-layer': 'states',
        paint: {
            'line-color': '#d97706',
            'line-width': 3
        },
        filter: ['==', 'STATE_ID', '']
    });

    updateMapColors();
    addInteractions();
}

function updateMapColors() {
    const colorExpression = getColorExpressionForView(currentView);
    map.setPaintProperty('state-fills', 'fill-color', colorExpression);
}

function getColorExpressionForView(view) {
    const statesData = window.statesData || {};
    const colorExpression = ['match', ['get', 'STATE_ID']];
    
    Object.keys(fipsToAbbr).forEach(fips => {
        const abbr = fipsToAbbr[fips];
        const state = statesData[abbr];
        let color = '#e5e7eb';
        
        if (state) {
            switch(view) {
                case 'status':
                    color = getStatusColor(state);
                    break;
                case 'expiration':
                    color = getExpirationColor(state);
                    break;
                case 'leadership':
                    color = getLeadershipColor(state);
                    break;
                case 'projects':
                    color = getProjectColor(state);
                    break;
                case 'training':
                    color = getTrainingRoadmapColor(state);
                    break;
            }
        }
        
        colorExpression.push(fips, color);
    });
    
    colorExpression.push('#e5e7eb');
    return colorExpression;
}

function getStatusColor(state) {
    switch(state.status_class) {
        case 'licensed': return '#10b981';
        case 'in_progress': return '#3b82f6';
        case 'due-soon': return '#f59e0b';
        case 'overdue': return '#ef4444';
        case 'not_licensed': return '#9ca3af';
        default: return '#e5e7eb';
    }
}

function getExpirationColor(state) {
    if (state.status !== 'licensed' || !state.days_remaining) {
        return '#e5e7eb';
    }
    
    const days = state.days_remaining;
    if (days < 0) return '#ef4444';        // Overdue - red
    if (days <= 30) return '#f59e0b';      // 30 days - orange
    if (days <= 90) return '#fbbf24';      // 90 days - yellow
    if (days <= 180) return '#84cc16';     // 180 days - lime
    return '#10b981';                      // Good - green
}

function getLeadershipColor(state) {
    // Leadership view: show coverage intensity
    if (state.status === 'licensed') return '#10b981';
    if (state.status === 'in_progress') return '#60a5fa';
    return '#d1d5db';
}

function getProjectColor(state) {
    // Placeholder for project view
    if (state.status === 'licensed') return '#8b5cf6';
    return '#e5e7eb';
}

function getTrainingRoadmapColor(state) {
    // Training roadmap view - show by step/priority
    const stateAbbr = state.state_abbr || Object.keys(window.statesData || {}).find(
        abbr => window.statesData[abbr].name === state.name
    );
    
    // Check if this state is in the training roadmap
    const roadmap = window.trainingRoadmap;
    if (!roadmap || !roadmap.path) return '#e5e7eb';
    
    const step = roadmap.path.find(s => s.state === stateAbbr);
    if (!step) return '#e5e7eb';
    
    // Color by step number (gradient from green to purple)
    const colors = ['#10b981', '#3b82f6', '#8b5cf6', '#d946ef', '#f59e0b'];
    return colors[step.step - 1] || '#6366f1';
}

function initializeViewSelector() {
    const viewTabs = document.querySelectorAll('.view-tab');
    
    viewTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const view = this.getAttribute('data-view');
            switchView(view);
            
            viewTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

function switchView(view) {
    currentView = view;
    updateMapColors();
    updateLegend(view);
}

function updateLegend(view) {
    const legendHeader = document.querySelector('.legend-header');
    const legendItems = document.getElementById('legendItems');
    
    const legends = {
        status: {
            title: 'License Status',
            items: [
                { color: 'licensed', label: 'Licensed' },
                { color: 'progress', label: 'In Progress' },
                { color: 'due', label: 'Due Soon' },
                { color: 'overdue', label: 'Overdue' },
                { color: 'none', label: 'Not Licensed' }
            ]
        },
        expiration: {
            title: 'Expiration Timeline',
            items: [
                { color: 'custom', customColor: '#10b981', label: '180+ days' },
                { color: 'custom', customColor: '#84cc16', label: '90-180 days' },
                { color: 'custom', customColor: '#fbbf24', label: '30-90 days' },
                { color: 'custom', customColor: '#f59e0b', label: '0-30 days' },
                { color: 'overdue', label: 'Overdue' }
            ]
        },
        leadership: {
            title: 'Coverage Status',
            items: [
                { color: 'licensed', label: 'Licensed' },
                { color: 'custom', customColor: '#60a5fa', label: 'In Progress' },
                { color: 'custom', customColor: '#d1d5db', label: 'No Coverage' }
            ]
        },
        projects: {
            title: 'Project Activity',
            items: [
                { color: 'custom', customColor: '#8b5cf6', label: 'Active States' },
                { color: 'none', label: 'Inactive' }
            ]
        },
        training: {
            title: 'Training Path',
            items: [
                { color: 'custom', customColor: '#10b981', label: 'Step 1 - Critical' },
                { color: 'custom', customColor: '#3b82f6', label: 'Step 2 - High' },
                { color: 'custom', customColor: '#8b5cf6', label: 'Step 3 - High' },
                { color: 'custom', customColor: '#d946ef', label: 'Step 4 - Medium' },
                { color: 'custom', customColor: '#f59e0b', label: 'Step 5 - Medium' }
            ]
        }
    };
    
    const legend = legends[view];
    legendHeader.textContent = legend.title;
    
    legendItems.innerHTML = legend.items.map(item => `
        <div class="legend-item">
            <span class="legend-dot ${item.customColor ? '' : 'legend-dot-' + item.color}" 
                  ${item.customColor ? 'style="background: ' + item.customColor + '"' : ''}></span>
            <span class="legend-text">${item.label}</span>
        </div>
    `).join('');
}

function addInteractions() {
    map.on('mouseenter', 'state-fills', function() {
        map.getCanvas().style.cursor = 'pointer';
    });

    map.on('mouseleave', 'state-fills', function() {
        map.getCanvas().style.cursor = '';
        map.setFilter('state-hover', ['==', 'STATE_ID', '']);
    });

    map.on('mousemove', 'state-fills', function(e) {
        if (e.features.length > 0) {
            const feature = e.features[0];
            const fips = feature.properties.STATE_ID;
            map.setFilter('state-hover', ['==', 'STATE_ID', fips]);
        }
    });

    map.on('click', 'state-fills', function(e) {
        if (e.features.length > 0) {
            const feature = e.features[0];
            const fips = feature.properties.STATE_ID;
            const stateAbbr = fipsToAbbr[fips];
            
            if (stateAbbr && window.handleStateClick) {
                window.handleStateClick(stateAbbr);
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('mapbox-map')) {
        initializeMapboxMap();
    }
});
