from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Boolean, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
import os
from sqlalchemy import func

Base = declarative_base()

#  DATABASE MODELS 

class NetworkNode(Base):
    __tablename__ = 'network_nodes'
    
    id = Column(String(50), primary_key=True)
    node_type = Column(String(20))  # gateway, router, end_device
    x = Column(Float)
    y = Column(Float)
    z = Column(Float, default=0)
    active = Column(Boolean, default=True)
    range = Column(Float, default=100)
    tx_power = Column(Float, default=20)
    frequency = Column(Float, default=2.4)
    battery_level = Column(Float, nullable=True)
    firmware_version = Column(String(20))
    last_seen = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    _metadata = Column(JSON, default={})

class NetworkLink(Base):
    __tablename__ = 'network_links'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(String(50))
    target_id = Column(String(50))
    link_type = Column(String(20), default='wireless')
    signal_strength = Column(Float)
    latency = Column(Float)
    bandwidth = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class NetworkAnalysis(Base):
    __tablename__ = 'network_analyses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_type = Column(String(50))  # topology, coverage, performance
    result = Column(JSON)
    recommendations = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    node_count = Column(Integer)
    link_count = Column(Integer)
    health_score = Column(Float)

class SensorData(Base):
    __tablename__ = 'sensor_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(String(50))
    sensor_type = Column(String(50))  # temperature, humidity, motion, etc.
    value = Column(Float)
    unit = Column(String(10))
    timestamp = Column(DateTime, default=datetime.utcnow)
    _metadata = Column(JSON, default={})

class DeviceEvent(Base):
    __tablename__ = 'device_events'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(String(50))
    event_type = Column(String(50))  # connected, disconnected, alert, command
    description = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    data = Column(JSON, default={})

class NetworkSimulation(Base):
    __tablename__ = 'network_simulations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100))
    description = Column(Text)
    scenario = Column(JSON)
    results = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(String(50), nullable=True)

class UserSession(Base):
    __tablename__ = 'user_sessions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100))
    user_name = Column(String(100), nullable=True)
    ip_address = Column(String(50))
    started_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    settings = Column(JSON, default={})

#  DATABASE MANAGER 

class Database:
    def __init__(self, db_path=None):
        """Initialize database connection"""
        try:
            if db_path is None:
                # Get the absolute path to the backend directory
                backend_dir = os.path.dirname(os.path.abspath(__file__))
                # Create database directory if it doesn't exist
                db_dir = os.path.join(backend_dir, "database")
                if not os.path.exists(db_dir):
                    os.makedirs(db_dir)
                    print(f"📁 Created database directory: {db_dir}")
                
                db_path = f'sqlite:///{os.path.join(db_dir, "network_data.db")}'
            
            print(f"📁 Database path: {db_path}")
            self.engine = create_engine(db_path, echo=False)
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
            print("✅ Database initialized successfully")
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            print("⚠️  Using in-memory database as fallback")
            self.engine = create_engine('sqlite:///:memory:', echo=False)
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
    
    # Node Operations 
    
    def save_node(self, node_data):
        """Save or update a network node"""
        session = self.Session()
        try:
            node = session.query(NetworkNode).filter_by(id=node_data['id']).first()
            
            if node:
                # Update existing node
                for key, value in node_data.items():
                    if hasattr(node, key):
                        setattr(node, key, value)
                node.last_seen = datetime.utcnow()
            else:
                # Create new node
                node = NetworkNode(
                    id=node_data['id'],
                    node_type=node_data.get('type', 'node'),
                    x=node_data.get('x', 0),
                    y=node_data.get('y', 0),
                    active=node_data.get('active', True),
                    range=node_data.get('range', 100),
                    tx_power=node_data.get('tx_power', 20),
                    frequency=node_data.get('frequency', 2.4),
                    last_seen=datetime.utcnow(),
                    _metadata=node_data.get('metadata', {})
                )
                session.add(node)
            
            session.commit()
            return node.id
        except Exception as e:
            session.rollback()
            print(f"Error saving node: {e}")
            return None
        finally:
            session.close()
    
    def get_all_nodes(self, active_only=False):
        """Get all network nodes"""
        session = self.Session()
        try:
            query = session.query(NetworkNode)
            if active_only:
                query = query.filter_by(active=True)
            nodes = query.all()
            
            return [{
                'id': n.id,
                'type': n.node_type,
                'x': n.x,
                'y': n.y,
                'z': n.z,
                'active': n.active,
                'range': n.range,
                'tx_power': n.tx_power,
                'frequency': n.frequency,
                'battery': n.battery_level,
                'last_seen': n.last_seen.isoformat() if n.last_seen else None,
                'metadata': n._metadata
            } for n in nodes]
        finally:
            session.close()
    
    def get_node(self, node_id):
        """Get a specific node by ID"""
        session = self.Session()
        try:
            node = session.query(NetworkNode).filter_by(id=node_id).first()
            if node:
                return {
                    'id': node.id,
                    'type': node.node_type,
                    'x': node.x,
                    'y': node.y,
                    'active': node.active,
                    'range': node.range,
                    'tx_power': node.tx_power,
                    'frequency': node.frequency,
                    'last_seen': node.last_seen.isoformat() if node.last_seen else None
                }
            return None
        finally:
            session.close()
    
    def delete_node(self, node_id):
        """Delete a node"""
        session = self.Session()
        try:
            node = session.query(NetworkNode).filter_by(id=node_id).first()
            if node:
                session.delete(node)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"Error deleting node: {e}")
            return False
        finally:
            session.close()
    
    # ========== Link Operations ==========
    
    def save_link(self, source_id, target_id, link_data=None):
        """Save or update a network link"""
        session = self.Session()
        try:
            link = session.query(NetworkLink).filter_by(
                source_id=source_id, 
                target_id=target_id
            ).first()
            
            if not link:
                link = session.query(NetworkLink).filter_by(
                    source_id=target_id, 
                    target_id=source_id
                ).first()
            
            if link:
                # Update existing link
                if link_data:
                    if 'signal_strength' in link_data:
                        link.signal_strength = link_data['signal_strength']
                    if 'latency' in link_data:
                        link.latency = link_data['latency']
                    if 'bandwidth' in link_data:
                        link.bandwidth = link_data['bandwidth']
                link.last_updated = datetime.utcnow()
            else:
                # Create new link
                link = NetworkLink(
                    source_id=source_id,
                    target_id=target_id,
                    signal_strength=link_data.get('signal_strength', -65) if link_data else -65,
                    latency=link_data.get('latency', 10) if link_data else 10,
                    bandwidth=link_data.get('bandwidth', 100) if link_data else 100,
                    link_type=link_data.get('link_type', 'wireless') if link_data else 'wireless'
                )
                session.add(link)
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error saving link: {e}")
            return False
        finally:
            session.close()
    
    def get_all_links(self):
        """Get all network links"""
        session = self.Session()
        try:
            links = session.query(NetworkLink).all()
            return [{
                'source': l.source_id,
                'target': l.target_id,
                'signal_strength': l.signal_strength,
                'latency': l.latency,
                'bandwidth': l.bandwidth,
                'type': l.link_type,
                'last_updated': l.last_updated.isoformat() if l.last_updated else None
            } for l in links]
        finally:
            session.close()
    
    #  Analysis Operations 
    
    def save_analysis(self, analysis_data):
        """Save network analysis result"""
        session = self.Session()
        try:
            analysis = NetworkAnalysis(
                analysis_type=analysis_data.get('type', 'general'),
                result=analysis_data.get('result', {}),
                recommendations=analysis_data.get('recommendations', []),
                node_count=analysis_data.get('node_count', 0),
                link_count=analysis_data.get('link_count', 0),
                health_score=analysis_data.get('health_score', 0)
            )
            session.add(analysis)
            session.commit()
            return analysis.id
        except Exception as e:
            session.rollback()
            print(f"Error saving analysis: {e}")
            return None
        finally:
            session.close()
    
    def get_recent_analyses(self, limit=10):
        """Get recent network analyses"""
        session = self.Session()
        try:
            analyses = session.query(NetworkAnalysis).order_by(
                NetworkAnalysis.created_at.desc()
            ).limit(limit).all()
            
            return [{
                'id': a.id,
                'type': a.analysis_type,
                'health_score': a.health_score,
                'node_count': a.node_count,
                'created_at': a.created_at.isoformat(),
                'recommendations': a.recommendations
            } for a in analyses]
        finally:
            session.close()
    
    # ========== Sensor Data Operations ==========
    
    def save_sensor_data(self, node_id, sensor_type, value, unit='', metadata=None):
        """Store sensor reading"""
        session = self.Session()
        try:
            sensor_data = SensorData(
                node_id=node_id,
                sensor_type=sensor_type,
                value=value,
                unit=unit,
                _metadata=metadata or {}
            )
            session.add(sensor_data)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error saving sensor data: {e}")
            return False
        finally:
            session.close()
    
    def get_sensor_history(self, node_id=None, sensor_type=None, limit=100):
        """Get historical sensor data"""
        session = self.Session()
        try:
            query = session.query(SensorData)
            
            if node_id:
                query = query.filter_by(node_id=node_id)
            if sensor_type:
                query = query.filter_by(sensor_type=sensor_type)
            
            data = query.order_by(SensorData.timestamp.desc()).limit(limit).all()
            
            return [{
                'node_id': d.node_id,
                'type': d.sensor_type,
                'value': d.value,
                'unit': d.unit,
                'timestamp': d.timestamp.isoformat(),
                'metadata': d._metadata
            } for d in data]
        finally:
            session.close()
    
    # ========== Event Operations ==========
    
    def log_event(self, node_id, event_type, description, data=None):
        """Log a device event"""
        session = self.Session()
        try:
            event = DeviceEvent(
                node_id=node_id,
                event_type=event_type,
                description=description,
                data=data or {}
            )
            session.add(event)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error logging event: {e}")
            return False
        finally:
            session.close()
    
    def get_recent_events(self, limit=50):
        """Get recent events"""
        session = self.Session()
        try:
            events = session.query(DeviceEvent).order_by(
                DeviceEvent.timestamp.desc()
            ).limit(limit).all()
            
            return [{
                'node_id': e.node_id,
                'type': e.event_type,
                'description': e.description,
                'timestamp': e.timestamp.isoformat(),
                'data': e.data
            } for e in events]
        finally:
            session.close()
    
    #  Simulation Operations 
    
    def save_simulation(self, name, description, scenario, results):
        """Save a network simulation"""
        session = self.Session()
        try:
            sim = NetworkSimulation(
                name=name,
                description=description,
                scenario=scenario,
                results=results
            )
            session.add(sim)
            session.commit()
            return sim.id
        except Exception as e:
            session.rollback()
            print(f"Error saving simulation: {e}")
            return None
        finally:
            session.close()
    
    # Export/Import 
    
    def export_network(self):
        """Export entire network configuration"""
        nodes = self.get_all_nodes()
        links = self.get_all_links()
        
        return {
            'nodes': nodes,
            'links': links,
            'exported_at': datetime.utcnow().isoformat()
        }
    
    def import_network(self, network_data):
        """Import network configuration"""
        session = self.Session()
        try:
            # Clear existing data
            session.query(NetworkLink).delete()
            session.query(NetworkNode).delete()
            
            # Import nodes
            for node_data in network_data.get('nodes', []):
                self.save_node(node_data)
            
            # Import links
            for link_data in network_data.get('links', []):
                self.save_link(
                    link_data['source'], 
                    link_data['target'], 
                    link_data
                )
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error importing network: {e}")
            return False
        finally:
            session.close()
    
    # Statistics 
    
    def get_network_stats(self):
        """Get network statistics"""
        session = self.Session()
        try:
            node_count = session.query(NetworkNode).count()
            active_nodes = session.query(NetworkNode).filter_by(active=True).count()
            link_count = session.query(NetworkLink).count()
            
            # Average signal strength
            avg_signal = session.query(NetworkLink).with_entities(
                func.avg(NetworkLink.signal_strength)
            ).scalar() or 0
            
            return {
                'total_nodes': node_count,
                'active_nodes': active_nodes,
                'total_links': link_count,
                'avg_signal_strength': avg_signal,
                'network_health': (active_nodes / node_count * 100) if node_count > 0 else 0
            }
        finally:
            session.close()

# Create database instance
db = Database()

# Example usage
if __name__ == "__main__":
    # Save a node
    db.save_node({
        'id': 'GW1',
        'type': 'gateway',
        'x': 400,
        'y': 300,
        'active': True,
        'range': 150
    })
    
    # Get all nodes
    nodes = db.get_all_nodes()
    print(f"Nodes: {nodes}")
    
    # Log an event
    db.log_event('GW1', 'connected', 'Gateway connected to network')
    
    # Save sensor data
    db.save_sensor_data('N1', 'temperature', 23.5, '°C')
    
    # Export network
    export = db.export_network()
    print(f"Export: {export}")