let isScanning = false;
let devicesData = [];
let sortColumn = 'name';
let sortDirection = 'asc';

// Initialize i18n and UI
async function initializeApp() {
    await i18n.init();
    updateUIText();
}

function updateUIText() {
    document.title = i18n.t('app_title');
    document.getElementById('pageTitle').textContent = i18n.t('page_title');
    document.getElementById('scanBtn').textContent = i18n.t('scan_button');
    document.getElementById('status').textContent = i18n.t('scan_status_ready');
}

// Wait for DOM and i18n to be ready
document.addEventListener('DOMContentLoaded', initializeApp);

async function startScan() {
    if (isScanning) return;
    
    isScanning = true;
    const btn = document.getElementById('scanBtn');
    const status = document.getElementById('status');
    const deviceList = document.getElementById('deviceList');
    
    btn.disabled = true;
    status.textContent = i18n.t('scan_status_scanning');
    deviceList.innerHTML = `<div class="loading"><div class="spinner"></div><div>${i18n.t('loading_message')}</div></div>`;
    
    try {
        const response = await fetch('/api/scan');
        const devices = await response.json();
        
        devicesData = devices;
        displayDevices(devices);
        status.textContent = i18n.t('scan_status_complete', { count: devices.length });
    } catch (error) {
        status.textContent = i18n.t('scan_status_error', { error: error.message });
        deviceList.innerHTML = `<div class="no-devices"><div class="no-devices-icon">⚠️</div><div>${i18n.t('error_occurred')}</div></div>`;
    } finally {
        isScanning = false;
        btn.disabled = false;
    }
}

function sortDevices(column) {
    if (sortColumn === column) {
        sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        sortColumn = column;
        sortDirection = 'asc';
    }

    devicesData.sort((a, b) => {
        let valA = a[column];
        let valB = b[column];

        if (typeof valA === 'boolean') {
            valA = valA ? 1 : 0;
            valB = valB ? 1 : 0;
        }

        if (typeof valA === 'string') {
            valA = valA.toLowerCase();
            valB = valB.toLowerCase();
        }

        if (valA < valB) return sortDirection === 'asc' ? -1 : 1;
        if (valA > valB) return sortDirection === 'asc' ? 1 : -1;
        return 0;
    });

    displayDevices(devicesData);
}

function displayDevices(devices) {
    const deviceList = document.getElementById('deviceList');
    
    if (devices.length === 0) {
        deviceList.innerHTML = `<div class="no-devices"><div class="no-devices-icon">🔍</div><div>${i18n.t('no_devices_found')}</div></div>`;
        return;
    }
    
    const getSortClass = (column) => {
        if (sortColumn !== column) return 'sortable';
        return sortDirection === 'asc' ? 'sort-asc' : 'sort-desc';
    };

    deviceList.innerHTML = `
        <div class="device-list">
            <table>
                <thead>
                    <tr>
                        <th class="${getSortClass('name')}" onclick="sortDevices('name')">${i18n.t('table_header_name')}</th>
                        <th class="${getSortClass('type')}" onclick="sortDevices('type')">${i18n.t('table_header_type')}</th>
                        <th class="${getSortClass('generation')}" onclick="sortDevices('generation')">${i18n.t('table_header_gen')}</th>
                        <th class="${getSortClass('ip')}" onclick="sortDevices('ip')">${i18n.t('table_header_ip')}</th>
                        <th class="${getSortClass('mac')}" onclick="sortDevices('mac')">${i18n.t('table_header_mac')}</th>
                        <th class="${getSortClass('fw')}" onclick="sortDevices('fw')">${i18n.t('table_header_fw')}</th>
                        <th class="${getSortClass('auth')}" onclick="sortDevices('auth')">${i18n.t('table_header_auth')}</th>
                    </tr>
                </thead>
                <tbody>
                    ${devices.map(device => {
                        const fwClass = device.has_update ? 'fw-outdated' : 'fw-latest';
                        let tooltipText = '';
                        let showButton = false;
                        
                        if (device.has_update) {
                            if (device.can_update) {
                                tooltipText = i18n.t('fw_update_to', { version: device.latest_version });
                                showButton = true;
                            } else {
                                tooltipText = i18n.t('fw_set_password');
                                showButton = false;
                            }
                        } else {
                            tooltipText = i18n.t('fw_latest');
                            showButton = false;
                        }
                        
                        return `
                        <tr>
                            <td>${escapeHtml(device.name)}</td>
                            <td><span class="device-type-badge">${escapeHtml(device.type)}</span></td>
                            <td>${i18n.t('gen_prefix')}${device.generation || 1}</td>
                            <td><a href="http://${escapeHtml(device.ip)}" target="_blank">${escapeHtml(device.ip)}</a></td>
                            <td>${escapeHtml(device.mac)}</td>
                            <td class="fw-cell">
                                <span class="${fwClass}">${escapeHtml(device.fw)}</span>
                                <div class="fw-tooltip">
                                    <div class="fw-tooltip-text">${tooltipText}</div>
                                    ${showButton ? `<button class="fw-update-btn" onclick="updateFirmware('${device.ip}', event)">${i18n.t('fw_update_btn')}</button>` : ''}
                                </div>
                            </td>
                            <td>
                                <span class="auth-badge ${device.auth ? 'auth-enabled' : 'auth-disabled'}">
                                    ${device.auth ? i18n.t('auth_enabled') : i18n.t('auth_disabled')}
                                </span>
                            </td>
                        </tr>
                    `;}).join('')}
                </tbody>
            </table>
        </div>
    `;
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, m => map[m]);
}

async function updateFirmware(ip, event) {
    event.stopPropagation(); // Prevent tooltip from closing
    
    const btn = event.target;
    const originalText = btn.textContent;
    
    if (!confirm(i18n.t('fw_update_confirm', { ip: ip }))) {
        return;
    }
    
    btn.disabled = true;
    btn.textContent = i18n.t('fw_updating');
    
    try {
        const response = await fetch(`/api/update/${ip}`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            btn.textContent = i18n.t('fw_updated');
            btn.style.background = '#3fb950';
            
            // Refresh device list after 30 seconds
            setTimeout(() => {
                startScan();
            }, 30000);
        } else {
            btn.textContent = i18n.t('fw_failed');
            btn.style.background = '#f85149';
            alert(i18n.t('fw_update_error', { error: data.error || 'Unknown error' }));
            setTimeout(() => {
                btn.textContent = originalText;
                btn.style.background = '';
                btn.disabled = false;
            }, 3000);
        }
    } catch (error) {
        btn.textContent = i18n.t('fw_error');
        btn.style.background = '#f85149';
        alert(i18n.t('fw_network_error', { error: error.message }));
        setTimeout(() => {
            btn.textContent = originalText;
            btn.style.background = '';
            btn.disabled = false;
        }, 3000);
    }
}
