let isScanning = false;
let devicesData = [];
let sortColumn = 'name';
let sortDirection = 'asc';

async function startScan() {
    if (isScanning) return;
    
    isScanning = true;
    const btn = document.getElementById('scanBtn');
    const status = document.getElementById('status');
    const deviceList = document.getElementById('deviceList');
    
    btn.disabled = true;
    status.textContent = 'Bezig met scannen...';
    deviceList.innerHTML = '<div class="loading"><div class="spinner"></div><div>Netwerk wordt gescand...</div></div>';
    
    try {
        const response = await fetch('/api/scan');
        const devices = await response.json();
        
        devicesData = devices;
        displayDevices(devices);
        status.textContent = `Scan voltooid. ${devices.length} Shelly device(s) gevonden.`;
    } catch (error) {
        status.textContent = 'Fout bij scannen: ' + error.message;
        deviceList.innerHTML = '<div class="no-devices"><div class="no-devices-icon">⚠️</div><div>Er is een fout opgetreden</div></div>';
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
        deviceList.innerHTML = '<div class="no-devices"><div class="no-devices-icon">🔍</div><div>Geen Shelly devices gevonden</div></div>';
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
                        <th class="${getSortClass('name')}" onclick="sortDevices('name')">Naam</th>
                        <th class="${getSortClass('type')}" onclick="sortDevices('type')">Type</th>
                        <th class="${getSortClass('ip')}" onclick="sortDevices('ip')">IP Adres</th>
                        <th class="${getSortClass('mac')}" onclick="sortDevices('mac')">MAC Adres</th>
                        <th class="${getSortClass('fw')}" onclick="sortDevices('fw')">Firmware</th>
                        <th class="${getSortClass('auth')}" onclick="sortDevices('auth')">Auth</th>
                    </tr>
                </thead>
                <tbody>
                    ${devices.map(device => `
                        <tr>
                            <td>${escapeHtml(device.name)}</td>
                            <td><span class="device-type-badge">${escapeHtml(device.type)}</span></td>
                            <td><a href="http://${escapeHtml(device.ip)}" target="_blank">${escapeHtml(device.ip)}</a></td>
                            <td>${escapeHtml(device.mac)}</td>
                            <td>${escapeHtml(device.fw)}</td>
                            <td>
                                <span class="auth-badge ${device.auth ? 'auth-enabled' : 'auth-disabled'}">
                                    ${device.auth ? 'Aan' : 'Uit'}
                                </span>
                            </td>
                        </tr>
                    `).join('')}
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
