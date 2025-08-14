package example_api

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"strings"
	"time"
)
// Type Definitions
type ListUsersResponse struct {
    Users []map[string]interface{} `json:"users"`
    Total int `json:"total"`
    Page int `json:"page"`
    Limit int `json:"limit"`
}

type ListUsersResponse struct {
    Id int `json:"id"`
    Name string `json:"name"`
    Email string `json:"email"`
    CreatedAt string `json:"created_at"`
    IsActive bool `json:"is_active"`
    Profile map[string]interface{} `json:"profile"`
}

type CreateUserRequest struct {
    Name string `json:"name"`
    Email string `json:"email"`
    Password string `json:"password"`
    Profile map[string]interface{} `json:"profile"`
}

type UpdateUserRequest struct {
    Name string `json:"name"`
    Email string `json:"email"`
    IsActive bool `json:"is_active"`
}

type UpdateUserResponse struct {
    Id int `json:"id"`
    Name string `json:"name"`
    Email string `json:"email"`
    CreatedAt string `json:"created_at"`
    UpdatedAt string `json:"updated_at"`
    IsActive bool `json:"is_active"`
}

type ListPostsResponse struct {
    Posts []map[string]interface{} `json:"posts"`
    Total int `json:"total"`
}

type CreatePostRequest struct {
    Title string `json:"title"`
    Content string `json:"content"`
    Tags []string `json:"tags"`
    Status string `json:"status"`
}

// Client Definition
type ExampleapiClient struct {
	BaseURL    string
	HTTPClient *http.Client
	Headers    map[string]string
}

// NewExampleapiClient creates a new API client
func NewExampleapiClient(baseURL string) *ExampleapiClient {
	if baseURL == "" {
		baseURL = "https://api.example.com"
	}
	return &ExampleapiClient{
		BaseURL:    strings.TrimSuffix(baseURL, "/"),
		HTTPClient: &http.Client{Timeout: 30 * time.Second},
		Headers:    make(map[string]string),
	}
}

// SetAuthToken sets the authorization token
func (c *ExampleapiClient) SetAuthToken(token string) {
	c.Headers["Authorization"] = fmt.Sprintf("Bearer %s", token)
}

// SetHeader sets a custom header
func (c *ExampleapiClient) SetHeader(key, value string) {
	c.Headers[key] = value
}

// doRequest performs the HTTP request
func (c *ExampleapiClient) doRequest(method, path string, params url.Values, body interface{}) ([]byte, error) {
	fullURL := c.BaseURL + path
	if params != nil && len(params) > 0 {
		fullURL = fullURL + "?" + params.Encode()
	}
	
	var bodyReader io.Reader
	if body != nil {
		jsonBody, err := json.Marshal(body)
		if err != nil {
			return nil, err
		}
		bodyReader = bytes.NewBuffer(jsonBody)
	}
	
	req, err := http.NewRequest(method, fullURL, bodyReader)
	if err != nil {
		return nil, err
	}
	
	if body != nil {
		req.Header.Set("Content-Type", "application/json")
	}
	
	for key, value := range c.Headers {
		req.Header.Set(key, value)
	}
	
	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()
	
	responseBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	
	if resp.StatusCode >= 400 {
		return nil, fmt.Errorf("API error: status=%d, body=%s", resp.StatusCode, string(responseBody))
	}
	
	return responseBody, nil
}

// ListUsers performs GET /v1/users
func (c *ExampleapiClient) ListUsers() (*ListUsersResponse, error) {
	path := "/v1/users"
	
	responseBody, err := c.doRequest("GET", path, nil, nil)
	if err != nil {
		return nil, err
	}
	
	var result ListUsersResponse
	if err := json.Unmarshal(responseBody, &result); err != nil {
		return nil, err
	}
	return &result, nil
}

// ListUsers performs GET /v1/users/{id}
func (c *ExampleapiClient) ListUsers(id string) (*ListUsersResponse, error) {
	path := `/v1/users/{id}`
	path = strings.Replace(path, "{id}", id, 1)
	
	responseBody, err := c.doRequest("GET", path, nil, nil)
	if err != nil {
		return nil, err
	}
	
	var result ListUsersResponse
	if err := json.Unmarshal(responseBody, &result); err != nil {
		return nil, err
	}
	return &result, nil
}

// CreateUser performs POST /v1/users
func (c *ExampleapiClient) CreateUser(data *CreateUserRequest) (map[string]interface{}, error) {
	path := "/v1/users"
	
	responseBody, err := c.doRequest("POST", path, nil, data)
	if err != nil {
		return nil, err
	}
	
	var result map[string]interface{}
	if err := json.Unmarshal(responseBody, &result); err != nil {
		return nil, err
	}
	return result, nil
}

// UpdateUser performs PUT /v1/users/{id}
func (c *ExampleapiClient) UpdateUser(id string, data *UpdateUserRequest) (*UpdateUserResponse, error) {
	path := `/v1/users/{id}`
	path = strings.Replace(path, "{id}", id, 1)
	
	responseBody, err := c.doRequest("PUT", path, nil, data)
	if err != nil {
		return nil, err
	}
	
	var result UpdateUserResponse
	if err := json.Unmarshal(responseBody, &result); err != nil {
		return nil, err
	}
	return &result, nil
}

// DeleteUser performs DELETE /v1/users/{id}
func (c *ExampleapiClient) DeleteUser(id string) (map[string]interface{}, error) {
	path := `/v1/users/{id}`
	path = strings.Replace(path, "{id}", id, 1)
	
	responseBody, err := c.doRequest("DELETE", path, nil, nil)
	if err != nil {
		return nil, err
	}
	
	var result map[string]interface{}
	if err := json.Unmarshal(responseBody, &result); err != nil {
		return nil, err
	}
	return result, nil
}

// ListPosts performs GET /v1/posts
func (c *ExampleapiClient) ListPosts() (*ListPostsResponse, error) {
	path := "/v1/posts"
	
	responseBody, err := c.doRequest("GET", path, nil, nil)
	if err != nil {
		return nil, err
	}
	
	var result ListPostsResponse
	if err := json.Unmarshal(responseBody, &result); err != nil {
		return nil, err
	}
	return &result, nil
}

// CreatePost performs POST /v1/posts
func (c *ExampleapiClient) CreatePost(data *CreatePostRequest) (map[string]interface{}, error) {
	path := "/v1/posts"
	
	responseBody, err := c.doRequest("POST", path, nil, data)
	if err != nil {
		return nil, err
	}
	
	var result map[string]interface{}
	if err := json.Unmarshal(responseBody, &result); err != nil {
		return nil, err
	}
	return result, nil
}