"""
Sample API server for testing the reverse engineering tool.

This creates a simple Flask API that can be used to test the traffic capture
and analysis functionality.
"""

from flask import Flask, jsonify, request, abort
import time
import random


app = Flask(__name__)

# Sample data
USERS = [
    {"id": 1, "name": "John Doe", "email": "john@example.com", "age": 30},
    {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "age": 25},
    {"id": 3, "name": "Bob Johnson", "email": "bob@example.com", "age": 35}
]

POSTS = [
    {"id": 1, "user_id": 1, "title": "Hello World", "content": "This is my first post"},
    {"id": 2, "user_id": 1, "title": "Python is Great", "content": "I love Python programming"},
    {"id": 3, "user_id": 2, "title": "API Design", "content": "Best practices for API design"}
]

# Simple auth token for testing
VALID_TOKEN = "test-token-12345"

def require_auth():
    """Check for valid authentication."""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        abort(401, description="Missing Authorization header")
    
    if not auth_header.startswith('Bearer '):
        abort(401, description="Invalid authorization format")
    
    token = auth_header[7:]  # Remove 'Bearer ' prefix
    if token != VALID_TOKEN:
        abort(401, description="Invalid token")

def add_rate_limit_headers(response):
    """Add rate limiting headers to responses."""
    response.headers['X-RateLimit-Limit'] = '100'
    response.headers['X-RateLimit-Remaining'] = str(random.randint(50, 99))
    response.headers['X-RateLimit-Reset'] = str(int(time.time()) + 3600)
    return response

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found", "message": str(error.description)}), 404

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({"error": "Unauthorized", "message": str(error.description)}), 401

@app.errorhandler(400)
def bad_request(error):
    return jsonify({"error": "Bad request", "message": str(error.description)}), 400

# Public endpoints (no auth required)
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    response = jsonify({"status": "healthy", "timestamp": time.time()})
    return add_rate_limit_headers(response)

@app.route('/version', methods=['GET'])
def get_version():
    """Get API version."""
    response = jsonify({"version": "1.0.0", "name": "Sample API"})
    return add_rate_limit_headers(response)

# User endpoints (require auth)
@app.route('/users', methods=['GET'])
def get_users():
    """Get all users with optional pagination."""
    require_auth()
    
    # Handle pagination
    limit = request.args.get('limit', default=10, type=int)
    offset = request.args.get('offset', default=0, type=int)
    include = request.args.get('include', default='')
    
    users = USERS[offset:offset+limit]
    
    # Handle include parameter
    if include == 'posts':
        for user in users:
            user['posts'] = [p for p in POSTS if p['user_id'] == user['id']]
    
    response = jsonify({
        "users": users,
        "total": len(USERS),
        "limit": limit,
        "offset": offset
    })
    return add_rate_limit_headers(response)

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get a specific user by ID."""
    require_auth()
    
    user = next((u for u in USERS if u['id'] == user_id), None)
    if not user:
        abort(404, description=f"User {user_id} not found")
    
    # Handle include parameter
    include = request.args.get('include', default='')
    if include == 'posts':
        user = user.copy()
        user['posts'] = [p for p in POSTS if p['user_id'] == user_id]
    
    response = jsonify(user)
    return add_rate_limit_headers(response)

@app.route('/users', methods=['POST'])
def create_user():
    """Create a new user."""
    require_auth()
    
    if not request.is_json:
        abort(400, description="Request must be JSON")
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'email']
    for field in required_fields:
        if field not in data:
            abort(400, description=f"Missing required field: {field}")
    
    # Create new user
    new_id = max(u['id'] for u in USERS) + 1
    new_user = {
        "id": new_id,
        "name": data['name'],
        "email": data['email'],
        "age": data.get('age', 0)
    }
    
    USERS.append(new_user)
    
    response = jsonify(new_user)
    response.status_code = 201
    return add_rate_limit_headers(response)

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update a user."""
    require_auth()
    
    user = next((u for u in USERS if u['id'] == user_id), None)
    if not user:
        abort(404, description=f"User {user_id} not found")
    
    if not request.is_json:
        abort(400, description="Request must be JSON")
    
    data = request.get_json()
    
    # Update user fields
    for field in ['name', 'email', 'age']:
        if field in data:
            user[field] = data[field]
    
    response = jsonify(user)
    return add_rate_limit_headers(response)

@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete a user."""
    require_auth()
    
    user_index = next((i for i, u in enumerate(USERS) if u['id'] == user_id), None)
    if user_index is None:
        abort(404, description=f"User {user_id} not found")
    
    deleted_user = USERS.pop(user_index)
    
    response = jsonify({"message": "User deleted", "user": deleted_user})
    return add_rate_limit_headers(response)

# Post endpoints
@app.route('/posts', methods=['GET'])
def get_posts():
    """Get all posts with optional filtering."""
    require_auth()
    
    user_id = request.args.get('user_id', type=int)
    limit = request.args.get('limit', default=10, type=int)
    offset = request.args.get('offset', default=0, type=int)
    
    posts = POSTS
    if user_id:
        posts = [p for p in posts if p['user_id'] == user_id]
    
    posts = posts[offset:offset+limit]
    
    response = jsonify({
        "posts": posts,
        "total": len(posts),
        "limit": limit,
        "offset": offset
    })
    return add_rate_limit_headers(response)

@app.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """Get a specific post by ID."""
    require_auth()
    
    post = next((p for p in POSTS if p['id'] == post_id), None)
    if not post:
        abort(404, description=f"Post {post_id} not found")
    
    response = jsonify(post)
    return add_rate_limit_headers(response)

@app.route('/users/<int:user_id>/posts', methods=['GET'])
def get_user_posts(user_id):
    """Get posts for a specific user."""
    require_auth()
    
    # Check if user exists
    user = next((u for u in USERS if u['id'] == user_id), None)
    if not user:
        abort(404, description=f"User {user_id} not found")
    
    user_posts = [p for p in POSTS if p['user_id'] == user_id]
    
    response = jsonify({"posts": user_posts})
    return add_rate_limit_headers(response)

@app.route('/users/<int:user_id>/posts', methods=['POST'])
def create_user_post(user_id):
    """Create a new post for a user."""
    require_auth()
    
    # Check if user exists
    user = next((u for u in USERS if u['id'] == user_id), None)
    if not user:
        abort(404, description=f"User {user_id} not found")
    
    if not request.is_json:
        abort(400, description="Request must be JSON")
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['title', 'content']
    for field in required_fields:
        if field not in data:
            abort(400, description=f"Missing required field: {field}")
    
    # Create new post
    new_id = max(p['id'] for p in POSTS) + 1
    new_post = {
        "id": new_id,
        "user_id": user_id,
        "title": data['title'],
        "content": data['content']
    }
    
    POSTS.append(new_post)
    
    response = jsonify(new_post)
    response.status_code = 201
    return add_rate_limit_headers(response)

if __name__ == '__main__':
    print("Starting Sample API Server...")
    print("Available endpoints:")
    print("  GET  /health - Health check (no auth)")
    print("  GET  /version - API version (no auth)")
    print("  GET  /users - List users (auth required)")
    print("  GET  /users/{id} - Get user (auth required)")
    print("  POST /users - Create user (auth required)")
    print("  PUT  /users/{id} - Update user (auth required)")
    print("  DELETE /users/{id} - Delete user (auth required)")
    print("  GET  /posts - List posts (auth required)")
    print("  GET  /posts/{id} - Get post (auth required)")
    print("  GET  /users/{id}/posts - Get user posts (auth required)")
    print("  POST /users/{id}/posts - Create user post (auth required)")
    print("")
    print("Authentication: Bearer test-token-12345")
    print("Rate limiting headers included in all responses")
    print("")
    print("Server running on http://localhost:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)