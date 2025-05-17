import os
import logging
import json
import datetime
import uuid
import subprocess
import tempfile
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from config import Config
from database import db as supabase_db
import sqlite3

# Import the shared SQLAlchemy instance
from extensions import db

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key-for-development")

# Load configuration
app.config.from_object(Config)

# Set environment variables for Supabase
os.environ["SUPABASE_URL"] = os.environ.get("SUPABASE_URL", "https://xxwrambzzwfmxqytoroh.supabase.co")
os.environ["SUPABASE_ANON_KEY"] = os.environ.get("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh4d3JhbWJ6endmbXhxeXRvcm9oIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDcwMDg3MzUsImV4cCI6MjA2MjU4NDczNX0.5Lhs8qnzbjQSSF_TH_ouamrWEmte6L3bb3_DRxpeRII")
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh4d3JhbWJ6endmbXhxeXRvcm9oIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NzAwODczNSwiZXhwIjoyMDYyNTg0NzM1fQ.gTjSiNnCTtz4D6GrBFs3UTr-liUNdNuJ7IKtdP2KLro")
os.environ["JWT_SECRET"] = os.environ.get("JWT_SECRET", "4hK0mlO2DRol5s/f2SlmjsXuDGHVtqM96RdrUfiLN62gec2guQj0Vzy380k/MYuqa/4NT+7jT2DOhmi62zFOCw==")

# Configure SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///alpha_q.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the app with the SQLAlchemy extension
db.init_app(app)

# Helper function to simulate running commands for the AI
def run_command(command):
    """Run a shell command and return the output."""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=10
        )
        return {
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            'stdout': '',
            'stderr': 'Command timed out after 10 seconds',
            'returncode': -1
        }
    except Exception as e:
        return {
            'stdout': '',
            'stderr': f'Error executing command: {str(e)}',
            'returncode': -1
        }

# Import Enhanced AI module (without external dependencies)
from enhanced_ai import EnhancedAI

# Initialize AI component
enhanced_ai = EnhancedAI()

# Helper function for AI responses
def generate_ai_response(message, conversation_history=None):
    """
    Generate AI response based on the user message using our enhanced AI.
    
    Args:
        message (str): User's message
        conversation_history (list, optional): List of previous messages
        
    Returns:
        dict: AI response with message and reasoning
    """
    # Keep original command execution functionality
    message_lower = message.lower()
    
    # Process commands separately from AI responses
    if message_lower.startswith('run:') or message_lower.startswith('execute:'):
        cmd = message[message.find(':')+1:].strip()
        result = run_command(cmd)
        if result['returncode'] == 0:
            response = f"Command executed successfully. Output:\n```\n{result['stdout']}\n```"
        else:
            response = f"Command failed with error code {result['returncode']}. Error:\n```\n{result['stderr']}\n```"
        reasoning = f"User requested command execution: '{cmd}'. I ran the command and returned the output."
        
        return {
            'message': response,
            'reasoning': reasoning,
            'model_used': 'command_processor',
            'type': 'command'
        }
    
    # File operations
    elif 'create file' in message_lower or 'write file' in message_lower:
        # Extract filename and content from message
        parts = message.split('with content', 1)
        if len(parts) > 1:
            filename = parts[0].replace('create file', '').replace('write file', '').strip()
            content = parts[1].strip()
            
            # Create a temporary file
            try:
                with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                    f.write(content)
                
                response = f"I've prepared the file '{filename}' with the specified content. You can download it from the temporary location: {f.name}"
                reasoning = f"User asked to create a file '{filename}' with specific content. I created a temporary file."
            except Exception as e:
                response = f"I couldn't create the file: {str(e)}"
                reasoning = f"User asked to create a file, but I encountered an error: {str(e)}"
        else:
            response = "I need both a filename and content to create a file. Please provide them in the format: 'Create file filename.txt with content your-content-here'"
            reasoning = "User's request to create a file was missing either the filename or content."
            
        return {
            'message': response,
            'reasoning': reasoning,
            'model_used': 'file_handler',
            'type': 'file_operation'
        }
    
    # For all other messages, use our Enhanced AI to generate a response
    try:
        # Get response from Enhanced AI
        ai_response = enhanced_ai.generate_response(message, conversation_history)
        return ai_response
    except Exception as e:
        logger.error(f"Error generating AI response: {str(e)}")
        # Fallback response
        return {
            'message': f"I'm having trouble processing your request due to a technical issue. Could you try rephrasing your question? (Error: {str(e)})",
            'reasoning': f"An error occurred while generating an AI response: {str(e)}",
            'model_used': 'error_handler',
            'type': 'error'
        

# Import models after initializing db
from models import User, Project, ChatMessage, AIModel, init_db

# Initialize the database
try:
    init_db(app)
except Exception as e:
    logger.error(f"Error initializing database: {str(e)}")

# Store conversations in memory for demo purposes
# In production, these would be stored in a database
conversations = {}

# Add global template context processor
@app.context_processor
def inject_global_context():
    # Always authenticated with HuggingFace
    is_authenticated = True
    
    # Database connection status (check Supabase connection)
    db_connected = supabase_db.check_connection()
    
    # SQLite database connection status
    sqlite_connected = False
    try:
        # Check if we can query the database
        User.query.first()
        sqlite_connected = True
    except Exception as e:
        logger.warning(f"SQLite database connection check failed: {str(e)}")
    
    # Get current time for timestamps
    current_time = datetime.datetime.now().strftime("%H:%M")
    
    # Get active AI model
    try:
        active_model = AIModel.query.filter_by(is_active=True).first()
        model_name = active_model.name if active_model else "Deepseek-Coder-33B-Instruct"
    except Exception as e:
        logger.warning(f"Error querying active model: {str(e)}")
        model_name = "Deepseek-Coder-33B-Instruct"
    
    # Add Alpha-Q specific context
    return dict(
        is_authenticated=is_authenticated,
        app_name="Alpha-Q",
        app_description="AI Application Builder",
        db_connected=db_connected,
        sqlite_connected=sqlite_connected,
        supabase_url=os.environ.get("SUPABASE_URL"),
        current_time=current_time,
        active_model=model_name
    )

@app.route('/')
def index():
    """Render the main page for Alpha-Q."""
    # Check if user is already in a conversation
    conversation_id = session.get('conversation_id')
    if conversation_id:
        # Redirect to chat if there's an active conversation
        return redirect(url_for('chat'))
    
    # Check Supabase database connection
    supabase_connected = supabase_db.check_connection()
    
    # Check SQLite database connection
    sqlite_connected = False
    try:
        # Check if we can query the database
        User.query.first()
        sqlite_connected = True
    except Exception as e:
        logger.warning(f"SQLite database connection check failed: {str(e)}")
    
    # Get Supabase database info
    db_info = supabase_db.get_database_info()
    
    return render_template('index.html', 
                          supabase_connected=supabase_connected,
                          sqlite_connected=sqlite_connected,
                          db_info=db_info)

@app.route('/chat')
def chat():
    """Render the chat interface."""
    conversation_id = session.get('conversation_id')
    messages = []
    
    # Generate new conversation ID if none exists
    if not conversation_id:
        conversation_id = str(uuid.uuid4())
        session['conversation_id'] = conversation_id
        conversations[conversation_id] = []
    
    # Get previous messages for this conversation from memory cache
    if conversation_id in conversations:
        messages = conversations[conversation_id]
    
    # If no messages in memory, try to get from database
    if not messages:
        try:
            messages_db = ChatMessage.query.filter_by(conversation_id=conversation_id).order_by(ChatMessage.timestamp).all()
            
            # Convert database messages to the format used in memory
            for msg in messages_db:
                message_dict = {
                    'role': msg.role,
                    'content': msg.content,
                    'timestamp': msg.timestamp.isoformat() if hasattr(msg.timestamp, 'isoformat') else str(msg.timestamp)
                }
                messages.append(message_dict)
                
            # Cache in memory
            conversations[conversation_id] = messages
        except Exception as e:
            logger.error(f"Error loading messages from database: {str(e)}")
    
    return render_template('chat.html', messages=messages)

@app.route('/models')
def models():
    """Render the models management interface."""
    # Get list of models from database
    try:
        models_list = AIModel.query.all()
    except Exception as e:
        logger.error(f"Error querying models: {str(e)}")
        models_list = []
    
    return render_template('models.html', models=models_list)

@app.route('/chat/message', methods=['POST'])
def chat_message():
    """Handle chat messages and return AI responses."""
    message = request.form.get('message', '')
    
    if not message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Generate conversation ID if not present
    conversation_id = session.get('conversation_id')
    if not conversation_id:
        conversation_id = str(uuid.uuid4())
        session['conversation_id'] = conversation_id
        conversations[conversation_id] = []
    
    # Store user message in memory (would go to database in production)
    user_message = {
        'role': 'user',
        'content': message,
        'timestamp': datetime.datetime.now().isoformat()
    }
    
    if conversation_id not in conversations:
        conversations[conversation_id] = []
    
    conversations[conversation_id].append(user_message)
    
    # Generate AI response
    ai_response = generate_ai_response(message)
    
    # Store AI response in memory
    assistant_message = {
        'role': 'assistant',
        'content': ai_response['message'],
        'reasoning': ai_response['reasoning'],
        'timestamp': datetime.datetime.now().isoformat()
    }
    
    conversations[conversation_id].append(assistant_message)
    
    # In a production app, we would store messages in the database:
    try:
        # Create demo user if needed
        user = User.query.filter_by(username='demo_user').first()
        if not user:
            user = User()
            user.username = 'demo_user'
            user.email = 'demo@example.com'
            db.session.add(user)
            db.session.commit()
        
        # Save messages to database
        user_chat_message = ChatMessage()
        user_chat_message.content = message
        user_chat_message.role = 'user'
        user_chat_message.conversation_id = conversation_id
        user_chat_message.user_id = user.id
        
        assistant_chat_message = ChatMessage()
        assistant_chat_message.content = ai_response['message']
        assistant_chat_message.role = 'assistant'
        assistant_chat_message.conversation_id = conversation_id
        assistant_chat_message.user_id = user.id
        
        db.session.add(user_chat_message)
        db.session.add(assistant_chat_message)
        db.session.commit()
    except Exception as e:
        logger.error(f"Error saving messages to database: {str(e)}")
    
    return jsonify(ai_response)

@app.route('/api/info')
def api_info():
    """Return basic info about the Alpha-Q application."""
    return jsonify({
        "name": "Alpha-Q",
        "version": "1.0.0",
        "description": "AI Application Builder",
        "features": [
            "Natural Language & Voice AI (local text + voice)",
            "Persistent Memory (Supabase DB or local DB + vector store)",
            "Full-Stack Code Creation, Issue Fixing, Deployment",
            "System Control & CLI Execution",
            "Web Preview/Build/Deploy",
            "Auth + GitHub Integration",
            "Browser & Internet Automation",
            "Bitget Integration",
            "User-Centric Learning/Context Retention"
        ],
        "database": db.get_database_info(),
        "huggingface": {
            "connected": True,
            "models": [
                "Deepseek-Coder-33B-Instruct",
                "CodeLlama-34B-Instruct",
                "Mixtral-8x7B-Instruct"
            ]
        }
    })

@app.route('/api/models')
def api_models():
    """Return information about available AI models."""
    return jsonify({
        "models": [
            {
                "id": "deepseek-coder-33b-instruct",
                "name": "Deepseek-Coder-33B-Instruct",
                "description": "A powerful code generation model trained on code repositories",
                "status": "active",
                "type": "code",
                "provider": "huggingface"
            },
            {
                "id": "codellama-34b-instruct",
                "name": "CodeLlama-34B-Instruct",
                "description": "Meta's code-specialized model for programming tasks",
                "status": "available",
                "type": "code",
                "provider": "huggingface"
            },
            {
                "id": "mixtral-8x7b-instruct",
                "name": "Mixtral-8x7B-Instruct",
                "description": "Mixture of Experts model with strong reasoning capabilities",
                "status": "available",
                "type": "general",
                "provider": "huggingface"
            }
        ],
        "active_model": "deepseek-coder-33b-instruct"
    })

@app.route('/authenticate', methods=['POST'])
def authenticate():
    """Authenticate with Alpha-Q using provided credentials."""
    token = request.form.get('token')
    
    if not token:
        flash('API token is required for authentication', 'danger')
        return redirect(url_for('index'))
    
    # Store the token in the session
    session['hf_token'] = token  # Keep this for compatibility
    session['api_token'] = token
    os.environ["HUGGINGFACE_TOKEN"] = token
    
    flash('Successfully authenticated with Alpha-Q!', 'success')
    return redirect(url_for('index'))

@app.route('/create-app', methods=['POST'])
def create_app():
    """Create a new application based on user specifications."""
    # Check if user is authenticated
    token = session.get('api_token') or session.get('hf_token') or os.environ.get("HUGGINGFACE_TOKEN")
    if not token:
        flash('You must authenticate first!', 'danger')
        return redirect(url_for('index'))
    
    app_name = request.form.get('app_name')
    app_description = request.form.get('app_description')
    app_type = request.form.get('app_type', 'web')
    framework = request.form.get('framework', 'react')
    
    # Validation
    if not app_name:
        flash('Application name is required', 'danger')
        return redirect(url_for('index'))
    
    if not app_description:
        flash('Application description is required', 'danger')
        return redirect(url_for('index'))
    
    try:
        # Simulate app creation process
        logger.info(f"Creating new {app_type} application: {app_name}")
        logger.info(f"Using framework: {framework}")
        
        # In a real implementation, we would generate the app structure and files
        project_details = {
            "name": app_name,
            "description": app_description,
            "type": app_type,
            "framework": framework,
            "created_at": "2025-05-13",
            "status": "created"
        }
        
        # Store project details in session for demo
        session['project'] = project_details
        
        flash(f"Successfully created {app_name} application!", 'success')
        return render_template('success.html', 
                              repo_name=app_name, 
                              repo_url=f"https://github.com/user/{app_name}")
            
    except Exception as e:
        logger.error(f"App creation error: {str(e)}")
        flash(f'Error during app creation: {str(e)}', 'danger')
        return render_template('error.html', error=str(e))

@app.route('/upload-model', methods=['POST'])
def upload_model():
    """Handle model upload to Hugging Face Hub (legacy route)."""
    # Redirect to new create-app route
    return redirect(url_for('create_app'))

@app.route('/logout')
def logout():
    """Clear authentication token."""
    # Clear from session
    if 'hf_token' in session:
        session.pop('hf_token')
    if 'api_token' in session:
        session.pop('api_token')
    if 'project' in session:
        session.pop('project')
    # Clear from environment
    if 'HUGGINGFACE_TOKEN' in os.environ:
        del os.environ['HUGGINGFACE_TOKEN']
    flash('Successfully logged out', 'success')
    return redirect(url_for('index'))

@app.route('/api/projects')
def api_projects():
    """Return list of user projects (mock data for now)."""
    if not session.get('api_token'):
        return jsonify({"error": "Not authenticated"}), 401
    
    # Mock project data
    projects = [
        {
            "id": 1,
            "name": "React Dashboard",
            "description": "Admin dashboard with React and Material UI",
            "type": "web",
            "framework": "react",
            "created_at": "2025-05-10",
            "status": "completed"
        },
        {
            "id": 2,
            "name": "E-commerce API",
            "description": "REST API for e-commerce platform",
            "type": "backend",
            "framework": "express",
            "created_at": "2025-05-11",
            "status": "in_progress"
        }
    ]
    
    # Add current project if available
    if session.get('project'):
        projects.append(session['project'])
    
    return jsonify({"projects": projects})

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error="Internal server error"), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
