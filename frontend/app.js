const API_BASE = '/api';

// --- Router ---
const routes = {
    '#/dashboard': { title: 'Dashboard', template: 'tpl-dashboard', init: initDashboard },
    '#/graph': { title: 'Neural Graph', template: 'tpl-graph', init: initGraph },
    '#/skills': { title: 'Skill Browser', template: 'tpl-skills', init: initSkills },
    '#/skill/': { title: 'Skill Detail', template: 'tpl-skill-detail', init: initSkillDetail },
    '#/pipeline': { title: 'Pipeline Control', template: 'tpl-pipeline', init: initPipeline },
    '#/audit': { title: 'Audit Queue', template: 'tpl-audit', init: initAudit },
};

function handleRoute() {
    let hash = window.location.hash || '#/dashboard';
    if (hash === '#/') hash = '#/dashboard';
    
    let routeKey = hash;
    let param = null;
    
    // Handle dynamic routes like #/skill/123
    if (hash.startsWith('#/skill/')) {
        routeKey = '#/skill/';
        param = hash.split('#/skill/')[1];
    }
    
    const route = routes[routeKey] || routes['#/dashboard'];
    
    // Update active nav
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === (routeKey === '#/skill/' ? '#/skills' : hash)) {
            link.classList.add('active');
        }
    });

    // Update Title
    document.getElementById('page-title').textContent = route.title;

    // Load Template
    const template = document.getElementById(route.template);
    const appDiv = document.getElementById('app');
    appDiv.innerHTML = '';
    appDiv.appendChild(template.content.cloneNode(true));
    
    // Re-initialize icons
    lucide.createIcons();

    // Init page logic
    if (route.init) {
        route.init(param);
    }
}

window.addEventListener('hashchange', handleRoute);

// --- Utilities ---
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let icon = 'info';
    if(type === 'success') icon = 'check-circle';
    if(type === 'error') icon = 'alert-circle';
    
    toast.innerHTML = `<i data-lucide="${icon}"></i> <span>${message}</span>`;
    container.appendChild(toast);
    lucide.createIcons();
    
    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s forwards';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

async function apiFetch(endpoint, options = {}) {
    try {
        const res = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        const isJson = res.headers.get('content-type')?.includes('application/json');
        const data = isJson ? await res.json() : await res.text();
        
        if (!res.ok) {
            throw new Error(data.detail || data.message || `HTTP error ${res.status}`);
        }
        return data;
    } catch (error) {
        showToast(error.message, 'error');
        throw error;
    }
}

// --- App Initialization ---
async function initApp() {
    handleRoute();
    
    // Check if we need to seed
    try {
        const stats = await apiFetch('/skills/');
        if (stats.total === 0) {
            document.getElementById('btn-seed').style.display = 'flex';
        }
    } catch (e) {
        console.error("API might not be ready", e);
    }

    document.getElementById('btn-seed').addEventListener('click', async () => {
        try {
            document.getElementById('btn-seed').disabled = true;
            await apiFetch('/ingestion/seed', { method: 'POST' });
            showToast('Database seeded successfully!', 'success');
            document.getElementById('btn-seed').style.display = 'none';
            handleRoute(); // refresh current view
        } catch (e) {
            document.getElementById('btn-seed').disabled = false;
        }
    });
}

// --- Dashboard ---
async function initDashboard() {
    try {
        const [skillsData, auditStats] = await Promise.all([
            apiFetch('/skills/'),
            apiFetch('/audit/stats').catch(() => ({ total_versions: 0, total_proposals: 0, pending_proposals: 0, quarantined_proposals: 0 }))
        ]);
        
        document.getElementById('stat-skills').textContent = skillsData.total;
        document.getElementById('stat-versions').textContent = auditStats.total_versions || skillsData.total;
        document.getElementById('stat-proposals').textContent = auditStats.total_proposals || 0;
        document.getElementById('stat-quarantined').textContent = auditStats.quarantined_proposals || 0;

        // Render Chart
        const chartContainer = document.getElementById('category-chart');
        chartContainer.innerHTML = '';
        if (skillsData.categories && skillsData.categories.length > 0) {
            const max = Math.max(...skillsData.categories.map(c => c.count));
            skillsData.categories.forEach(cat => {
                const height = Math.max(15, (cat.count / max) * 100);
                chartContainer.innerHTML += `
                    <div class="bar-wrap" onclick="window.location.hash='#/skills'" style="cursor:pointer;">
                        <div class="bar" style="height: ${height}%;" title="${cat.category}: ${cat.count}"></div>
                        <div class="bar-label" title="${cat.category}">${cat.category} (${cat.count})</div>
                    </div>
                `;
            });
        } else {
            chartContainer.innerHTML = `
                <div style="text-align:center; padding: 24px 12px; width:100%;">
                    <p class="text-muted mb-4">No skills loaded yet in the local registry.</p>
                    <button class="btn btn-primary" id="btn-seed-inline">
                        <i data-lucide="database"></i> Seed Curated Skills Ecosystem
                    </button>
                </div>
            `;
            setTimeout(() => {
                const inlineSeed = document.getElementById('btn-seed-inline');
                if (inlineSeed) {
                    inlineSeed.onclick = () => document.getElementById('btn-seed').click();
                }
                lucide.createIcons();
            }, 50);
        }

        // Mock Activity Feed
        const feed = document.getElementById('activity-feed');
        if (skillsData.total > 0) {
            feed.innerHTML = `
                <div class="activity-item">
                    <div class="activity-icon"><i data-lucide="git-merge"></i></div>
                    <div class="activity-content">
                        <div class="activity-text">Merged batch for <b>Data Processing</b></div>
                        <div class="activity-time">2 mins ago</div>
                    </div>
                </div>
                <div class="activity-item">
                    <div class="activity-icon"><i data-lucide="file-plus"></i></div>
                    <div class="activity-content">
                        <div class="activity-text">New proposal submitted by Veteran Dev</div>
                        <div class="activity-time">1 hour ago</div>
                    </div>
                </div>
            `;
            lucide.createIcons();
        // Start Mini Dashboard Neural Preview
        initMiniNeuralPreview();

    } catch (e) {
        console.error("Dashboard error", e);
    }
}

// --- Skills Browser ---
async function initSkills() {
    try {
        const data = await apiFetch('/skills/');
        const grid = document.getElementById('skills-grid');
        const pills = document.getElementById('category-pills');
        let allSkills = data.skills || [];
        let activeCategory = 'all';

        function renderSkillCards(skills) {
            grid.innerHTML = '';
            if (skills.length === 0) {
                grid.innerHTML = '<div class="text-muted w-full text-center py-8">No matching skills found.</div>';
                return;
            }

            skills.forEach(skill => {
                grid.innerHTML += `
                    <div class="skill-card glass-panel" onclick="window.location.hash='#/skill/${skill.id}'">
                        <div class="skill-card-header">
                            <h3>${skill.name}</h3>
                            <span class="badge badge-primary">${skill.category}</span>
                        </div>
                        <p class="skill-card-desc">${skill.description || 'No description provided.'}</p>
                        <div class="skill-card-footer">
                            <span class="stat-mini"><i data-lucide="git-branch"></i> Active</span>
                            <span class="stat-mini"><i data-lucide="play-circle"></i> Open Skill &rarr;</span>
                        </div>
                    </div>
                `;
            });
            lucide.createIcons();
        }

        // Render Category Pills with click handlers
        if (data.categories) {
            pills.innerHTML = '<button class="pill active" data-category="all">All</button>';
            data.categories.forEach(c => {
                pills.innerHTML += `<button class="pill" data-category="${c.category}">${c.category} (${c.count})</button>`;
            });

            pills.querySelectorAll('.pill').forEach(btn => {
                btn.addEventListener('click', () => {
                    pills.querySelectorAll('.pill').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    activeCategory = btn.dataset.category;
                    const filtered = activeCategory === 'all' 
                        ? allSkills 
                        : allSkills.filter(s => s.category === activeCategory);
                    renderSkillCards(filtered);
                });
            });
        }

        renderSkillCards(allSkills);

        // Topbar search filter connection
        const searchInput = document.querySelector('.search-bar input');
        if (searchInput) {
            searchInput.oninput = (e) => {
                const term = e.target.value.toLowerCase().trim();
                let filtered = allSkills.filter(s => 
                    s.name.toLowerCase().includes(term) || 
                    (s.description && s.description.toLowerCase().includes(term)) ||
                    s.category.toLowerCase().includes(term)
                );
                if (activeCategory !== 'all') {
                    filtered = filtered.filter(s => s.category === activeCategory);
                }
                renderSkillCards(filtered);
            };
        }

    } catch (e) {
        console.error("Skills error", e);
    }
}

// --- Skill Detail ---
let currentSkillContent = '';
async function initSkillDetail(id) {
    if (!id) return;
    
    try {
        const [skill, versions, proposals] = await Promise.all([
            apiFetch(`/skills/${id}`),
            apiFetch(`/skills/${id}/versions`),
            apiFetch(`/proposals/skills/${id}/proposals`).catch(() => [])
        ]);

        document.getElementById('detail-name').textContent = skill.name;
        document.getElementById('detail-category').textContent = skill.category;
        document.getElementById('detail-desc').textContent = skill.description;
        document.getElementById('detail-vcount').textContent = versions.length || 0;
        
        if (skill.current_version && skill.current_version.content) {
            currentSkillContent = skill.current_version.content;
            document.getElementById('detail-content').textContent = currentSkillContent;
            document.getElementById('proposal-content').value = currentSkillContent;
        }

        // Tabs logic
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                
                e.target.classList.add('active');
                document.getElementById(`tab-${e.target.dataset.tab}`).classList.add('active');
            });
        });

        // Use Skill
        document.getElementById('btn-use-skill').addEventListener('click', async () => {
            try {
                await apiFetch(`/skills/${id}/use`, {
                    method: 'POST',
                    body: JSON.stringify({ user_id: 'demo-user' })
                });
                showToast('Skill executed successfully', 'success');
                let uc = document.getElementById('detail-ucount');
                uc.textContent = parseInt(uc.textContent) + 1;
            } catch (e) {}
        });

        // Submit Proposal
        document.getElementById('btn-submit-proposal').addEventListener('click', async () => {
            const isModify = document.querySelector('.tab-btn[data-tab="modify"]').classList.contains('active');
            const type = isModify ? 'modification' : 'issue_report';
            const content = isModify ? document.getElementById('proposal-content').value : null;
            const issue = isModify ? null : document.getElementById('proposal-issue').value;
            const proposer = document.getElementById('proposal-proposer').value;

            try {
                await apiFetch(`/proposals/skills/${id}/proposals`, {
                    method: 'POST',
                    body: JSON.stringify({
                        proposer_id: proposer,
                        proposal_type: type,
                        proposed_content: content,
                        issue_text: issue
                    })
                });
                showToast('Proposal submitted successfully', 'success');
                initSkillDetail(id); // Reload to show new proposal
            } catch (e) {}
        });

        // Render Timeline
        const timeline = document.getElementById('version-timeline');
        timeline.innerHTML = '';
        if(versions && versions.length > 0) {
            versions.slice(0, 5).forEach(v => {
                timeline.innerHTML += `
                    <div class="timeline-item">
                        <div class="timeline-dot"></div>
                        <div class="timeline-content">
                            <h4>v${v.id.substring(0,8)}</h4>
                            <p>${new Date(v.created_at).toLocaleString()}</p>
                        </div>
                    </div>
                `;
            });
        } else {
             timeline.innerHTML = '<p class="text-muted">No versions yet.</p>';
        }

        // Render Proposals
        const activeProps = document.getElementById('active-proposals');
        activeProps.innerHTML = '';
        if(proposals && proposals.length > 0) {
            proposals.forEach(p => {
                let badgeClass = p.status === 'pending' ? 'yellow' : (p.status === 'rejected' ? 'red' : 'green');
                activeProps.innerHTML += `
                    <div class="p-3 border-b border-gray-700 last:border-0" style="border-bottom: 1px solid rgba(255,255,255,0.1); padding: 12px 0;">
                        <div style="display:flex; justify-content:space-between;">
                            <span style="font-size:0.875rem; font-weight:600;">${p.proposal_type}</span>
                            <span style="font-size:0.75rem; color:var(--color-${badgeClass})">${p.status}</span>
                        </div>
                        <p style="font-size:0.75rem; color:var(--text-muted); margin-top:4px;">by ${p.proposer_id}</p>
                    </div>
                `;
            });
        } else {
            activeProps.innerHTML = '<p class="text-muted">No active proposals.</p>';
        }

    } catch (e) {
        console.error(e);
    }
}

// --- Pipeline ---
function logPipeline(msg, type='info') {
    const console = document.getElementById('pipeline-console');
    console.innerHTML += `<div class="log-entry ${type}">> ${msg}</div>`;
    console.scrollTop = console.scrollHeight;
}

async function initPipeline() {
    try {
        const data = await apiFetch('/skills/');
        const select = document.getElementById('pipeline-skill-select');
        
        data.skills.forEach(s => {
            const opt = document.createElement('option');
            opt.value = s.id;
            opt.textContent = s.name;
            select.appendChild(opt);
        });

        let currentBatchId = null;

        select.addEventListener('change', (e) => {
            const skillId = e.target.value;
            const btnProcess = document.getElementById('btn-process-batch');
            const btnFull = document.getElementById('btn-run-full');
            
            if (skillId) {
                btnProcess.disabled = false;
                btnFull.disabled = false;
                logPipeline(`Selected skill: ${skillId}`);
                document.getElementById('stage-batch').classList.add('active');
            } else {
                btnProcess.disabled = true;
                btnFull.disabled = true;
            }
        });

        document.getElementById('btn-process-batch').addEventListener('click', async () => {
            const skillId = select.value;
            try {
                logPipeline(`Processing batch for ${skillId}...`, 'system');
                const res = await apiFetch('/batches/process', {
                    method: 'POST',
                    body: JSON.stringify({ skill_id: skillId })
                });
                currentBatchId = res.batch_id;
                logPipeline(`Batch processed! ID: ${currentBatchId}`, 'success');
                if (res.merge_candidate_version_id) {
                    logPipeline(`Merge candidate: ${res.merge_candidate_version_id.substring(0,8)}...`, 'info');
                }
                logPipeline(res.message || '', 'info');
                
                document.getElementById('stage-audit').classList.add('active');
                document.getElementById('btn-run-audit').disabled = false;
            } catch (e) {
                logPipeline(`Batch processing failed: ${e.message}`, 'error');
            }
        });

        document.getElementById('btn-run-audit').addEventListener('click', async () => {
            if (!currentBatchId) return;
            try {
                logPipeline(`Running audit on batch ${currentBatchId}...`, 'system');
                const res = await apiFetch(`/audit/batch/${currentBatchId}/audit`, { method: 'POST' });
                logPipeline(`Audit complete: ${res.clean_count} clean, ${res.suspicious_count} suspicious out of ${res.total}`, 
                    res.suspicious_count > 0 ? 'error' : 'success');
                
                if (res.quarantined_proposal_ids && res.quarantined_proposal_ids.length > 0) {
                    logPipeline(`Quarantined: ${res.quarantined_proposal_ids.length} proposal(s)`, 'error');
                }
                
                if (res.clean_count > 0) {
                    document.getElementById('stage-release').classList.add('active');
                    document.getElementById('btn-release').disabled = false;
                } else {
                    logPipeline('All proposals quarantined. Release blocked.', 'error');
                }
            } catch (e) {
                logPipeline(`Audit failed: ${e.message}`, 'error');
            }
        });

        document.getElementById('btn-release').addEventListener('click', async () => {
            if (!currentBatchId) return;
            try {
                logPipeline(`Releasing batch ${currentBatchId}...`, 'system');
                const res = await apiFetch(`/audit/batch/${currentBatchId}/release`, { method: 'POST' });
                logPipeline(`Release successful! New version created.`, 'success');
            } catch (e) {
                logPipeline(`Release failed: ${e.message}`, 'error');
            }
        });

        document.getElementById('btn-run-full').addEventListener('click', async () => {
            const skillId = select.value;
            try {
                logPipeline(`Starting full pipeline for ${skillId}...`, 'system');
                
                document.querySelectorAll('.stage-card').forEach(c => c.classList.add('active'));
                
                const res = await apiFetch(`/audit/pipeline/${skillId}/run-full`, { method: 'POST' });
                
                logPipeline(`Batch ${res.batch_id} processed.`, 'info');
                if (res.audit_summary) {
                    logPipeline(`Audit: ${res.audit_summary.clean_count} clean, ${res.audit_summary.suspicious_count} suspicious`, res.audit_summary.suspicious_count > 0 ? 'error' : 'success');
                }
                if (res.version_id) {
                    logPipeline(`Released! New version: ${res.version_id.substring(0, 8)}...`, 'success');
                } else {
                    logPipeline(`${res.release_message}`, 'error');
                }
            } catch (e) {
                logPipeline(`Pipeline error: ${e.message}`, 'error');
            }
        });

    } catch(e) {
        console.error(e);
    }
}

// --- Audit Queue ---
async function initAudit() {
    try {
        const quarantined = await apiFetch('/audit/quarantined').catch(() => []);
        const tbody = document.getElementById('audit-table-body');
        const emptyState = document.getElementById('audit-empty');
        const table = document.querySelector('.data-table');

        if (!quarantined || quarantined.length === 0) {
            table.style.display = 'none';
            emptyState.style.display = 'block';
            return;
        }

        table.style.display = 'table';
        emptyState.style.display = 'none';
        tbody.innerHTML = '';

        quarantined.forEach(q => {
            const trustScore = q.proposer_trust_snapshot?.computed_score || 0;
            tbody.innerHTML += `
                <tr>
                    <td>${q.skill_id.substring(0, 8)}...</td>
                    <td>${q.proposer_id}</td>
                    <td><span class="badge badge-yellow">${q.proposal_type}</span></td>
                    <td><span style="color:var(--color-cyan);">${trustScore.toFixed(2)}</span></td>
                    <td><span style="color:var(--color-red); font-weight:600;">${q.status}</span></td>
                    <td>
                        <button class="btn btn-icon btn-approve" data-id="${q.id}" title="Approve"><i data-lucide="check" class="text-green"></i></button>
                        <button class="btn btn-icon btn-reject" data-id="${q.id}" title="Reject"><i data-lucide="x" class="text-red"></i></button>
                    </td>
                </tr>
            `;
        });
        
        lucide.createIcons();

        document.querySelectorAll('.btn-approve').forEach(btn => {
            btn.addEventListener('click', () => handleAuditAction(btn.dataset.id, 'approve'));
        });
        document.querySelectorAll('.btn-reject').forEach(btn => {
            btn.addEventListener('click', () => handleAuditAction(btn.dataset.id, 'reject'));
        });

    } catch (e) {
        console.error(e);
    }
}

// --- Mini Dashboard Neural Canvas Preview ---
let miniAnimId = null;
function initMiniNeuralPreview() {
    const canvas = document.getElementById('dashboard-neural-preview');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    if (miniAnimId) cancelAnimationFrame(miniAnimId);

    const nodes = [
        { x: 40, y: 75, color: '#00d4ff', r: 8, label: 'A' },
        { x: 100, y: 40, color: '#818cf8', r: 7, label: 'B' },
        { x: 100, y: 110, color: '#a855f7', r: 7, label: 'C' },
        { x: 170, y: 75, color: '#f43f5e', r: 9, label: 'D' },
        { x: 240, y: 75, color: '#10b981', r: 10, label: 'LIVE' },
    ];
    const links = [
        [0, 1], [0, 2], [1, 3], [2, 3], [3, 4]
    ];
    let particles = [
        { linkIdx: 0, progress: 0.1, speed: 0.015, color: '#00d4ff' },
        { linkIdx: 1, progress: 0.6, speed: 0.012, color: '#a855f7' },
        { linkIdx: 2, progress: 0.3, speed: 0.018, color: '#818cf8' },
        { linkIdx: 3, progress: 0.8, speed: 0.014, color: '#f43f5e' },
        { linkIdx: 4, progress: 0.5, speed: 0.02, color: '#10b981' }
    ];

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Draw links
        ctx.lineWidth = 1.5;
        links.forEach(([i, j]) => {
            const n1 = nodes[i];
            const n2 = nodes[j];
            const grad = ctx.createLinearGradient(n1.x, n1.y, n2.x, n2.y);
            grad.addColorStop(0, n1.color + '66');
            grad.addColorStop(1, n2.color + '66');
            ctx.strokeStyle = grad;
            ctx.beginPath();
            ctx.moveTo(n1.x, n1.y);
            ctx.lineTo(n2.x, n2.y);
            ctx.stroke();
        });

        // Update & draw particles
        particles.forEach(p => {
            p.progress += p.speed;
            if (p.progress > 1) p.progress = 0;
            const [i, j] = links[p.linkIdx];
            const n1 = nodes[i];
            const n2 = nodes[j];
            const px = n1.x + (n2.x - n1.x) * p.progress;
            const py = n1.y + (n2.y - n1.y) * p.progress;

            ctx.fillStyle = p.color;
            ctx.shadowColor = p.color;
            ctx.shadowBlur = 8;
            ctx.beginPath();
            ctx.arc(px, py, 3, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0;
        });

        // Draw nodes
        nodes.forEach(n => {
            ctx.shadowColor = n.color;
            ctx.shadowBlur = 10;
            ctx.fillStyle = n.color;
            ctx.beginPath();
            ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0;

            ctx.fillStyle = '#fff';
            ctx.font = 'bold 8px Inter, sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(n.label, n.x, n.y);
        });

        miniAnimId = requestAnimationFrame(draw);
    }
    draw();
}

// --- Interactive Neural Graph View ---
let graphAnimId = null;
async function initGraph() {
    const canvas = document.getElementById('neural-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    if (graphAnimId) cancelAnimationFrame(graphAnimId);

    // Viewport state
    let width = 0;
    let height = 0;
    let scale = 1.0;
    let offsetX = 0;
    let offsetY = 0;
    let isDragging = false;
    let isPanning = false;
    let dragNode = null;
    let startX = 0;
    let startY = 0;
    let hoverNode = null;
    let selectedNode = null;
    let currentMode = 'ecosystem'; // 'ecosystem' | 'cortex' | 'lineage'
    let physicsRunning = true;

    // Graph Data
    let nodes = [];
    let links = [];
    let particles = [];
    let bgDust = [];

    function resize() {
        const parent = canvas.parentElement;
        if (!parent) return;
        const dpr = window.devicePixelRatio || 1;
        width = parent.clientWidth;
        height = parent.clientHeight;
        canvas.width = width * dpr;
        canvas.height = height * dpr;
        canvas.style.width = width + 'px';
        canvas.style.height = height + 'px';
        ctx.scale(dpr, dpr);
    }
    resize();
    window.addEventListener('resize', resize);

    // Initialize background dust particles
    bgDust = Array.from({ length: 60 }, () => ({
        x: Math.random() * 2000 - 1000,
        y: Math.random() * 2000 - 1000,
        r: Math.random() * 1.5 + 0.5,
        alpha: Math.random() * 0.5 + 0.1,
        speed: Math.random() * 0.002 + 0.001
    }));

    // Fetch live graph data
    try {
        const graphData = await apiFetch('/graph/neural-data');
        const rawNodes = graphData.nodes || [];
        const rawLinks = graphData.links || [];

        // Update HUD
        const elNodes = document.getElementById('hud-node-count');
        const elLinks = document.getElementById('hud-link-count');
        const elQuarantine = document.getElementById('hud-quarantine-count');
        if (elNodes) elNodes.textContent = rawNodes.length;
        if (elLinks) elLinks.textContent = rawLinks.length;
        const qCount = rawNodes.filter(n => n.type === 'quarantined').length;
        if (elQuarantine) elQuarantine.textContent = qCount;

        // Position nodes initially
        const nodeMap = new Map();
        nodes = rawNodes.map((n, i) => {
            let x = (Math.random() - 0.5) * (width * 0.8);
            let y = (Math.random() - 0.5) * (height * 0.8);

            // Give cortex stages nice horizontal spread
            if (n.x_hint !== undefined) {
                x = n.x_hint;
                y = n.y_hint;
            }

            const nodeObj = {
                ...n,
                x: x,
                y: y,
                vx: 0,
                vy: 0,
                r: n.size || 16,
                baseR: n.size || 16,
                pulseVal: Math.random() * Math.PI * 2
            };
            nodeMap.set(n.id, nodeObj);
            return nodeObj;
        });

        links = rawLinks.map(l => ({
            ...l,
            sourceNode: nodeMap.get(l.source),
            targetNode: nodeMap.get(l.target),
        })).filter(l => l.sourceNode && l.targetNode);

        // Create initial traveling particles along links
        links.forEach((link, idx) => {
            if (link.animated || Math.random() > 0.4) {
                particles.push({
                    link: link,
                    progress: Math.random(),
                    speed: 0.006 + Math.random() * 0.008,
                    color: link.color || '#38bdf8',
                    size: 2.5 + Math.random() * 2
                });
            }
        });

    } catch (e) {
        console.error("Failed to load neural data", e);
        showToast('Failed to load neural graph data', 'error');
    }

    // Set initial view offset to center
    offsetX = width / 2;
    offsetY = height / 2;

    // --- Physics Engine ---
    function updatePhysics() {
        if (!physicsRunning) return;

        const kRepulsion = 1200;
        const springLength = 110;
        const springStrength = 0.035;
        const centerGravity = 0.015;
        const friction = 0.88;

        // Node-node repulsion
        for (let i = 0; i < nodes.length; i++) {
            for (let j = i + 1; j < nodes.length; j++) {
                const n1 = nodes[i];
                const n2 = nodes[j];
                const dx = n2.x - n1.x;
                const dy = n2.y - n1.y;
                const distSq = dx * dx + dy * dy + 100;
                const dist = Math.sqrt(distSq);

                if (dist < 400) {
                    const force = kRepulsion / distSq;
                    const fx = (dx / dist) * force;
                    const fy = (dy / dist) * force;
                    if (n1 !== dragNode) { n1.vx -= fx; n1.vy -= fy; }
                    if (n2 !== dragNode) { n2.vx += fx; n2.vy += fy; }
                }
            }
        }

        // Link spring attraction
        links.forEach(l => {
            const n1 = l.sourceNode;
            const n2 = l.targetNode;
            const dx = n2.x - n1.x;
            const dy = n2.y - n1.y;
            const dist = Math.sqrt(dx * dx + dy * dy) || 1;
            const targetL = (l.type === 'cortex_flow' ? 160 : springLength);
            const force = (dist - targetL) * springStrength;
            const fx = (dx / dist) * force;
            const fy = (dy / dist) * force;

            if (n1 !== dragNode) { n1.vx += fx; n1.vy += fy; }
            if (n2 !== dragNode) { n2.vx += fx; n2.vy += fy; }
        });

        // Center gravity or mode alignment
        nodes.forEach(n => {
            if (n === dragNode) return;

            if (currentMode === 'cortex' && n.x_hint !== undefined) {
                // Pull cortex stages to structured horizontal line
                n.vx += (n.x_hint - n.x) * 0.05;
                n.vy += (n.y_hint - n.y) * 0.05;
            } else if (currentMode === 'lineage' && n.type === 'version') {
                // Pull versions below skills
                n.vy += (120 - n.y) * 0.03;
            } else {
                // Normal gentle center pull
                n.vx -= n.x * centerGravity;
                n.vy -= n.y * centerGravity;
            }

            // Apply friction & update position
            n.vx *= friction;
            n.vy *= friction;
            n.x += n.vx;
            n.y += n.vy;
            n.pulseVal += 0.04;
        });

        // Update traveling particles
        particles.forEach(p => {
            p.progress += p.speed;
            if (p.progress >= 1) p.progress = 0;
        });
    }

    // --- Render Loop ---
    function render() {
        updatePhysics();

        ctx.save();
        ctx.clearRect(0, 0, width, height);

        // Apply viewport transform (pan + zoom)
        ctx.translate(offsetX, offsetY);
        ctx.scale(scale, scale);

        // 1. Draw Starry Neural Dust
        bgDust.forEach(d => {
            d.alpha += Math.sin(d.x + d.y + Date.now() * d.speed) * 0.005;
            ctx.fillStyle = `rgba(148, 163, 184, ${Math.max(0.05, Math.min(0.4, d.alpha))})`;
            ctx.beginPath();
            ctx.arc(d.x, d.y, d.r, 0, Math.PI * 2);
            ctx.fill();
        });

        // 2. Draw Synapses (Links)
        links.forEach(l => {
            const n1 = l.sourceNode;
            const n2 = l.targetNode;
            const isHovered = (hoverNode === n1 || hoverNode === n2);

            ctx.lineWidth = (l.value || 1.5) * (isHovered ? 2 : 1);
            const grad = ctx.createLinearGradient(n1.x, n1.y, n2.x, n2.y);
            grad.addColorStop(0, (n1.color || '#38bdf8') + (isHovered ? 'cc' : '44'));
            grad.addColorStop(1, (n2.color || '#a855f7') + (isHovered ? 'cc' : '44'));
            ctx.strokeStyle = grad;

            ctx.beginPath();
            ctx.moveTo(n1.x, n1.y);
            ctx.lineTo(n2.x, n2.y);
            ctx.stroke();
        });

        // 3. Draw Synaptic Signal Particles
        particles.forEach(p => {
            const n1 = p.link.sourceNode;
            const n2 = p.link.targetNode;
            const px = n1.x + (n2.x - n1.x) * p.progress;
            const py = n1.y + (n2.y - n1.y) * p.progress;

            ctx.fillStyle = p.color;
            ctx.shadowColor = p.color;
            ctx.shadowBlur = 12;
            ctx.beginPath();
            ctx.arc(px, py, p.size, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0;
        });

        // 4. Draw Nodes
        nodes.forEach(n => {
            const isHovered = (n === hoverNode);
            const isSelected = (n === selectedNode);
            const r = n.r + (isHovered ? 4 : (isSelected ? 3 : 0));
            const pulse = Math.sin(n.pulseVal) * 2;

            // Outer Pulsing Glow Aura
            ctx.shadowColor = n.color;
            ctx.shadowBlur = isHovered ? 25 : (isSelected ? 20 : 12);

            // Node Outer Shell / Gradient
            const radial = ctx.createRadialGradient(n.x, n.y, 2, n.x, n.y, r + pulse);
            radial.addColorStop(0, n.color);
            radial.addColorStop(0.7, n.color + 'dd');
            radial.addColorStop(1, n.color + '44');

            ctx.fillStyle = radial;
            ctx.beginPath();
            ctx.arc(n.x, n.y, r, 0, Math.PI * 2);
            ctx.fill();
            ctx.shadowBlur = 0;

            // Orbital Ring for special nodes (Cortex, Proposer, Live Version)
            if (n.type === 'cortex' || n.type === 'proposer' || n.is_live) {
                ctx.strokeStyle = n.color + '88';
                ctx.lineWidth = 1.5;
                ctx.setLineDash([4, 4]);
                ctx.beginPath();
                ctx.arc(n.x, n.y, r + 6 + pulse, 0, Math.PI * 2);
                ctx.stroke();
                ctx.setLineDash([]);
            }

            // Inner Core
            ctx.fillStyle = '#0a0e1a';
            ctx.beginPath();
            ctx.arc(n.x, n.y, r * 0.45, 0, Math.PI * 2);
            ctx.fill();

            // Core dot
            ctx.fillStyle = n.color;
            ctx.beginPath();
            ctx.arc(n.x, n.y, r * 0.25, 0, Math.PI * 2);
            ctx.fill();

            // Node Label
            ctx.font = `${n.type === 'cortex' ? 'bold 11px' : '10px'} Inter, sans-serif`;
            ctx.fillStyle = isHovered ? '#fff' : '#cbd5e1';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'top';
            ctx.shadowColor = '#000';
            ctx.shadowBlur = 4;
            ctx.fillText(n.name, n.x, n.y + r + 6);
            ctx.shadowBlur = 0;
        });

        ctx.restore();

        graphAnimId = requestAnimationFrame(render);
    }
    render();

    // --- Mouse & Touch Coordinates Conversion ---
    function getCanvasCoords(e) {
        const rect = canvas.getBoundingClientRect();
        const clientX = e.clientX || (e.touches && e.touches[0].clientX);
        const clientY = e.clientY || (e.touches && e.touches[0].clientY);
        const screenX = clientX - rect.left;
        const screenY = clientY - rect.top;
        const worldX = (screenX - offsetX) / scale;
        const worldY = (screenY - offsetY) / scale;
        return { screenX, screenY, worldX, worldY };
    }

    function findNodeAt(worldX, worldY) {
        for (let i = nodes.length - 1; i >= 0; i--) {
            const n = nodes[i];
            const dx = worldX - n.x;
            const dy = worldY - n.y;
            if (dx * dx + dy * dy <= (n.r + 8) * (n.r + 8)) {
                return n;
            }
        }
        return null;
    }

    // --- Event Listeners ---
    const tooltip = document.getElementById('neural-tooltip');

    canvas.addEventListener('mousemove', (e) => {
        const { screenX, screenY, worldX, worldY } = getCanvasCoords(e);

        if (isDragging && dragNode) {
            dragNode.x = worldX;
            dragNode.y = worldY;
            dragNode.vx = 0;
            dragNode.vy = 0;
            return;
        }

        if (isPanning) {
            offsetX += e.clientX - startX;
            offsetY += e.clientY - startY;
            startX = e.clientX;
            startY = e.clientY;
            return;
        }

        // Hover detection
        const target = findNodeAt(worldX, worldY);
        hoverNode = target;

        if (target && tooltip) {
            canvas.style.cursor = 'pointer';
            tooltip.style.display = 'block';
            tooltip.style.left = screenX + 'px';
            tooltip.style.top = screenY + 'px';
            tooltip.innerHTML = `
                <div class="tt-title">${target.name}</div>
                <div class="tt-sub">${target.desc || target.type.toUpperCase()}</div>
            `;
        } else if (tooltip) {
            canvas.style.cursor = isPanning ? 'grabbing' : 'grab';
            tooltip.style.display = 'none';
        }
    });

    canvas.addEventListener('mousedown', (e) => {
        const { worldX, worldY } = getCanvasCoords(e);
        const target = findNodeAt(worldX, worldY);

        if (target) {
            isDragging = true;
            dragNode = target;
        } else {
            isPanning = true;
            startX = e.clientX;
            startY = e.clientY;
        }
    });

    window.addEventListener('mouseup', (e) => {
        if (isDragging && dragNode) {
            dragNode = null;
        }
        isDragging = false;
        isPanning = false;
    });

    canvas.addEventListener('click', (e) => {
        const { worldX, worldY } = getCanvasCoords(e);
        const target = findNodeAt(worldX, worldY);
        if (target) {
            openNodeInspector(target);
        }
    });

    canvas.addEventListener('wheel', (e) => {
        e.preventDefault();
        const zoomFactor = e.deltaY < 0 ? 1.12 : 0.89;
        const newScale = Math.max(0.25, Math.min(3.5, scale * zoomFactor));

        const rect = canvas.getBoundingClientRect();
        const mouseX = e.clientX - rect.left;
        const mouseY = e.clientY - rect.top;

        offsetX = mouseX - (mouseX - offsetX) * (newScale / scale);
        offsetY = mouseY - (mouseY - offsetY) * (newScale / scale);
        scale = newScale;
    }, { passive: false });

    // --- HUD Controls ---
    document.getElementById('btn-zoom-in')?.addEventListener('click', () => {
        scale = Math.min(3.5, scale * 1.25);
    });
    document.getElementById('btn-zoom-out')?.addEventListener('click', () => {
        scale = Math.max(0.25, scale * 0.8);
    });
    document.getElementById('btn-reset-view')?.addEventListener('click', () => {
        scale = 1.0;
        offsetX = width / 2;
        offsetY = height / 2;
    });
    document.getElementById('btn-toggle-physics')?.addEventListener('click', (e) => {
        physicsRunning = !physicsRunning;
        showToast(`Simulation ${physicsRunning ? 'Resumed' : 'Paused'}`, 'info');
    });

    // Mode toggles
    document.querySelectorAll('.btn-mode').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.btn-mode').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentMode = btn.dataset.mode;
            showToast(`Switched to ${btn.textContent.trim()} mode`, 'info');
        });
    });

    // Pulse Generator Button
    document.getElementById('btn-fire-pulse')?.addEventListener('click', () => {
        showToast('Firing proposal signals through neural synapses! ⚡', 'success');
        for (let i = 0; i < 15; i++) {
            const randomLink = links[Math.floor(Math.random() * links.length)];
            if (randomLink) {
                particles.push({
                    link: randomLink,
                    progress: 0,
                    speed: 0.02 + Math.random() * 0.02,
                    color: '#00d4ff',
                    size: 4
                });
            }
        }
    });

    // Close Inspector
    document.getElementById('btn-close-inspector')?.addEventListener('click', () => {
        const inspector = document.getElementById('neural-inspector');
        if (inspector) inspector.style.display = 'none';
        selectedNode = null;
    });

    // Open Inspector Drawer
    function openNodeInspector(node) {
        selectedNode = node;
        const inspector = document.getElementById('neural-inspector');
        if (!inspector) return;
        inspector.style.display = 'flex';

        document.getElementById('inspector-name').textContent = node.name;
        const badge = document.getElementById('inspector-badge');
        badge.textContent = node.type.toUpperCase();
        badge.style.backgroundColor = node.color + '33';
        badge.style.color = node.color;
        badge.style.border = `1px solid ${node.color}`;

        const body = document.getElementById('inspector-body');
        const footer = document.getElementById('inspector-footer');

        let html = `
            <div class="inspector-section">
                <h4>Description</h4>
                <p class="text-muted">${node.desc || 'No description provided.'}</p>
            </div>
        `;

        if (node.type === 'proposer') {
            html += `
                <div class="inspector-section">
                    <h4>Trust Signals</h4>
                    <div class="inspector-metrics-grid">
                        <div class="inspector-metric-card">
                            <div class="val">${(node.trust * 100).toFixed(0)}%</div>
                            <div class="lbl">Trust Score</div>
                        </div>
                        <div class="inspector-metric-card">
                            <div class="val">${node.stars || 0}</div>
                            <div class="lbl">Verified Stars</div>
                        </div>
                    </div>
                </div>
            `;
            footer.innerHTML = `<button class="btn btn-outline w-full" onclick="window.location.hash='#/skills'"><i data-lucide="file-plus"></i> Submit Proposal</button>`;
        } else if (node.type === 'skill') {
            html += `
                <div class="inspector-section">
                    <h4>Skill Hub Properties</h4>
                    <div class="inspector-metrics-grid">
                        <div class="inspector-metric-card">
                            <div class="val">${node.category}</div>
                            <div class="lbl">Domain</div>
                        </div>
                        <div class="inspector-metric-card">
                            <div class="val">${node.current_version_id ? node.current_version_id.substring(0, 8) : 'None'}</div>
                            <div class="lbl">Live Version</div>
                        </div>
                    </div>
                </div>
            `;
            footer.innerHTML = `<button class="btn btn-primary w-full" onclick="window.location.hash='#/skill/${node.raw_id}'"><i data-lucide="external-link"></i> Open Skill Detail</button>`;
        } else if (node.type === 'quarantined') {
            html += `
                <div class="inspector-section">
                    <h4>Security Quarantine Flag</h4>
                    <div class="inspector-code-block" style="color:#ef4444;">
                        Status: QUARANTINED
                        Flag: Threat detected by Static/Canary AST analysis.
                        Cherry-picked from batch to preserve pipeline health.
                    </div>
                </div>
            `;
            footer.innerHTML = `<button class="btn btn-danger w-full" onclick="window.location.hash='#/audit'"><i data-lucide="shield-alert"></i> Review in Quarantine Queue</button>`;
        } else if (node.type === 'cortex') {
            html += `
                <div class="inspector-section">
                    <h4>Pipeline Cortex Hub</h4>
                    <p class="text-muted">Part of the autonomous 7-stage evolution engine.</p>
                </div>
            `;
            footer.innerHTML = `<button class="btn btn-gradient w-full" onclick="window.location.hash='#/pipeline'"><i data-lucide="git-merge"></i> Open Pipeline Controller</button>`;
        } else {
            footer.innerHTML = `<button class="btn btn-outline w-full" onclick="window.location.hash='#/skills'"><i data-lucide="layers"></i> Browse Ecosystem</button>`;
        }

        body.innerHTML = html;
        lucide.createIcons();
    }
}

// Start
document.addEventListener('DOMContentLoaded', initApp);
