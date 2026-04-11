/**
 * Dream Decoder - Charts Module
 * Handles all Chart.js visualizations
 */

// Chart instances (for updating)
let emotionChart = null;
let sleepChart = null;
let emotionPieChart = null;
let sentimentMiniChart = null;
let sleepMiniChart = null;
let themesChart = null;
let dreamWeekdayChart = null;
let sleepSentimentChart = null;

// Emotion colors
const EMOTION_COLORS = {
    joy: '#fbbf24',
    sadness: '#60a5fa',
    fear: '#a78bfa',
    anger: '#f87171',
    surprise: '#f472b6',
    love: '#fb7185',
    neutral: '#6b6980'
};

// Chart.js global defaults
Chart.defaults.color = '#a8a6b8';
Chart.defaults.borderColor = 'rgba(167, 139, 250, 0.1)';
Chart.defaults.font.family = "'Inter', sans-serif";

/**
 * Initialize or update the emotion trends chart
 */
function renderEmotionChart(trendData) {
    const ctx = document.getElementById('emotion-chart');
    if (!ctx) return;

    // Process data for the chart
    const labels = trendData.map(d => formatDate(d.date));
    const datasets = [];

    // Collect all emotions across all days
    const allEmotions = new Set();
    trendData.forEach(day => {
        Object.keys(day.emotions || {}).forEach(e => allEmotions.add(e));
    });

    // Build stacked datasets for each emotion by day
    allEmotions.forEach(emotion => {
        const color = EMOTION_COLORS[emotion] || '#6b6980';
        datasets.push({
            label: capitalize(emotion),
            data: trendData.map(d => (d.emotions && d.emotions[emotion]) || 0),
            backgroundColor: `${color}CC`,
            borderColor: color,
            borderWidth: 1,
            borderRadius: 4,
            barPercentage: 0.9,
            categoryPercentage: 0.9,
        });
    });

    // If no data, show placeholder
    if (datasets.length === 0) {
        datasets.push({
            label: 'Dreams',
            data: trendData.map(d => d.count || 0),
            borderColor: '#4fd1ff',
            backgroundColor: 'rgba(79, 209, 255, 0.6)',
            borderWidth: 1,
            borderRadius: 4,
        });
    }

    const config = {
        type: 'bar',
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: {
                        boxWidth: 12,
                        padding: 15,
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(26, 24, 37, 0.95)',
                    titleColor: '#f1f0f5',
                    bodyColor: '#a8a6b8',
                    borderColor: 'rgba(167, 139, 250, 0.3)',
                    borderWidth: 1,
                    padding: 12,
                    cornerRadius: 8,
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { stepSize: 1 },
                    grid: { color: 'rgba(167, 139, 250, 0.05)' },
                    stacked: true,
                    title: {
                        display: true,
                        text: 'Dream Count',
                        color: '#4fd1ff'
                    }
                },
                x: {
                    grid: { display: false },
                    stacked: true,
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    };

    if (emotionChart) {
        emotionChart.data = config.data;
        emotionChart.update();
    } else {
        emotionChart = new Chart(ctx, config);
    }
}

/**
 * Initialize or update the sleep quality chart
 */
function renderSleepChart(sleepData) {
    const ctx = document.getElementById('sleep-chart');
    if (!ctx) return;

    const labels = sleepData.map(d => formatDate(d.date));

    const config = {
        type: 'line',
        data: {
            labels,
            datasets: [
                {
                    label: 'Sleep Quality',
                    data: sleepData.map(d => d.quality),
                    borderColor: '#00e5ff',
                    backgroundColor: 'rgba(0, 229, 255, 0.18)',
                    pointBackgroundColor: '#00e5ff',
                    pointBorderColor: '#0b0f1a',
                    pointBorderWidth: 2,
                    borderWidth: 3,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    tension: 0.35,
                    fill: true,
                    yAxisID: 'y',
                },
                {
                    label: 'Hours Slept',
                    data: sleepData.map(d => d.duration),
                    borderColor: '#4fd1ff',
                    backgroundColor: 'rgba(79, 209, 255, 0.16)',
                    pointBackgroundColor: '#4fd1ff',
                    pointBorderColor: '#0b0f1a',
                    pointBorderWidth: 2,
                    borderWidth: 2.5,
                    pointRadius: 3,
                    pointHoverRadius: 5,
                    fill: true,
                    tension: 0.4,
                    yAxisID: 'y1',
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    labels: { boxWidth: 12, padding: 15 }
                },
                tooltip: {
                    backgroundColor: 'rgba(26, 24, 37, 0.95)',
                    titleColor: '#f1f0f5',
                    bodyColor: '#a8a6b8',
                    borderColor: 'rgba(167, 139, 250, 0.3)',
                    borderWidth: 1,
                    padding: 12,
                    cornerRadius: 8,
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    position: 'left',
                    min: 0,
                    max: 10,
                    title: {
                        display: true,
                        text: 'Quality (1-10)',
                        color: '#00e5ff'
                    },
                    grid: { color: 'rgba(167, 139, 250, 0.05)' }
                },
                y1: {
                    type: 'linear',
                    position: 'right',
                    min: 0,
                    max: 12,
                    title: {
                        display: true,
                        text: 'Hours',
                        color: '#4fd1ff'
                    },
                    grid: { display: false }
                },
                x: {
                    grid: { display: false }
                }
            },
            interaction: {
                mode: 'index',
                intersect: false
            }
        }
    };

    if (sleepChart) {
        sleepChart.data = config.data;
        sleepChart.update();
    } else {
        sleepChart = new Chart(ctx, config);
    }
}

/**
 * Initialize or update the emotion pie chart
 */
function renderEmotionPieChart(emotionBreakdown) {
    const ctx = document.getElementById('emotion-pie-chart');
    if (!ctx) return;

    const entries = Object.entries(emotionBreakdown || {})
        .filter(([, value]) => Number(value) > 0)
        .sort((a, b) => Number(b[1]) - Number(a[1]));

    const labels = entries.length ? entries.map(([emotion]) => capitalize(emotion)) : ['No Data'];
    const data = entries.length ? entries.map(([, value]) => Number(value)) : [1];
    const colors = entries.length
        ? entries.map(([emotion]) => EMOTION_COLORS[emotion] || '#6b6980')
        : ['#6b6980'];

    const config = {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{
                data,
                backgroundColor: colors,
                borderColor: 'rgba(255, 255, 255, 0.8)',
                borderWidth: 2,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '58%',
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        boxWidth: 12,
                        color: '#ffffff',
                        padding: 15,
                        generateLabels: function (chart) {
                            const dataset = chart.data.datasets[0];
                            const total = dataset.data.reduce((sum, value) => sum + Number(value || 0), 0);
                            return chart.data.labels.map((label, i) => {
                                const value = Number(dataset.data[i] || 0);
                                const percentage = total > 0 ? Math.round((value / total) * 100) : 0;
                                return {
                                    text: `${label} (${percentage}%)`,
                                    fillStyle: dataset.backgroundColor[i],
                                    strokeStyle: dataset.borderColor,
                                    lineWidth: dataset.borderWidth,
                                    color: '#ffffff',
                                    fontColor: '#ffffff',
                                    index: i
                                };
                            });
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(26, 24, 37, 0.95)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: 'rgba(167, 139, 250, 0.3)',
                    borderWidth: 1,
                    padding: 12,
                    cornerRadius: 8,
                    callbacks: {
                        label: function (context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = Math.round((context.raw / total) * 100);
                            return `${context.label}: ${context.raw} dreams (${percentage}%)`;
                        }
                    }
                }
            }
        }
    };

    if (emotionPieChart) {
        emotionPieChart.data = config.data;
        emotionPieChart.update();
    } else {
        emotionPieChart = new Chart(ctx, config);
    }
}

/**
 * Render top themes as ranked horizontal bars
 */
function renderThemesChart(keywords = []) {
    const ctx = document.getElementById('themes-chart');
    const noteEl = document.getElementById('themes-chart-note');
    if (!ctx) return;

    const list = Array.isArray(keywords) ? keywords.slice(0, 10) : [];
    if (!list.length) {
        if (noteEl) noteEl.textContent = 'Record more dreams to see themes';
        if (themesChart) {
            themesChart.destroy();
            themesChart = null;
        }
        return;
    }

    // Weighted by rank (top keyword gets highest score)
    const labels = list.map((k) => String(k));
    const values = list.map((_, i) => list.length - i);
    if (noteEl) noteEl.textContent = `Showing top ${list.length} themes ranked by frequency`;

    const config = {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Theme Weight',
                data: values,
                backgroundColor: labels.map((_, i) => i < 3 ? 'rgba(0, 229, 255, 0.7)' : 'rgba(79, 209, 255, 0.45)'),
                borderColor: labels.map(() => '#00e5ff'),
                borderWidth: 1.5,
                borderRadius: 8,
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(26, 24, 37, 0.95)',
                    titleColor: '#f1f0f5',
                    bodyColor: '#a8a6b8'
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: { precision: 0 },
                    grid: { color: 'rgba(167, 139, 250, 0.05)' }
                },
                y: {
                    grid: { display: false }
                }
            }
        }
    };

    if (themesChart) {
        themesChart.data = config.data;
        themesChart.update();
    } else {
        themesChart = new Chart(ctx, config);
    }
}

/**
 * Render dream activity distribution across weekdays
 */
function renderDreamWeekdayChart(dreams = []) {
    const ctx = document.getElementById('dream-weekday-chart');
    if (!ctx) return;

    const dayLabels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const counts = [0, 0, 0, 0, 0, 0, 0];

    dreams.forEach((dream) => {
        const raw = dream.created_at || dream.date;
        const date = new Date(raw);
        if (!Number.isNaN(date.getTime())) {
            counts[date.getDay()] += 1;
        }
    });

    const config = {
        type: 'bar',
        data: {
            labels: dayLabels,
            datasets: [{
                label: 'Dream Count',
                data: counts,
                backgroundColor: counts.map((v) => v > 0 ? 'rgba(0, 229, 255, 0.55)' : 'rgba(107, 105, 128, 0.35)'),
                borderColor: '#00e5ff',
                borderWidth: 1.5,
                borderRadius: 8,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(26, 24, 37, 0.95)',
                    titleColor: '#f1f0f5',
                    bodyColor: '#a8a6b8',
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { precision: 0, stepSize: 1 },
                    grid: { color: 'rgba(167, 139, 250, 0.05)' }
                },
                x: {
                    grid: { display: false }
                }
            }
        }
    };

    if (dreamWeekdayChart) {
        dreamWeekdayChart.data = config.data;
        dreamWeekdayChart.update();
    } else {
        dreamWeekdayChart = new Chart(ctx, config);
    }
}

/**
 * Render scatter of sleep quality vs dream sentiment score
 */
function renderSleepSentimentChart(dreams = [], sleepByDate = {}) {
    const ctx = document.getElementById('sleep-sentiment-chart');
    if (!ctx) return;

    const points = [];
    dreams.forEach((dream) => {
        const dateKey = toDateKey(dream.created_at || dream.date);
        const sentimentScore = Number(dream.sentiment_score);
        const linked = sleepByDate[dateKey];
        const quality = linked && linked.length ? Number(linked[0].quality_rating) : NaN;

        if (Number.isFinite(sentimentScore) && Number.isFinite(quality)) {
            points.push({
                x: quality,
                y: sentimentScore,
                emotion: dream.primary_emotion || 'neutral'
            });
        }
    });

    const config = {
        type: 'scatter',
        data: {
            datasets: [{
                label: 'Dream Points',
                data: points,
                backgroundColor: points.map((p) => EMOTION_COLORS[p.emotion] || '#4fd1ff'),
                borderColor: '#00e5ff',
                borderWidth: 1,
                pointRadius: 5,
                pointHoverRadius: 7,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(26, 24, 37, 0.95)',
                    titleColor: '#f1f0f5',
                    bodyColor: '#a8a6b8',
                    callbacks: {
                        label: (context) => `Quality: ${context.raw.x}/10 | Sentiment: ${context.raw.y.toFixed(2)}`
                    }
                }
            },
            scales: {
                x: {
                    min: 0,
                    max: 10,
                    title: { display: true, text: 'Sleep Quality (1-10)', color: '#00e5ff' },
                    grid: { color: 'rgba(167, 139, 250, 0.05)' }
                },
                y: {
                    min: -1,
                    max: 1,
                    title: { display: true, text: 'Sentiment Score (-1 to 1)', color: '#4fd1ff' },
                    grid: { color: 'rgba(167, 139, 250, 0.05)' }
                }
            }
        }
    };

    if (sleepSentimentChart) {
        sleepSentimentChart.data = config.data;
        sleepSentimentChart.update();
    } else {
        sleepSentimentChart = new Chart(ctx, config);
    }
}

/**
 * Render compact sentiment chart for dashboard summary
 */
function renderSentimentMiniChart(sentimentBreakdown = {}) {
    const ctx = document.getElementById('analytics-sentiment-mini-chart');
    if (!ctx) return;

    const entries = Object.entries(sentimentBreakdown)
        .filter(([, count]) => Number(count) > 0)
        .sort((a, b) => b[1] - a[1]);

    const labels = entries.length ? entries.map(([label]) => capitalize(label)) : ['No Data'];
    const values = entries.length ? entries.map(([, value]) => Number(value)) : [1];
    const colors = entries.length
        ? labels.map((label) => {
            const key = label.toLowerCase();
            if (key === 'positive') return '#22c55e';
            if (key === 'negative') return '#ef4444';
            return '#4fd1ff';
        })
        : ['#6b6980'];

    const config = {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{
                data: values,
                backgroundColor: colors,
                borderColor: 'rgba(18, 24, 43, 0.9)',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '62%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { boxWidth: 10, padding: 10 }
                },
                tooltip: {
                    backgroundColor: 'rgba(26, 24, 37, 0.95)',
                    titleColor: '#f1f0f5',
                    bodyColor: '#a8a6b8',
                }
            }
        }
    };

    if (sentimentMiniChart) {
        sentimentMiniChart.data = config.data;
        sentimentMiniChart.update();
    } else {
        sentimentMiniChart = new Chart(ctx, config);
    }
}

/**
 * Render compact sleep pattern chart for dashboard summary
 */
function renderSleepMiniChart(records = []) {
    const ctx = document.getElementById('analytics-sleep-mini-chart');
    if (!ctx) return;

    const qualityValues = records.map((r) => Number(r.quality_rating)).filter((v) => Number.isFinite(v));
    const durationValues = records.map((r) => Number(r.duration_hours)).filter((v) => Number.isFinite(v));
    const wakeValues = records.map((r) => Number(r.wakeups || 0)).filter((v) => Number.isFinite(v));

    const avgQuality = qualityValues.length ? qualityValues.reduce((a, b) => a + b, 0) / qualityValues.length : 0;
    const avgDuration = durationValues.length ? durationValues.reduce((a, b) => a + b, 0) / durationValues.length : 0;
    const avgWake = wakeValues.length ? wakeValues.reduce((a, b) => a + b, 0) / wakeValues.length : 0;

    const config = {
        type: 'bar',
        data: {
            labels: ['Avg Quality', 'Avg Duration (h)', 'Avg Wakeups'],
            datasets: [{
                data: [avgQuality, avgDuration, avgWake],
                backgroundColor: ['#00e5ffb3', '#4fd1ffb3', '#7ca7d8b3'],
                borderColor: ['#00e5ff', '#4fd1ff', '#7ca7d8'],
                borderWidth: 2,
                borderRadius: 8,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(26, 24, 37, 0.95)',
                    titleColor: '#f1f0f5',
                    bodyColor: '#a8a6b8',
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(167, 139, 250, 0.05)' }
                },
                x: {
                    grid: { display: false }
                }
            }
        }
    };

    if (sleepMiniChart) {
        sleepMiniChart.data = config.data;
        sleepMiniChart.update();
    } else {
        sleepMiniChart = new Chart(ctx, config);
    }
}

/**
 * Render keywords cloud
 */
function renderKeywordsCloud(keywords) {
    const container = document.getElementById('keywords-cloud');
    if (!container) return;

    if (!keywords || keywords.length === 0) {
        container.innerHTML = `
            <div class="empty-state small">
                <p>Record more dreams to see themes</p>
            </div>
        `;
        return;
    }

    // Assign sizes based on position (first ones are more frequent)
    const html = keywords.map((keyword, index) => {
        let sizeClass = '';
        if (index < 3) sizeClass = 'large';
        else if (index < 7) sizeClass = 'medium';

        return `<span class="keyword-cloud-item ${sizeClass}">${escapeHtml(keyword)}</span>`;
    }).join('');

    container.innerHTML = html;
}

// ==========================================
// HELPER FUNCTIONS
// ==========================================

/**
 * Format date for display
 */
function formatDate(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) return dateStr; // Return original string if invalid
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

/**
 * Capitalize first letter
 */
function capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}
