package splunk

/*
SPLUNK GO CODING PATTERNS SUMMARY
==================================
Common patterns and best practices for Splunk development with Go
*/

import (
	"bytes"
	"context"
	"crypto/tls"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strings"
	"time"
)

// ============================================================================
// 1. CLIENT SETUP PATTERNS
// ============================================================================

// SplunkClient represents a Splunk API client
type SplunkClient struct {
	BaseURL    string
	AuthToken  string
	HTTPClient *http.Client
}

// NewSplunkClient creates a new Splunk client with common configurations
func NewSplunkClient(baseURL, authToken string) *SplunkClient {
	return &SplunkClient{
		BaseURL:   baseURL,
		AuthToken: authToken,
		HTTPClient: &http.Client{
			Timeout: 30 * time.Second,
			Transport: &http.Transport{
				TLSClientConfig: &tls.Config{
					InsecureSkipVerify: false, // Set to true only for dev/testing
				},
				MaxIdleConns:        100,
				MaxIdleConnsPerHost: 10,
				IdleConnTimeout:     90 * time.Second,
			},
		},
	}
}

// ============================================================================
// 2. HTTP EVENT COLLECTOR (HEC) PATTERNS
// ============================================================================

// HECEvent represents a Splunk HEC event structure
type HECEvent struct {
	Time       int64                  `json:"time,omitempty"`       // Unix timestamp
	Host       string                 `json:"host,omitempty"`       // Hostname
	Source     string                 `json:"source,omitempty"`     // Event source
	SourceType string                 `json:"sourcetype,omitempty"` // Source type
	Index      string                 `json:"index,omitempty"`      // Target index
	Event      interface{}            `json:"event"`                // Event data
	Fields     map[string]interface{} `json:"fields,omitempty"`     // Indexed fields
}

// HECClient represents an HTTP Event Collector client
type HECClient struct {
	URL        string
	Token      string
	HTTPClient *http.Client
}

// SendEvent sends a single event to HEC
func (h *HECClient) SendEvent(ctx context.Context, event *HECEvent) error {
	data, err := json.Marshal(event)
	if err != nil {
		return fmt.Errorf("marshal event: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, "POST", h.URL, bytes.NewReader(data))
	if err != nil {
		return fmt.Errorf("create request: %w", err)
	}

	req.Header.Set("Authorization", "Splunk "+h.Token)
	req.Header.Set("Content-Type", "application/json")

	resp, err := h.HTTPClient.Do(req)
	if err != nil {
		return fmt.Errorf("send request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("HEC error (status %d): %s", resp.StatusCode, string(body))
	}

	return nil
}

// BatchSendEvents sends multiple events in a single request (more efficient)
func (h *HECClient) BatchSendEvents(ctx context.Context, events []*HECEvent) error {
	var buf bytes.Buffer
	encoder := json.NewEncoder(&buf)

	for _, event := range events {
		if err := encoder.Encode(event); err != nil {
			return fmt.Errorf("encode event: %w", err)
		}
	}

	req, err := http.NewRequestWithContext(ctx, "POST", h.URL, &buf)
	if err != nil {
		return fmt.Errorf("create request: %w", err)
	}

	req.Header.Set("Authorization", "Splunk "+h.Token)
	req.Header.Set("Content-Type", "application/json")

	resp, err := h.HTTPClient.Do(req)
	if err != nil {
		return fmt.Errorf("send request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("HEC error (status %d): %s", resp.StatusCode, string(body))
	}

	return nil
}

// ============================================================================
// 3. SEARCH API PATTERNS
// ============================================================================

// SearchJob represents a Splunk search job
type SearchJob struct {
	SID string `json:"sid"` // Search ID
}

// SearchResults represents search results
type SearchResults struct {
	Results []map[string]interface{} `json:"results"`
	Fields  []map[string]interface{} `json:"fields"`
}

// CreateSearch creates a search job and returns the SID
func (c *SplunkClient) CreateSearch(ctx context.Context, query string, params map[string]string) (string, error) {
	endpoint := fmt.Sprintf("%s/services/search/jobs", c.BaseURL)

	data := url.Values{}
	data.Set("search", query)
	data.Set("output_mode", "json")

	for key, value := range params {
		data.Set(key, value)
	}

	req, err := http.NewRequestWithContext(ctx, "POST", endpoint, strings.NewReader(data.Encode()))
	if err != nil {
		return "", fmt.Errorf("create request: %w", err)
	}

	req.Header.Set("Authorization", "Bearer "+c.AuthToken)
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return "", fmt.Errorf("send request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusCreated {
		body, _ := io.ReadAll(resp.Body)
		return "", fmt.Errorf("create search failed (status %d): %s", resp.StatusCode, string(body))
	}

	var result struct {
		SID string `json:"sid"`
	}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return "", fmt.Errorf("decode response: %w", err)
	}

	return result.SID, nil
}

// WaitForSearch polls until search job is complete
func (c *SplunkClient) WaitForSearch(ctx context.Context, sid string) error {
	endpoint := fmt.Sprintf("%s/services/search/jobs/%s?output_mode=json", c.BaseURL, sid)
	ticker := time.NewTicker(1 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-ticker.C:
			req, err := http.NewRequestWithContext(ctx, "GET", endpoint, nil)
			if err != nil {
				return fmt.Errorf("create request: %w", err)
			}

			req.Header.Set("Authorization", "Bearer "+c.AuthToken)

			resp, err := c.HTTPClient.Do(req)
			if err != nil {
				return fmt.Errorf("send request: %w", err)
			}

			var result struct {
				Entry []struct {
					Content struct {
						IsDone bool `json:"isDone"`
					} `json:"content"`
				} `json:"entry"`
			}

			if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
				resp.Body.Close()
				return fmt.Errorf("decode response: %w", err)
			}
			resp.Body.Close()

			if len(result.Entry) > 0 && result.Entry[0].Content.IsDone {
				return nil
			}
		}
	}
}

// GetSearchResults retrieves results from a completed search job
func (c *SplunkClient) GetSearchResults(ctx context.Context, sid string, offset, count int) (*SearchResults, error) {
	endpoint := fmt.Sprintf("%s/services/search/jobs/%s/results?output_mode=json&offset=%d&count=%d",
		c.BaseURL, sid, offset, count)

	req, err := http.NewRequestWithContext(ctx, "GET", endpoint, nil)
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}

	req.Header.Set("Authorization", "Bearer "+c.AuthToken)

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("send request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("get results failed (status %d): %s", resp.StatusCode, string(body))
	}

	var results SearchResults
	if err := json.NewDecoder(resp.Body).Decode(&results); err != nil {
		return nil, fmt.Errorf("decode results: %w", err)
	}

	return &results, nil
}

// OneShot executes a blocking search (for quick searches)
func (c *SplunkClient) OneShot(ctx context.Context, query string) (*SearchResults, error) {
	endpoint := fmt.Sprintf("%s/services/search/jobs/export", c.BaseURL)

	data := url.Values{}
	data.Set("search", query)
	data.Set("output_mode", "json")

	req, err := http.NewRequestWithContext(ctx, "POST", endpoint, strings.NewReader(data.Encode()))
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}

	req.Header.Set("Authorization", "Bearer "+c.AuthToken)
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("send request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("oneshot search failed (status %d): %s", resp.StatusCode, string(body))
	}

	var results SearchResults
	if err := json.NewDecoder(resp.Body).Decode(&results); err != nil {
		return nil, fmt.Errorf("decode results: %w", err)
	}

	return &results, nil
}

// ============================================================================
// 4. AUTHENTICATION PATTERNS
// ============================================================================

// AuthResponse represents authentication response
type AuthResponse struct {
	SessionKey string `json:"sessionKey"`
}

// Authenticate gets a session token from username/password
func Authenticate(ctx context.Context, baseURL, username, password string) (string, error) {
	endpoint := fmt.Sprintf("%s/services/auth/login", baseURL)

	data := url.Values{}
	data.Set("username", username)
	data.Set("password", password)
	data.Set("output_mode", "json")

	req, err := http.NewRequestWithContext(ctx, "POST", endpoint, strings.NewReader(data.Encode()))
	if err != nil {
		return "", fmt.Errorf("create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")

	client := &http.Client{Timeout: 10 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return "", fmt.Errorf("send request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return "", fmt.Errorf("authentication failed (status %d): %s", resp.StatusCode, string(body))
	}

	var authResp AuthResponse
	if err := json.NewDecoder(resp.Body).Decode(&authResp); err != nil {
		return "", fmt.Errorf("decode response: %w", err)
	}

	return authResp.SessionKey, nil
}

// ============================================================================
// 5. INDEX MANAGEMENT PATTERNS
// ============================================================================

// Index represents a Splunk index
type Index struct {
	Name             string `json:"name"`
	MaxDataSize      string `json:"maxDataSize,omitempty"`
	FrozenTimePeriod string `json:"frozenTimePeriodInSecs,omitempty"`
}

// CreateIndex creates a new index
func (c *SplunkClient) CreateIndex(ctx context.Context, index *Index) error {
	endpoint := fmt.Sprintf("%s/services/data/indexes", c.BaseURL)

	data := url.Values{}
	data.Set("name", index.Name)
	if index.MaxDataSize != "" {
		data.Set("maxDataSize", index.MaxDataSize)
	}
	if index.FrozenTimePeriod != "" {
		data.Set("frozenTimePeriodInSecs", index.FrozenTimePeriod)
	}

	req, err := http.NewRequestWithContext(ctx, "POST", endpoint, strings.NewReader(data.Encode()))
	if err != nil {
		return fmt.Errorf("create request: %w", err)
	}

	req.Header.Set("Authorization", "Bearer "+c.AuthToken)
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return fmt.Errorf("send request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusCreated {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("create index failed (status %d): %s", resp.StatusCode, string(body))
	}

	return nil
}

// ============================================================================
// 6. ERROR HANDLING PATTERNS
// ============================================================================

// SplunkError represents a Splunk API error
type SplunkError struct {
	StatusCode int
	Message    string
	Details    string
}

func (e *SplunkError) Error() string {
	return fmt.Sprintf("splunk error (status %d): %s - %s", e.StatusCode, e.Message, e.Details)
}

// ParseSplunkError extracts error details from response
func ParseSplunkError(resp *http.Response) error {
	body, _ := io.ReadAll(resp.Body)

	var errResp struct {
		Messages []struct {
			Type string `json:"type"`
			Text string `json:"text"`
		} `json:"messages"`
	}

	if err := json.Unmarshal(body, &errResp); err != nil {
		return &SplunkError{
			StatusCode: resp.StatusCode,
			Message:    "failed to parse error response",
			Details:    string(body),
		}
	}

	if len(errResp.Messages) > 0 {
		return &SplunkError{
			StatusCode: resp.StatusCode,
			Message:    errResp.Messages[0].Type,
			Details:    errResp.Messages[0].Text,
		}
	}

	return &SplunkError{
		StatusCode: resp.StatusCode,
		Message:    "unknown error",
		Details:    string(body),
	}
}

// ============================================================================
// 7. RETRY PATTERNS WITH EXPONENTIAL BACKOFF
// ============================================================================

// RetryConfig defines retry behavior
type RetryConfig struct {
	MaxRetries     int
	InitialBackoff time.Duration
	MaxBackoff     time.Duration
	Multiplier     float64
}

// DefaultRetryConfig returns sensible defaults
func DefaultRetryConfig() *RetryConfig {
	return &RetryConfig{
		MaxRetries:     3,
		InitialBackoff: 1 * time.Second,
		MaxBackoff:     30 * time.Second,
		Multiplier:     2.0,
	}
}

// RetryWithBackoff executes a function with exponential backoff
func RetryWithBackoff(ctx context.Context, config *RetryConfig, fn func() error) error {
	backoff := config.InitialBackoff

	for attempt := 0; attempt <= config.MaxRetries; attempt++ {
		err := fn()
		if err == nil {
			return nil
		}

		if attempt == config.MaxRetries {
			return fmt.Errorf("max retries exceeded: %w", err)
		}

		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-time.After(backoff):
			backoff = time.Duration(float64(backoff) * config.Multiplier)
			if backoff > config.MaxBackoff {
				backoff = config.MaxBackoff
			}
		}
	}

	return nil
}

// ============================================================================
// 8. CONCURRENT BATCH PROCESSING PATTERN
// ============================================================================

// BatchProcessor processes items concurrently with rate limiting
type BatchProcessor struct {
	Workers    int
	BufferSize int
}

// ProcessBatch processes items concurrently
func (bp *BatchProcessor) ProcessBatch(ctx context.Context, items []interface{}, processFn func(interface{}) error) error {
	itemsCh := make(chan interface{}, bp.BufferSize)
	errCh := make(chan error, bp.Workers)
	doneCh := make(chan struct{})

	// Start workers
	for i := 0; i < bp.Workers; i++ {
		go func() {
			for item := range itemsCh {
				if err := processFn(item); err != nil {
					select {
					case errCh <- err:
					default:
					}
				}
			}
			doneCh <- struct{}{}
		}()
	}

	// Send items
	go func() {
		for _, item := range items {
			select {
			case <-ctx.Done():
				close(itemsCh)
				return
			case itemsCh <- item:
			}
		}
		close(itemsCh)
	}()

	// Wait for workers
	for i := 0; i < bp.Workers; i++ {
		<-doneCh
	}

	select {
	case err := <-errCh:
		return err
	default:
		return nil
	}
}

// ============================================================================
// 9. RATE LIMITING PATTERN
// ============================================================================

// RateLimiter implements token bucket rate limiting
type RateLimiter struct {
	tokens   chan struct{}
	rate     time.Duration
	stopCh   chan struct{}
}

// NewRateLimiter creates a new rate limiter
func NewRateLimiter(requestsPerSecond int) *RateLimiter {
	rl := &RateLimiter{
		tokens: make(chan struct{}, requestsPerSecond),
		rate:   time.Second / time.Duration(requestsPerSecond),
		stopCh: make(chan struct{}),
	}

	// Fill initial tokens
	for i := 0; i < requestsPerSecond; i++ {
		rl.tokens <- struct{}{}
	}

	// Refill tokens
	go func() {
		ticker := time.NewTicker(rl.rate)
		defer ticker.Stop()

		for {
			select {
			case <-ticker.C:
				select {
				case rl.tokens <- struct{}{}:
				default:
				}
			case <-rl.stopCh:
				return
			}
		}
	}()

	return rl
}

// Wait blocks until a token is available
func (rl *RateLimiter) Wait(ctx context.Context) error {
	select {
	case <-ctx.Done():
		return ctx.Err()
	case <-rl.tokens:
		return nil
	}
}

// Stop stops the rate limiter
func (rl *RateLimiter) Stop() {
	close(rl.stopCh)
}

// ============================================================================
// 10. COMMON SPL QUERY PATTERNS
// ============================================================================

// SPL Query Builder Patterns (as constants)
const (
	// Time-based queries
	SPLLast24Hours   = `earliest=-24h latest=now`
	SPLLast7Days     = `earliest=-7d latest=now`
	SPLLastHour      = `earliest=-1h latest=now`
	SPLCustomTime    = `earliest="%s" latest="%s"`

	// Search patterns
	SPLBasicSearch   = `search index=%s %s`
	SPLStatsCount    = `index=%s | stats count by %s`
	SPLTimechart     = `index=%s | timechart span=%s count by %s`
	SPLTop           = `index=%s | top limit=%d %s`
	SPLRare          = `index=%s | rare limit=%d %s`

	// Transformation patterns
	SPLEval          = `| eval %s=%s`
	SPLWhere         = `| where %s`
	SPLFields        = `| fields %s`
	SPLRename        = `| rename %s as %s`
	SPLDedup         = `| dedup %s`
	SPLSort          = `| sort %s %s`
	SPLHead          = `| head %d`
	SPLTail          = `| tail %d`

	// Join pattern
	SPLJoin          = `| join type=%s %s [search index=%s | fields %s]`

	// Lookup pattern
	SPLLookup        = `| lookup %s %s OUTPUT %s`
)

// BuildSearchQuery is a helper to construct SPL queries safely
func BuildSearchQuery(index, searchTerms, timeRange string) string {
	return fmt.Sprintf(`search index=%s %s %s`, index, searchTerms, timeRange)
}

// ============================================================================
// 11. TESTING PATTERNS
// ============================================================================

// MockSplunkClient for testing
type MockSplunkClient struct {
	CreateSearchFunc     func(ctx context.Context, query string, params map[string]string) (string, error)
	GetSearchResultsFunc func(ctx context.Context, sid string, offset, count int) (*SearchResults, error)
}

func (m *MockSplunkClient) CreateSearch(ctx context.Context, query string, params map[string]string) (string, error) {
	if m.CreateSearchFunc != nil {
		return m.CreateSearchFunc(ctx, query, params)
	}
	return "mock-sid", nil
}

func (m *MockSplunkClient) GetSearchResults(ctx context.Context, sid string, offset, count int) (*SearchResults, error) {
	if m.GetSearchResultsFunc != nil {
		return m.GetSearchResultsFunc(ctx, sid, offset, count)
	}
	return &SearchResults{
		Results: []map[string]interface{}{
			{"field1": "value1", "field2": "value2"},
		},
	}, nil
}

// ============================================================================
// 12. CONFIGURATION PATTERNS
// ============================================================================

// Config represents application configuration
type Config struct {
	SplunkURL      string        `json:"splunk_url"`
	AuthToken      string        `json:"auth_token"`
	HECToken       string        `json:"hec_token"`
	DefaultIndex   string        `json:"default_index"`
	Timeout        time.Duration `json:"timeout"`
	MaxRetries     int           `json:"max_retries"`
	VerifySSL      bool          `json:"verify_ssl"`
}

// LoadConfig loads configuration from environment or file
func LoadConfig() (*Config, error) {
	// Implementation would load from env vars or config file
	return &Config{
		SplunkURL:    "https://splunk.example.com:8089",
		Timeout:      30 * time.Second,
		MaxRetries:   3,
		VerifySSL:    true,
	}, nil
}

// ============================================================================
// 13. STRUCTURED LOGGING PATTERNS
// ============================================================================

// Logger interface for structured logging
type Logger interface {
	Info(msg string, fields map[string]interface{})
	Error(msg string, err error, fields map[string]interface{})
	Debug(msg string, fields map[string]interface{})
}

// LogEvent logs with structured data ready for Splunk ingestion
func LogEvent(logger Logger, eventType string, data map[string]interface{}) {
	fields := map[string]interface{}{
		"event_type": eventType,
		"timestamp":  time.Now().Unix(),
	}

	for k, v := range data {
		fields[k] = v
	}

	logger.Info(eventType, fields)
}

// ============================================================================
// USAGE EXAMPLES
// ============================================================================

/*
Example 1: Send events to HEC

	hecClient := &HECClient{
		URL:   "https://splunk.example.com:8088/services/collector",
		Token: "your-hec-token",
		HTTPClient: &http.Client{Timeout: 10 * time.Second},
	}

	event := &HECEvent{
		Time:       time.Now().Unix(),
		Host:       "myapp",
		Source:     "application",
		SourceType: "json",
		Index:      "main",
		Event: map[string]interface{}{
			"level":   "info",
			"message": "User logged in",
			"user_id": 12345,
		},
	}

	err := hecClient.SendEvent(context.Background(), event)

Example 2: Execute a search

	client := NewSplunkClient("https://splunk.example.com:8089", "your-token")

	sid, err := client.CreateSearch(
		context.Background(),
		"search index=main error | stats count by host",
		map[string]string{"earliest_time": "-24h"},
	)

	if err := client.WaitForSearch(context.Background(), sid); err != nil {
		log.Fatal(err)
	}

	results, err := client.GetSearchResults(context.Background(), sid, 0, 100)

Example 3: Batch processing with rate limiting

	rateLimiter := NewRateLimiter(10) // 10 requests per second
	defer rateLimiter.Stop()

	for _, item := range items {
		if err := rateLimiter.Wait(ctx); err != nil {
			return err
		}
		// Process item
	}

Example 4: Retry with backoff

	config := DefaultRetryConfig()
	err := RetryWithBackoff(ctx, config, func() error {
		return hecClient.SendEvent(ctx, event)
	})

*/
