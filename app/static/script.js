let isScanning = false;
let devicesData = [];
let filteredDevices = [];
let sortColumn = 'name';
let sortDirection = 'asc';
let selectionMode = false;
let selectedDevices = new Set();

// Helper function to get correct API URL
function getApiUrl(endpoint) {
    if (!endpoint.startsWith('/')) {
        endpoint = '/' + endpoint;
    }
    if (!endpoint.startsWith('/api/')) {
        endpoint = '/api' + endpoint;
    }
    return endpoint;
}

// Initialize i18n and UI
async function initializeApp() {
    await i18n.init();
    updateUIText();
    setupSearchListener();
}

function updateUIText() {
    document.title = i18n.t('app_title');
    document.getElementById('scanBtnText').textContent = i18n.t('scan_button');
    document.getElementById('searchInput').placeholder = i18n.t('search_placeholder') || 'Search devices...';
    document.getElementById('statusMessage').textContent = i18n.t('scan_status_ready');
}

function setupSearchListener() {
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', (e) => {
        filterDevices(e.target.value);
    });
}

function filterDevices(searchTerm) {
    if (!searchTerm.trim()) {
        filteredDevices = [...devicesData];
    } else {
        const term = searchTerm.toLowerCase();
        filteredDevices = devicesData.filter(device => 
            device.name.toLowerCase().includes(term) ||
            device.ip.includes(term) ||
            device.mac.toLowerCase().includes(term) ||
            device.type.toLowerCase().includes(term) ||
            device.fw.toLowerCase().includes(term)
        );
    }
    displayDevices(filteredDevices);
}

// Wait for DOM and i18n to be ready
document.addEventListener('DOMContentLoaded', initializeApp);

async function startScan() {
    if (isScanning) return;
    
    isScanning = true;
    const btn = document.getElementById('scanBtn');
    const btnText = document.getElementById('scanBtnText');
    const status = document.getElementById('statusMessage');
    const deviceTable = document.getElementById('deviceTable');
    
    btn.disabled = true;
    btnText.textContent = i18n.t('scan_status_scanning');
    status.textContent = i18n.t('scan_status_scanning');
    deviceTable.innerHTML = '<div class="loading"><div class="mdc-circular-progress"></div><div>' + i18n.t('loading_message') + '</div></div>';
    
    try {
        const response = await fetch(getApiUrl('/api/scan'));
        const devices = await response.json();
        
        devicesData = devices;
        filteredDevices = [...devices];
        displayDevices(filteredDevices);
        status.textContent = i18n.t('scan_status_complete', { count: devices.length });
    } catch (error) {
        status.textContent = i18n.t('scan_status_error', { error: error.message });
        deviceTable.innerHTML = '<div class="empty-state"><div class="empty-state__icon">⚠️</div><div class="empty-state__message">' + i18n.t('error_occurred') + '</div></div>';
    } finally {
        isScanning = false;
        btn.disabled = false;
        btnText.textContent = i18n.t('scan_button');
    }
}

function sortDevices(column) {
    if (sortColumn === column) {
        sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
        sortColumn = column;
        sortDirection = 'asc';
    }

    filteredDevices.sort((a, b) => {
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

    displayDevices(filteredDevices);
}

function displayDevices(devices) {
    const deviceTable = document.getElementById('deviceTable');
    
    if (devices.length === 0) {
        deviceTable.innerHTML = '<div class="empty-state"><div class="empty-state__icon">🔍</div><div class="empty-state__message">' + i18n.t('no_devices_found') + '</div></div>';
        return;
    }
    
    const getSortClass = (column) => {
        if (sortColumn !== column) return '';
        return sortDirection === 'asc' ? 'mdc-data-table__header-cell--sorted-ascending' : 'mdc-data-table__header-cell--sorted-descending';
    };

    const checkboxColumn = selectionMode ? `<th class="mdc-data-table__header-cell mdc-data-table__header-cell--checkbox">
        <div class="mdc-checkbox">
            <input type="checkbox" class="mdc-checkbox__native-control" id="selectAll" onchange="toggleSelectAll(this.checked)">
            <div class="mdc-checkbox__background">
                <div class="mdc-checkbox__checkmark"></div>
            </div>
        </div>
    </th>` : '';

    deviceTable.innerHTML = `
        <div class="mdc-data-table">
            <table class="mdc-data-table__table">
                <thead>
                    <tr class="mdc-data-table__header-row">
                        ${checkboxColumn}
                        <th class="mdc-data-table__header-cell ${getSortClass('name')} ${sortColumn === 'name' ? 'mdc-data-table__header-cell--sorted' : ''}" onclick="sortDevices('name')">${i18n.t('table_header_name')}</th>
                        <th class="mdc-data-table__header-cell ${getSortClass('type')} ${sortColumn === 'type' ? 'mdc-data-table__header-cell--sorted' : ''}" onclick="sortDevices('type')">${i18n.t('table_header_type')}</th>
                        <th class="mdc-data-table__header-cell ${getSortClass('generation')} ${sortColumn === 'generation' ? 'mdc-data-table__header-cell--sorted' : ''}" onclick="sortDevices('generation')">${i18n.t('table_header_gen')}</th>
                        <th class="mdc-data-table__header-cell ${getSortClass('ip')} ${sortColumn === 'ip' ? 'mdc-data-table__header-cell--sorted' : ''}" onclick="sortDevices('ip')">${i18n.t('table_header_ip')}</th>
                        <th class="mdc-data-table__header-cell ${getSortClass('mac')} ${sortColumn === 'mac' ? 'mdc-data-table__header-cell--sorted' : ''}" onclick="sortDevices('mac')">${i18n.t('table_header_mac')}</th>
                        <th class="mdc-data-table__header-cell ${getSortClass('fw')} ${sortColumn === 'fw' ? 'mdc-data-table__header-cell--sorted' : ''}" onclick="sortDevices('fw')">${i18n.t('table_header_fw')}</th>
                        <th class="mdc-data-table__header-cell ${getSortClass('auth')} ${sortColumn === 'auth' ? 'mdc-data-table__header-cell--sorted' : ''}" onclick="sortDevices('auth')">${i18n.t('table_header_auth')}</th>
                    </tr>
                </thead>
                <tbody class="mdc-data-table__content">
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
                            }
                        } else {
                            tooltipText = i18n.t('fw_latest');
                        }

                        const checkboxCell = selectionMode ? `<td class="mdc-data-table__cell mdc-data-table__cell--checkbox">
                            <div class="mdc-checkbox">
                                <input type="checkbox" class="mdc-checkbox__native-control device-checkbox" value="${device.ip}" onchange="toggleDevice('${device.ip}', this.checked)" ${selectedDevices.has(device.ip) ? 'checked' : ''}>
                                <div class="mdc-checkbox__background">
                                    <div class="mdc-checkbox__checkmark"></div>
                                </div>
                            </div>
                        </td>` : '';
                        
                        return `
                        <tr class="mdc-data-table__row ${selectedDevices.has(device.ip) ? 'mdc-data-table__row--selected' : ''}">
                            ${checkboxCell}
                            <td class="mdc-data-table__cell">${escapeHtml(device.name)}</td>
                            <td class="mdc-data-table__cell"><span class="device-type-badge">${escapeHtml(device.type)}</span></td>
                            <td class="mdc-data-table__cell">${i18n.t('gen_prefix')}${device.generation || 1}</td>
                            <td class="mdc-data-table__cell"><a href="http://${escapeHtml(device.ip)}" target="_blank">${escapeHtml(device.ip)}</a></td>
                            <td class="mdc-data-table__cell">${escapeHtml(device.mac)}</td>
                            <td class="mdc-data-table__cell fw-cell">
                                <span class="${fwClass}">${escapeHtml(device.fw)}</span>
                                <div class="fw-tooltip">
                                    <div class="fw-tooltip-text">${tooltipText}</div>
                                    ${showButton ? `<button class="fw-update-btn" onclick="updateFirmware('${device.ip}', event)">${i18n.t('fw_update_btn')}</button>` : ''}
                                </div>
                            </td>
                            <td class="mdc-data-table__cell">
                                <span class="auth-badge ${device.auth ? 'auth-enabled' : 'auth-disabled'}" 
                                      onclick="toggleAuth('${device.ip}', ${device.auth}, event)"
                                      title="Click to ${device.auth ? 'disable' : 'enable'} authentication">
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

// Selection mode functions
function toggleSelectionMode() {
    selectionMode = !selectionMode;
    const btn = document.getElementById('selectionModeBtn');
    const batchToolbar = document.getElementById('batchToolbar');
    
    btn.style.backgroundColor = selectionMode ? 'rgba(3, 169, 244, 0.12)' : '';
    batchToolbar.style.display = selectionMode ? 'flex' : 'none';
    
    if (!selectionMode) {
        selectedDevices.clear();
    }
    
    displayDevices(filteredDevices);
    updateSelectedCount();
}

function toggleDevice(ip, checked) {
    if (checked) {
        selectedDevices.add(ip);
    } else {
        selectedDevices.delete(ip);
    }
    updateSelectedCount();
}

function toggleSelectAll(checked) {
    if (checked) {
        filteredDevices.forEach(device => selectedDevices.add(device.ip));
    } else {
        selectedDevices.clear();
    }
    displayDevices(filteredDevices);
    updateSelectedCount();
}

function clearSelection() {
    selectedDevices.clear();
    displayDevices(filteredDevices);
    updateSelectedCount();
}

function updateSelectedCount() {
    document.getElementById('selectedCount').textContent = `${selectedDevices.size} selected`;
}

// Batch operations (placeholders for v0.7.0)
function batchUpdate() {
    if (selectedDevices.size === 0) return;
    alert(`Batch update for ${selectedDevices.size} devices will be implemented in v0.7.0`);
}

function batchToggleAuth() {
    if (selectedDevices.size === 0) return;
    alert(`Batch auth toggle for ${selectedDevices.size} devices will be implemented in v0.7.0`);
}

function batchReboot() {
    if (selectedDevices.size === 0) return;
    alert(`Batch reboot for ${selectedDevices.size} devices will be implemented in v0.7.0`);
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

// Keep existing firmware update and auth toggle functions
async function updateFirmware(ip, event) {
    event.stopPropagation();
    
    const btn = event.target;
    const originalText = btn.textContent;
    
    if (!confirm(i18n.t('fw_update_confirm', { ip: ip }))) {
        return;
    }
    
    btn.disabled = true;
    btn.textContent = i18n.t('fw_updating');
    
    try {
        const response = await fetch(getApiUrl(`/api/update/${ip}`), {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            btn.textContent = i18n.t('fw_updated');
            btn.style.background = '#3fb950';
            
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

async function toggleAuth(ip, currentlyEnabled, event) {
    const badge = event.target;
    const originalText = badge.textContent;
    
    const enable = !currentlyEnabled;
    const message = enable 
        ? i18n.t('auth_toggle_enable_message', { ip: ip })
        : i18n.t('auth_toggle_disable_message', { ip: ip });
    
    if (!confirm(message)) {
        return;
    }
    
    badge.classList.add('disabled');
    badge.textContent = i18n.t('auth_toggling');
    
    try {
        const response = await fetch(getApiUrl(`/api/auth/${ip}`), {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ enable: enable })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            badge.textContent = i18n.t('auth_toggle_success');
            
            setTimeout(() => {
                startScan();
            }, 2000);
        } else {
            badge.textContent = i18n.t('auth_toggle_failed');
            alert(i18n.t('auth_toggle_error', { error: data.error || 'Unknown error' }));
            setTimeout(() => {
                badge.textContent = originalText;
                badge.classList.remove('disabled');
            }, 2000);
        }
    } catch (error) {
        badge.textContent = i18n.t('auth_toggle_failed');
        alert(i18n.t('auth_toggle_error', { error: error.message }));
        setTimeout(() => {
            badge.textContent = originalText;
            badge.classList.remove('disabled');
        }, 2000);
    }
}
