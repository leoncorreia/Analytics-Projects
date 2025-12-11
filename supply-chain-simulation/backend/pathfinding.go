package main

import (
	"container/heap"
	"math"
)

// Item is an item in the priority queue
type Item struct {
	NodeID   string
	Priority float64 // The current shortest distance to this node
	Index    int
}

// PriorityQueue implements heap.Interface and holds Items
type PriorityQueue []*Item

func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool {
	return pq[i].Priority < pq[j].Priority
}

func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
	pq[i].Index = i
	pq[j].Index = j
}

func (pq *PriorityQueue) Push(x interface{}) {
	n := len(*pq)
	item := x.(*Item)
	item.Index = n
	*pq = append(*pq, item)
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	old[n-1] = nil
	item.Index = -1
	*pq = old[0 : n-1]
	return item
}

// FindShortestPath returns the sequence of Node IDs and total distance
func (g *Graph) FindShortestPath(startID, endID string) ([]string, float64) {
	dist := make(map[string]float64)
	prev := make(map[string]string)
	pq := make(PriorityQueue, 0)
	heap.Init(&pq)

	// Initialize distances
	for id := range g.Nodes {
		if id == startID {
			dist[id] = 0
		} else {
			dist[id] = math.Inf(1)
		}
		heap.Push(&pq, &Item{NodeID: id, Priority: dist[id]})
	}

	for pq.Len() > 0 {
		u := heap.Pop(&pq).(*Item)
		uID := u.NodeID

		if uID == endID {
			break // Found target
		}

		// Check neighbors
		// Check neighbors
		for _, edge := range g.Edges[uID] {
			// CRITICAL CHANGE: If the target node is inactive (Blocked), skip it!
			if !g.Nodes[edge.ToID].Active {
				continue
			}

			alt := dist[uID] + edge.Weight
			if alt < dist[edge.ToID] {
				dist[edge.ToID] = alt
				prev[edge.ToID] = uID
				heap.Push(&pq, &Item{NodeID: edge.ToID, Priority: alt})
			}
		}
	}

	// Reconstruct path
	path := []string{}
	curr := endID
	for curr != "" {
		path = append([]string{curr}, path...) // Prepend
		if curr == startID {
			break
		}
		curr = prev[curr]
	}

	return path, dist[endID]
}