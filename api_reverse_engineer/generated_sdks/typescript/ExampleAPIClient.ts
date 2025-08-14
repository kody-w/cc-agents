// Auto-generated TypeScript SDK for ExampleAPI API
// Base URL: https://api.example.com

// Type Definitions
interface ListUsersResponse {
  users: Record<string, any>[];
  total: number;
  page: number;
  limit: number;
}

interface ListUsersResponse {
  id: number;
  name: string;
  email: string;
  created_at: string;
  is_active: boolean;
  profile: Record<string, any>;
}

interface CreateUserRequest {
  name: string;
  email: string;
  password: string;
  profile: Record<string, any>;
}

interface UpdateUserRequest {
  name: string;
  email: string;
  is_active: boolean;
}

interface UpdateUserResponse {
  id: number;
  name: string;
  email: string;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}

interface ListPostsResponse {
  posts: Record<string, any>[];
  total: number;
}

interface CreatePostRequest {
  title: string;
  content: string;
  tags: string[];
  status: string;
}

// API Client
export class ExampleapiClient {
  private baseUrl: string;
  private headers: Record<string, string>;

  constructor(baseUrl: string = 'https://api.example.com', headers: Record<string, string> = {}) {
    this.baseUrl = baseUrl.replace(/\/+$/, '');
    this.headers = {
      'Content-Type': 'application/json',
      ...headers
    };
  }

  setAuthToken(token: string): void {
    this.headers['Authorization'] = `Bearer ${token}`;
  }

  setHeader(key: string, value: string): void {
    this.headers[key] = value;
  }

  private async request<T>(options: {
    method: string;
    path: string;
    params?: Record<string, any>;
    body?: any;
    headers?: Record<string, string>;
  }): Promise<T> {
    const url = new URL(`${this.baseUrl}${options.path}`);
    
    if (options.params) {
      Object.entries(options.params).forEach(([key, value]) => {
        if (value !== null && value !== undefined) {
          url.searchParams.append(key, String(value));
        }
      });
    }
    
    const response = await fetch(url.toString(), {
      method: options.method,
      headers: {
        ...this.headers,
        ...options.headers
      },
      body: options.body ? JSON.stringify(options.body) : undefined
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return response.json() as Promise<T>;
    }
    
    return {} as T;
  }

  async list_users(): Promise<Record<string, any>> {
    const path = `/v1/users`;
    
    return this.request<Record<string, any>>({
      method: 'GET',
      path,
    });
  }

  async list_users(id: string): Promise<Record<string, any>> {
    const path = `/v1/users/${id}`;
    
    return this.request<Record<string, any>>({
      method: 'GET',
      path,
    });
  }

  async create_user(data?: Record<string, any>): Promise<any> {
    const path = `/v1/users`;
    
    return this.request<any>({
      method: 'POST',
      path,
      body: data,
    });
  }

  async update_user(id: string, data?: Record<string, any>): Promise<Record<string, any>> {
    const path = `/v1/users/${id}`;
    
    return this.request<Record<string, any>>({
      method: 'PUT',
      path,
      body: data,
    });
  }

  async delete_user(id: string): Promise<any> {
    const path = `/v1/users/${id}`;
    
    return this.request<any>({
      method: 'DELETE',
      path,
    });
  }

  async list_posts(): Promise<Record<string, any>> {
    const path = `/v1/posts`;
    
    return this.request<Record<string, any>>({
      method: 'GET',
      path,
    });
  }

  async create_post(data?: Record<string, any>): Promise<any> {
    const path = `/v1/posts`;
    
    return this.request<any>({
      method: 'POST',
      path,
      body: data,
    });
  }

}