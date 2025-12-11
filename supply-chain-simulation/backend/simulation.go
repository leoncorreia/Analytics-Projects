package main

import (
	"encoding/json"
	"fmt"
	"math"
	"time"
)

// Agent represents a ship/truck
type Agent struct {
	ID          string   `json:"id"`
	CurrentNode string   `json:"current_node"`
	NextNode    string   `json:"next_node"`
	Path        []string `json:"-"`
	PathIndex   int      `json:"-"`
	Progress    float64  `json:"-"`
	Speed       float64  `json:"-"`
	Lat         float64  `json:"lat"`
	Lon         float64  `json:"lon"`
	Heading     float64  `json:"heading"` // NEW: Degrees (0-360)
	Status      string   `json:"status"`
}

type SimulationEngine struct {
	Graph     *Graph
	Agents    []*Agent
	TickRate  time.Duration
	Server    *Server
}

func NewEngine(g *Graph, tickRate time.Duration, s *Server) *SimulationEngine {
	return &SimulationEngine{
		Graph:    g,
		Agents:   []*Agent{},
		TickRate: tickRate,
		Server:   s,
	}
}

func (s *SimulationEngine) SpawnAgent(id, startID, endID string, speed float64) {
	path, _ := s.Graph.FindShortestPath(startID, endID)
	if len(path) < 2 { return }

	startNode := s.Graph.Nodes[startID]
	nextNode := s.Graph.Nodes[path[1]]

	// Calculate initial heading
	initialHeading := CalculateBearing(startNode.Lat, startNode.Lon, nextNode.Lat, nextNode.Lon)

	newAgent := &Agent{
		ID:          id,
		CurrentNode: startID,
		NextNode:    path[1],
		Path:        path,
		PathIndex:   0,
		Progress:    0.0,
		Speed:       speed,
		Lat:         startNode.Lat,
		Lon:         startNode.Lon,
		Heading:     initialHeading,
		Status:      "MOVING",
	}
	s.Agents = append(s.Agents, newAgent)
}

func (s *SimulationEngine) TogglePortStatus(nodeID string) {
	node, ok := s.Graph.Nodes[nodeID]
	if !ok { return }

	node.Active = !node.Active
	status := "CLOSED"
	if node.Active { status = "OPENED" }
	fmt.Printf("⚠️ PORT EVENT: %s has been %s. Re-calculating routes...\n", node.Name, status)

	for _, agent := range s.Agents {
		if agent.Status == "ARRIVED" { continue }

		affected := false
		for i := agent.PathIndex + 1; i < len(agent.Path); i++ {
			if agent.Path[i] == nodeID {
				affected = true
				break
			}
		}

		if affected && !node.Active {
			startSearchFrom := agent.NextNode
			destination := agent.Path[len(agent.Path)-1]
			newPartialPath, dist := s.Graph.FindShortestPath(startSearchFrom, destination)

			if dist == math.Inf(1) {
				fmt.Printf("Agent %s is stranded! No path to %s\n", agent.ID, destination)
			} else {
				currentPathSoFar := agent.Path[:agent.PathIndex+1]
				if len(newPartialPath) > 0 {
					agent.Path = append(currentPathSoFar, newPartialPath...)
				}
			}
		}
	}
}

func (s *SimulationEngine) Update() {
	for _, agent := range s.Agents {
		if agent.Status == "ARRIVED" { continue }

		startNode := s.Graph.Nodes[agent.CurrentNode]
		targetNode := s.Graph.Nodes[agent.NextNode]
		dist := Haversine(startNode.Lat, startNode.Lon, targetNode.Lat, targetNode.Lon)

		// Update Heading so the ship points to the target
		agent.Heading = CalculateBearing(startNode.Lat, startNode.Lon, targetNode.Lat, targetNode.Lon)

		if dist > 0 { agent.Progress += agent.Speed / dist }

		agent.Lat = startNode.Lat + (targetNode.Lat-startNode.Lat)*agent.Progress
		agent.Lon = startNode.Lon + (targetNode.Lon-startNode.Lon)*agent.Progress

		if agent.Progress >= 1.0 {
			agent.Progress = 0.0
			agent.CurrentNode = agent.NextNode
			agent.PathIndex++

			if agent.PathIndex >= len(agent.Path)-1 {
				agent.Status = "ARRIVED"
				agent.Lat = targetNode.Lat
				agent.Lon = targetNode.Lon
			} else {
				agent.NextNode = agent.Path[agent.PathIndex+1]
			}
		}
	}

	payload, _ := json.Marshal(s.Agents)
	select {
	case s.Server.Broadcast <- payload:
	default:
	}
}

func (s *SimulationEngine) Run() {
	ticker := time.NewTicker(s.TickRate)
	defer ticker.Stop()
	for range ticker.C {
		s.Update()
	}
}

// CalculateBearing returns the degree (0-360) between two points
func CalculateBearing(lat1, lon1, lat2, lon2 float64) float64 {
	dLon := (lon2 - lon1) * math.Pi / 180.0
	lat1Rad := lat1 * math.Pi / 180.0
	lat2Rad := lat2 * math.Pi / 180.0

	y := math.Sin(dLon) * math.Cos(lat2Rad)
	x := math.Cos(lat1Rad)*math.Sin(lat2Rad) - math.Sin(lat1Rad)*math.Cos(lat2Rad)*math.Cos(dLon)
	brng := math.Atan2(y, x) * 180.0 / math.Pi

	return math.Mod(brng+360, 360) // Normalize to 0-360
}