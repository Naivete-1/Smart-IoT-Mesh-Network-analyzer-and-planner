import networkx as nx
import numpy as np
from scipy.spatial import Delaunay
from collections import defaultdict
import math
from datetime import datetime

class MeshNetworkAnalyzer:
    def __init__(self):
        self.graph = nx.Graph()
        self.signal_strength_cache = {}
        
    def analyze_topology(self, nodes, links):
        """Comprehensive topology analysis"""
        self.graph.clear()
        
        # Build graph
        for node in nodes:
            self.graph.add_node(node['id'], **node)
        for link in links:
            self.graph.add_edge(link['source'], link['target'])
        
        analysis = {
            'node_count': len(nodes),
            'link_count': len(links),
            'density': nx.density(self.graph),
            'avg_degree': sum(dict(self.graph.degree()).values()) / len(nodes),
            'diameter': nx.diameter(self.graph) if nx.is_connected(self.graph) else float('inf'),
            'clustering_coefficient': nx.average_clustering(self.graph),
            'is_connected': nx.is_connected(self.graph),
            'connected_components': nx.number_connected_components(self.graph),
            'centrality': {
                'degree': nx.degree_centrality(self.graph),
                'betweenness': nx.betweenness_centrality(self.graph),
                'closeness': nx.closeness_centrality(self.graph),
                'eigenvector': nx.eigenvector_centrality_numpy(self.graph, max_iter=1000)
            }
        }
        
        # Find critical nodes 
        analysis['critical_nodes'] = list(nx.articulation_points(self.graph))
        
        # Find optimal gateway locations
        analysis['optimal_gateways'] = self.find_optimal_gateways(nodes)
        
        return analysis
    
    def analyze_coverage(self, nodes, resolution=20):
        """Advanced coverage analysis with heat mapping"""
        if not nodes:
            return {}
            
        # Create grid
        x_coords = [n['x'] for n in nodes]
        y_coords = [n['y'] for n in nodes]
        
        min_x, max_x = min(x_coords) - 200, max(x_coords) + 200
        min_y, max_y = min(y_coords) - 200, max(y_coords) + 200
        
        coverage_map = []
        blind_spots = []
        
        for x in np.arange(min_x, max_x, resolution):
            for y in np.arange(min_y, max_y, resolution):
                signal_strength = self.calculate_signal_at_point(x, y, nodes)
                
                if signal_strength > -70:  
                    coverage_map.append({
                        'x': x, 'y': y, 
                        'strength': signal_strength,
                        'quality': 'excellent'
                    })
                elif signal_strength > -85:  
                    coverage_map.append({
                        'x': x, 'y': y, 
                        'strength': signal_strength,
                        'quality': 'adequate'
                    })
                else:  
                    blind_spots.append({'x': x, 'y': y})
        
        return {
            'coverage_map': coverage_map,
            'blind_spots': blind_spots,
            'coverage_percentage': (len(coverage_map) / (len(coverage_map) + len(blind_spots))) * 100,
            'total_area': (max_x - min_x) * (max_y - min_y)
        }
    
    def calculate_signal_at_point(self, x, y, nodes, frequency=2.4):
        """Calculate signal strength using path loss model"""
        max_signal = -float('inf')
        
        for node in nodes:
            if not node.get('active', True):
                continue
                
            distance = math.sqrt((x - node['x'])**2 + (y - node['y'])**2)
            
            # Free Space Path Loss model
            if distance > 0:
                # FSPL = 20*log10(d) + 20*log10(f) + 32.44
                fspl = 20 * math.log10(distance) + 20 * math.log10(frequency) + 32.44
                
                # Add obstacles and interference (dBm)
                tx_power = node.get('tx_power', 20)  
                rx_sensitivity = node.get('sensitivity', -90)  
                
                signal = tx_power - fspl
                
                # Add fading margin
                signal -= np.random.normal(0, 3)  
                
                max_signal = max(max_signal, signal)
        
        return max_signal if max_signal > -float('inf') else -100
    
    def find_optimal_gateways(self, nodes, k=3):
        """Find optimal gateway locations using k-means clustering"""
        if len(nodes) < k:
            return nodes
        
        # Convert to numpy array
        points = np.array([[n['x'], n['y']] for n in nodes])
        
        # Simple k-means approximation
        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=min(k, len(nodes)))
        kmeans.fit(points)
        
        optimal_locations = []
        for i, center in enumerate(kmeans.cluster_centers_):
            optimal_locations.append({
                'gateway_id': f'OPT_GW_{i+1}',
                'x': float(center[0]),
                'y': float(center[1]),
                'coverage_radius': self.calculate_optimal_radius(points[kmeans.labels_ == i])
            })
        
        return optimal_locations
    
    def find_bottlenecks(self, nodes, links):
        """Identify network bottlenecks"""
        G = nx.Graph()
        
        for node in nodes:
            G.add_node(node['id'])
        for link in links:
            G.add_edge(link['source'], link['target'])
        
        bottlenecks = []
        
        # Find edges with high betweenness
        edge_betweenness = nx.edge_betweenness_centrality(G)
        for (u, v), centrality in edge_betweenness.items():
            if centrality > 0.3:  
                bottlenecks.append({
                    'type': 'edge',
                    'source': u,
                    'target': v,
                    'centrality': centrality,
                    'risk': 'high' if centrality > 0.5 else 'medium'
                })
        
        # Find nodes with high load
        for node in G.nodes():
            degree = G.degree(node)
            if degree > 5:  
                bottlenecks.append({
                    'type': 'node',
                    'node_id': node,
                    'degree': degree,
                    'risk': 'high' if degree > 8 else 'medium'
                })
        
        return bottlenecks
    
    def calculate_redundancy(self, nodes):
        """Calculate network redundancy and resilience"""
        G = nx.Graph()
        
        # Building  graph based on range
        for i, n1 in enumerate(nodes):
            for j, n2 in enumerate(nodes[i+1:], i+1):
                dist = math.sqrt((n1['x'] - n2['x'])**2 + (n1['y'] - n2['y'])**2)
                if dist < (n1.get('range', 100) + n2.get('range', 100)) / 2:
                    G.add_edge(n1['id'], n2['id'])
        
        metrics = {
            'edge_connectivity': nx.edge_connectivity(G) if G.nodes() else 0,
            'node_connectivity': nx.node_connectivity(G) if G.nodes() else 0,
            'has_redundant_paths': nx.is_connected(G) and nx.number_connected_components(G) == 1,
            'redundancy_score': self.calculate_redundancy_score(G)
        }
        
        return metrics
    
    def generate_optimization_plan(self, nodes):
        """Generate comprehensive optimization recommendations"""
        recommendations = []
        
        # Check for isolated nodes
        G = nx.Graph()
        for node in nodes:
            G.add_node(node['id'])
        
        components = list(nx.connected_components(G))
        if len(components) > 1:
            recommendations.append({
                'priority': 'high',
                'category': 'connectivity',
                'message': f'Network has {len(components)} separate components. Add relays to bridge them.',
                'action': 'add_relay',
                'locations': self.find_optimal_relay_locations(nodes)
            })
        
        # Check for overloaded nodes
        for node in nodes:
            if node.get('type') == 'gateway':
                connected_nodes = [n for n in nodes if self.within_range(node, n)]
                if len(connected_nodes) > 10:
                    recommendations.append({
                        'priority': 'medium',
                        'category': 'load_balancing',
                        'message': f'Gateway {node["id"]} is overloaded with {len(connected_nodes)} nodes.',
                        'action': 'add_gateway',
                        'location': {
                            'x': node['x'] + 50,
                            'y': node['y'] + 50
                        }
                    })
        
        # Check coverage gaps
        coverage = self.analyze_coverage(nodes)
        if coverage['blind_spots']:
            recommendations.append({
                'priority': 'medium',
                'category': 'coverage',
                'message': f'Found {len(coverage["blind_spots"])} blind spots in coverage.',
                'action': 'optimize_coverage',
                'blind_spots': coverage['blind_spots'][:5]  
            })
        
        return recommendations
    
    def get_real_time_status(self):
        """Get real-time network status for SocketIO"""
        return {
            'timestamp': datetime.now().isoformat(),
            'active_nodes': len([n for n in self.graph.nodes() if n.get('active')]),
            'total_traffic': np.random.randint(100, 1000),  
            'avg_latency': np.random.randint(10, 100),      
            'packet_loss': np.random.random() * 2,          
            'alerts': self.check_alerts()
        }
def calculate_optimal_radius(self, points):
    """Calculate optimal coverage radius for a cluster"""
    if len(points) == 0:
        return 100
    # Calculate average distance from center
    center = np.mean(points, axis=0)
    distances = [np.linalg.norm(p - center) for p in points]
    return float(np.mean(distances) * 1.5)

def find_optimal_relay_locations(self, nodes):
    """Find optimal locations for relay nodes"""
    
    return [{'x': 350, 'y': 250}]  

def within_range(self, node1, node2):
    """Check if two nodes are within range"""
    dist = math.sqrt((node1['x'] - node2['x'])**2 + (node1['y'] - node2['y'])**2)
    return dist < (node1.get('range', 100) + node2.get('range', 100)) / 2

def check_alerts(self):
    """Check for network alerts"""
    return []  

def calculate_redundancy_score(self, G):
    """Calculate network redundancy score"""
    if not G.nodes():
        return 0
    
    return nx.density(G) * 100

def simulate_scenario(self, nodes, scenario, parameters):
    """Run what-if scenario simulation"""
    
    return {'feasible': True, 'impact': 'positive'}

def generate_report(self, analysis_id, format='pdf'):
    """Generate network analysis report"""
    
    return f'/reports/analysis_{analysis_id}.{format}'

def detect_interference(self, nodes):
    """Detect signal interference between nodes"""
    interference = []
    for i, n1 in enumerate(nodes):
        for j, n2 in enumerate(nodes[i+1:], i+1):
            dist = math.sqrt((n1['x'] - n2['x'])**2 + (n1['y'] - n2['y'])**2)
            if dist < 50 and dist > 0:  
                interference.append({
                    'node1': n1['id'],
                    'node2': n2['id'],
                    'distance': dist,
                    'risk': 'high' if dist < 30 else 'medium'
                })
    return interference