/**
 * AI-60 Customer Segmentation Dashboard
 * Client-Side Interactivity and Chart.js Initializations
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Mobile Navigation Toggle
    initMobileNav();

    // 2. Accordion Toggles (Segments Page)
    initAccordions();

    // 3. Chart Initializations
    initSegmentsCharts();
    initBundlesPage();
    initModelsCharts();
});

/**
 * Mobile Navigation Menu Handler
 */
function initMobileNav() {
    const toggleBtn = document.querySelector('.nav-toggle-btn');
    const navMenu = document.querySelector('.nav-menu');
    
    if (toggleBtn && navMenu) {
        toggleBtn.addEventListener('click', () => {
            navMenu.classList.toggle('mobile-open');
            const icon = toggleBtn.querySelector('i');
            if (icon) {
                icon.classList.toggle('fa-bars');
                icon.classList.toggle('fa-xmark');
            }
        });
    }
}

/**
 * Accordion Expand/Collapse Functionality
 */
function initAccordions() {
    const accordionHeaders = document.querySelectorAll('.accordion-header');
    
    accordionHeaders.forEach(header => {
        header.addEventListener('click', () => {
            const item = header.closest('.accordion-item');
            if (item) {
                item.classList.toggle('active');
            }
        });
    });
}

/**
 * Segments Page Charts (Bar Chart & Doughnut Chart)
 */
function initSegmentsCharts() {
    const barCanvas = document.getElementById('segmentBarChart');
    const pieCanvas = document.getElementById('segmentPieChart');

    if (!barCanvas && !pieCanvas) return;

    fetch('/api/segments-data')
        .then(res => res.json())
        .then(data => {
            // Chart 1: Bar Chart (Cluster Counts)
            if (barCanvas) {
                new Chart(barCanvas, {
                    type: 'bar',
                    data: {
                        labels: data.cluster_labels,
                        datasets: [{
                            label: 'Customer Count',
                            data: data.cluster_counts,
                            backgroundColor: data.cluster_colors,
                            borderRadius: 8,
                            borderWidth: 1,
                            borderColor: data.cluster_colors
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false },
                            tooltip: {
                                padding: 12,
                                boxPadding: 6,
                                callbacks: {
                                    label: (ctx) => ` Customers: ${ctx.parsed.y.toLocaleString()}`
                                }
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                grid: { color: '#f1f5f9' },
                                ticks: { font: { family: 'Inter' }, color: '#64748b' }
                            },
                            x: {
                                grid: { display: false },
                                ticks: { font: { family: 'Inter', size: 11 }, color: '#334155' }
                            }
                        }
                    }
                });
            }

            // Chart 2: Doughnut / Pie Chart (Aggregated Share)
            if (pieCanvas && data.aggregated) {
                new Chart(pieCanvas, {
                    type: 'doughnut',
                    data: {
                        labels: data.aggregated.labels,
                        datasets: [{
                            data: data.aggregated.counts,
                            backgroundColor: data.aggregated.colors,
                            hoverOffset: 6,
                            borderWidth: 2,
                            borderColor: '#ffffff'
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: {
                                    font: { family: 'Inter', size: 12 },
                                    boxWidth: 14,
                                    padding: 16
                                }
                            },
                            tooltip: {
                                padding: 12,
                                callbacks: {
                                    label: (ctx) => {
                                        const val = ctx.parsed;
                                        const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                                        const pct = ((val / total) * 100).toFixed(1);
                                        return ` ${ctx.label}: ${val.toLocaleString()} (${pct}%)`;
                                    }
                                }
                            }
                        },
                        cutout: '65%'
                    }
                });
            }
        })
        .catch(err => console.error('Failed to load segments data:', err));
}

/**
 * Bundles Page: Dynamic Filtering & Lift Bar Chart
 */
let bundlesChartInstance = null;

function initBundlesPage() {
    const segmentSelect = document.getElementById('segmentFilterSelect');
    const searchInput = document.getElementById('bundleSearchInput');
    const tableBody = document.getElementById('bundleTableBody');
    const chartCanvas = document.getElementById('bundleLiftChart');

    if (!segmentSelect || !tableBody) return;

    // Load initial data
    loadBundlesData('All Segments');

    // Dropdown change event
    segmentSelect.addEventListener('change', (e) => {
        loadBundlesData(e.target.value);
    });

    // Search input event
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase().trim();
            const rows = tableBody.querySelectorAll('tr');
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(term) ? '' : 'none';
            });
        });
    }

    function loadBundlesData(segment) {
        const url = `/api/bundles-data?segment=${encodeURIComponent(segment)}`;
        fetch(url)
            .then(res => res.json())
            .then(bundles => {
                renderBundlesTable(bundles);
                if (chartCanvas) {
                    renderBundlesChart(bundles);
                }
            })
            .catch(err => console.error('Error fetching bundles:', err));
    }

    function renderBundlesTable(bundles) {
        tableBody.innerHTML = '';
        if (!bundles || bundles.length === 0) {
            tableBody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: #94a3b8; padding: 2rem;">No bundle recommendations found for this segment.</td></tr>`;
            return;
        }

        bundles.forEach(b => {
            const tr = document.createElement('tr');
            const segmentBadgeClass = getSegmentBadgeClass(b.Segment);

            tr.innerHTML = `
                <td><span class="badge ${segmentBadgeClass}">${escapeHtml(b.Segment)}</span></td>
                <td style="font-weight: 600; color: #0f172a;">${escapeHtml(b['Bundle Products'] || '')}</td>
                <td><code style="background: #f1f5f9; padding: 2px 6px; border-radius: 4px; color: #1e293b; font-size: 0.85rem;">${escapeHtml(b.Antecedents || '')}</code></td>
                <td><code style="background: #eff6ff; padding: 2px 6px; border-radius: 4px; color: #2563eb; font-size: 0.85rem;">${escapeHtml(b.Consequents || '')}</code></td>
                <td><span class="metric-pill">${(parseFloat(b.Confidence) * 100).toFixed(1)}%</span></td>
                <td><span class="badge badge-champion" style="font-size: 0.85rem;">${parseFloat(b.Lift).toFixed(2)}x</span></td>
            `;
            tableBody.appendChild(tr);
        });
    }

    function renderBundlesChart(bundles) {
        // Take top 8 rules by Lift for clean chart layout
        const topBundles = bundles.slice(0, 8);
        const labels = topBundles.map(b => truncateText(b['Bundle Products'], 30));
        const liftValues = topBundles.map(b => parseFloat(b.Lift));
        const confValues = topBundles.map(b => (parseFloat(b.Confidence) * 100).toFixed(1));

        if (bundlesChartInstance) {
            bundlesChartInstance.destroy();
        }

        bundlesChartInstance = new Chart(chartCanvas, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Association Lift Score',
                    data: liftValues,
                    backgroundColor: 'rgba(37, 99, 235, 0.85)',
                    hoverBackgroundColor: '#1d4ed8',
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        padding: 12,
                        callbacks: {
                            title: (items) => topBundles[items[0].dataIndex]['Bundle Products'],
                            label: (ctx) => ` Lift: ${ctx.parsed.x}x | Confidence: ${confValues[ctx.dataIndex]}%`
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        grid: { color: '#f1f5f9' },
                        title: { display: true, text: 'Lift Multiplier (x)', font: { family: 'Inter', size: 12 } }
                    },
                    y: {
                        grid: { display: false },
                        ticks: { font: { family: 'Inter', size: 11 }, color: '#334155' }
                    }
                }
            }
        });
    }
}

/**
 * Models Page: Silhouette Score Comparison Bar Chart
 */
function initModelsCharts() {
    const modelCanvas = document.getElementById('modelComparisonChart');
    if (!modelCanvas) return;

    fetch('/api/models-data')
        .then(res => res.json())
        .then(data => {
            new Chart(modelCanvas, {
                type: 'bar',
                data: {
                    labels: data.models,
                    datasets: [{
                        label: 'Silhouette Score',
                        data: data.silhouette_scores,
                        backgroundColor: [
                            '#2563eb', // K-Means (Champion Blue)
                            '#64748b', // Hierarchical (Slate Challenger)
                            '#ef4444'  # DBSCAN (Red/Excluded)
                        ],
                        borderRadius: 8,
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            padding: 12,
                            callbacks: {
                                label: (ctx) => ` Silhouette Score: ${ctx.parsed.y.toFixed(4)}`
                            }
                        }
                    },
                    scales: {
                        y: {
                            suggestedMin: -0.15,
                            suggestedMax: 0.50,
                            grid: { color: '#f1f5f9' },
                            ticks: { font: { family: 'Inter' }, color: '#64748b' }
                        },
                        x: {
                            grid: { display: false },
                            ticks: { font: { family: 'Inter', size: 13, weight: '600' }, color: '#1e293b' }
                        }
                    }
                }
            });
        })
        .catch(err => console.error('Failed to load model comparison data:', err));
}

// Helpers
function getSegmentBadgeClass(segmentName) {
    if (!segmentName) return 'badge-secondary';
    if (segmentName.includes('Regular')) return 'badge-blue';
    if (segmentName.includes('New') || segmentName.includes('Occasional')) return 'badge-amber';
    if (segmentName.includes('At-Risk')) return 'badge-rose';
    return 'badge-secondary';
}

function truncateText(str, maxLen) {
    if (!str) return '';
    return str.length > maxLen ? str.substring(0, maxLen) + '...' : str;
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
    return String(text).replace(/[&<>"']/g, m => map[m]);
}
