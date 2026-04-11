/**
 * Dream Decoder - Main Application
 * UI logic and event handling
 */

// ==========================================
// INITIALIZATION
// ==========================================

let lastDreamText = ''; // Store the latest dream text for Jungian analysis
let dreamJournalCache = [];

document.addEventListener('DOMContentLoaded', () => {
    console.log('🌙 Dream Decoder - Initializing...');

    // Check if running via file:// protocol
    if (window.location.protocol === 'file:') {
        showToast('error', 'App is running from a local file. Please use http://localhost:5000 to access the application properly.');
        // Add a visible warning to the page too
        const mainContent = document.querySelector('.main-content');
        if (mainContent) {
            const warning = document.createElement('div');
            warning.className = 'protocol-warning';
            warning.innerHTML = `
                <div class="card" style="border: 2px solid var(--color-error); margin-bottom: 20px;">
                    <div class="card-body">
                        <h3>⚠️ Connection Warning</h3>
                        <p>It looks like you opened the <code>index.html</code> file directly. This will prevent the AI from saving and analyzing your dreams.</p>
                        <p>Please use the <strong>start.bat</strong> script and open <strong>http://localhost:5000</strong> in your browser.</p>
                    </div>
                </div>
            `;
            mainContent.prepend(warning);
        }
    }

    // Initialize components
    initTabs();
    initForms();
    initDateDefaults();

    // Load initial data
    loadDreams();
    loadSleepRecords();

    // Check API health
    checkHealth();
});

/**
 * Check API health on startup
 */
async function checkHealth() {
    try {
        await healthCheck();
        console.log('✅ API is healthy');
    } catch (error) {
        console.error('❌ API health check failed:', error);
        showToast('error', 'Cannot connect to server. Make sure the backend is running.');
    }
}

/**
 * Toggle loading overlay visibility
 */
function toggleLoadingOverlay(show, text = null) {
    const overlay = document.getElementById('loading-overlay');
    if (!overlay) return;

    if (text) {
        const textEl = overlay.querySelector('.loading-text');
        if (textEl) textEl.textContent = text;
    }

    if (show) {
        overlay.classList.add('active');
    } else {
        overlay.classList.remove('active');
    }
}

// ==========================================
// TAB NAVIGATION
// ==========================================

function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.dataset.tab;

            // Update buttons
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Update panels
            tabPanels.forEach(panel => {
                panel.classList.remove('active');
                if (panel.id === `${tabId}-panel`) {
                    panel.classList.add('active');
                }
            });

            // Load data for the tab
            onTabChange(tabId);
        });
    });
}

/**
 * Handle tab changes - load relevant data
 */
function onTabChange(tabId) {
    switch (tabId) {
        case 'journal':
            break;
        case 'dream-journal':
            loadDreams();
            break;
        case 'sleep':
            loadSleepRecords();
            break;
        case 'analytics':
            loadAnalytics();
            break;
        case 'insights':
            loadInsights();
            break;
        case 'jungian':
            handleJungianTab();
            break;
    }
}

// ==========================================
// FORM HANDLING
// ==========================================

function initForms() {
    // Dream form
    const dreamForm = document.getElementById('dream-form');
    if (dreamForm) {
        dreamForm.addEventListener('submit', handleDreamSubmit);
    }

    // Sleep form
    const sleepForm = document.getElementById('sleep-form');
    if (sleepForm) {
        sleepForm.addEventListener('submit', handleSleepSubmit);
    }

    // Quality slider
    const qualitySlider = document.getElementById('sleep-quality');
    const qualityValue = document.getElementById('quality-value');
    if (qualitySlider && qualityValue) {
        qualitySlider.addEventListener('input', () => {
            qualityValue.textContent = qualitySlider.value;
        });
    }

    // Period selector for analytics
    const periodSelect = document.getElementById('emotion-period');
    if (periodSelect) {
        periodSelect.addEventListener('change', () => {
            loadAnalytics();
        });
    }

    // Refresh insights button
    const refreshBtn = document.getElementById('refresh-insights');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', () => {
            loadInsights();
        });
    }

    const dreamSearch = document.getElementById('dream-journal-search');
    if (dreamSearch) {
        dreamSearch.addEventListener('input', renderDreamJournalList);
    }

    const dreamEmotionFilter = document.getElementById('dream-journal-emotion-filter');
    if (dreamEmotionFilter) {
        dreamEmotionFilter.addEventListener('change', renderDreamJournalList);
    }

    // Jungian re-analyze button
    const jungianBtn = document.getElementById('analyze-jungian-btn');
    if (jungianBtn) {
        jungianBtn.addEventListener('click', () => {
            handleJungianTab();
        });
    }
}

/**
 * Set default dates
 */
function initDateDefaults() {
    const dateInput = document.getElementById('sleep-date');
    if (dateInput) {
        dateInput.value = new Date().toISOString().split('T')[0];
    }

    const dreamDateInput = document.getElementById('dream-date');
    if (dreamDateInput && !dreamDateInput.value) {
        dreamDateInput.value = new Date().toISOString().split('T')[0];
    }

    const dreamTimeInput = document.getElementById('dream-time');
    if (dreamTimeInput && !dreamTimeInput.value) {
        const now = new Date();
        dreamTimeInput.value = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
    }
}

function getLiveDateTimeParts() {
    const now = new Date();
    const date = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
    const time = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
    return { date, time };
}

function toDateKey(value) {
    if (!value) return '';

    const text = String(value).trim();
    const directMatch = text.match(/^(\d{4}-\d{2}-\d{2})/);
    if (directMatch) return directMatch[1];

    const parsed = new Date(text);
    if (!Number.isNaN(parsed.getTime())) {
        const y = parsed.getFullYear();
        const m = String(parsed.getMonth() + 1).padStart(2, '0');
        const d = String(parsed.getDate()).padStart(2, '0');
        return `${y}-${m}-${d}`;
    }

    return '';
}

// ==========================================
// DREAM HANDLING
// ==========================================

/**
 * Handle dream form submission
 */
async function handleDreamSubmit(e) {
    e.preventDefault();

    const contentInput = document.getElementById('dream-content');
    const submitBtn = document.getElementById('submit-dream');
    const dreamDateInput = document.getElementById('dream-date');
    const dreamTimeInput = document.getElementById('dream-time');
    const sleepDurationInput = document.getElementById('dream-sleep-duration');
    const sleepQualityInput = document.getElementById('dream-sleep-quality');
    const sleepWakeupsInput = document.getElementById('dream-sleep-wakeups');
    const sleepTimeInput = document.getElementById('dream-sleep-time');
    const wakeTimeInput = document.getElementById('dream-wake-time');
    const dreamNotesInput = document.getElementById('dream-notes');

    const content = contentInput.value.trim();

    // Save for potential Jungian analysis
    lastDreamText = content;

    if (!content) {
        showToast('warning', 'Please describe your dream first.');
        return;
    }

    if (content.length < 10) {
        showToast('warning', 'Please provide a bit more detail (at least 10 characters) for a better analysis.');
        return;
    }

    // Disable button during processing
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="btn-icon">⏳</span><span>Analyzing...</span>';

    try {
        toggleLoadingOverlay(true, 'Analyzing your dream...');

        // Always capture timestamp from live clock at submit time.
        const liveDateTime = getLiveDateTimeParts();
        if (dreamDateInput) {
            dreamDateInput.value = liveDateTime.date;
        }
        if (dreamTimeInput) {
            dreamTimeInput.value = liveDateTime.time;
        }

        const sleepTime = sleepTimeInput?.value || '';
        const wakeTime = wakeTimeInput?.value || '';
        let durationHours = parseFloat(sleepDurationInput?.value);

        if ((!Number.isFinite(durationHours) || durationHours <= 0) && sleepTime && wakeTime) {
            const sleep = new Date(`2000-01-01T${sleepTime}`);
            let wake = new Date(`2000-01-01T${wakeTime}`);
            if (wake <= sleep) {
                wake = new Date(`2000-01-02T${wakeTime}`);
            }
            durationHours = (wake - sleep) / (1000 * 60 * 60);
        }

        const payload = {
            content,
            dream_date: liveDateTime.date,
            dream_time: liveDateTime.time,
            sleep_data: {
                date: liveDateTime.date,
                duration_hours: Number.isFinite(durationHours) ? Number(durationHours.toFixed(2)) : undefined,
                quality_rating: parseInt(sleepQualityInput?.value || '7', 10),
                interruptions: parseInt(sleepWakeupsInput?.value || '0', 10),
                sleep_time: sleepTime || undefined,
                wake_time: wakeTime || undefined,
                notes: (dreamNotesInput?.value || '').trim(),
            },
        };

        // Create dream with analysis and optional sleep scoring
        const dream = await createDream(payload);

        // Show success
        showToast('success', 'Dream saved and analyzed!');

        // Show analysis preview
        showAnalysisPreview(dream);

        // Clear form
        contentInput.value = '';
        if (dreamNotesInput) {
            dreamNotesInput.value = '';
        }

        // Reload dreams list
        await loadDreams();

        // Reload analytics and insights to reflect new data
        console.log('🔄 Reloading analytics and insights after submission...');
        loadAnalytics();
        loadInsights();

        // Auto-open modal for the new dream to show full interpretation
        if (dream.id) {
            openDreamModal({
                id: dream.id,
                content: content,
                emotion: dream.primary_emotion || 'neutral',
                sentiment: dream.sentiment || 'neutral',
                keywords: dream.keywords || [],
                date: 'Just now'
            });
        }

    } catch (error) {
        showToast('error', `Failed to save dream: ${error.message}`);
    } finally {
        toggleLoadingOverlay(false);
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<span class="btn-icon">🧠</span><span>Analyze & Save</span>';
    }
}

/**
 * Show analysis preview after saving
 */
function showAnalysisPreview(dream) {
    const preview = document.getElementById('analysis-preview');
    const content = preview.querySelector('.analysis-content');

    if (!preview || !content) return;

    const sentiment = dream.sentiment || 'neutral';
    const sentimentClass = `sentiment-${sentiment}`;
    const primaryEmotion = dream.primary_emotion || dream.emotion || 'neutral';
    const emotionEmoji = getEmotionEmoji(primaryEmotion);
    const sleepQuality = dream.analysis?.sleep?.quality;
    const disturbance = dream.analysis?.sleep?.disturbance;
    const themes = Array.isArray(dream.analysis?.themes) ? dream.analysis.themes : [];
    const topTheme = themes.length > 0 ? themes[0] : null;
    const topKeywords = (dream.keywords || []).slice(0, 3);

    const emotionTipMap = {
        fear: 'Try grounding and calming breathing before sleep.',
        sadness: 'Be gentle with yourself and allow emotional rest today.',
        anger: 'Release stress through movement and a short wind-down routine.',
        joy: 'Keep your current habits; they are supporting positive dreams.',
        surprise: 'Reflect on recent changes and what they may be teaching you.',
        neutral: 'Continue journaling consistently to reveal deeper patterns.',
        confusion: 'Take a few minutes to write what felt unclear in the dream.'
    };
    const processingTip = emotionTipMap[primaryEmotion] || 'Take time for self-care today.';

    content.innerHTML = `
        <div class="analysis-row">
            <span class="analysis-label">Top Emotion:</span>
            <span class="analysis-value">
                ${emotionEmoji} ${capitalize(primaryEmotion)}
            </span>
        </div>
        <div class="analysis-row">
            <span class="analysis-label">Sentiment:</span>
            <span class="analysis-value ${sentimentClass}">
                ${capitalize(sentiment)} ${typeof dream.sentiment_score === 'number' ? `(Polarity: ${dream.sentiment_score.toFixed(2)})` : ''}
            </span>
        </div>
        ${sleepQuality ? `
        <div class="analysis-row">
            <span class="analysis-label">Sleep Quality:</span>
            <span class="analysis-value">
                ${sleepQuality.overall_score}/100 (${sleepQuality.grade})
            </span>
        </div>
        ` : ''}
        ${disturbance ? `
        <div class="analysis-row">
            <span class="analysis-label">Disturbance Risk:</span>
            <span class="analysis-value">
                ${disturbance.risk_level} (${Math.round((disturbance.probability || 0) * 100)}%)
            </span>
        </div>
        ` : ''}
        ${topKeywords.length ? `
        <div class="analysis-row">
            <span class="analysis-label">Keywords:</span>
            <span class="analysis-value">
                ${topKeywords.map(k => `<span class="keyword-tag">${k}</span>`).join(' ')}
            </span>
        </div>
        ` : ''}
        ${topTheme ? `
        <div class="analysis-row">
            <span class="analysis-label">Theme:</span>
            <span class="analysis-value">${escapeHtml(topTheme)}</span>
        </div>
        ` : ''}
        <div class="analysis-row" style="flex-direction: column; align-items: flex-start;">
            <span class="analysis-label">Processing ${capitalize(primaryEmotion)}:</span>
            <span class="analysis-value" style="margin-top: 8px;">${processingTip}</span>
        </div>
    `;

    preview.classList.remove('hidden');

    // Hide after 10 seconds
    setTimeout(() => {
        preview.classList.add('hidden');
    }, 10000);
}

/**
 * Load and display dreams list
 */
async function loadDreams() {
    const container = document.getElementById('dreams-list');
    const countEl = document.getElementById('dream-count');

    if (!container) return;

    try {
        const [response, sleepResp] = await Promise.all([
            getDreams(50, 0),
            getSleepRecords(500, 0)
        ]);

        const dreams = response.dreams || [];
        const sleepRecords = (sleepResp?.records || []).slice().sort((a, b) => {
            const aTs = new Date(a.created_at || a.date || 0).getTime();
            const bTs = new Date(b.created_at || b.date || 0).getTime();
            return bTs - aTs;
        });

        // Pair sleep records to dreams by date and order, so each dream card shows one sleep log.
        const sleepByDate = {};
        sleepRecords.forEach((record) => {
            const key = toDateKey(record.date);
            if (!key) return;
            if (!sleepByDate[key]) sleepByDate[key] = [];
            sleepByDate[key].push(record);
        });

        const dreamDateIndices = {};
        dreamJournalCache = dreams.map((dream) => {
            const dateKey = toDateKey(dream.created_at || dream.date);
            dreamDateIndices[dateKey] = (dreamDateIndices[dateKey] || 0);
            const idx = dreamDateIndices[dateKey];
            const linkedSleep = (sleepByDate[dateKey] && sleepByDate[dateKey][idx]) ? sleepByDate[dateKey][idx] : null;
            dreamDateIndices[dateKey] += 1;

            return {
                ...dream,
                linked_sleep: linkedSleep
            };
        });

        // Update count
        if (countEl) {
            countEl.textContent = `${response.total} dream${response.total !== 1 ? 's' : ''}`;
        }

        const emotionFilter = document.getElementById('dream-journal-emotion-filter');
        if (emotionFilter) {
            const emotions = Array.from(new Set(dreams.map(d => (d.primary_emotion || 'neutral').toLowerCase())));
            emotionFilter.innerHTML = ['all', ...emotions]
                .map(e => `<option value="${e}">${e === 'all' ? 'All' : capitalize(e)}</option>`)
                .join('');
        }

        if (dreams.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <span class="empty-icon">🌟</span>
                    <p>No dreams recorded yet</p>
                    <p class="hint">Start your journey by recording your first dream!</p>
                </div>
            `;
            return;
        }

        renderDreamJournalList();

    } catch (error) {
        container.innerHTML = `
            <div class="empty-state">
                <span class="empty-icon">⚠️</span>
                <p>Failed to load dreams</p>
                <p class="hint">${error.message}</p>
            </div>
        `;
    }
}

function renderDreamJournalList() {
    const container = document.getElementById('dreams-list');
    const countEl = document.getElementById('dream-count');
    if (!container) {
        return;
    }

    const query = (document.getElementById('dream-journal-search')?.value || '').toLowerCase().trim();
    const selectedEmotion = (document.getElementById('dream-journal-emotion-filter')?.value || 'all').toLowerCase();

    const dreams = dreamJournalCache.filter(dream => {
        const emotion = (dream.primary_emotion || 'neutral').toLowerCase();
        const text = `${dream.content || ''} ${dream.sentiment || ''} ${dream.primary_emotion || ''} ${(dream.keywords || []).join(' ')}`.toLowerCase();
        const emotionMatch = selectedEmotion === 'all' || emotion === selectedEmotion;
        const queryMatch = !query || text.includes(query);
        return emotionMatch && queryMatch;
    });

    if (countEl) {
        countEl.textContent = `${dreams.length} dream${dreams.length !== 1 ? 's' : ''}`;
    }

    if (dreams.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <span class="empty-icon">🌟</span>
                <p>No dreams match your filter</p>
            </div>
        `;
        return;
    }

    container.innerHTML = dreams.map(dream => renderDreamItem(dream)).join('');

    // Add click handlers for dream items (opens modal)
    container.querySelectorAll('.dream-item').forEach(item => {
        item.addEventListener('click', (e) => {
            if (e.target.closest('.btn-delete')) return;

            const dreamData = {
                id: item.dataset.id,
                content: item.dataset.content,
                emotion: item.dataset.emotion || 'neutral',
                sentiment: item.dataset.sentiment || 'neutral',
                keywords: item.dataset.keywords ? item.dataset.keywords.split(',') : [],
                date: item.dataset.date || ''
            };
            openDreamModal(dreamData);
        });
    });

    // Add delete handlers
    container.querySelectorAll('.btn-delete').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.stopPropagation();
            const id = btn.dataset.id;
            if (confirm('Are you sure you want to delete this dream?')) {
                try {
                    await deleteDream(id);
                    showToast('success', 'Dream deleted');
                    loadDreams();
                } catch (error) {
                    showToast('error', 'Failed to delete dream');
                }
            }
        });
    });
}

/**
 * Render a single dream item
 */
function renderDreamItem(dream) {
    const emotionEmoji = getEmotionEmoji(dream.primary_emotion);
    const date = formatDateTime(dream.created_at);
    const keywords = (dream.keywords || []).slice(0, 4);
    const keywordsStr = (dream.keywords || []).join(',');
    const linkedSleep = dream.linked_sleep;

    const sleepLogHtml = linkedSleep ? `
        <div class="dream-sleep-log">
            <div class="dream-sleep-title">😴 Sleep Log</div>
            <div class="dream-sleep-row">
                <span>Duration: ${typeof linkedSleep.duration_hours === 'number' ? linkedSleep.duration_hours.toFixed(1) : '-'}h</span>
                <span>Quality: ${linkedSleep.quality_rating ?? '-'} / 10</span>
                <span>Wake-ups: ${linkedSleep.wakeups ?? 0}</span>
            </div>
            ${(linkedSleep.sleep_time && linkedSleep.wake_time) ? `<div class="dream-sleep-row muted">${linkedSleep.sleep_time} - ${linkedSleep.wake_time}</div>` : ''}
            ${linkedSleep.notes ? `<div class="dream-sleep-row muted">${escapeHtml(linkedSleep.notes)}</div>` : ''}
        </div>
    ` : `
        <div class="dream-sleep-log muted">
            <div class="dream-sleep-title">😴 Sleep Log</div>
            <div class="dream-sleep-row">No linked sleep record</div>
        </div>
    `;

    // Get categories badges (NEW!)
    const categories = dream.categories || [];
    const categoryBadges = categories
        .filter(cat => cat !== 'ordinary')
        .map(cat => `<span class="category-badge badge-${cat}">${capitalize(cat)}</span>`)
        .join('');

    return `
        <div class="dream-item" 
             data-id="${dream.id}"
             data-content="${escapeHtml(dream.content).replace(/"/g, '&quot;')}"
             data-emotion="${dream.primary_emotion || 'neutral'}"
             data-sentiment="${dream.sentiment || 'neutral'}"
             data-keywords="${keywordsStr}"
             data-date="${date}">
            <div class="dream-item-header">
                <div class="dream-header-left">
                    <span class="dream-date">${date}</span>
                    <div class="dream-badges">${categoryBadges}</div>
                </div>
                <span class="dream-emotion">${emotionEmoji} ${capitalize(dream.primary_emotion || 'neutral')}</span>
            </div>
            <p class="dream-content">${escapeHtml(dream.content)}</p>
            ${keywords.length > 0 ? `
            <div class="dream-keywords">
                ${keywords.map(k => `<span class="keyword-tag">${k}</span>`).join('')}
            </div>
            ` : ''}
            ${sleepLogHtml}
            <div class="dream-actions">
                <button class="btn-delete" data-id="${dream.id}" title="Delete dream">🗑️</button>
            </div>
        </div>
    `;
}

// ==========================================
// DREAM MODAL
// ==========================================

/**
 * Open dream detail modal
 */
function openDreamModal(dream) {
    const modal = document.getElementById('dream-modal');
    if (!modal) return;

    // Health insights for emotions
    const healthInsights = {
        fear: 'Fear-based dreams often reflect daytime anxiety or unresolved stress. Consider relaxation techniques like deep breathing before bed.',
        sadness: 'Sad dreams may indicate unprocessed emotions. Journaling during the day can help you work through these feelings.',
        anger: 'Anger in dreams often reflects suppressed frustrations. Physical exercise and creative outlets can provide healthy release.',
        joy: 'Joyful dreams indicate emotional balance! Your subconscious is reflecting positive life experiences and contentment.',
        surprise: 'Dreams of surprise often relate to unexpected changes in your life. Embrace adaptability and stay open to new experiences.',
        love: 'Dreams of love reflect your emotional connections. Nurture your relationships and express gratitude to loved ones.'
    };

    // Populate modal
    document.getElementById('modal-date').textContent = dream.date;
    document.getElementById('modal-dream-text').textContent = dream.content;
    document.getElementById('modal-emotion').innerHTML = `${getEmotionEmoji(dream.emotion)} ${capitalize(dream.emotion)}`;

    // Sentiment
    const sentimentEl = document.getElementById('modal-sentiment');
    const sentiment = dream.sentiment || 'neutral';
    sentimentEl.textContent = capitalize(sentiment);
    sentimentEl.className = `modal-sentiment ${sentiment}`;

    // Keywords
    const keywordsEl = document.getElementById('modal-keywords');
    if (dream.keywords && dream.keywords.length > 0) {
        keywordsEl.innerHTML = dream.keywords
            .filter(k => k.trim())
            .map(k => `<span class="keyword-tag">${k}</span>`)
            .join('');
    } else {
        keywordsEl.innerHTML = '<span style="color: var(--color-text-muted);">No keywords extracted</span>';
    }

    // Health insight
    const healthSection = document.getElementById('modal-health-section');
    const healthInsightEl = document.getElementById('modal-health-insight');
    const analyticsReportEl = document.getElementById('modal-analytics-report');
    const emotionKey = (dream.emotion || 'neutral').toLowerCase();
    const insight = healthInsights[emotionKey];

    if (analyticsReportEl) {
        analyticsReportEl.innerHTML = '<p class="hint">Loading detailed analytics...</p>';
    }

    if (insight) {
        healthInsightEl.textContent = insight;
        healthSection.style.display = 'block';
    } else {
        healthSection.style.display = 'none';
    }

    // Show modal
    modal.classList.remove('hidden');

    // Fetch full dream details for interpretation
    const fetchFullDetails = async () => {
        try {
            const [fullDream, sleepResp] = await Promise.all([
                getDream(dream.id),
                getSleepRecords(365, 0)
            ]);
            if (fullDream && fullDream.interpretation) {
                renderInterpretation(fullDream.interpretation);
            }
            renderAnalyticsReport(fullDream, sleepResp?.records || []);
        } catch (error) {
            console.error('Failed to fetch dream interpretation:', error);
            if (analyticsReportEl) {
                analyticsReportEl.innerHTML = '<p class="hint">Unable to load detailed analytics for this dream.</p>';
            }
        }
    };
    fetchFullDetails();

    function renderAnalyticsReport(fullDream, sleepRecords) {
        if (!analyticsReportEl || !fullDream) {
            return;
        }

        const emotionScores = fullDream.emotion_scores || {};
        const topEmotions = Object.entries(emotionScores)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 5);

        const dreamDate = (fullDream.created_at || '').split('T')[0].split(' ')[0];
        const matchedSleep = sleepRecords.find(r => (r.date || '').split('T')[0] === dreamDate);

        const qualityOutOf100 = matchedSleep?.quality_rating
            ? Math.round((matchedSleep.quality_rating / 10) * 100)
            : null;

        const highRiskEmotions = new Set(['fear', 'anxiety', 'nervousness', 'anger', 'sadness', 'grief']);
        let riskScore = 0;
        const riskFactors = [];

        for (const [emotion, score] of Object.entries(emotionScores)) {
            const v = Number(score) || 0;
            if (highRiskEmotions.has(String(emotion).toLowerCase()) && v > 0.5) {
                riskScore += v;
                riskFactors.push(`${capitalize(emotion)} (${(v * 100).toFixed(0)}%)`);
            }
        }

        const disturbanceProbability = Math.min(riskScore / 3.0, 1);
        const disturbanceLevel = disturbanceProbability < 0.3 ? 'Low' : disturbanceProbability < 0.6 ? 'Moderate' : 'High';

        const keywords = (fullDream.keywords || []).slice(0, 8);
        const topTheme = keywords.find(k => /house|home|school|water|road|family|work|office/i.test(k || ''))
            || (keywords[0] || 'Not enough data');

        const topEmotion = topEmotions[0]?.[0] || (fullDream.primary_emotion || 'neutral');
        const tipMap = {
            confusion: 'Take time for self-care today. Be gentle with yourself.',
            fear: 'Try a calm bedtime routine and grounding breaths before sleep.',
            sadness: 'Rest and emotional journaling can help release lingering stress.',
            anger: 'Release tension with light movement and a short cooldown routine.',
            joy: 'Keep these habits; they support stable positive emotional processing.',
            neutral: 'Continue journaling to detect deeper recurring patterns.'
        };

        analyticsReportEl.innerHTML = `
            <div class="analytics-grid-compact">
                <div class="analytics-block">
                    <h5>Top Emotions Detected</h5>
                    <div class="analytics-list">
                        ${topEmotions.length ? topEmotions.map(([emotion, score]) => `
                            <div class="analytics-line">
                                <span>${getEmotionEmoji(emotion)} ${capitalize(emotion)}</span>
                                <strong>${Math.round((Number(score) || 0) * 100)}%</strong>
                            </div>
                        `).join('') : '<div class="analytics-line"><span>No emotion scores available</span></div>'}
                    </div>
                </div>

                <div class="analytics-block">
                    <h5>Sentiment</h5>
                    <p>${capitalize(fullDream.sentiment || 'neutral')}</p>
                    <p>Polarity: ${typeof fullDream.sentiment_score === 'number' ? fullDream.sentiment_score.toFixed(2) : '-'}</p>
                </div>

                <div class="analytics-block">
                    <h5>Sleep Quality</h5>
                    <p>${qualityOutOf100 !== null ? `${qualityOutOf100}/100` : 'N/A'}</p>
                    <p>${qualityOutOf100 !== null ? `Grade: ${qualityOutOf100 >= 90 ? 'A' : qualityOutOf100 >= 80 ? 'B' : qualityOutOf100 >= 70 ? 'C' : qualityOutOf100 >= 60 ? 'D' : 'F'}` : 'No matching sleep log'}</p>
                </div>

                <div class="analytics-block">
                    <h5>Disturbance Risk</h5>
                    <p>${disturbanceLevel}</p>
                    <p>Probability: ${Math.round(disturbanceProbability * 100)}%</p>
                </div>

                <div class="analytics-block analytics-span-2">
                    <h5>Keywords</h5>
                    <div class="modal-keywords">
                        ${keywords.length ? keywords.map(k => `<span class="keyword-tag">${escapeHtml(k)}</span>`).join('') : '<span class="hint">No keywords available</span>'}
                    </div>
                </div>

                <div class="analytics-block">
                    <h5>Theme</h5>
                    <p>${escapeHtml(topTheme)}</p>
                </div>

                <div class="analytics-block analytics-span-2">
                    <h5>Processing ${capitalize(topEmotion)}</h5>
                    <p>Your dream shows ${escapeHtml(topEmotion)}. Dreams help process emotions.</p>
                    <p><strong>Tip:</strong> ${tipMap[String(topEmotion).toLowerCase()] || 'Take time for self-care today. Be gentle with yourself.'}</p>
                    ${riskFactors.length ? `<p class="hint">Risk factors: ${escapeHtml(riskFactors.join(', '))}</p>` : ''}
                </div>
            </div>
        `;
    }

    function renderInterpretation(ip) {
        const elementsEl = document.getElementById('modal-elements');
        const overallEl = document.getElementById('modal-overall-interpretation');
        const finalEl = document.getElementById('modal-final-insight');
        const interpSection = document.getElementById('modal-interpretation-section');

        if (!ip || (!ip.numbered_elements?.length && !ip.overall_interpretation)) {
            if (interpSection) interpSection.style.display = 'none';
            return;
        }

        if (interpSection) interpSection.style.display = 'block';

        // Render Numbered Elements
        if (ip.numbered_elements && ip.numbered_elements.length > 0) {
            elementsEl.innerHTML = ip.numbered_elements.map(el => `
                <div class="interpretation-element">
                    <div class="element-header">
                        <span class="element-number">${escapeHtml(el.number)}</span>
                        <span class="element-text">${escapeHtml(el.element)}</span>
                    </div>
                    <div class="element-body">
                        <div class="element-insight">
                            <strong>Symbolic Meaning:</strong>
                            <p>${escapeHtml(el.symbolic_meaning)}</p>
                        </div>
                        <div class="element-insight">
                            <strong>Subconscious Insight:</strong>
                            <p>${escapeHtml(el.subconscious_insight)}</p>
                        </div>
                    </div>
                </div>
            `).join('');
        } else {
            elementsEl.innerHTML = '';
        }

        // Render Overall
        if (ip.overall_interpretation) {
            overallEl.innerHTML = `
                <div class="overall-interpretation">
                    <h5>Overall Interpretation</h5>
                    <p>${escapeHtml(ip.overall_interpretation)}</p>
                </div>
            `;
        } else {
            overallEl.innerHTML = '';
        }

        // Render Final
        if (ip.final_insight) {
            finalEl.innerHTML = `
                <div class="final-insight">
                    <p><em>${escapeHtml(ip.final_insight)}</em></p>
                </div>
            `;
        } else {
            finalEl.innerHTML = '';
        }
    }

    // Close handlers
    const closeModal = () => modal.classList.add('hidden');

    document.getElementById('close-modal').onclick = closeModal;
    modal.querySelector('.modal-overlay').onclick = closeModal;

    // Close on escape key
    const escHandler = (e) => {
        if (e.key === 'Escape') {
            closeModal();
            document.removeEventListener('keydown', escHandler);
        }
    };
    document.addEventListener('keydown', escHandler);
}

// ==========================================
// SLEEP HANDLING
// ==========================================

/**
 * Handle sleep form submission
 */
async function handleSleepSubmit(e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);

    const data = {
        date: formData.get('date'),
        sleep_time: formData.get('sleep_time'),
        wake_time: formData.get('wake_time'),
        wakeups: 0,
        quality_rating: parseInt(formData.get('quality_rating')),
        notes: formData.get('notes') || ''
    };

    if (!data.date || !data.sleep_time || !data.wake_time) {
        showToast('warning', 'Please fill in required fields correctly.');
        return;
    }

    // Calculate duration
    const sleep = new Date(`2000-01-01T${data.sleep_time}`);
    let wake = new Date(`2000-01-01T${data.wake_time}`);

    if (wake <= sleep) {
        // Crosses midnight
        wake = new Date(`2000-01-02T${data.wake_time}`);
    }

    data.duration_hours = (wake - sleep) / (1000 * 60 * 60);

    if (data.quality_rating < 1 || data.quality_rating > 10) {
        showToast('warning', 'Sleep quality must be between 1 and 10.');
        return;
    }

    try {
        await createSleepRecord(data);
        showToast('success', 'Sleep record saved!');

        // Reset form
        form.reset();
        initDateDefaults();
        document.getElementById('quality-value').textContent = '5';

        // Reload records
        loadSleepRecords();

    } catch (error) {
        showToast('error', `Failed to save: ${error.message}`);
    }
}

/**
 * Load and display sleep records
 */
async function loadSleepRecords() {
    const container = document.getElementById('sleep-list');
    const avgQuality = document.getElementById('avg-quality');
    const avgDuration = document.getElementById('avg-duration');

    if (!container) return;

    try {
        const [response, dreamsResp] = await Promise.all([
            getRecentSleep(30),
            getDreams(200, 0)
        ]);

        const records = response.records || [];
        const dreams = dreamsResp?.dreams || [];

        // Group dreams by date and sort by recency for one-to-one pairing with sleep records.
        const dreamsByDate = dreams.reduce((acc, dream) => {
            const dateKey = toDateKey(dream.created_at || dream.date);
            if (!dateKey) return acc;
            if (!acc[dateKey]) acc[dateKey] = [];
            acc[dateKey].push(dream);
            return acc;
        }, {});

        Object.keys(dreamsByDate).forEach((dateKey) => {
            dreamsByDate[dateKey].sort((a, b) => {
                const aTs = new Date(a.created_at || a.date || 0).getTime();
                const bTs = new Date(b.created_at || b.date || 0).getTime();
                return bTs - aTs;
            });
        });

        // Update stats
        if (avgQuality) {
            avgQuality.textContent = response.averages?.quality
                ? `${response.averages.quality}/10`
                : '-';
        }
        if (avgDuration) {
            avgDuration.textContent = response.averages?.duration
                ? `${response.averages.duration}h`
                : '-';
        }

        if (records.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <span class="empty-icon">🛏️</span>
                    <p>No sleep records yet</p>
                </div>
            `;
            return;
        }

        const recordDateIndices = {};
        container.innerHTML = records.map(record => {
            const dateKey = toDateKey(record.date);
            const idx = recordDateIndices[dateKey] || 0;
            const relatedDream = (dreamsByDate[dateKey] || [])[idx] || null;
            const relatedDreams = relatedDream ? [relatedDream] : [];
            recordDateIndices[dateKey] = idx + 1;
            return renderSleepItem(record, relatedDreams);
        }).join('');

        // Add delete handlers for individual sleep records
        container.querySelectorAll('.btn-delete-sleep').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const id = btn.dataset.id;
                if (confirm('Are you sure you want to delete this sleep record?')) {
                    try {
                        await deleteSleepRecord(id);
                        showToast('success', 'Sleep record deleted');
                        loadSleepRecords();
                    } catch (error) {
                        showToast('error', 'Failed to delete sleep record');
                    }
                }
            });
        });

        // Add handler for "Delete All" button if it's the first time
        const deleteAllBtn = document.getElementById('delete-all-sleep');
        if (deleteAllBtn && !deleteAllBtn.dataset.listener) {
            deleteAllBtn.dataset.listener = 'true';
            deleteAllBtn.addEventListener('click', async () => {
                if (confirm('⚠️ WARNING: This will permanently delete ALL your sleep records. This action cannot be undone. Proceed?')) {
                    try {
                        const response = await deleteAllSleepRecords();
                        showToast('success', `Deleted ${response.count} sleep records`);
                        loadSleepRecords();
                    } catch (error) {
                        showToast('error', 'Failed to delete sleep history');
                    }
                }
            });
        }

    } catch (error) {
        container.innerHTML = `
            <div class="empty-state">
                <span class="empty-icon">⚠️</span>
                <p>Failed to load sleep records</p>
            </div>
        `;
    }
}

/**
 * Render a single sleep record
 */
function renderSleepItem(record, relatedDreams = []) {
    const date = formatDate(record.date);
    const qualityPercent = ((record.quality_rating || 5) / 10) * 100;

    // Format times for display if available
    const formatTimeForDisplay = (timeStr) => {
        if (!timeStr) return '';
        const [hours, minutes] = timeStr.split(':');
        const h = parseInt(hours);
        const ampm = h >= 12 ? 'PM' : 'AM';
        const h12 = h % 12 || 12;
        return `${h12}:${minutes} ${ampm}`;
    };

    const sleepTime = record.sleep_time ? formatTimeForDisplay(record.sleep_time) : '';
    const wakeTime = record.wake_time ? formatTimeForDisplay(record.wake_time) : '';
    const timeDisplay = sleepTime && wakeTime ? `<div class="sleep-item-times">${sleepTime} - ${wakeTime}</div>` : '';

    const dreamLogHtml = relatedDreams.length
        ? `
            <details class="sleep-item-dream-log sleep-item-dream-accordion">
                <summary class="sleep-item-dream-title">📝 Dream Log (${relatedDreams.length})</summary>
                <div class="sleep-item-dream-list">
                    ${relatedDreams.map((dream) => {
            const emotion = dream.primary_emotion || 'neutral';
            const fullText = escapeHtml(dream.content || '');
            return `
                            <div class="sleep-item-dream-entry">
                                <span class="dream-entry-emotion">${getEmotionEmoji(emotion)} ${capitalize(emotion)}</span>
                                <span class="dream-entry-text">${fullText}</span>
                            </div>
                        `;
        }).join('')}
                </div>
            </details>
        `
        : `
            <div class="sleep-item-dream-log muted">
                <div class="sleep-item-dream-title">📝 Dream Log</div>
                <div class="sleep-item-dream-empty">No dream entry on this date.</div>
            </div>
        `;

    return `
        <div class="sleep-item">
            <div class="sleep-item-info">
                <span class="sleep-item-date">${date}</span>
                ${timeDisplay}
                <div class="sleep-item-stats">
                    <span>💤 ${record.duration_hours.toFixed(1)}h</span>
                    <span>🔔 ${record.wakeups || 0} wakeups</span>
                    <div class="sleep-quality-bar">
                        <div class="sleep-quality-fill" style="width: ${qualityPercent}%"></div>
                    </div>
                </div>
                ${dreamLogHtml}
            </div>
            <div class="sleep-item-actions">
                <button class="btn-delete-sleep" data-id="${record.id}" title="Delete record">🗑️</button>
            </div>
        </div>
    `;
}

// ==========================================
// ANALYTICS
// ==========================================

/**
 * Load analytics data and render charts
 */
async function loadAnalytics() {
    const periodSelect = document.getElementById('emotion-period');
    const days = periodSelect ? parseInt(periodSelect.value) : 30;

    const analyticsTotalDreams = document.getElementById('analytics-total-dreams');
    const analyticsAvgSleep = document.getElementById('analytics-avg-sleep');
    const analyticsDominantSentiment = document.getElementById('analytics-dominant-sentiment');
    const analyticsTopEmotion = document.getElementById('analytics-top-emotion');
    const analyticsSentimentNote = document.getElementById('analytics-sentiment-note');
    const analyticsSleepNote = document.getElementById('analytics-sleep-note');

    console.log(`📊 Loading analytics for ${days} days...`);
    try {
        const [trendsResult, insightsResult, recentDreamsResult, recentSleepResult] = await Promise.allSettled([
            getTrends(days),
            getInsights(days),
            getRecentDreams(days),
            getRecentSleep(days)
        ]);

        const trends = trendsResult.status === 'fulfilled' ? trendsResult.value : null;
        const insights = insightsResult.status === 'fulfilled' ? insightsResult.value : null;
        const recentDreamsResp = recentDreamsResult.status === 'fulfilled' ? recentDreamsResult.value : null;
        const recentSleepResp = recentSleepResult.status === 'fulfilled' ? recentSleepResult.value : null;

        if (trendsResult.status === 'rejected') {
            console.warn('⚠️ Trends endpoint failed:', trendsResult.reason);
        }
        if (insightsResult.status === 'rejected') {
            console.warn('⚠️ Insights endpoint failed:', insightsResult.reason);
        }
        if (recentDreamsResult.status === 'rejected') {
            console.warn('⚠️ Recent dreams endpoint failed:', recentDreamsResult.reason);
        }
        if (recentSleepResult.status === 'rejected') {
            console.warn('⚠️ Recent sleep endpoint failed:', recentSleepResult.reason);
        }

        console.log('✅ Analytics payload readiness:', {
            trends: !!trends,
            insights: !!insights,
            recentDreams: !!recentDreamsResp,
            recentSleep: !!recentSleepResp
        });

        const dreams = recentDreamsResp?.dreams || [];
        const sleepRecords = recentSleepResp?.records || [];
        const sleepByDate = sleepRecords.reduce((acc, record) => {
            const dateKey = toDateKey(record.date);
            if (!dateKey) return acc;
            if (!acc[dateKey]) acc[dateKey] = [];
            acc[dateKey].push(record);
            return acc;
        }, {});

        renderAnalyticsDashboard(
            dreams,
            sleepRecords,
            insights?.stats || {},
            analyticsSentimentNote,
            analyticsSleepNote,
            analyticsTotalDreams,
            analyticsAvgSleep,
            analyticsDominantSentiment,
            analyticsTopEmotion
        );

        // Render emotion trends chart
        if (trends?.emotions) {
            renderEmotionChart(trends.emotions);
        }

        // Render sleep chart
        if (trends?.sleep) {
            renderSleepChart(trends.sleep);
        }

        // Render emotion pie chart
        if (insights?.stats && insights.stats.emotion_breakdown) {
            const breakdown = insights.stats.emotion_breakdown;
            if (Object.keys(breakdown).length > 0) {
                renderEmotionPieChart(breakdown);
            }
        }

        // Render themes chart
        if (insights?.stats && insights.stats.top_keywords) {
            renderThemesChart(insights.stats.top_keywords);
        }

        // Render advanced analytics visuals
        renderDreamWeekdayChart(dreams);
        renderSleepSentimentChart(dreams, sleepByDate);

    } catch (error) {
        console.error('Failed to load analytics:', error);
    }
}

function renderAnalyticsDashboard(
    dreams,
    sleepRecords,
    stats,
    sentimentNoteEl,
    sleepNoteEl,
    totalDreamsEl,
    avgSleepEl,
    dominantSentimentEl,
    topEmotionEl
) {
    if (totalDreamsEl) totalDreamsEl.textContent = stats.total_dreams || dreams.length || 0;

    if (avgSleepEl) {
        avgSleepEl.textContent = stats.avg_sleep_quality !== null && stats.avg_sleep_quality !== undefined
            ? `${Number(stats.avg_sleep_quality).toFixed(0)}/100`
            : 'N/A';
    }

    if (dominantSentimentEl) {
        const sentiments = stats.sentiment_breakdown || {};
        const topSentiment = Object.entries(sentiments).sort((a, b) => b[1] - a[1])[0];
        dominantSentimentEl.textContent = topSentiment ? capitalize(topSentiment[0]) : '-';
    }

    if (topEmotionEl) {
        const emotions = stats.emotion_breakdown || {};
        const topEmotion = Object.entries(emotions).sort((a, b) => b[1] - a[1])[0];
        topEmotionEl.textContent = topEmotion ? `${getEmotionEmoji(topEmotion[0])} ${capitalize(topEmotion[0])}` : '-';
    }

    const sentimentBreakdown = stats.sentiment_breakdown || {};
    const sentimentEntries = Object.entries(sentimentBreakdown).filter(([, count]) => Number(count) > 0);
    if (sentimentNoteEl) {
        if (!sentimentEntries.length) {
            sentimentNoteEl.textContent = 'Not enough sentiment data yet';
        } else {
            const topSentiment = sentimentEntries.sort((a, b) => b[1] - a[1])[0];
            sentimentNoteEl.textContent = `Top sentiment: ${capitalize(topSentiment[0])} (${topSentiment[1]} dreams)`;
        }
    }

    const records = Array.isArray(sleepRecords) ? sleepRecords : [];
    if (sleepNoteEl) {
        if (!records.length) {
            sleepNoteEl.textContent = 'No sleep records available yet';
        } else {
            const avgDuration = records
                .map((r) => Number(r.duration_hours))
                .filter((v) => Number.isFinite(v));
            const durationVal = avgDuration.length ? (avgDuration.reduce((a, b) => a + b, 0) / avgDuration.length) : null;
            sleepNoteEl.textContent = durationVal !== null
                ? `Average sleep duration: ${durationVal.toFixed(1)}h`
                : 'Sleep records found, duration not available';
        }
    }

    renderSentimentMiniChart(sentimentBreakdown);
    renderSleepMiniChart(records);
}

// ==========================================
// INSIGHTS
// ==========================================

/**
 * Load and display insights
 */
async function loadInsights() {
    const insightsList = document.getElementById('insights-list');
    const recommendationsList = document.getElementById('recommendations-list');
    const healthTipsList = document.getElementById('health-tips-list');
    const totalDreams = document.getElementById('total-dreams');
    const totalSleep = document.getElementById('total-sleep');
    const topEmotion = document.getElementById('top-emotion');

    if (!insightsList) return;

    // Show loading state
    insightsList.innerHTML = `
        <div class="loading-state">
            <span class="loading-icon">⏳</span>
            <p>Analyzing your patterns...</p>
        </div>
    `;

    console.log('💡 Loading insights for 7 days...');
    try {
        const data = await getInsights(7);
        console.log('✅ Received insights data:', data);

        // Render insights
        if (data.insights && data.insights.length > 0) {
            insightsList.innerHTML = data.insights.map(insight => renderInsight(insight)).join('');
        } else {
            insightsList.innerHTML = `
                <div class="empty-state small">
                    <p>No insights yet. Record more dreams!</p>
                </div>
            `;
        }

        // Render health tips (NEW!)
        if (healthTipsList) {
            if (data.health_tips && data.health_tips.length > 0) {
                healthTipsList.innerHTML = data.health_tips.map(tip => renderHealthTip(tip)).join('');
            } else {
                healthTipsList.innerHTML = `
                    <div class="empty-state small">
                        <p>Keep journaling to receive personalized health tips!</p>
                    </div>
                `;
            }
        }

        // Render recommendations
        if (recommendationsList) {
            if (data.recommendations && data.recommendations.length > 0) {
                recommendationsList.innerHTML = data.recommendations.map(rec => renderRecommendation(rec)).join('');
            } else {
                recommendationsList.innerHTML = `
                    <div class="empty-state small">
                        <p>Keep journaling for personalized tips!</p>
                    </div>
                `;
            }
        }

        // Update quick stats
        if (data.stats) {
            if (totalDreams) totalDreams.textContent = data.stats.total_dreams || 0;
            if (totalSleep) totalSleep.textContent = data.stats.total_sleep_records || 0;
            if (topEmotion) {
                const emotions = data.stats.emotion_breakdown || {};
                const top = Object.entries(emotions).sort((a, b) => b[1] - a[1])[0];
                topEmotion.textContent = top ? capitalize(top[0]) : '-';
            }
        }

    } catch (error) {
        insightsList.innerHTML = `
            <div class="empty-state small">
                <span class="empty-icon">⚠️</span>
                <p>Failed to load insights</p>
            </div>
        `;
    }
}

/**
 * Render a health tip section
 */
function renderHealthTip(tip) {
    const categoryIcons = {
        emotional: '💭',
        sleep: '🛏️'
    };
    const icon = categoryIcons[tip.category] || '💡';

    return `
        <div class="health-tip-card">
            <div class="health-tip-header">
                <span class="health-tip-icon">${icon}</span>
                <h4>${escapeHtml(tip.title)}</h4>
            </div>
            ${tip.insight ? `<p class="health-tip-insight">${escapeHtml(tip.insight)}</p>` : ''}
            <ul class="health-tip-list">
                ${tip.tips.map(t => `<li>${escapeHtml(t)}</li>`).join('')}
            </ul>
        </div>
    `;
}

/**
 * Render a recommendation item
 */
function renderRecommendation(rec) {
    const priorityClass = rec.priority === 'high' ? 'priority-high' :
        rec.priority === 'medium' ? 'priority-medium' : '';
    return `
        <div class="recommendation-item ${priorityClass}">
            <h4>${escapeHtml(rec.title)}</h4>
            <p>${escapeHtml(rec.message)}</p>
        </div>
    `;
}

/**
 * Render a single insight
 */
function renderInsight(insight) {
    const iconMap = {
        emotion: '🎭',
        warning: '⚠️',
        positive: '🌟',
        sleep: '😴',
        themes: '🔮',
        info: '💡'
    };

    const icon = iconMap[insight.type] || '💡';

    return `
        <div class="insight-item type-${insight.type}">
            <span class="insight-icon">${icon}</span>
            <div class="insight-content">
                <h4>${escapeHtml(insight.title)}</h4>
                <p>${escapeHtml(insight.message)}</p>
            </div>
        </div>
    `;
}

// ==========================================
// TOAST NOTIFICATIONS
// ==========================================

/**
 * Show a toast notification
 */
function showToast(type, message, duration = 4000) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const iconMap = {
        success: '✨',
        error: '🚨',
        warning: '⚠️',
        info: 'ℹ️'
    };

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <span class="toast-icon">${iconMap[type] || '✨'}</span>
            <span class="toast-message">${escapeHtml(message)}</span>
            <button class="toast-close">&times;</button>
        </div>
        <div class="toast-progress">
            <div class="toast-progress-bar" style="animation-duration: ${duration}ms"></div>
        </div>
    `;

    container.appendChild(toast);

    const removeToast = () => {
        toast.style.animation = 'fadeOut 0.3s ease forwards';
        setTimeout(() => {
            if (toast.parentElement) toast.remove();
        }, 300);
    };

    // Close on click
    toast.querySelector('.toast-close').addEventListener('click', removeToast);

    // Auto-remove
    setTimeout(removeToast, duration);
}

// ==========================================
// HELPER FUNCTIONS
// ==========================================

// ==========================================
// VOICE TO TEXT
// ==========================================

const voiceBtn = document.getElementById('voice-btn');
let recognition = null;

if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    // Set language to support Hinglish/Hindi/Marathi/English
    recognition.lang = 'hi-IN';

    let finalTranscript = '';

    recognition.onstart = () => {
        voiceBtn.classList.add('recording');
        voiceBtn.innerHTML = '<span class="voice-icon" title="Stop Mic">🛑</span>';
        voiceBtn.title = 'Stop Mic';
        showToast('info', 'Microphone active. Listening continuously...');
    };

    recognition.onend = () => {
        // Auto-restart if the button state still implies we should be recording
        // (This prevents the browser from stopping due to silence)
        if (voiceBtn.classList.contains('recording')) {
            try {
                recognition.start();
            } catch (err) {
                console.log('Recognition restart failed:', err);
            }
            return;
        }
        voiceBtn.classList.remove('recording');
        voiceBtn.innerHTML = '<span class="voice-icon" title="Start Mic">🎤</span>';
        voiceBtn.title = 'Start Mic';
    };

    recognition.onresult = (event) => {
        let interimTranscript = '';
        const dreamContent = document.getElementById('dream-content');
        if (!dreamContent) return;

        // Get current cursor position or just append at the end
        // For simplicity in a dream journal, we'll maintain a specific session transcript
        for (let i = event.resultIndex; i < event.results.length; ++i) {
            const transcript = event.results[i][0].transcript;
            if (event.results[i].isFinal) {
                // If it's final, add it to our persistent box
                const currentVal = dreamContent.value.trim();
                dreamContent.value = currentVal ? `${currentVal} ${transcript}` : transcript;
                dreamContent.dispatchEvent(new Event('input'));
            } else {
                interimTranscript += transcript;
            }
        }

        // You could show interimTranscript in a small overlay or status bar if desired
        if (interimTranscript) {
            console.log('Interim speech:', interimTranscript);
        }
    };

    recognition.onerror = (event) => {
        if (event.error === 'no-speech') return; // Ignore silence errors
        console.error('Speech recognition error:', event.error);
        showToast('error', `Speech recognition error: ${event.error}`);
    };
}

if (voiceBtn) {
    voiceBtn.title = 'Start Mic'; // Initial title
    voiceBtn.addEventListener('click', () => {
        if (!recognition) {
            showToast('warning', 'Speech recognition is not supported in your browser.');
            return;
        }

        if (voiceBtn.classList.contains('recording')) {
            voiceBtn.classList.remove('recording'); // Remove class first so onend doesn't restart
            recognition.stop();
        } else {
            recognition.start();
        }
    });
}

// ==========================================
// PDF EXPORT
// ==========================================

async function handlePdfExport(dreamId) {
    const btn = document.getElementById('btn-export-pdf');
    const originalHtml = btn.innerHTML;

    try {
        btn.disabled = true;
        btn.innerHTML = '<span class="btn-icon">⏳</span><span>Generating...</span>';

        // Open the export URL in a new tab or trigger download
        const exportUrl = `${API_BASE}/api/dreams/${dreamId}/export`;

        // Use a hidden anchor to trigger download
        const a = document.createElement('a');
        a.href = exportUrl;
        a.download = `dream_export_${dreamId}.pdf`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

        showToast('success', 'PDF generation started!');
    } catch (error) {
        console.error('Failed to export PDF:', error);
        showToast('error', 'Failed to generate PDF. Is the backend running?');
    } finally {
        setTimeout(() => {
            btn.disabled = false;
            btn.innerHTML = originalHtml;
        }, 2000);
    }
}

// ==========================================
// IMAGE GENERATION (PLACEHOLDER)
// ==========================================

function handleImageGenerationPlaceholder(dream) {
    const modalBody = document.querySelector('.modal-body');
    const existingPlaceholder = document.querySelector('.image-placeholder-container');

    if (existingPlaceholder) {
        existingPlaceholder.remove();
        return;
    }

    const placeholder = document.createElement('div');
    placeholder.className = 'image-placeholder-container';
    placeholder.innerHTML = `
        <span class="image-placeholder-icon">🖼️</span>
        <div class="image-placeholder-text">AI Image Generation coming soon!</div>
        <div class="image-placeholder-hint">Visualizing your dream: "${dream.content.substring(0, 50)}..."</div>
        <div class="image-placeholder-hint" style="margin-top: 10px;">
            > [!TIP]<br>
            Visual dream scene generation is a planned feature coming in a future update.
        </div>
    `;

    modalBody.appendChild(placeholder);
    placeholder.scrollIntoView({ behavior: 'smooth' });
}

// Update openDreamModal to handle buttons
const originalOpenDreamModal = openDreamModal;
openDreamModal = function (dream) {
    if (!dream) return;
    originalOpenDreamModal(dream);

    const exportBtn = document.getElementById('btn-export-pdf');
    const generateBtn = document.getElementById('btn-generate-image');

    if (exportBtn) {
        exportBtn.onclick = () => handlePdfExport(dream.id);
    }

    if (generateBtn) {
        generateBtn.onclick = () => handleImageGenerationPlaceholder(dream);
    }
};

/**
 * Format date for display
 */
function formatDate(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
        weekday: 'short',
        month: 'short',
        day: 'numeric'
    });
}

/**
 * Format datetime for display
 */
function formatDateTime(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: 'numeric',
        minute: '2-digit'
    });
}

/**
 * Truncate long text for compact list rendering
 */
function truncateText(text, maxLength = 160) {
    if (text === null || text === undefined) return '';
    const normalized = String(text).trim();
    if (normalized.length <= maxLength) return normalized;
    return `${normalized.slice(0, maxLength).trimEnd()}...`;
}


/**
 * Capitalize first letter of a string
 */
function capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

/**
 * Get emoji for an emotion
 */
function getEmotionEmoji(emotion) {
    const emojiMap = {
        joy: '😊',
        sadness: '😢',
        anger: '😠',
        fear: '😨',
        surprise: '😲',
        love: '❤️',
        neutral: '😐',
        disgust: '🤢',
        anticipation: '🤔',
        trust: '🤝'
    };
    return emojiMap[emotion?.toLowerCase()] || '🌙';
}

/**
 * Handle switching to the Jungian Psychology tab
 */
function handleJungianTab() {
    const emptyState = document.getElementById('jungian-empty-state');
    const resultDiv = document.getElementById('jungian-result');
    const contentDiv = document.getElementById('jungian-content');
    const analyzeBtn = document.getElementById('analyze-jungian-btn');

    if (!emptyState || !resultDiv || !contentDiv) {
        return;
    }

    const loadStoredReports = async () => {
        try {
            if (analyzeBtn) analyzeBtn.disabled = true;
            contentDiv.innerHTML = '<p class="hint">Loading stored Jungian reports...</p>';

            const response = await getDreams(200, 0);
            const dreams = response?.dreams || [];
            const withReports = dreams.filter(d => d.jungian_report && d.jungian_report.analysis);

            if (!withReports.length) {
                emptyState.classList.remove('hidden');
                resultDiv.classList.add('hidden');
                return;
            }

            emptyState.classList.add('hidden');
            resultDiv.classList.remove('hidden');

            contentDiv.innerHTML = withReports.map(dream => {
                const report = dream.jungian_report || {};
                const dateLabel = formatDateTime(dream.created_at || dream.date || '');
                const provider = report.provider || 'Google Gemini';
                const generatedLabel = report.generated_at ? formatDateTime(report.generated_at) : '';
                const reportText = report.analysis || 'No Jungian analysis available.';
                const previewText = reportText.length > 180 ? `${reportText.slice(0, 180)}...` : reportText;

                return `
                    <div class="jungian-journal-item" data-dream-id="${dream.id}" tabindex="0" role="button" aria-expanded="false">
                        <div class="jungian-report-meta">
                            <span>Dream: ${escapeHtml(dateLabel || 'Unknown date')}</span>
                            <span>Provider: ${escapeHtml(provider)}</span>
                            ${generatedLabel ? `<span>Generated: ${escapeHtml(generatedLabel)}</span>` : ''}
                            <button type="button" class="btn-delete jungian-delete-btn" aria-label="Delete Jungian analysis for this dream" title="Delete Jungian analysis">🗑️</button>
                        </div>
                        <div class="jungian-dream-preview">${escapeHtml((dream.content || '').slice(0, 180))}${(dream.content || '').length > 180 ? '...' : ''}</div>
                        <div class="jungian-report-preview">${escapeHtml(previewText)}</div>
                        <div class="jungian-report-body hidden">${escapeHtml(reportText)}</div>
                    </div>
                `;
            }).join('');

            const items = Array.from(contentDiv.querySelectorAll('.jungian-journal-item'));
            items.forEach((item) => {
                const dreamId = item.dataset.dreamId;
                const deleteBtn = item.querySelector('.jungian-delete-btn');

                if (deleteBtn) {
                    deleteBtn.addEventListener('click', async (event) => {
                        event.preventDefault();
                        event.stopPropagation();

                        const confirmed = window.confirm('Delete this Jungian analysis? The dream entry will stay.');
                        if (!confirmed) return;

                        try {
                            deleteBtn.disabled = true;
                            await deleteJungianReport(dreamId);
                            showToast('success', 'Jungian analysis deleted successfully.');
                            await loadStoredReports();
                        } catch (error) {
                            console.error('Failed to delete Jungian analysis:', error);
                            showToast('error', `Failed to delete Jungian analysis: ${error.message}`);
                            deleteBtn.disabled = false;
                        }
                    });
                }

                const toggleItem = () => {
                    const isActive = item.classList.contains('expanded');

                    items.forEach((otherItem) => {
                        const otherBody = otherItem.querySelector('.jungian-report-body');
                        const otherPreview = otherItem.querySelector('.jungian-report-preview');
                        otherItem.classList.remove('expanded');
                        otherItem.setAttribute('aria-expanded', 'false');
                        if (otherBody) otherBody.classList.add('hidden');
                        if (otherPreview) otherPreview.classList.remove('hidden');
                    });

                    if (!isActive) {
                        const body = item.querySelector('.jungian-report-body');
                        const preview = item.querySelector('.jungian-report-preview');
                        item.classList.add('expanded');
                        item.setAttribute('aria-expanded', 'true');
                        if (preview) preview.classList.add('hidden');
                        if (body) body.classList.remove('hidden');
                    }
                };

                item.addEventListener('click', toggleItem);
                item.addEventListener('keydown', (event) => {
                    if (event.key === 'Enter' || event.key === ' ') {
                        event.preventDefault();
                        toggleItem();
                    }
                });
            });
        } catch (error) {
            console.error('Failed to load stored Jungian reports:', error);
            showToast('error', `Failed to load Jungian reports: ${error.message}`);
            emptyState.classList.remove('hidden');
            resultDiv.classList.add('hidden');
        } finally {
            if (analyzeBtn) analyzeBtn.disabled = false;
        }
    };

    loadStoredReports();
}

/**
 * Parse and render the structured Jungian output
 */
function renderJungianOutput(text, container) {
    if (!text) {
        container.innerHTML = '<p>No analysis received.</p>';
        return;
    }

    // Split text into sections based on the numbered sections
    const sections = text.split(/\d\.\s+/);
    const sectionNames = ["Symbols Meaning", "Archetypes Identified", "Emotional Insight", "Personal Growth Message"];

    let html = '';

    // Check if we have the expected number of sections (plus content before first section)
    if (sections.length >= 5) {
        for (let i = 0; i < 4; i++) {
            const sectionContent = sections[i + 1] || "";
            const sectionName = sectionNames[i];

            html += `
                <div class="jungian-section" style="margin-bottom: 20px;">
                    <h4 style="color: var(--color-foam); margin-bottom: 8px; border-bottom: 1px solid var(--color-bg-tertiary); padding-bottom: 4px;">${sectionName}</h4>
                    <p style="color: var(--color-text-secondary); line-height: 1.6;">${escapeHtml(sectionContent.trim())}</p>
                </div>
            `;
        }
    } else {
        // Fallback for different formats
        html = `<div class="jungian-raw-text" style="white-space: pre-wrap; color: var(--color-text-secondary);">${escapeHtml(text)}</div>`;
    }

    container.innerHTML = html;
}
