import os
import logging
from flask import Flask, render_template, request, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from datetime import datetime

# Import components
from src.utils.logger import setup_logger
from src.utils import config
from src.database.db_connector import db
from models.chatbot_model import model_handler
from src.database.query_handler import QueryHandler
from src.nlp.preprocessor import preprocessor
from src.training.train import trainer
from src.training.learning import learning_manager
from admin.admin_panel import admin_bp

# Set up logging
logger = setup_logger(name='app', log_file=config.LOG_FILE, level=logging.INFO)

# Initialize Flask app
app = Flask(__name__, 
            static_folder=config.STATIC_FOLDER, 
            template_folder=config.TEMPLATES_FOLDER)

# Register blueprints
app.register_blueprint(admin_bp)

# Create scheduler
scheduler = BackgroundScheduler()

@app.route('/')
def index():
    """Render chat interface"""
    return render_template('index.html')

@app.route('/api/v1/chat', methods=['POST'])
def chat():
    """Chat API endpoint"""
    try:
        # Get request data
        data = request.json
        query = data.get('query', '')
        
        if not query:
            return jsonify({'error': 'No query provided'}), 400
        
        # Preprocess query
        processed_query = preprocessor.preprocess_user_input(query)
        
        # First check if there's a similar query in the database
        similar_query = QueryHandler.find_similar_query(query)
        if similar_query and similar_query.get('user_provided_answer'):
            logger.info(f"Found similar query in database: {similar_query['user_query']}")
            return jsonify({
                'response': similar_query['user_provided_answer'],
                'confidence': similar_query.get('confidence_score', 0.9),
                'intent': 'database_match'
            })
        
        # If no database match, predict intent
        tag, confidence, predictions = model_handler.predict(query)
        
        logger.info(f"Query: {query}")
        logger.info(f"Predicted intent: {tag} with confidence: {confidence}")
        
        # List of predefined banking question patterns to match for banking-related questions
        banking_question_patterns = [
            "what type", "types of account", "minimum balance", "how do i open", 
            "interest rate", "joint account", "register for", "online banking", 
            "mobile banking", "deposit check", "transaction limit", "reset", "password",
            "types of loan", "interest rate for", "loan approval", "documents", "pay off",
            "credit card", "report", "lost", "stolen", "card fee", "credit limit", "redeem",
            "transfer money", "wire transfer", "international transfer", "recurring transfer",
            "pay bills", "branch", "banking hours", "atm withdrawal", "maximum amount", 
            "deposit cash", "suspicious", "security measure", "contact customer", "update contact",
            "forget", "pin", "wealth management", "mortgage", "refinancing", "business banking",
            "account for child", "safe deposit"
        ]
        
        # Force certain banking questions to be handled as unknown queries regardless of confidence
        is_banking_question = any(pattern.lower() in query.lower() for pattern in banking_question_patterns)
        
        # Always store banking questions for admin panel review
        if is_banking_question:
            # Store in database without affecting the response flow
            QueryHandler.handle_unknown_query(query, confidence)
        
        # Check confidence threshold for providing proper response
        if confidence < config.CONFIDENCE_THRESHOLD:
            # Only store non-banking questions here since banking ones are already stored
            if not is_banking_question:
                QueryHandler.handle_unknown_query(query, confidence)
            
            # In production mode, provide a direct response instead of asking for teaching
            if hasattr(config, 'PRODUCTION_MODE') and config.PRODUCTION_MODE:
                # Get a default response for the tag or use unknown tag response
                response, context = model_handler.get_response(tag if confidence > 0.25 else "unknown")
                
                return jsonify({
                    'response': response,
                    'confidence': confidence,
                    'intent': tag
                })
            else:
                # In development/learning mode, ask for teaching
                return jsonify({
                    'query_id': query_id if 'query_id' in locals() else QueryHandler.handle_unknown_query(query, confidence),
                    'message': "I'm not sure how to respond to that. Would you like to teach me?"
                })
        
        # Get response for high confidence predictions
        response, context = model_handler.get_response(tag)
        
        # Handle context-specific actions
        if context:
            # Call context handler if available
            context_handler = getattr(QueryHandler, f"handle_{context}", None)
            
            if context_handler:
                context_response = context_handler()
                
                if context_response:
                    response = context_response
        
        return jsonify({
            'response': response,
            'confidence': confidence,
            'intent': tag
        })
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/v1/chat/learn/<int:query_id>', methods=['POST'])
def learn(query_id):
    """Save user's answer for an unknown query"""
    try:
        # Get request data
        data = request.json
        answer = data.get('answer', '')
        
        if not answer:
            return jsonify({'error': 'No answer provided'}), 400
        
        # Save answer
        success = QueryHandler.save_user_response(query_id, answer)
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to save answer'}), 500
    
    except Exception as e:
        logger.error(f"Error in learn endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/v1/intents', methods=['GET'])
def get_intents():
    """Get all intents"""
    try:
        return jsonify({
            'intents': model_handler.intents.get('intents', [])
        })
    
    except Exception as e:
        logger.error(f"Error in intents endpoint: {e}")
        return jsonify({'error': 'Internal server error'}), 500

def train_model_job():
    """Background job to train the model from unknown queries"""
    try:
        # Check if it's the freezing time (12 AM - 1 AM)
        now = datetime.now()
        start_hour = int(config.FREEZING_TIME_START.split(':')[0])
        end_hour = int(config.FREEZING_TIME_END.split(':')[0])
        
        if now.hour >= start_hour and now.hour < end_hour:
            logger.info("Starting scheduled training job")
            
            # Train model
            success, metrics = learning_manager.learn_from_unknown_queries(
                batch_size=config.LEARNING_BATCH_SIZE
            )
            
            if success:
                logger.info(f"Scheduled training completed: {metrics}")
            else:
                logger.error(f"Scheduled training failed: {metrics}")
    
    except Exception as e:
        logger.error(f"Error in scheduled training job: {e}")

def initialize_app():
    """Initialize the application"""
    try:
        # Initialize database
        db.initialize_database()
        
        # Check if model exists, if not, train it
        if not os.path.exists(config.MODEL_PATH):
            logger.info("Model not found, training initial model")
            trainer.train_model()
        
        # Add scheduled job
        scheduler.add_job(
            func=train_model_job,
            trigger='interval',
            minutes=60  # Check every hour
        )
        
        # Start scheduler
        scheduler.start()
        
        # Register scheduler shutdown
        atexit.register(lambda: scheduler.shutdown())
        
        logger.info("Application initialized successfully")
    
    except Exception as e:
        logger.error(f"Error initializing application: {e}")

if __name__ == '__main__':
    # Initialize application
    initialize_app()
    
    # Run app
    app.run(
        host=config.HOST,
        port=8080,
        debug=config.DEBUG
    )
else:
    # Initialize application when imported by WSGI server
    initialize_app()


    