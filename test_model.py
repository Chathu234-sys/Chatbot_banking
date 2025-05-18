import sys
import logging
from models.chatbot_model import model_handler
from src.utils import config
from src.utils.logger import setup_logger

# Set up logging
logger = setup_logger(name='test_model', log_file='logs/test_model.log', level=logging.INFO)

def test_query(query, confidence_threshold=0.5):
    """
    Test a query against the model and display the results
    
    Args:
        query (str): The query to test
        confidence_threshold (float): The confidence threshold to use
    """
    print(f"\nTesting query: '{query}'")
    
    # Predict intent
    tag, confidence, predictions = model_handler.predict(query)
    
    print(f"Top prediction: {tag} (confidence: {confidence:.2%})")
    
    # Show if it would pass the confidence threshold
    if confidence >= confidence_threshold:
        print(f"✅ Passes confidence threshold ({confidence_threshold:.2%})")
        response, context = model_handler.get_response(tag)
        print(f"Response: \"{response}\"")
    else:
        print(f"❌ Below confidence threshold ({confidence_threshold:.2%})")
        if hasattr(config, 'PRODUCTION_MODE') and config.PRODUCTION_MODE:
            # In production mode, get a response for the tag if confidence is reasonable
            if confidence > 0.25:
                response, context = model_handler.get_response(tag)
                print(f"Production mode low-confidence response: \"{response}\"")
            else:
                response, context = model_handler.get_response("unknown")
                print(f"Unknown response: \"{response}\"")
        else:
            print("In development mode: Would ask to teach the model")
    
    # Show top 3 predictions
    print("\nTop 3 intent predictions:")
    for i, pred in enumerate(predictions[:3]):
        print(f"  {i+1}. {pred['tag']}: {pred['probability']:.2%}")

def main():
    """
    Main function
    """
    # Default confidence threshold
    confidence_threshold = 0.5
    
    if len(sys.argv) > 1:
        # Use the first argument as the query
        query = sys.argv[1]
        
        # If a second argument is provided, use it as the confidence threshold
        if len(sys.argv) > 2:
            try:
                confidence_threshold = float(sys.argv[2])
            except ValueError:
                print(f"Invalid confidence threshold: {sys.argv[2]}. Using default: {confidence_threshold}")
        
        test_query(query, confidence_threshold)
    else:
        # Test some pre-defined queries
        print("Testing pre-defined queries with standard confidence threshold:", confidence_threshold)
        
        test_queries = [
            "What are your banking hours?",
            "what are the intrest rates",
            "Do you offer carbon offset credits with your checking accounts?",
            "What international wire transfer services do you offer?",
            "Do you have any cryptocurrency investment options?",
            "Hi",
            "What types of accounts do you offer?",
            "How do I open a checking account?",
            "Can I manage my account online?",
            "What are the fees for a checking account?"
        ]
        
        for query in test_queries:
            test_query(query, confidence_threshold)

if __name__ == "__main__":
    main() 