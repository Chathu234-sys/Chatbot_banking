#!/usr/bin/env python3
"""
A simple test script to check if we can find answers to banking questions
using the find_similar_query functionality in the database.
"""

import logging
import sys
from src.database.db_connector import db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_queries():
    """Test some banking queries to see if we can find them in the database"""
    
    # Connect to database
    db.initialize_database()
    
    # List of test queries with variations of the questions we added
    test_queries = [
        # Account related
        "What types of bank accounts do you have?",
        "What's the minimum I need to keep in my savings?",
        "How can I open an account with your bank?",
        "What interest rate do I get on a savings account?",
        "Can I have a joint account with my spouse?",
        
        # Loan related
        "What kind of loans can I get from your bank?",
        "What's the interest on home loans currently?",
        "How long does it take to approve a loan?",
        "What papers do I need for getting a personal loan?",
        "Is there a penalty if I pay off my loan before time?",
        
        # Card related
        "Tell me about the credit cards you offer",
        "My card was stolen, what should I do?",
        "What are the annual fees for credit cards?",
        "How can I get a higher limit on my credit card?",
        "How do I get my cashback rewards from my card?",
        
        # Branch/ATM related
        "Where are all your bank branches?",
        "When are you open during the week?",
        "Do I have to pay fees at other bank ATMs?",
        "How much cash can I take out from ATMs daily?",
        "Can I deposit money at your ATMs?",
        
        # New test questions
        "What's the minimum balance for a student account?",
        "How do I open a joint account with my spouse?",
        "What's the current interest rate for fixed deposits?",
        "How do I register for mobile banking?"
    ]
    
    # Test each query
    success_count = 0
    all_results = []
    
    for i, query in enumerate(test_queries):
        logger.info(f"\nTesting query #{i+1}: {query}")
        
        # Try to find a similar query
        result = db.simple_find_similar_query(query)
        
        if result:
            logger.info(f"Found match: {result['user_query']}")
            answer_preview = result['user_provided_answer'][:100] + "..." if len(result['user_provided_answer']) > 100 else result['user_provided_answer']
            logger.info(f"Answer: {answer_preview}")
            
            # Simple relevance check
            query_words = set(query.lower().split())
            answer_words = set(result['user_provided_answer'].lower().split())
            match_words = set(result['user_query'].lower().split())
            
            # Check for common words in both query and answer
            common_with_query = query_words.intersection(match_words)
            common_words_in_answer = query_words.intersection(answer_words)
            
            if len(common_with_query) > 1 or any(word in query.lower() for word in ["what", "how", "where", "when", "which", "who", "why", "can", "do"]):
                relevance = "✅ HIGH"
                success_count += 1
            elif len(common_words_in_answer) > 0:
                relevance = "⚠️ MEDIUM"
                success_count += 0.5
            else:
                relevance = "❌ LOW"
            
            logger.info(f"Relevance: {relevance} (matched {len(common_with_query)} keywords with query)")
            
            # Store results
            all_results.append({
                "query": query,
                "match": result['user_query'],
                "relevance": relevance,
                "keywords": len(common_with_query)
            })
        else:
            logger.info("❌ No match found in database")
            all_results.append({
                "query": query,
                "match": "No match",
                "relevance": "❌ NONE",
                "keywords": 0
            })
    
    # Print summary
    total = len(test_queries)
    success_rate = success_count / total * 100
    
    logger.info(f"\n===== Summary =====")
    logger.info(f"Successfully matched: {success_count}/{total} queries ({success_rate:.1f}%)")
    
    logger.info(f"\n===== All Results =====")
    for i, result in enumerate(all_results):
        logger.info(f"{i+1}. Query: {result['query']}")
        logger.info(f"   Match: {result['match']}")
        logger.info(f"   Relevance: {result['relevance']} ({result['keywords']} keywords)")
    
    # Disconnect from database
    db.disconnect()

if __name__ == "__main__":
    test_queries() 