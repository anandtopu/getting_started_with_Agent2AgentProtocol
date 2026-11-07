// Granite's native Go agent. Run from this directory: go run .
package main

import (
	"context"
	"crypto/subtle"
	"encoding/json"
	"flag"
	"iter"
	"log"
	"math"
	"net/http"
	"os"
	"time"

	"github.com/a2aproject/a2a-go/v2/a2a"
	"github.com/a2aproject/a2a-go/v2/a2asrv"
)

func main() {
	dataPath := flag.String("data", "../../../../data/venues.json", "Synthetic venue inventory")
	flag.Parse()
	token := os.Getenv("MAPLEWOOD_TOKEN")
	if token == "" {
		log.Fatal("Set MAPLEWOOD_TOKEN outside A2A messages, or run scripts/check_go_interop.py.")
	}
	raw, err := os.ReadFile(*dataPath)
	if err != nil {
		log.Fatal(err)
	}
	var venues []map[string]any
	if err := json.Unmarshal(raw, &venues); err != nil {
		log.Fatal(err)
	}
	executor := a2asrv.AgentExecutorFunc(func(ctx context.Context, ec *a2asrv.ExecutorContext) iter.Seq2[a2a.Event, error] {
		return func(yield func(a2a.Event, error) bool) {
			guests, date := float64(40), "2027-06-01"
			for _, part := range ec.Message.Parts {
				if brief, ok := part.Data().(map[string]any); ok {
					if n, ok := brief["guests"].(float64); ok {
						guests = n
					} else if _, present := brief["guests"]; present {
						guests = math.NaN()
					}
					if d, ok := brief["date"].(string); ok {
						date = d
					}
				}
			}
			task := a2a.NewSubmittedTask(ec, ec.Message)
			task.Status.State = a2a.TaskStateRejected
			var selection map[string]any
			if guests >= 1 && guests <= 1000 && math.Trunc(guests) == guests {
				for _, venue := range venues {
					available, _ := venue["availability"].(map[string]any)[date].(bool)
					if available && venue["capacity"].(float64) >= guests &&
						(selection == nil || venue["price_cents"].(float64) < selection["price_cents"].(float64)) {
						selection = venue
					}
				}
			}
			if selection != nil {
				quote := map[string]any{"vendor": "venues", "selection": selection["id"], "guests": int(guests),
					"currency": "USD", "total_cents": selection["price_cents"], "approved": false}
				task.Artifacts = []*a2a.Artifact{{ID: "quote", Name: "venue quote", Parts: a2a.ContentParts{a2a.NewDataPart(quote)}}}
				task.Status.State = a2a.TaskStateCompleted
			}
			yield(task, nil)
		}
	})
	identity := &a2a.AgentCard{
		Name: "Granite Hall Venues (Go)", Description: "Quote synthetic rooms by guest count and date; no purchase.",
		Version: "1.0.0", SupportedInterfaces: []*a2a.AgentInterface{a2a.NewAgentInterface("http://127.0.0.1:8400/rpc", a2a.TransportProtocolJSONRPC)},
		DefaultInputModes: []string{"application/json"}, DefaultOutputModes: []string{"application/json"},
		Skills: []a2a.AgentSkill{{ID: "venues.quote", Name: "Venue quote", Description: "Return an available room and an integer-cent quote.", Tags: []string{"venues"}}},
	}
	// Declare the same standard bearer policy enforced at the HTTP boundary.
	encoded, _ := json.Marshal(identity)
	var document map[string]any
	if err := json.Unmarshal(encoded, &document); err != nil {
		log.Fatal(err)
	}
	document["securitySchemes"] = map[string]any{"vendor_token": map[string]any{"httpAuthSecurityScheme": map[string]any{"scheme": "Bearer"}}}
	document["securityRequirements"] = []any{map[string]any{"schemes": map[string]any{"vendor_token": map[string]any{}}}}
	encoded, _ = json.Marshal(document)
	if err := json.Unmarshal(encoded, identity); err != nil {
		log.Fatal(err)
	}
	rpc := a2asrv.NewJSONRPCHandler(a2asrv.NewHandler(executor))
	mux := http.NewServeMux()
	mux.Handle(a2asrv.WellKnownAgentCardPath, a2asrv.NewStaticAgentCardHandler(identity))
	mux.HandleFunc("/rpc", func(w http.ResponseWriter, r *http.Request) {
		if subtle.ConstantTimeCompare([]byte(r.Header.Get("Authorization")), []byte("Bearer "+token)) != 1 {
			w.Header().Set("WWW-Authenticate", "Bearer")
			http.Error(w, "Authentication required", http.StatusUnauthorized)
			return
		}
		r.Body = http.MaxBytesReader(w, r.Body, 1_000_000)
		rpc.ServeHTTP(w, r)
	})
	server := &http.Server{Addr: "127.0.0.1:8400", Handler: mux, ReadHeaderTimeout: 5 * time.Second}
	log.Print("Granite Go vendor ready on loopback port 8400")
	log.Fatal(server.ListenAndServe())
}
