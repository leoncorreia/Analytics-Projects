package main

import (
	"log"
	"net/http"
	"sync"
	"github.com/gorilla/websocket"
)

var upgrader = websocket.Upgrader{
	CheckOrigin: func(r *http.Request) bool { return true },
}

type Server struct {
	Clients   map[*websocket.Conn]bool
	Broadcast chan []byte
	Incoming  chan string // New channel for Node IDs to toggle
	Mutex     sync.Mutex
}

func NewServer() *Server {
	return &Server{
		Clients:   make(map[*websocket.Conn]bool),
		Broadcast: make(chan []byte),
		Incoming:  make(chan string),
	}
}

func (s *Server) HandleConnections(w http.ResponseWriter, r *http.Request) {
	ws, err := upgrader.Upgrade(w, r, nil)
	if err != nil { log.Fatal(err) }

	s.Mutex.Lock()
	s.Clients[ws] = true
	s.Mutex.Unlock()

	// Reader Loop
	go func() {
		defer ws.Close()
		for {
			var msg map[string]string
			err := ws.ReadJSON(&msg)
			if err != nil {
				s.Mutex.Lock()
				delete(s.Clients, ws)
				s.Mutex.Unlock()
				break
			}
			// If frontend sends { "id": "SIN" }, we push "SIN" to the channel
			if id, ok := msg["id"]; ok {
				s.Incoming <- id
			}
		}
	}()
}

func (s *Server) HandleMessages() {
	for {
		msg := <-s.Broadcast
		s.Mutex.Lock()
		for client := range s.Clients {
			client.WriteMessage(websocket.TextMessage, msg)
		}
		s.Mutex.Unlock()
	}
}