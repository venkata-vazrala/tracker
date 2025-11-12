// API Base URL
const API_BASE = '/api';

// Global state
let currentPipelines = [];
let currentRuns = [];
let trendChart = null;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initButtons();
    loadDashboard();
});

// Navigation
function initNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const view = item.dataset.view;
            switchView(view);
        });
    });
}

function switchView(viewName) {
    // Update nav
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
    });
    document.querySelector(`[data-view="${viewName}"]`).classList.add('active');

    // Update view
    document.querySelectorAll('.view').forEach(view => {
        view.classList.remove('active');
    });

    const pageTitle = document.getElementById('page-title');
    
    switch(viewName) {
        case 'dashboard':
            document.getElementById('dashboardView').classList.add('active');
            pageTitle.textContent = 'Dashboard';
            loadDashboard();
            break;
        case 'pipelines':
            document.getElementById('pipelinesView').classList.add('active');
            pageTitle.textContent = 'Pipelines';
            loadPipelines();
            break;
        case 'runs':
            document.getElementById('runsView').classList.add('active');
            pageTitle.textContent = 'Runs';
            loadAllRuns();
            break;
        case 'trends':
            document.getElementById('trendsView').classList.add('active');
            pageTitle.textContent = 'Trends';
            loadTrendsView();
            break;
    }
}

// Initialize buttons
function initButtons() {
    document.getElementById('refreshBtn').addEventListener('click', () => {
        const activeView = document.querySelector('.nav-item.active').dataset.view;
        switchView(activeView);
    });

    document.getElementById('createRunBtn').addEventListener('click', openCreateRunModal);
    document.getElementById('createRunForm').addEventListener('submit', handleCreateRun);
}

// Dashboard
async function loadDashboard() {
    try {
        const [pipelines, runs] = await Promise.all([
            fetch(`${API_BASE}/pipelines/`).then(r => r.json()),
            fetch(`${API_BASE}/runs/`).then(r => r.json())
        ]);

        currentPipelines = pipelines.results || pipelines;
        currentRuns = runs.results || runs;

        updateStats();
        displayRecentRuns();
        displayPipelinesOverview();
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

function updateStats() {
    document.getElementById('totalPipelines').textContent = currentPipelines.length;
    document.getElementById('totalRuns').textContent = currentRuns.length;
    
    const activeRuns = currentRuns.filter(r => r.status === 'running').length;
    document.getElementById('activeRuns').textContent = activeRuns;

    const avgScore = currentRuns.length > 0
        ? (currentRuns.reduce((sum, r) => sum + (r.overall_score || 0), 0) / currentRuns.length).toFixed(1)
        : 0;
    document.getElementById('avgScore').textContent = `${avgScore}%`;
}

function displayRecentRuns() {
    const container = document.getElementById('recentRunsList');
    const recentRuns = currentRuns.slice(0, 5);

    if (recentRuns.length === 0) {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-inbox"></i><p>No runs yet</p></div>';
        return;
    }

    container.innerHTML = recentRuns.map(run => `
        <div class="run-item" onclick="showRunDetails(${run.id})">
            <div class="run-header">
                <span class="run-title">Run #${run.id}</span>
                <span class="badge ${getStatusBadgeClass(run.status)}">${run.status}</span>
            </div>
            <div class="run-meta">
                <span><i class="fas fa-clock"></i> ${formatDate(run.start_time)}</span>
                <span><i class="fas fa-chart-line"></i> ${run.overall_score}%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${run.overall_score}%"></div>
            </div>
        </div>
    `).join('');
}

function displayPipelinesOverview() {
    const container = document.getElementById('pipelinesList');
    
    if (currentPipelines.length === 0) {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-sitemap"></i><p>No pipelines configured</p></div>';
        return;
    }

    container.innerHTML = currentPipelines.slice(0, 5).map(pipeline => `
        <div class="pipeline-item" onclick="showPipelineDetails(${pipeline.id})">
            <div class="pipeline-header">
                <span class="run-title">${pipeline.name}</span>
                <span class="badge info">${pipeline.stages?.length || 0} stages</span>
            </div>
            <div class="run-meta">
                <span><i class="fas fa-project-diagram"></i> ${pipeline.project || 'N/A'}</span>
            </div>
        </div>
    `).join('');
}

// Pipelines View
async function loadPipelines() {
    try {
        const response = await fetch(`${API_BASE}/pipelines/`);
        const data = await response.json();
        currentPipelines = data.results || data;

        displayAllPipelines();
    } catch (error) {
        console.error('Error loading pipelines:', error);
    }
}

function displayAllPipelines() {
    const container = document.getElementById('allPipelinesList');
    
    if (currentPipelines.length === 0) {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-sitemap"></i><p>No pipelines found</p></div>';
        return;
    }

    container.innerHTML = currentPipelines.map(pipeline => `
        <div class="pipeline-item" onclick="showPipelineDetails(${pipeline.id})">
            <div class="pipeline-header">
                <div>
                    <div class="run-title">${pipeline.name}</div>
                    <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.25rem;">
                        ${pipeline.description || 'No description'}
                    </div>
                </div>
                <span class="badge info">${pipeline.stages?.length || 0} stages</span>
            </div>
            <div class="run-meta" style="margin-top: 0.75rem;">
                <span><i class="fas fa-code-branch"></i> ${pipeline.version || 'v1.0'}</span>
                <span><i class="fas fa-project-diagram"></i> Project #${pipeline.project}</span>
            </div>
        </div>
    `).join('');
}

// Runs View
async function loadAllRuns() {
    try {
        const response = await fetch(`${API_BASE}/runs/`);
        const data = await response.json();
        currentRuns = data.results || data;

        displayAllRuns();
        populatePipelineFilter();
    } catch (error) {
        console.error('Error loading runs:', error);
    }
}

function displayAllRuns() {
    const container = document.getElementById('allRunsList');
    
    if (currentRuns.length === 0) {
        container.innerHTML = '<div class="empty-state"><i class="fas fa-play-circle"></i><p>No runs found</p></div>';
        return;
    }

    container.innerHTML = currentRuns.map(run => `
        <div class="run-item" onclick="showRunDetails(${run.id})">
            <div class="run-header">
                <div>
                    <div class="run-title">Run #${run.id}</div>
                    <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.25rem;">
                        ${run.triggered_by || 'Unknown trigger'}
                    </div>
                </div>
                <span class="badge ${getStatusBadgeClass(run.status)}">${run.status}</span>
            </div>
            <div class="run-meta" style="margin-top: 0.75rem;">
                <span><i class="fas fa-calendar"></i> ${formatDate(run.start_time)}</span>
                <span><i class="fas fa-sitemap"></i> Pipeline #${run.pipeline}</span>
                <span><i class="fas fa-chart-line"></i> ${run.overall_score}%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${run.overall_score}%"></div>
            </div>
        </div>
    `).join('');
}

function populatePipelineFilter() {
    const select = document.getElementById('pipelineFilter');
    select.innerHTML = '<option value="">All Pipelines</option>' +
        currentPipelines.map(p => `<option value="${p.id}">${p.name}</option>`).join('');
}

// Trends View
async function loadTrendsView() {
    const select = document.getElementById('trendPipelineSelect');
    select.innerHTML = '<option value="">Select Pipeline</option>' +
        currentPipelines.map(p => `<option value="${p.id}">${p.name}</option>`).join('');

    select.addEventListener('change', async (e) => {
        const pipelineId = e.target.value;
        if (pipelineId) {
            await loadTrendData(pipelineId);
        }
    });
}

async function loadTrendData(pipelineId) {
    try {
        const response = await fetch(`${API_BASE}/pipelines/${pipelineId}/trend/?n=10`);
        const data = await response.json();

        displayTrendChart(data);
    } catch (error) {
        console.error('Error loading trend data:', error);
    }
}

function displayTrendChart(data) {
    const ctx = document.getElementById('trendChart').getContext('2d');

    if (trendChart) {
        trendChart.destroy();
    }

    const labels = data.map(d => `Run #${d.run_id}`).reverse();
    const scores = data.map(d => d.overall_score).reverse();

    trendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Overall Score (%)',
                data: scores,
                borderColor: '#007AFF',
                backgroundColor: 'rgba(0, 122, 255, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    labels: {
                        color: '#FFFFFF'
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        color: '#8E8E93'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: '#8E8E93'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        }
    });
}

// Run Details Modal
async function showRunDetails(runId) {
    try {
        const response = await fetch(`${API_BASE}/runs/${runId}/summary/`);
        const run = await response.json();

        const modalBody = document.getElementById('runModalBody');
        modalBody.innerHTML = `
            <div style="margin-bottom: 1.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h4>Run #${run.id}</h4>
                    <span class="badge ${getStatusBadgeClass(run.status)}">${run.status}</span>
                </div>
                <div class="run-meta">
                    <span><i class="fas fa-user"></i> ${run.triggered_by || 'Unknown'}</span>
                    <span><i class="fas fa-calendar"></i> ${formatDate(run.start_time)}</span>
                </div>
                <div style="margin-top: 1rem;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                        <span>Overall Score</span>
                        <span style="font-weight: 600;">${run.overall_score}%</span>
                    </div>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${run.overall_score}%"></div>
                    </div>
                </div>
            </div>

            <h4 style="margin-bottom: 1rem;">Stage Results</h4>
            ${run.stage_results.map(stage => `
                <div class="stage-item">
                    <div class="stage-header">
                        <span class="stage-name">${stage.stage_name}</span>
                        <span class="badge ${getStatusBadgeClass(stage.status)}">${stage.completion_percent}%</span>
                    </div>
                    ${stage.substage_results.map(sub => `
                        <div class="substage-item">
                            <span class="substage-name">
                                <i class="fas fa-circle" style="font-size: 0.5rem; margin-right: 0.5rem;"></i>
                                ${sub.substage_name}
                            </span>
                            <span class="badge ${getStatusBadgeClass(sub.status)}">${sub.completion_percent}%</span>
                        </div>
                    `).join('')}
                </div>
            `).join('')}
        `;

        document.getElementById('runModal').classList.add('active');
    } catch (error) {
        console.error('Error loading run details:', error);
    }
}

function closeModal() {
    document.getElementById('runModal').classList.remove('active');
}

// Pipeline Details
async function showPipelineDetails(pipelineId) {
    try {
        const response = await fetch(`${API_BASE}/pipelines/${pipelineId}/`);
        const pipeline = await response.json();

        const modalBody = document.getElementById('runModalBody');
        modalBody.innerHTML = `
            <div style="margin-bottom: 1.5rem;">
                <h4>${pipeline.name}</h4>
                <p style="color: var(--text-secondary); font-size: 0.875rem; margin-top: 0.5rem;">
                    ${pipeline.description || 'No description available'}
                </p>
                <div class="run-meta" style="margin-top: 1rem;">
                    <span><i class="fas fa-code-branch"></i> ${pipeline.version || 'v1.0'}</span>
                    <span><i class="fas fa-project-diagram"></i> Project #${pipeline.project}</span>
                </div>
            </div>

            <h4 style="margin-bottom: 1rem;">Stages Configuration</h4>
            ${pipeline.stages.map(stage => `
                <div class="stage-item">
                    <div class="stage-header">
                        <span class="stage-name">${stage.name}</span>
                        <span class="badge info">Weight: ${(stage.weight * 100).toFixed(0)}%</span>
                    </div>
                    <div style="font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 0.75rem;">
                        ${stage.substages.length} substages • ${stage.dod_type} validation
                    </div>
                    ${stage.substages.map(sub => `
                        <div class="substage-item">
                            <span class="substage-name">
                                <i class="fas fa-circle" style="font-size: 0.5rem; margin-right: 0.5rem;"></i>
                                ${sub.name}
                            </span>
                            <span class="badge ${sub.dod_type === 'auto' ? 'success' : 'warning'}">${sub.dod_type}</span>
                        </div>
                    `).join('')}
                </div>
            `).join('')}
        `;

        document.getElementById('runModal').classList.add('active');
    } catch (error) {
        console.error('Error loading pipeline details:', error);
    }
}

// Create Run Modal
async function openCreateRunModal() {
    const select = document.getElementById('pipelineSelect');
    
    if (currentPipelines.length === 0) {
        await loadPipelines();
    }
    
    select.innerHTML = '<option value="">Select Pipeline</option>' +
        currentPipelines.map(p => `<option value="${p.id}">${p.name}</option>`).join('');

    document.getElementById('createRunModal').classList.add('active');
}

function closeCreateRunModal() {
    document.getElementById('createRunModal').classList.remove('active');
    document.getElementById('createRunForm').reset();
}

async function handleCreateRun(e) {
    e.preventDefault();

    const pipelineId = document.getElementById('pipelineSelect').value;
    const triggeredBy = document.getElementById('triggeredBy').value;

    try {
        const response = await fetch(`${API_BASE}/runs/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                pipeline: parseInt(pipelineId),
                triggered_by: triggeredBy
            })
        });

        if (response.ok) {
            closeCreateRunModal();
            loadDashboard();
            alert('Run created successfully!');
        } else {
            alert('Failed to create run');
        }
    } catch (error) {
        console.error('Error creating run:', error);
        alert('Error creating run');
    }
}

// Utility functions
function getStatusBadgeClass(status) {
    const statusMap = {
        'completed': 'success',
        'running': 'warning',
        'failed': 'danger',
        'pending': 'info'
    };
    return statusMap[status] || 'info';
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) {
        return `${diffMins}m ago`;
    } else if (diffHours < 24) {
        return `${diffHours}h ago`;
    } else if (diffDays < 7) {
        return `${diffDays}d ago`;
    } else {
        return date.toLocaleDateString();
    }
}

// Click outside modal to close
window.onclick = function(event) {
    const runModal = document.getElementById('runModal');
    const createModal = document.getElementById('createRunModal');
    
    if (event.target === runModal) {
        closeModal();
    }
    if (event.target === createModal) {
        closeCreateRunModal();
    }
}
