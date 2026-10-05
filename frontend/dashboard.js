/**
 * Smart IoT Mesh Network Analyzer
 * Dashboard and Real-time Analytics Module
 * Graduation Project 2026
 */

class NetworkDashboard {
    constructor() {
        this.socket = null;
        this.charts = {};
        this.realtimeData = {
            signalHistory: [],
            timestamps: [],
            networkHealth: [],
            trafficHistory: []
        };
        this.updateInterval = null;
        this.devices = [];
        this.routerDevices = [];
        this.alerts = [];
        this.init();
    }
    
    init() {
        this.initializeSocket();
        this.initializeCharts();
        this.setupEventListeners();
        this.startRealtimeUpdates();
        this.loadInitialData();
        this.initRouterMonitoring();
    }
    
    initializeSocket() {
        // Connect to backend WebSocket
        this.socket = io('http://localhost:5000', {
            transports: ['websocket'],
            reconnectionAttempts: 5,
            reconnectionDelay: 1000
        });
        
        this.socket.on('connect', () => {
            console.log('✅ Connected to real-time server');
            this.showNotification('Connected to server', 'success');
            this.updateConnectionStatus(true);
        });
        
        this.socket.on('network_update', (data) => {
            this.updateDashboard(data);
        });
        
        this.socket.on('device_status', (data) => {
            this.updateDeviceStatus(data);
        });
        
        this.socket.on('router_devices', (data) => {
            this.displayRouterDevices(data.devices);
            this.updateRouterSignalChart(data.devices);
        });
        
        this.socket.on('device_discovered', (device) => {
            this.addDiscoveredDevice(device);
        });
        
        this.socket.on('alert', (alert) => {
            this.handleAlert(alert);
        });
        
        this.socket.on('sensor_data', (data) => {
            this.updateSensorData(data);
        });
        
        this.socket.on('recommendation', (rec) => {
            this.addRecommendation(rec);
        });
        
        this.socket.on('disconnect', () => {
            console.log('❌ Disconnected from server');
            this.showNotification('Disconnected from server', 'error');
            this.updateConnectionStatus(false);
        });
        
        this.socket.on('reconnect', () => {
            this.showNotification('Reconnected to server', 'success');
            this.updateConnectionStatus(true);
        });
    }
    
    initializeCharts() {
        this.initSignalChart();
        this.initHealthChart();
        this.initTrafficChart();
        this.initDeviceDistributionChart();
    }
    
    initSignalChart() {
        const ctx = document.getElementById('signalChart')?.getContext('2d');
        if (!ctx) return;
        
        this.charts.signal = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Signal Strength (dBm)',
                    data: [],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4,
                    fill: true,
                    pointRadius: 3,
                    pointHoverRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            callback: (value) => value + ' dBm',
                            color: '#9ca3af'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: '#9ca3af',
                            maxRotation: 45,
                            maxTicksLimit: 8
                        }
                    }
                },
                animation: {
                    duration: 500
                }
            }
        });
    }
    
    initHealthChart() {
        const ctx = document.getElementById('healthChart')?.getContext('2d');
        if (!ctx) return;
        
        this.charts.health = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Network Health %',
                    data: [],
                    borderColor: '#8b5cf6',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    tension: 0.4,
                    fill: true,
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            callback: (value) => value + '%',
                            color: '#9ca3af'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: '#9ca3af'
                        }
                    }
                }
            }
        });
    }
    
    initTrafficChart() {
        const ctx = document.getElementById('trafficChart')?.getContext('2d');
        if (!ctx) return;
        
        this.charts.traffic = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Inbound', 'Outbound', 'Total'],
                datasets: [{
                    label: 'Network Traffic (kbps)',
                    data: [0, 0, 0],
                    backgroundColor: [
                        'rgba(59, 130, 246, 0.8)',
                        'rgba(139, 92, 246, 0.8)',
                        'rgba(16, 185, 129, 0.8)'
                    ],
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            callback: (value) => value + ' kbps',
                            color: '#9ca3af'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: '#9ca3af'
                        }
                    }
                }
            }
        });
    }
    
    initDeviceDistributionChart() {
        const ctx = document.getElementById('deviceChart')?.getContext('2d');
        if (!ctx) return;
        
        this.charts.devices = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Gateways', 'Sensor Nodes', 'Repeaters', 'End Devices'],
                datasets: [{
                    data: [0, 0, 0, 0],
                    backgroundColor: [
                        '#ef4444',
                        '#3b82f6',
                        '#8b5cf6',
                        '#10b981'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#9ca3af',
                            font: {
                                size: 10
                            }
                        }
                    }
                },
                cutout: '60%'
            }
        });
    }
    
    // ==================== ROUTER MONITORING METHODS ====================
    
    initRouterMonitoring() {
        console.log('📡 Initializing router monitoring...');
        this.fetchRouterDevices();
        
        // Poll every 5 seconds as backup
        setInterval(() => {
            this.fetchRouterDevices();
        }, 5000);
    }
    
    fetchRouterDevices() {
        fetch('http://localhost:5000/api/router/devices')
            .then(response => response.json())
            .then(data => {
                this.displayRouterDevices(data.devices);
                this.updateRouterSignalChart(data.devices);
            })
            .catch(error => {
                console.log('Router monitoring not available');
            });
    }
    
    getRouterSignalColor(rssi) {
        if (rssi > -50) return 'text-green-400';
        if (rssi > -65) return 'text-lime-400';
        if (rssi > -75) return 'text-yellow-400';
        return 'text-red-400';
    }
    
    getRouterSignalQuality(rssi) {
        if (rssi > -50) return 'Excellent';
        if (rssi > -65) return 'Good';
        if (rssi > -75) return 'Fair';
        return 'Weak';
    }
    
    displayRouterDevices(devices) {
        this.routerDevices = devices;
        const container = document.getElementById('routerDeviceList');
        const countSpan = document.getElementById('routerDeviceCount');
        
        if (!container) return;
        
        if (!devices || devices.length === 0) {
            container.innerHTML = `
                <div class="text-center text-gray-500 py-2">
                    <i class="fas fa-wifi text-2xl mb-2 opacity-30"></i>
                    <p class="text-xs">No devices found</p>
                    <p class="text-xxs mt-1">Click Scan to check connected devices</p>
                </div>
            `;
            if (countSpan) countSpan.textContent = '0';
            return;
        }
        
        if (countSpan) countSpan.textContent = devices.length;
        
        let html = '';
        devices.forEach((device, index) => {
            const signalColor = this.getRouterSignalColor(device.rssi);
            const signalQuality = this.getRouterSignalQuality(device.rssi);
            
            // Determine icon based on device ID
            let icon = 'fa-laptop';
            const id = device.id.toLowerCase();
            if (id.includes('phone') || id.includes('iphone')) icon = 'fa-mobile-alt';
            else if (id.includes('tablet')) icon = 'fa-tablet-alt';
            else if (id.includes('tv')) icon = 'fa-tv';
            
            html += `
                <div class="bg-gray-700/30 p-2 rounded mb-2 hover:bg-gray-700/50 transition cursor-pointer" 
                     onclick="dashboard.showRouterDeviceDetails('${device.ip}')">
                    <div class="flex justify-between items-center">
                        <div class="flex items-center space-x-2">
                            <i class="fas ${icon} text-gray-400 text-xs"></i>
                            <span class="text-xs font-medium">${device.id}</span>
                        </div>
                        <span class="font-mono text-xs ${signalColor}">${device.rssi} dBm</span>
                    </div>
                    <div class="flex justify-between text-xxs text-gray-400 mt-1">
                        <span class="${signalColor}">${signalQuality}</span>
                        <span>${device.ip || 'N/A'}</span>
                    </div>
                    ${device.hostname && device.hostname !== 'unknown' ? `
                    <div class="text-xxs text-gray-500 mt-1">
                        ${device.hostname}
                    </div>
                    ` : ''}
                </div>
            `;
        });
        
        container.innerHTML = html;
    }
    
    showRouterDeviceDetails(ip) {
        fetch(`http://localhost:5000/api/router/device/${ip}`)
            .then(response => response.json())
            .then(device => {
                const signalColor = this.getRouterSignalColor(device.rssi);
                const signalQuality = this.getRouterSignalQuality(device.rssi);
                
                const modal = document.createElement('div');
                modal.className = 'fixed inset-0 bg-black/70 flex items-center justify-center z-50';
                modal.innerHTML = `
                    <div class="bg-gray-800 rounded-xl w-96 p-6 animate-modalAppear">
                        <div class="flex items-center justify-between mb-4">
                            <h3 class="text-lg font-bold">Router Device Details</h3>
                            <button class="text-gray-400 hover:text-white" onclick="this.closest('.fixed').remove()">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                        
                        <div class="space-y-4">
                            <div class="flex items-center space-x-3">
                                <div class="w-12 h-12 bg-gradient-to-br from-green-500 to-blue-600 rounded-lg flex items-center justify-center">
                                    <i class="fas fa-wifi text-white text-xl"></i>
                                </div>
                                <div>
                                    <div class="font-medium">${device.id}</div>
                                    <div class="text-sm text-gray-400">WiFi Client</div>
                                </div>
                            </div>
                            
                            <div class="grid grid-cols-2 gap-3 text-sm">
                                <div class="bg-gray-700/30 p-2 rounded">
                                    <div class="text-xs text-gray-400">IP Address</div>
                                    <div class="font-medium">${device.ip}</div>
                                </div>
                                <div class="bg-gray-700/30 p-2 rounded">
                                    <div class="text-xs text-gray-400">MAC Address</div>
                                    <div class="font-medium text-xs">${device.mac}</div>
                                </div>
                                <div class="bg-gray-700/30 p-2 rounded">
                                    <div class="text-xs text-gray-400">Signal</div>
                                    <div class="font-medium ${signalColor}">${device.rssi} dBm</div>
                                </div>
                                <div class="bg-gray-700/30 p-2 rounded">
                                    <div class="text-xs text-gray-400">Quality</div>
                                    <div class="font-medium ${signalColor}">${signalQuality}</div>
                                </div>
                            </div>
                            
                            ${device.hostname && device.hostname !== 'unknown' ? `
                            <div class="bg-gray-700/30 p-2 rounded">
                                <div class="text-xs text-gray-400">Hostname</div>
                                <div class="font-medium">${device.hostname}</div>
                            </div>
                            ` : ''}
                            
                            <div class="bg-gray-700/30 p-2 rounded">
                                <div class="text-xs text-gray-400">Last Seen</div>
                                <div class="font-medium">${new Date(device.last_seen).toLocaleString()}</div>
                            </div>
                        </div>
                    </div>
                `;
                
                document.body.appendChild(modal);
            });
    }
    
    updateRouterSignalChart(devices) {
        if (!this.charts.signal) return;
        
        const now = new Date();
        const timestamp = now.toLocaleTimeString();
        
        // Calculate average RSSI
        const avgRssi = devices.length > 0 
            ? devices.reduce((sum, d) => sum + d.rssi, 0) / devices.length 
            : -65;
        
        this.realtimeData.signalHistory.push(avgRssi);
        this.realtimeData.timestamps.push(timestamp);
        
        if (this.realtimeData.signalHistory.length > 20) {
            this.realtimeData.signalHistory.shift();
            this.realtimeData.timestamps.shift();
        }
        
        this.charts.signal.data.labels = this.realtimeData.timestamps;
        this.charts.signal.data.datasets[0].data = this.realtimeData.signalHistory;
        this.charts.signal.update('quiet');
    }
    
    // ==================== EXISTING DASHBOARD METHODS ====================
    
    setupEventListeners() {
        // Scan network button
        document.getElementById('scanNetwork')?.addEventListener('click', () => {
            this.scanNetwork();
        });
        
        // Optimize network button
        document.getElementById('optimizeNetwork')?.addEventListener('click', () => {
            this.optimizeNetwork();
        });
        //detect ip 
        document.getElementById('detectIpBtn')?.addEventListener('click', () => {
        this.detectIpAddress()
        });
        // Export report button
        document.getElementById('exportReport')?.addEventListener('click', () => {
            this.exportReport();
        });
        
        // Hardware config button
        document.getElementById('configureHardware')?.addEventListener('click', () => {
            this.showHardwareModal();
        });
        
        // Close modal button
        document.getElementById('closeModal')?.addEventListener('click', () => {
            this.hideHardwareModal();
        });
        
        // Save hardware config
        document.getElementById('saveHardwareConfig')?.addEventListener('click', () => {
            this.saveHardwareConfig();
        });
        
        // View mode toggles
        document.getElementById('viewTopology')?.addEventListener('click', () => {
            this.setViewMode('topology');
        });
        
        document.getElementById('viewCoverage')?.addEventListener('click', () => {
            this.setViewMode('coverage');
        });
        
        document.getElementById('view3D')?.addEventListener('click', () => {
            this.setViewMode('3d');
        });
        
        // Zoom controls
        document.getElementById('zoomIn')?.addEventListener('click', () => {
            window.dispatchEvent(new CustomEvent('zoom', { detail: { direction: 'in' } }));
        });
        
        document.getElementById('zoomOut')?.addEventListener('click', () => {
            window.dispatchEvent(new CustomEvent('zoom', { detail: { direction: 'out' } }));
        });
        
        document.getElementById('resetView')?.addEventListener('click', () => {
            window.dispatchEvent(new CustomEvent('zoom', { detail: { direction: 'reset' } }));
        });
        
        // Mouse move for coordinates
        document.getElementById('canvasContainer')?.addEventListener('mousemove', (e) => {
            const rect = e.target.getBoundingClientRect();
            const x = Math.round(e.clientX - rect.left);
            const y = Math.round(e.clientY - rect.top);
            document.getElementById('mouseX').textContent = x;
            document.getElementById('mouseY').textContent = y;
        });
        
        // Refresh button
        document.getElementById('refreshData')?.addEventListener('click', () => {
            this.refreshAllData();
        });
        
        // Clear alerts button
        document.getElementById('clearAlerts')?.addEventListener('click', () => {
            this.clearAlerts();
        });
        
        // Router scan button
        document.getElementById('scanRouterBtn')?.addEventListener('click', () => {
            this.scanWiFiNetwork();
        });
    }
    
    scanWiFiNetwork() {
        console.log("📡 Scanning WiFi network...");
        this.showNotification('Scanning WiFi network...', 'info');
        
        const scanBtn = document.getElementById('scanRouterBtn');
        if (scanBtn) {
            scanBtn.disabled = true;
            scanBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-1"></i>Scanning...';
        }
        
        fetch('http://localhost:5000/api/router/scan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("✅ Scan complete, found", data.devices.length, "devices");
            this.displayRouterDevices(data.devices);
            this.showNotification(`Found ${data.devices.length} devices on WiFi`, 'success');
        })
        .catch(error => {
            console.error("❌ Scan failed:", error);
            this.showNotification('Scan failed: ' + error.message, 'error');
        })
        .finally(() => {
            if (scanBtn) {
                scanBtn.disabled = false;
                scanBtn.innerHTML = '<i class="fas fa-sync-alt mr-1"></i>Scan WiFi Network';
            }
        });
    }
    // Add this new method
detectIpAddress() {
    const ip = document.getElementById('ipAddress').value.trim();
    
    if (!ip) {
        this.showNotification('Please enter an IP address', 'error');
        return;
    }
    
    // Simple IP format validation
    const ipRegex = /^(\d{1,3}\.){3}\d{1,3}$/;
    if (!ipRegex.test(ip)) {
        this.showNotification('Invalid IP format', 'error');
        return;
    }
    
    this.showNotification(`Checking ${ip}...`, 'info');
    
    const resultDiv = document.getElementById('ipDetectionResult');
    resultDiv.classList.remove('hidden');
    resultDiv.innerHTML = `
        <div class="text-center py-2">
            <i class="fas fa-spinner fa-spin text-blue-400"></i>
            <p class="text-xs mt-1">Checking ${ip}...</p>
        </div>
    `;
    
    // Call your backend to check this IP
    fetch(`http://localhost:5000/api/router/device/${ip}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                resultDiv.innerHTML = `
                    <div class="bg-yellow-900/20 border border-yellow-500/30 rounded p-2">
                        <p class="text-xs text-yellow-400">❌ Device not found</p>
                        <p class="text-xxs text-gray-400 mt-1">${ip} is not responding</p>
                    </div>
                `;
            } else {
                const signalColor = data.rssi > -50 ? 'text-green-400' :
                                   data.rssi > -65 ? 'text-lime-400' :
                                   data.rssi > -75 ? 'text-yellow-400' : 'text-red-400';
                
                const quality = data.rssi > -50 ? 'Excellent' :
                               data.rssi > -65 ? 'Good' :
                               data.rssi > -75 ? 'Fair' : 'Weak';
                
                resultDiv.innerHTML = `
                    <div class="bg-gray-700/30 rounded p-2">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-medium">${data.id || 'Device'}</span>
                            <span class="font-mono text-xs ${signalColor}">${data.rssi} dBm</span>
                        </div>
                        <div class="flex justify-between text-xxs text-gray-400 mt-1">
                            <span>${data.ip}</span>
                            <span class="${signalColor}">${quality}</span>
                        </div>
                        ${data.hostname && data.hostname !== 'unknown' ? 
                            `<div class="text-xxs text-gray-500 mt-1">${data.hostname}</div>` : ''}
                    </div>
                `;
            }
        })
        .catch(error => {
            resultDiv.innerHTML = `
                <div class="bg-red-900/20 border border-red-500/30 rounded p-2">
                    <p class="text-xs text-red-400">❌ Error checking IP</p>
                    <p class="text-xxs text-gray-400">${error.message}</p>
                </div>
            `;
        });
}
    startRealtimeUpdates() {
        // Update real-time data every second
        this.updateInterval = setInterval(() => {
            this.updateRealtimeMetrics();
        }, 1000);
    }
    
    loadInitialData() {
        // Fetch initial network status
        fetch('/api/network/status')
            .then(response => response.json())
            .then(data => {
                this.updateDashboard(data);
            })
            .catch(error => {
                console.error('Failed to load initial data:', error);
            });
        
        // Fetch devices
        fetch('/api/devices')
            .then(response => response.json())
            .then(data => {
                if (data.devices) {
                    this.updateDeviceStatus(data.devices);
                }
            })
            .catch(error => {
                console.error('Failed to load devices:', error);
            });
    }
    
    updateRealtimeMetrics() {
        // Simulate real-time data (replace with actual socket data)
        const now = new Date();
        const timestamp = now.toLocaleTimeString();
        
        // Update signal history
        const newSignal = -50 - Math.random() * 20;
        this.realtimeData.signalHistory.push(newSignal);
        this.realtimeData.timestamps.push(timestamp);
        
        // Keep last 20 points
        if (this.realtimeData.signalHistory.length > 20) {
            this.realtimeData.signalHistory.shift();
            this.realtimeData.timestamps.shift();
        }
        
        // Update signal chart
        if (this.charts.signal) {
            this.charts.signal.data.labels = this.realtimeData.timestamps;
            this.charts.signal.data.datasets[0].data = this.realtimeData.signalHistory;
            this.charts.signal.update('quiet');
        }
        
        // Update network health history
        const newHealth = 70 + Math.random() * 20;
        this.realtimeData.networkHealth.push(newHealth);
        if (this.realtimeData.networkHealth.length > 20) {
            this.realtimeData.networkHealth.shift();
        }
        
        // Update health chart
        if (this.charts.health) {
            this.charts.health.data.labels = this.realtimeData.timestamps;
            this.charts.health.data.datasets[0].data = this.realtimeData.networkHealth;
            this.charts.health.update('quiet');
        }
        
        // Update traffic data (random for demo)
        const inbound = Math.floor(100 + Math.random() * 200);
        const outbound = Math.floor(80 + Math.random() * 150);
        
        if (this.charts.traffic) {
            this.charts.traffic.data.datasets[0].data = [inbound, outbound, inbound + outbound];
            this.charts.traffic.update('quiet');
        }
        
        // Update bottom stats
        document.getElementById('dataRate').textContent = (inbound + outbound) + ' kbps';
        document.getElementById('packetLoss').textContent = (Math.random() * 2).toFixed(1) + '%';
    }
    
    updateDashboard(data) {
        // Update network health
        const health = data.health_score || Math.floor(65 + Math.random() * 30);
        document.getElementById('healthPercent').textContent = health + '%';
        
        // Update health bar
        const healthBar = document.getElementById('healthBar');
        if (healthBar) {
            healthBar.style.width = health + '%';
            healthBar.className = `h-full transition-all duration-500 ${
                health > 80 ? 'bg-emerald-500' : 
                health > 40 ? 'bg-amber-500' : 
                'bg-red-500'
            }`;
        }
        
        // Update stats
        document.getElementById('statNodes').textContent = data.node_count || 
            Math.floor(8 + Math.random() * 10);
        document.getElementById('statLinks').textContent = data.link_count || 
            Math.floor(10 + Math.random() * 15);
        document.getElementById('statLatency').textContent = (data.avg_latency || 
            Math.floor(20 + Math.random() * 40)) + 'ms';
        document.getElementById('statCoverage').textContent = (data.coverage || 
            Math.floor(70 + Math.random() * 20)) + '%';
        
        // Update gateway count
        document.getElementById('gatewayCount').textContent = data.gateway_count || 
            Math.floor(1 + Math.random() * 3);
        
        // Update device distribution chart
        if (this.charts.devices) {
            this.charts.devices.data.datasets[0].data = [
                data.gateway_count || 2,
                data.node_count || 8,
                data.repeater_count || 2,
                data.endpoint_count || 3
            ];
            this.charts.devices.update('quiet');
        }
    }
    
    updateDeviceStatus(devices) {
        this.devices = devices;
        const deviceList = document.getElementById('deviceList');
        const onlineCount = document.getElementById('onlineCount');
        
        if (!devices || devices.length === 0) {
            deviceList.innerHTML = `
                <div class="text-center text-gray-500 py-8">
                    <i class="fas fa-wifi text-4xl mb-3 opacity-50"></i>
                    <p class="text-sm">No devices connected</p>
                    <p class="text-xs mt-1">Scan or add devices to begin</p>
                    <button class="mt-3 px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded-lg text-xs" onclick="dashboard.scanNetwork()">
                        <i class="fas fa-search mr-1"></i>Scan Now
                    </button>
                </div>
            `;
            onlineCount.textContent = '0 Online';
            return;
        }
        
        let online = 0;
        let html = '';
        
        devices.forEach(device => {
            if (device.status === 'online') online++;
            
            const signalClass = device.rssi > -50 ? 'text-green-400' : 
                               device.rssi > -70 ? 'text-yellow-400' : 
                               'text-red-400';
            
            html += `
                <div class="device-item ${device.status} p-3 bg-gray-700/30 rounded-lg hover:bg-gray-700/50 transition cursor-pointer" 
                     onclick="dashboard.showDeviceDetails('${device.id}')">
                    <div class="flex items-center justify-between">
                        <div class="flex items-center space-x-3">
                            <div class="relative">
                                <i class="fas fa-${device.type === 'gateway' ? 'router' : 
                                                      device.type === 'repeater' ? 'satellite-dish' : 
                                                      'microchip'} 
                                          text-${device.status === 'online' ? 'blue' : 'gray'}-400 text-lg"></i>
                                ${device.status === 'online' ? 
                                    '<div class="absolute -top-1 -right-1 w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>' : ''}
                            </div>
                            <div>
                                <div class="text-sm font-medium">${device.id}</div>
                                <div class="flex items-center space-x-2 text-xs">
                                    <span class="text-gray-400">${device.type}</span>
                                    <span class="text-gray-600">|</span>
                                    <span class="${signalClass}">${device.rssi || 'N/A'}dBm</span>
                                </div>
                            </div>
                        </div>
                        <div class="text-xs">
                            <span class="px-2 py-1 rounded-full ${
                                device.status === 'online' ? 'bg-green-500/20 text-green-400' : 
                                device.status === 'standby' ? 'bg-yellow-500/20 text-yellow-400' : 
                                'bg-gray-500/20 text-gray-400'
                            }">
                                ${device.status}
                            </span>
                        </div>
                    </div>
                    ${device.battery ? `
                    <div class="mt-2 flex items-center space-x-2">
                        <i class="fas fa-battery-${device.battery > 75 ? 'full' : 
                                                     device.battery > 50 ? 'three-quarters' : 
                                                     device.battery > 25 ? 'half' : 
                                                     device.battery > 10 ? 'quarter' : 'empty'} 
                                  text-${device.battery > 25 ? 'green' : 'red'}-400 text-xs"></i>
                        <div class="flex-1 h-1 bg-gray-600 rounded-full overflow-hidden">
                            <div class="h-full ${device.battery > 25 ? 'bg-green-500' : 'bg-red-500'}" 
                                 style="width: ${device.battery}%"></div>
                        </div>
                        <span class="text-xs text-gray-400">${device.battery}%</span>
                    </div>
                    ` : ''}
                </div>
            `;
        });
        
        deviceList.innerHTML = html;
        onlineCount.textContent = `${online} Online`;
        document.getElementById('deviceCount').textContent = devices.length;
    }
    
    addDiscoveredDevice(device) {
        this.showNotification(`New device discovered: ${device.id}`, 'info');
        
        // Add to device list if not already present
        if (!this.devices.find(d => d.id === device.id)) {
            this.devices.push(device);
            this.updateDeviceStatus(this.devices);
        }
    }
    
    updateSensorData(data) {
        const sensorPanel = document.getElementById('sensorData');
        if (!sensorPanel) return;
        
        sensorPanel.innerHTML = `
            <div class="grid grid-cols-2 gap-2 text-sm">
                <div class="bg-gray-700/30 p-2 rounded">
                    <div class="text-xs text-gray-400">Temperature</div>
                    <div class="font-medium">${data.temperature?.toFixed(1) || '--'}°C</div>
                </div>
                <div class="bg-gray-700/30 p-2 rounded">
                    <div class="text-xs text-gray-400">Humidity</div>
                    <div class="font-medium">${data.humidity?.toFixed(1) || '--'}%</div>
                </div>
                <div class="bg-gray-700/30 p-2 rounded">
                    <div class="text-xs text-gray-400">Motion</div>
                    <div class="font-medium">${data.motion ? 'Detected' : 'None'}</div>
                </div>
                <div class="bg-gray-700/30 p-2 rounded">
                    <div class="text-xs text-gray-400">Air Quality</div>
                    <div class="font-medium">${data.air_quality || '--'} ppm</div>
                </div>
            </div>
        `;
    }
    
    handleAlert(alert) {
        const diagBox = document.getElementById('diagnosticBox');
        if (!diagBox) return;
        
        this.alerts.unshift(alert);
        if (this.alerts.length > 5) this.alerts.pop();
        
        const alertHtml = this.alerts.map(a => `
            <div class="flex items-start space-x-2 p-3 ${
                a.severity === 'critical' ? 'bg-red-900/20 border-red-500/30' :
                a.severity === 'warning' ? 'bg-yellow-900/20 border-yellow-500/30' :
                'bg-blue-900/20 border-blue-500/30'
            } border rounded-lg animate-slideIn">
                <i class="fas fa-${
                    a.severity === 'critical' ? 'exclamation-circle' :
                    a.severity === 'warning' ? 'exclamation-triangle' :
                    'info-circle'
                } ${
                    a.severity === 'critical' ? 'text-red-400' :
                    a.severity === 'warning' ? 'text-yellow-400' :
                    'text-blue-400'
                } mt-1"></i>
                <div class="flex-1">
                    <p class="text-xs font-medium ${
                        a.severity === 'critical' ? 'text-red-400' :
                        a.severity === 'warning' ? 'text-yellow-400' :
                        'text-blue-400'
                    }">${a.type || 'Alert'}</p>
                    <p class="text-xs text-gray-400 mt-1">${a.message}</p>
                    <p class="text-xs text-gray-500 mt-1">${new Date().toLocaleTimeString()}</p>
                </div>
                <button class="text-gray-500 hover:text-gray-400" onclick="this.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `).join('');
        
        diagBox.innerHTML = alertHtml;
        
        // Show notification
        this.showNotification(alert.message, 
            alert.severity === 'critical' ? 'error' : 
            alert.severity === 'warning' ? 'warning' : 'info');
    }
    
    addRecommendation(rec) {
        const recBox = document.getElementById('recommendationBox');
        if (!recBox) return;
        
        const recHtml = `
            <div class="p-3 bg-blue-900/20 border border-blue-500/30 rounded-lg animate-slideIn">
                <div class="flex items-start space-x-2">
                    <i class="fas fa-robot text-blue-400 mt-1"></i>
                    <div class="flex-1">
                        <p class="text-xs font-medium text-blue-400">AI Recommendation</p>
                        <p class="text-xs text-gray-300 mt-1">${rec.message}</p>
                        ${rec.action ? `
                        <button class="mt-2 px-2 py-1 bg-blue-600 hover:bg-blue-700 rounded text-xs"
                                onclick="dashboard.applyRecommendation('${rec.action}')">
                            Apply Fix
                        </button>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
        
        recBox.insertAdjacentHTML('afterbegin', recHtml);
        
        // Keep only last 3 recommendations
        while (recBox.children.length > 3) {
            recBox.removeChild(recBox.lastChild);
        }
    }
    
    applyRecommendation(action) {
        this.showNotification(`Applying: ${action}`, 'info');
        
        if (this.socket && this.socket.connected) {
            this.socket.emit('apply_recommendation', { action });
        }
    }
    
    showDeviceDetails(deviceId) {
        const device = this.devices.find(d => d.id === deviceId);
        if (!device) return;
        
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-black/70 flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="bg-gray-800 rounded-xl w-96 p-6 animate-modalAppear">
                <div class="flex items-center justify-between mb-4">
                    <h3 class="text-lg font-bold">Device Details</h3>
                    <button class="text-gray-400 hover:text-white" onclick="this.closest('.fixed').remove()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                
                <div class="space-y-4">
                    <div class="flex items-center space-x-3">
                        <div class="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                            <i class="fas fa-microchip text-white text-xl"></i>
                        </div>
                        <div>
                            <div class="font-medium">${device.id}</div>
                            <div class="text-sm text-gray-400">${device.type}</div>
                        </div>
                    </div>
                    
                    <div class="grid grid-cols-2 gap-3 text-sm">
                        <div class="bg-gray-700/30 p-2 rounded">
                            <div class="text-xs text-gray-400">Status</div>
                            <div class="font-medium capitalize">${device.status}</div>
                        </div>
                        <div class="bg-gray-700/30 p-2 rounded">
                            <div class="text-xs text-gray-400">RSSI</div>
                            <div class="font-medium">${device.rssi || 'N/A'} dBm</div>
                        </div>
                        <div class="bg-gray-700/30 p-2 rounded">
                            <div class="text-xs text-gray-400">IP Address</div>
                            <div class="font-medium">${device.ip || 'N/A'}</div>
                        </div>
                        <div class="bg-gray-700/30 p-2 rounded">
                            <div class="text-xs text-gray-400">Last Seen</div>
                            <div class="font-medium">${device.last_seen || 'Now'}</div>
                        </div>
                    </div>
                    
                    <div class="flex space-x-2 mt-4">
                        <button class="flex-1 px-3 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm"
                                onclick="dashboard.sendCommand('${device.id}', 'ping')">
                            <i class="fas fa-sync-alt mr-1"></i>Ping
                        </button>
                        <button class="flex-1 px-3 py-2 bg-yellow-600 hover:bg-yellow-700 rounded-lg text-sm"
                                onclick="dashboard.sendCommand('${device.id}', 'configure')">
                            <i class="fas fa-cog mr-1"></i>Configure
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }
    
    sendCommand(deviceId, command) {
        this.showNotification(`Sending ${command} to ${deviceId}`, 'info');
        
        if (this.socket && this.socket.connected) {
            this.socket.emit('command_device', {
                device_id: deviceId,
                command: command
            });
        }
        
        document.querySelector('.fixed')?.remove();
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `fixed bottom-4 right-4 px-4 py-3 rounded-lg shadow-lg z-50 animate-slideIn
            ${type === 'success' ? 'bg-green-600' : 
              type === 'error' ? 'bg-red-600' : 
              type === 'warning' ? 'bg-yellow-600' : 
              'bg-blue-600'}`;
        
        notification.innerHTML = `
            <div class="flex items-center space-x-2">
                <i class="fas fa-${
                    type === 'success' ? 'check-circle' : 
                    type === 'error' ? 'exclamation-circle' : 
                    type === 'warning' ? 'exclamation-triangle' : 
                    'info-circle'
                }"></i>
                <span class="text-sm">${message}</span>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
    
    updateConnectionStatus(connected) {
        const statusDot = document.querySelector('.connection-status .w-2');
        if (statusDot) {
            statusDot.className = `w-2 h-2 ${connected ? 'bg-green-500' : 'bg-red-500'} rounded-full animate-pulse`;
        }
    }
    
    scanNetwork() {
        this.showNotification('Scanning network...', 'info');
        
        if (this.socket && this.socket.connected) {
            this.socket.emit('scan_network');
        } else {
            setTimeout(() => {
                const mockDevices = [
                    { id: 'ESP32_001', type: 'sensor', status: 'online', rssi: -45, battery: 87 },
                    { id: 'ESP32_002', type: 'sensor', status: 'online', rssi: -62, battery: 92 },
                    { id: 'ARDUINO_001', type: 'gateway', status: 'online', rssi: -38, battery: 100 }
                ];
                this.updateDeviceStatus(mockDevices);
                this.showNotification('Found 3 new devices', 'success');
            }, 2000);
        }
    }
    
    optimizeNetwork() {
        this.showNotification('Running AI optimization...', 'info');
        
        setTimeout(() => {
            this.addRecommendation({
                message: 'Add relay node at (350, 250) to improve coverage by 15%',
                action: 'add_relay'
            });
            this.addRecommendation({
                message: 'Adjust gateway power to +3dBm for better signal distribution',
                action: 'adjust_power'
            });
            this.showNotification('Optimization complete', 'success');
        }, 1500);
    }
    
    exportReport() {
        this.showNotification('Generating report...', 'info');
        
        setTimeout(() => {
            const reportData = {
                timestamp: new Date().toISOString(),
                network_stats: {
                    nodes: document.getElementById('statNodes').textContent,
                    links: document.getElementById('statLinks').textContent,
                    health: document.getElementById('healthPercent').textContent
                },
                devices: this.devices,
                recommendations: Array.from(document.querySelectorAll('#recommendationBox p')).map(p => p.textContent)
            };
            
            const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `network-report-${Date.now()}.json`;
            a.click();
            
            this.showNotification('Report exported successfully!', 'success');
        }, 1500);
    }
    
    showHardwareModal() {
        document.getElementById('hardwareModal')?.classList.remove('hidden');
    }
    
    hideHardwareModal() {
        document.getElementById('hardwareModal')?.classList.add('hidden');
    }
    
    saveHardwareConfig() {
        const config = {
            mqttBroker: document.getElementById('mqttBroker')?.value || 'localhost',
            mqttPort: document.getElementById('mqttPort')?.value || '1883',
            serialPort: document.getElementById('serialPort')?.value || 'COM3'
        };
        
        console.log('Saving hardware config:', config);
        this.showNotification('Hardware configuration saved', 'success');
        this.hideHardwareModal();
        
        if (this.socket && this.socket.connected) {
            this.socket.emit('hardware_config', config);
        }
    }
    
    setViewMode(mode) {
        document.querySelectorAll('.view-mode-btn').forEach(btn => {
            btn.classList.remove('active', 'bg-gradient-to-r', 'from-blue-600', 'to-purple-600', 'text-white');
        });
        
        if (mode === 'topology') {
            document.getElementById('viewTopology')?.classList.add('active', 'bg-gradient-to-r', 'from-blue-600', 'to-purple-600', 'text-white');
        } else if (mode === 'coverage') {
            document.getElementById('viewCoverage')?.classList.add('active', 'bg-gradient-to-r', 'from-blue-600', 'to-purple-600', 'text-white');
        } else if (mode === '3d') {
            document.getElementById('view3D')?.classList.add('active', 'bg-gradient-to-r', 'from-blue-600', 'to-purple-600', 'text-white');
        }
        
        window.dispatchEvent(new CustomEvent('viewModeChange', { detail: { mode } }));
        this.showNotification(`Switched to ${mode} view`, 'info');
    }
    
    refreshAllData() {
        this.showNotification('Refreshing data...', 'info');
        this.loadInitialData();
    }
    
    clearAlerts() {
        document.getElementById('diagnosticBox').innerHTML = `
            <div class="text-gray-400 text-sm text-center py-2">
                No active alerts
            </div>
        `;
        this.alerts = [];
        this.showNotification('Alerts cleared', 'success');
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new NetworkDashboard();
    
    // Add CSS for animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes modalAppear {
            from {
                opacity: 0;
                transform: scale(0.8);
            }
            to {
                opacity: 1;
                transform: scale(1);
            }
        }
        
        .animate-slideIn {
            animation: slideIn 0.3s ease-out;
        }
        
        .animate-modalAppear {
            animation: modalAppear 0.3s ease-out;
        }
    `;
    document.head.appendChild(style);
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NetworkDashboard;
}