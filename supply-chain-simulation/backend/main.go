package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"math/rand"
	"net/http"
	"os"
	"time"
)

func main() {
	// 1. Setup Graph
	world := NewGraph()

	// Load Ports from JSON
	jsonFile, err := os.Open("ports.json")
	if err != nil {
		log.Fatal(err)
	}
	defer jsonFile.Close()
	byteValue, _ := ioutil.ReadAll(jsonFile)
	var nodes []Node
	json.Unmarshal(byteValue, &nodes)
	for _, n := range nodes {
		newNode := n
		world.AddNode(&newNode)
	}
	fmt.Printf("Loaded %d ports into the graph.\n", len(world.Nodes))

	// Add Edges (The World Graph Topology)
	world.AddEdge("NYC", "LON")
	world.AddEdge("NYC", "ROT")
	world.AddEdge("LON", "ROT")
	world.AddEdge("LON", "SIN")
	world.AddEdge("ROT", "SIN")
	world.AddEdge("SIN", "SHA")
	world.AddEdge("SIN", "TOK")
	world.AddEdge("SHA", "TOK")
	world.AddEdge("SHA", "LAX")
	world.AddEdge("TOK", "LAX")
	world.AddEdge("LAX", "NYC")

	// 2. Setup WebSocket Server
	server := NewServer()
	
	// Handle broadcasting messages to clients
	go server.HandleMessages()
	
	// HTTP Route for Websockets
	http.HandleFunc("/ws", server.HandleConnections)
	
	// Start HTTP Server in background
	go func() {
		fmt.Println("📡 WebSocket Server started on :8080")
		if err := http.ListenAndServe(":8080", nil); err != nil {
			log.Fatal("ListenAndServe: ", err)
		}
	}()

	// 3. Initialize Simulation Engine
	// Tick Rate: 50ms (20 ticks/second) for smooth visuals
	sim := NewEngine(world, 50*time.Millisecond, server)

	// 4. Chaos Mode Listener
	// Listens for clicks from the Frontend to toggle port status
	go func() {
		for nodeID := range server.Incoming {
			sim.TogglePortStatus(nodeID)
		}
	}()

	// 5. Spawner: Create 50 Ships with Random Routes
	rand.Seed(time.Now().UnixNano())
	fmt.Println("🚀 Spawning 50 ships with random routes...")

	var portIDs []string
	for _, n := range nodes {
		portIDs = append(portIDs, n.ID)
	}

	for i := 0; i < 50; i++ {
		start := portIDs[rand.Intn(len(portIDs))]
		end := portIDs[rand.Intn(len(portIDs))]

		if start != end {
			// Random speed between 50 and 150 km/tick
			speed := 50.0 + rand.Float64()*100.0
			agentID := fmt.Sprintf("Ship-%d", i)

			// Stagger spawns slightly so they don't all appear at once
			go func(id, s, e string, spd float64) {
				time.Sleep(time.Duration(rand.Intn(5000)) * time.Millisecond)
				sim.SpawnAgent(id, s, e, spd)
			}(agentID, start, end, speed)
		}
	}

	// 6. Start the Game Loop
	fmt.Println("⚡ Simulation Running...")
	sim.Run()
}