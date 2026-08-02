// TradePilot Web App Logic

document.addEventListener("DOMContentLoaded", () => {
    loadStats();
    loadActivityLogs();
    loadCampaigns();
    loadContacts();
    loadTemplates();
});

function showTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));
    
    document.getElementById(`tab-${tabName}`).classList.add('active');
    event.target.classList.add('active');

    if (tabName === 'dashboard') loadStats();
    if (tabName === 'campaigns') loadCampaigns();
    if (tabName === 'contacts') loadContacts();
    if (tabName === 'templates') loadTemplates();
    if (tabName === 'exports') loadExports();
}

async function loadStats() {
    try {
        const res = await fetch('/api/stats');
        const data = await res.json();
        document.getElementById('stat-contacts').innerText = data.total_contacts || 0;
        document.getElementById('stat-campaigns').innerText = data.total_campaigns || 0;
        document.getElementById('stat-sent').innerText = data.sent_today || 0;
        document.getElementById('stat-rate').innerText = `${data.success_rate || 100}%`;
    } catch (e) {
        console.error("Stats load failed", e);
    }
}

async function loadActivityLogs() {
    try {
        const res = await fetch('/api/logs?limit=10');
        const logs = await res.json();
        const tbody = document.getElementById('activity-tbody');
        if (logs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="text-center">No recent activity</td></tr>';
            return;
        }
        tbody.innerHTML = logs.map(l => `
            <tr>
                <td>#${l.id}</td>
                <td>${l.email}</td>
                <td><span class="badge">${l.status}</span></td>
                <td>${l.timestamp}</td>
            </tr>
        `).join('');
    } catch (e) {
        console.error("Logs load failed", e);
    }
}

async function loadCampaigns() {
    try {
        const res = await fetch('/api/campaigns');
        const campaigns = await res.json();
        const tbody = document.getElementById('campaigns-tbody');
        tbody.innerHTML = campaigns.map(c => `
            <tr>
                <td>#${c.id}</td>
                <td>${c.name}</td>
                <td>${c.status}</td>
                <td>${c.sent_count} / ${c.total_recipients}</td>
                <td><a href="/api/campaigns/${c.id}/export-bundle" class="btn btn-primary" style="font-size:12px; padding:4px 8px;">📦 PDF & TXT Zip</a></td>
            </tr>
        `).join('');
    } catch (e) {
        console.error("Campaigns load failed", e);
    }
}

async function loadContacts() {
    try {
        const res = await fetch('/api/contacts');
        const contacts = await res.json();
        const tbody = document.getElementById('contacts-tbody');
        tbody.innerHTML = contacts.map(c => `
            <tr>
                <td>#${c.id}</td>
                <td>${c.company}</td>
                <td>${c.contact_name}</td>
                <td>${c.email}</td>
                <td>${c.country}</td>
            </tr>
        `).join('');
    } catch (e) {
        console.error("Contacts load failed", e);
    }
}

async function loadTemplates() {
    try {
        const res = await fetch('/api/templates');
        const templates = await res.json();
        const select = document.getElementById('camp-template');
        select.innerHTML = templates.map(t => `<option value="${t.id}">${t.name} (Subject: ${t.subject})</option>`).join('');
    } catch (e) {
        console.error("Templates load failed", e);
    }
}

async function loadExports() {
    try {
        const res = await fetch('/api/campaigns');
        const campaigns = await res.json();
        const container = document.getElementById('exports-list');
        if (campaigns.length === 0) {
            container.innerHTML = '<p>No campaigns found to export.</p>';
            return;
        }
        container.innerHTML = campaigns.map(c => `
            <div style="background: rgba(255,255,255,0.03); border:1px solid var(--border-color); padding:16px; margin-bottom:12px; border-radius:8px; display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <strong>Campaign #${c.id}: ${c.name}</strong>
                    <p style="color:var(--text-muted); font-size:12px;">Total Emails Rendered: ${c.total_recipients}</p>
                </div>
                <a href="/api/campaigns/${c.id}/export-bundle" class="btn btn-primary">⬇ Download Per-Email PDF & TXT Bundle (.ZIP)</a>
            </div>
        `).join('');
    } catch (e) {
        console.error("Exports load failed", e);
    }
}

async function handleCreateCampaign(e) {
    e.preventDefault();
    const formData = new FormData();
    formData.append('name', document.getElementById('camp-name').value);
    formData.append('template_id', document.getElementById('camp-template').value);
    formData.append('subject_override', document.getElementById('camp-subject').value);
    formData.append('min_delay', document.getElementById('camp-min-delay').value);
    formData.append('max_delay', document.getElementById('camp-max-delay').value);
    formData.append('is_dry_run', document.getElementById('camp-dryrun').checked);

    try {
        const res = await fetch('/api/campaigns/create', { method: 'POST', body: formData });
        const data = await res.json();
        alert(`Campaign #${data.campaign_id} created successfully! Generated ${data.pdf_txt_export.total_emails} per-email PDF & TXT documents.`);
        loadCampaigns();
        loadStats();
    } catch (err) {
        alert("Failed to create campaign: " + err.message);
    }
}

async function handleCreateTemplate(e) {
    e.preventDefault();
    const formData = new FormData();
    formData.append('name', document.getElementById('tpl-name').value);
    formData.append('subject', document.getElementById('tpl-subject').value);
    formData.append('body_content', document.getElementById('tpl-body').value);

    try {
        const res = await fetch('/api/templates', { method: 'POST', body: formData });
        alert("Template saved successfully!");
        loadTemplates();
    } catch (err) {
        alert("Failed to save template: " + err.message);
    }
}

async function uploadContactFile(e) {
    const file = e.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    try {
        const res = await fetch('/api/contacts/upload', { method: 'POST', body: formData });
        const data = await res.json();
        alert(`Imported ${data.inserted} contacts successfully!`);
        loadContacts();
        loadStats();
    } catch (err) {
        alert("Upload failed: " + err.message);
    }
}
