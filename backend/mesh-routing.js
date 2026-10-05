/**
 * =====================================================
 * MESH ROUTING & ADVANCED FEATURES 
 * =====================================================
 * This module provides advanced mesh networking capabilities:
 * - Multiple path finding
 * - Path visualization
 * =====================================================
 */

//GLOBAL VARIABLES 
let selectedNodeForFailure = null;
let dragStarted = false;

// FIND ALL POSSIBLE PATHS 
function findAllPaths(startId, endId, maxPaths = 3) {
    const start = nodes.find(n => n.id === startId);
    const end = nodes.find(n => n.id === endId);
    
    if (!start || !end || !start.active || !end.active) return [];
    
    const paths = [];
    const visited = new Set();
    
    function dfs(currentNode, path) {
        if (path.length > 10) return;
        if (currentNode === endId) {
            paths.push([...path]);
            return;
        }
        
        visited.add(currentNode);
        
        if (window.links && window.links.length > 0) {
            window.links.forEach(link => {
                if (link.source === currentNode || link.target === currentNode) {
                    const neighbor = link.source === currentNode ? link.target : link.source;
                    const neighborNode = nodes.find(n => n.id === neighbor);
                    
                    if (neighborNode && neighborNode.active && !visited.has(neighbor)) {
                        dfs(neighbor, [...path, neighbor]);
                    }
                }
            });
        }
        
        visited.delete(currentNode);
    }
    
    dfs(startId, [startId]);
    return paths.sort((a, b) => a.length - b.length).slice(0, maxPaths);
}

// ==================== FIND PATH WITH REROUTING ====================
function findPathWithRerouting(startId, endId, failedNodeId = null) {
    const start = nodes.find(n => n.id === startId);
    const end = nodes.find(n => n.id === endId);
    
    if (!start || !end || !start.active || !end.active) return null;
    
    const queue = [{ node: startId, path: [startId] }];
    const visited = new Set([startId]);
    
    while (queue.length > 0) {
        const current = queue.shift();
        
        if (current.node === endId) {
            return current.path;
        }
        
        if (window.links && window.links.length > 0) {
            window.links.forEach(link => {
                if (link.source === current.node || link.target === current.node) {
                    const neighbor = link.source === current.node ? link.target : link.source;
                    
                    if (failedNodeId && neighbor === failedNodeId) return;
                    
                    const neighborNode = nodes.find(n => n.id === neighbor);
                    if (neighborNode && neighborNode.active && !visited.has(neighbor)) {
                        visited.add(neighbor);
                        queue.push({
                            node: neighbor,
                            path: [...current.path, neighbor]
                        });
                    }
                }
            });
        }
    }
    
    return null;
}

// ==================== SIMPLE CLICK HANDLER - NO MODIFIERS NEEDED ====================
function setupClickHandler() {
    console.log("🔧 Setting up click handler...");
    
    // Remove any existing click handlers we might have added
    svg.removeEventListener('click', handleSvgClick);
    
    // Add our click handler
    svg.addEventListener('click', handleSvgClick);
    
    // Track drag start to differentiate from clicks
    svg.addEventListener('mousedown', () => {
        dragStarted = false;
    });
    
    svg.addEventListener('mousemove', () => {
        dragStarted = true;
    });
    
    console.log("✅ Click handler setup complete");
}

function handleSvgClick(e) {
    // If this was a drag, don't treat as click
    if (dragStarted) {
        dragStarted = false;
        return;
    }
    
    const rect = svg.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    
    // Find clicked node
    const clickedNode = nodes.find(node => {
        const dist = Math.sqrt((node.x - mouseX) ** 2 + (node.y - mouseY) ** 2);
        return dist < 15;
    });
    
    if (!clickedNode) return;
    
    e.preventDefault();
    e.stopPropagation();
    
    // SIMPLE TOGGLE - just click to turn on/off
    toggleNode(clickedNode);
}

// ==================== TOGGLE NODE ON/OFF ====================
function toggleNode(node) {
    // Mark as user-controlled
    node.userToggled = true;
    
    // Toggle active state
    node.active = !node.active;
    node.status = node.active ? 'online' : 'offline';
    
    if (!node.active) {
        node.signalQuality = 'offline';
        node.rssi = -100;
        console.log(`🔴 Node ${node.id} turned OFF`);
    } else {
        node.signalQuality = 'good';
        node.rssi = -65;
        console.log(`🟢 Node ${node.id} turned ON`);
    }
    
    // Force complete redraw
    refreshView();
    
    // Update displays
    if (typeof updateIPDisplay === 'function') updateIPDisplay();
    if (typeof updatePingDropdowns === 'function') updatePingDropdowns();
    
    // Show feedback
    const diagBox = document.getElementById('diagnosticBox');
    if (diagBox) {
        diagBox.innerHTML = `
            <div class="p-2 ${node.active ? 'bg-green-900/20 border-green-500/30' : 'bg-red-900/20 border-red-500/30'} rounded">
                <p class="text-xs ${node.active ? 'text-green-400' : 'text-red-400'} font-bold">
                    ${node.active ? '🟢' : '🔴'} Node ${node.id} ${node.active ? 'ONLINE' : 'OFFLINE'}
                </p>
            </div>
        `;
    }
}

// ==================== SELECT NODE FOR ENTER-KEY FAILURE ====================
function selectNodeForFailure(node) {
    clearNodeSelection();
    
    selectedNodeForFailure = node.id;
    
    // Visual feedback
    const circles = svg.querySelectorAll('circle');
    circles.forEach(circle => {
        const cx = parseFloat(circle.getAttribute('cx'));
        const cy = parseFloat(circle.getAttribute('cy'));
        
        if (Math.abs(cx - node.x) < 2 && Math.abs(cy - node.y) < 2) {
            circle.setAttribute('stroke', '#fbbf24');
            circle.setAttribute('stroke-width', '4');
            circle.setAttribute('data-selected', 'true');
        }
    });
    
    const diagBox = document.getElementById('diagnosticBox');
    if (diagBox) {
        diagBox.innerHTML = `
            <div class="p-2 bg-blue-900/20 border border-blue-500/30 rounded">
                <p class="text-xs text-blue-400">🔵 Selected: ${node.id}</p>
                <p class="text-xxs text-gray-400">Press ENTER to simulate failure</p>
                <p class="text-xxs text-gray-500 mt-1">(This is just simulation - node stays online)</p>
            </div>
        `;
    }
}

function clearNodeSelection() {
    selectedNodeForFailure = null;
    
    const selectedCircles = svg.querySelectorAll('circle[data-selected="true"]');
    selectedCircles.forEach(circle => {
        circle.setAttribute('stroke', '#fff');
        circle.setAttribute('stroke-width', '2');
        circle.removeAttribute('data-selected');
    });
}

// ==================== ENTER KEY HANDLER ====================
document.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && selectedNodeForFailure) {
        e.preventDefault();
        simulateReroutingFailure(selectedNodeForFailure);
        // Don't clear selection - keep node selected
    }
});

// ==================== SIMULATE FAILURE (READ-ONLY) ====================
function simulateReroutingFailure(nodeId) {
    const failedNode = nodes.find(n => n.id === nodeId);
    if (!failedNode) return;
    
    console.log(`💡 SIMULATING failure of: ${nodeId}`);
    
    // Find affected connections WITHOUT actually deactivating the node
    const affected = [];
    const endDevices = nodes.filter(n => n.active && n.type === 'node' && n.id !== nodeId);
    const gateways = nodes.filter(n => n.type === 'gateway' && n.active);
    
    endDevices.forEach(device => {
        gateways.forEach(gateway => {
            const path = findPathWithRerouting(device.id, gateway.id, nodeId);
            if (!path) {
                affected.push(device.id);
            }
        });
    });
    
    const diagBox = document.getElementById('diagnosticBox');
    diagBox.innerHTML = `
        <div class="p-3 bg-yellow-900/20 border border-yellow-500/30 rounded">
            <p class="text-xs text-yellow-400 font-bold mb-2">⚠️ FAILURE SIMULATION: ${nodeId}</p>
            <p class="text-xxs text-gray-400">${affected.length} devices would be affected</p>
            ${affected.length > 0 ? `
                <p class="text-xxs text-red-400 mt-1">Affected devices:</p>
                <div class="text-xxs text-gray-300 mt-1">
                    ${affected.slice(0, 5).map(id => `• ${id}`).join('<br>')}
                </div>
            ` : '<p class="text-xxs text-green-400 mt-1">No devices affected (redundant paths exist)</p>'}
            <p class="text-xxs text-gray-500 mt-2">Node ${nodeId} is still ONLINE (simulation only)</p>
        </div>
    `;
}

// ==================== SHOW ALL PATHS ====================
function showAllPaths(sourceId, targetId) {
    const paths = findAllPaths(sourceId, targetId, 5);
    const flowDiv = document.getElementById('packetFlow');
    
    if (!flowDiv) return;
    
    let content = `\n📋 All paths from ${sourceId} to ${targetId}:`;
    
    if (paths.length === 0) {
        content += `\n  ❌ No paths available`;
    } else {
        paths.forEach((path, index) => {
            const status = index === 0 ? '🟢 Primary' : '🟡 Alternate';
            content += `\n  ${status}: ${path.join(' → ')}`;
        });
    }
    
    flowDiv.innerHTML += content;
    flowDiv.scrollTop = flowDiv.scrollHeight;
}

// ==================== SETUP SHOW PATHS BUTTON ====================
function setupShowPathsButton() {
    const showPathsBtn = document.getElementById('showPathsBtn');
    if (!showPathsBtn) return;
    
    showPathsBtn.addEventListener('click', () => {
        const source = document.getElementById('pingSource')?.value;
        const target = document.getElementById('pingTarget')?.value;
        
        if (!source || !target) {
            alert('Please select source and target first');
            return;
        }
        
        showAllPaths(source, target);
    });
}

// ==================== RESET USER TOGGLES ====================
function resetUserToggles() {
    nodes.forEach(node => {
        node.userToggled = false;
        node.active = true;
        node.status = 'online';
        node.signalQuality = 'good';
        node.rssi = -65;
    });
    
    refreshView();
    updateIPDisplay();
    updatePingDropdowns();
    clearNodeSelection();
    
    const diagBox = document.getElementById('diagnosticBox');
    if (diagBox) {
        diagBox.innerHTML = `
            <div class="p-2 bg-green-900/20 border border-green-500/30 rounded">
                <p class="text-xs text-green-400">✅ Network reset</p>
                <p class="text-xxs text-gray-400">All nodes back online</p>
            </div>
        `;
    }
}

// ==================== INITIALIZATION ====================
function initMeshRouting() {
    console.log('🔄 Mesh Module Initialized');
    
    // Wait for everything to be ready
    setTimeout(() => {
        setupClickHandler();
        setupShowPathsButton();
        
        // Add reset button
        const targetPanel = document.getElementById('diagnosticBox')?.parentElement;
        if (targetPanel && !document.getElementById('resetNetworkBtn')) {
            const resetBtn = document.createElement('button');
            resetBtn.id = 'resetNetworkBtn';
            resetBtn.className = 'w-full mt-2 px-3 py-1.5 bg-gray-600 hover:bg-gray-700 rounded text-xs font-medium';
            resetBtn.innerHTML = '<i class="fas fa-undo mr-1"></i>Reset Network';
            resetBtn.onclick = resetUserToggles;
            targetPanel.appendChild(resetBtn);
        }
        
        console.log('✅ Mesh Module Ready - Click any node to toggle on/off');
    }, 2000);
}

// Auto-initialize
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initMeshRouting);
} else {
    initMeshRouting();
}

// Export functions
window.findAllPaths = findAllPaths;
window.findPathWithRerouting = findPathWithRerouting;
window.showAllPaths = showAllPaths;
window.toggleNode = toggleNode;
window.resetUserToggles = resetUserToggles;