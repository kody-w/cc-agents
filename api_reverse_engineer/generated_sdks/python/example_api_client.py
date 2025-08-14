import requests
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json
from urllib.parse import urljoin, quote

# Data Classes
class ListUsersResponse:
    users: List[Dict[str, Any]]
    total: int
    page: int
    limit: int

class ListUsersResponse:
    id: int
    name: str
    email: str
    created_at: str
    is_active: bool
    profile: Dict[str, Any]

class CreateUserRequest:
    name: str
    email: str
    password: str
    profile: Dict[str, Any]

class UpdateUserRequest:
    name: str
    email: str
    is_active: bool

class UpdateUserResponse:
    id: int
    name: str
    email: str
    created_at: str
    updated_at: str
    is_active: bool

class ListPostsResponse:
    posts: List[Dict[str, Any]]
    total: int

class CreatePostRequest:
    title: str
    content: str
    tags: List[str]
    status: str


class ExampleapiClient:
    """
    Auto-generated SDK for ExampleAPI API
    Base URL: https://api.example.com
    """
    
    def __init__(self, base_url: str = "https://api.example.com", headers: Optional[Dict[str, str]] = None):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        if headers:
            self.session.headers.update(headers)
    
    def set_auth_token(self, token: str):
        """Set the authorization token for all requests"""
        self.session.headers["Authorization"] = f"Bearer {token}"
    
    def set_header(self, key: str, value: str):
        """Set a custom header for all requests"""
        self.session.headers[key] = value

    def list_users(self, **kwargs) -> Dict[str, Any]:
        """
        GET /v1/users
        """
        path = f"/v1/users"
        url = urljoin(self.base_url, path)
        
        response = self.session.get(url, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else {}
    
    def list_users(self, id: str, **kwargs) -> Dict[str, Any]:
        """
        GET /v1/users/{id}
        
        Path Parameters:
            - id: str
        """
        path = f"/v1/users/{quote(str(id))}"
        url = urljoin(self.base_url, path)
        
        response = self.session.get(url, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else {}
    
    def create_user(self, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """
        POST /v1/users
        
        Request Body:
            Dict[str, Any]
        """
        path = f"/v1/users"
        url = urljoin(self.base_url, path)
        
        if data and isinstance(data, dict):
            json_data = data
        elif data:
            json_data = data if isinstance(data, dict) else vars(data)
        else:
            json_data = None
        response = self.session.post(url, json=json_data, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else {}
    
    def update_user(self, id: str, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """
        PUT /v1/users/{id}
        
        Path Parameters:
            - id: str
        
        Request Body:
            Dict[str, Any]
        """
        path = f"/v1/users/{quote(str(id))}"
        url = urljoin(self.base_url, path)
        
        if data and isinstance(data, dict):
            json_data = data
        elif data:
            json_data = data if isinstance(data, dict) else vars(data)
        else:
            json_data = None
        response = self.session.put(url, json=json_data, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else {}
    
    def delete_user(self, id: str, **kwargs) -> Dict[str, Any]:
        """
        DELETE /v1/users/{id}
        
        Path Parameters:
            - id: str
        """
        path = f"/v1/users/{quote(str(id))}"
        url = urljoin(self.base_url, path)
        
        response = self.session.delete(url, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else {}
    
    def list_posts(self, **kwargs) -> Dict[str, Any]:
        """
        GET /v1/posts
        """
        path = f"/v1/posts"
        url = urljoin(self.base_url, path)
        
        response = self.session.get(url, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else {}
    
    def create_post(self, data: Optional[Dict[str, Any]] = None, **kwargs) -> Dict[str, Any]:
        """
        POST /v1/posts
        
        Request Body:
            Dict[str, Any]
        """
        path = f"/v1/posts"
        url = urljoin(self.base_url, path)
        
        if data and isinstance(data, dict):
            json_data = data
        elif data:
            json_data = data if isinstance(data, dict) else vars(data)
        else:
            json_data = None
        response = self.session.post(url, json=json_data, **kwargs)
        response.raise_for_status()
        return response.json() if response.content else {}
    