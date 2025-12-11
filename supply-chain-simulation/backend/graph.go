package main

import (
	"math"
)

type Node struct {
	ID     string  `json:"id"`
	Name   string  `json:"name"`
	Lat    float64 `json:"lat"`
	Lon    float64 `json:"lon"`
	Active bool    `json:"active"` // NEW: Is the port open?
}

type Edge struct {
	FromID string
	ToID   string
	Weight float64
}

type Graph struct {
	Nodes map[string]*Node
	Edges map[string][]Edge
}

func NewGraph() *Graph {
	return &Graph{
		Nodes: make(map[string]*Node),
		Edges: make(map[string][]Edge),
	}
}

func (g *Graph) AddNode(n *Node) {
	n.Active = true // Default to active
	g.Nodes[n.ID] = n
}

func (g *Graph) AddEdge(fromID, toID string) {
	fromNode, ok1 := g.Nodes[fromID]
	toNode, ok2 := g.Nodes[toID]
	if !ok1 || !ok2 { return }

	dist := Haversine(fromNode.Lat, fromNode.Lon, toNode.Lat, toNode.Lon)
	g.Edges[fromID] = append(g.Edges[fromID], Edge{FromID: fromID, ToID: toID, Weight: dist})
	g.Edges[toID] = append(g.Edges[toID], Edge{FromID: toID, ToID: fromID, Weight: dist})
}

func Haversine(lat1, lon1, lat2, lon2 float64) float64 {
	const R = 6371 
	dLat := (lat2 - lat1) * (math.Pi / 180.0)
	dLon := (lon2 - lon1) * (math.Pi / 180.0)
	lat1Rad := lat1 * (math.Pi / 180.0)
	lat2Rad := lat2 * (math.Pi / 180.0)
	a := math.Sin(dLat/2)*math.Sin(dLat/2) +
		math.Sin(dLon/2)*math.Sin(dLon/2)*math.Cos(lat1Rad)*math.Cos(lat2Rad)
	c := 2 * math.Atan2(math.Sqrt(a), math.Sqrt(1-a))
	return R * c
}