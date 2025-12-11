import React, { useState, useEffect, useRef } from 'react';
import DeckGL from '@deck.gl/react';
import { ScatterplotLayer, IconLayer, ArcLayer } from '@deck.gl/layers';
import { Map } from 'react-map-gl/maplibre';
import 'maplibre-gl/dist/maplibre-gl.css';

// -- CONFIGURATION --
const INITIAL_VIEW_STATE = {
  longitude: -20,
  latitude: 20,
  zoom: 1.8,
  pitch: 40,
  bearing: 0
};

// Static data for visuals
const PORTS = [
  {"id": "NYC", "coordinates": [-74.0060, 40.7128]},
  {"id": "LON", "coordinates": [-0.1278, 51.5074]},
  {"id": "SHA", "coordinates": [121.4737, 31.2304]},
  {"id": "SIN", "coordinates": [103.8198, 1.3521]},
  {"id": "LAX", "coordinates": [-118.2742, 33.7423]},
  {"id": "ROT", "coordinates": [4.4777, 51.9244]},
  {"id": "TOK", "coordinates": [139.6503, 35.6762]}
];

const ROUTES = [
  {from: [-74.0060, 40.7128], to: [-0.1278, 51.5074]}, 
  {from: [-74.0060, 40.7128], to: [4.4777, 51.9244]},  
  {from: [-0.1278, 51.5074], to: [4.4777, 51.9244]},   
  {from: [-0.1278, 51.5074], to: [103.8198, 1.3521]},  
  {from: [4.4777, 51.9244], to: [103.8198, 1.3521]},   
  {from: [103.8198, 1.3521], to: [121.4737, 31.2304]}, 
  {from: [103.8198, 1.3521], to: [139.6503, 35.6762]}, 
  {from: [121.4737, 31.2304], to: [139.6503, 35.6762]},
  {from: [121.4737, 31.2304], to: [-118.2742, 33.7423]},
  {from: [139.6503, 35.6762], to: [-118.2742, 33.7423]},
  {from: [-118.2742, 33.7423], to: [-74.0060, 40.7128]},
];

function App() {
  const [agents, setAgents] = useState([]);
  const wsRef = useRef(null);

  // 1. WebSocket Connection
  useEffect(() => {
    wsRef.current = new WebSocket('ws://localhost:8080/ws');
    
    wsRef.current.onopen = () => console.log("Connected to Simulation");
    
    wsRef.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setAgents(data);
      } catch (e) {
        console.error("Parse error", e);
      }
    };

    return () => wsRef.current.close();
  }, []);

  // 2. Click Handler for Chaos Mode
  const handlePortClick = (info) => {
    if (info.object && wsRef.current) {
      console.log(`Command: Block Port ${info.object.id}`);
      wsRef.current.send(JSON.stringify({ id: info.object.id }));
      alert(`Simulation Event: Toggling Blockade at ${info.object.id}`);
    }
  };

  // 3. Define Layers
  
  // Layer A: Static Ports (Clickable)
  const portsLayer = new ScatterplotLayer({
    id: 'ports',
    data: PORTS,
    getPosition: d => d.coordinates,
    getFillColor: [255, 255, 255],
    getRadius: 50000, 
    radiusMinPixels: 5,
    pickable: true,
    onClick: handlePortClick,
    autoHighlight: true,
    highlightColor: [255, 0, 0, 255], 
  });

  // Layer B: Visual Routes (Blue Arcs)
  const routeLayer = new ArcLayer({
    id: 'routes',
    data: ROUTES,
    getSourcePosition: d => d.from,
    getTargetPosition: d => d.to,
    getSourceColor: [0, 100, 200, 100], 
    getTargetColor: [0, 100, 200, 100],
    getWidth: 2,
  });

  // Layer C: Agents (Green Icons)
  // We use a fallback Icon Atlas from deck.gl examples
  // Layer C: Agents (Ships)
  const shipLayer = new IconLayer({
    id: 'ships',
    data: agents,
    // Using a public arrow icon (looks like a paper airplane/ship)
    iconAtlas: 'https://raw.githubusercontent.com/visgl/deck.gl-data/master/website/icon-atlas.png',
    iconMapping: {
      marker: {x: 0, y: 0, width: 128, height: 128, anchorY: 128, mask: true}
    },
    getIcon: d => 'marker',
    getPosition: d => [d.lon, d.lat],
    getSize: 45, // Slightly bigger
    getColor: [0, 255, 128], // Neon Green
    
    // ROTATION MAGIC:
    // Deck.gl rotates counter-clockwise. We need to adjust our bearing.
    // We invert the heading (-d.heading) and add 45 or 90 depending on the icon's natural direction.
    // For this specific 'marker' icon, it points UP by default.
    getAngle: d => -d.heading + 45, 
    
    billboard: false, // FALSE is crucial. It makes the icon lie flat on the map surface.
    sizeScale: 1,
    updateTriggers: {
      getPosition: [agents],
      getAngle: [agents]
    }
  });

  return (
    <div>
      <DeckGL
        initialViewState={INITIAL_VIEW_STATE}
        controller={true}
        layers={[portsLayer, routeLayer, shipLayer]}
        getTooltip={({object}) => object && object.id ? `${object.id}\nStatus: ${object.status}` : null}
      >
        <Map
          mapStyle="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
        />
      </DeckGL>
      
      {/* Dashboard Overlay */}
      <div style={{
        position: 'absolute', 
        top: 20, 
        left: 20, 
        color: 'white', 
        background: 'rgba(0,0,0,0.7)', 
        padding: '20px', 
        borderRadius: '8px',
        pointerEvents: 'none',
        backdropFilter: 'blur(4px)'
      }}>
        <h1 style={{margin: '0 0 10px 0', fontSize: '24px', fontFamily: 'monospace'}}>
          GLOBAL SUPPLY CHAIN
        </h1>
        <div style={{fontSize: '14px', color: '#0f0', fontFamily: 'monospace'}}>
          ● ACTIVE AGENTS: {agents.length}
        </div>
        <div style={{fontSize: '14px', color: '#aaa', fontFamily: 'monospace'}}>
          ● NODES: {PORTS.length}
        </div>
        <div style={{marginTop: '15px', fontSize: '12px', color: '#666', borderTop: '1px solid #444', paddingTop: '5px'}}>
          * Click a white port node to toggle blockade
        </div>
      </div>
    </div>
  );
}

export default App;