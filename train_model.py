import argparse
import json
import csv
import os
import logging
from datetime import datetime
from models.chatbot_model import model_handler
from src.training.train import trainer
from src.utils.logger import setup_logger

# Set up logging
logger = setup_logger(name='train_cli', log_file='logs/train_cli.log', level=logging.INFO)

def train_model(args):
    """
    Train the model with specified parameters
    """
    logger.info("Training model with parameters:")
    logger.info(f"  Epochs: {args.epochs}")
    logger.info(f"  Batch Size: {args.batch_size}")
    logger.info(f"  Learning Rate: {args.learning_rate}")
    logger.info(f"  Hidden Size: {args.hidden_size}")
    
    # Train model
    model, words, classes, accuracy = trainer.train_model(
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.learning_rate,
        hidden_size=args.hidden_size
    )
    
    if model:
        logger.info(f"Training completed successfully with accuracy: {accuracy:.4f}")
        logger.info(f"Model trained with {len(words)} words and {len(classes)} classes")
        return True
    else:
        logger.error("Training failed")
        return False

def add_intents_from_file(file_path, file_type='json'):
    """
    Add intents from a file
    
    Args:
        file_path (str): Path to the file
        file_type (str): Type of file (json or csv)
        
    Returns:
        bool: Success status
    """
    try:
        logger.info(f"Adding intents from file: {file_path}")
        
        if file_type.lower() == 'json':
            # Load JSON file
            with open(file_path, 'r') as f:
                intents_data = json.load(f)
            
            # Check if it's an array or an object with intents key
            if isinstance(intents_data, list):
                intents = intents_data
            else:
                intents = intents_data.get('intents', [])
            
            # Add each intent
            success_count = 0
            for intent in intents:
                tag = intent.get('tag', '')
                patterns = intent.get('patterns', [])
                responses = intent.get('responses', [])
                context_set = intent.get('context_set', '')
                
                # Make sure tag, patterns, and responses are not empty
                if tag and patterns and responses:
                    # Add intent
                    success = trainer.add_intent(tag, patterns, responses, context_set)
                    if success:
                        success_count += 1
                        logger.info(f"Added intent: {tag}")
                    else:
                        logger.error(f"Failed to add intent: {tag}")
            
            logger.info(f"Added {success_count}/{len(intents)} intents from file")
            return success_count > 0
            
        elif file_type.lower() == 'csv':
            # Load CSV file
            with open(file_path, 'r') as f:
                reader = csv.reader(f)
                # Skip header
                header = next(reader)
                
                # Determine column indices based on header
                try:
                    tag_index = header.index('tag')
                    pattern_index = header.index('pattern')
                    response_index = header.index('response')
                    # Context is optional
                    context_index = header.index('context') if 'context' in header else -1
                except ValueError:
                    logger.error("CSV file must have columns named 'tag', 'pattern', and 'response'")
                    return False
                
                # Process rows
                current_tag = ""
                patterns = []
                responses = []
                context_set = ""
                success_count = 0
                intents_count = 0
                
                for row in reader:
                    # Skip empty rows
                    if not row or len(row) < 3:
                        continue
                    
                    # Get values
                    tag = row[tag_index].strip()
                    pattern = row[pattern_index].strip()
                    response = row[response_index].strip()
                    context = row[context_index].strip() if context_index >= 0 and context_index < len(row) else ""
                    
                    # If tag is empty, use the previous one
                    if not tag:
                        tag = current_tag
                    
                    # If this is a new tag, add the previous one
                    if tag != current_tag and current_tag:
                        # Add previous intent
                        success = trainer.add_intent(current_tag, patterns, responses, context_set)
                        if success:
                            success_count += 1
                            logger.info(f"Added intent: {current_tag}")
                        else:
                            logger.error(f"Failed to add intent: {current_tag}")
                        intents_count += 1
                        
                        # Reset for new tag
                        patterns = []
                        responses = []
                        context_set = ""
                    
                    # Update current tag and add pattern/response
                    current_tag = tag
                    if pattern:
                        patterns.append(pattern)
                    if response and response not in responses:
                        responses.append(response)
                    if context:
                        context_set = context
                
                # Add the last intent
                if current_tag and patterns and responses:
                    success = trainer.add_intent(current_tag, patterns, responses, context_set)
                    if success:
                        success_count += 1
                        logger.info(f"Added intent: {current_tag}")
                    else:
                        logger.error(f"Failed to add intent: {current_tag}")
                    intents_count += 1
                
                logger.info(f"Added {success_count}/{intents_count} intents from file")
                return success_count > 0
        else:
            logger.error(f"Unsupported file type: {file_type}")
            return False
            
    except Exception as e:
        logger.error(f"Error adding intents from file: {e}")
        return False

def backup_intents_file():
    """
    Create a backup of the intents file
    
    Returns:
        bool: Success status
    """
    try:
        intents_file = "data/intents.json"
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_file = f"{intents_file}.bak.{timestamp}"
        
        # Copy file
        with open(intents_file, 'r') as src:
            with open(backup_file, 'w') as dst:
                dst.write(src.read())
        
        logger.info(f"Created backup of intents file: {backup_file}")
        return True
    
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        return False

def main():
    """
    Main function
    """
    parser = argparse.ArgumentParser(description='Train chatbot model and add intents')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Train command
    train_parser = subparsers.add_parser('train', help='Train the model')
    train_parser.add_argument('--epochs', type=int, default=1000, help='Number of training epochs')
    train_parser.add_argument('--batch-size', type=int, default=8, help='Batch size for training')
    train_parser.add_argument('--learning-rate', type=float, default=0.01, help='Learning rate')
    train_parser.add_argument('--hidden-size', type=int, default=8, help='Size of hidden layer')
    
    # Add intents command
    add_parser = subparsers.add_parser('add', help='Add intents from a file')
    add_parser.add_argument('file', help='Path to the file containing intents')
    add_parser.add_argument('--type', choices=['json', 'csv'], default='json', help='Type of file (json or csv)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute command
    if args.command == 'train':
        # Backup intents file
        backup_intents_file()
        
        # Train model
        success = train_model(args)
        
        if success:
            print("Model trained successfully")
        else:
            print("Error training model. Check logs for details.")
    
    elif args.command == 'add':
        # Backup intents file
        backup_intents_file()
        
        # Add intents
        success = add_intents_from_file(args.file, args.type)
        
        if success:
            print("Intents added successfully")
            
            # Ask if user wants to train the model
            while True:
                response = input("Do you want to train the model with the new intents? (y/n): ").lower()
                if response in ['y', 'yes']:
                    # Train model with default parameters
                    success = train_model(parser.parse_args(['train']))
                    
                    if success:
                        print("Model trained successfully")
                    else:
                        print("Error training model. Check logs for details.")
                    break
                elif response in ['n', 'no']:
                    print("Model not trained. Remember to train it later for the changes to take effect.")
                    break
                else:
                    print("Please enter 'y' or 'n'")
        else:
            print("Error adding intents. Check logs for details.")
    
    else:
        parser.print_help()

if __name__ == '__main__':
    main() 