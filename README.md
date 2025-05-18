# Banking Assistant Chatbot

A Flask-based banking assistant chatbot with natural language processing capabilities that can answer customer questions about banking services.

## Features

- Natural language understanding for banking-related queries
- Intent recognition for common banking questions
- Support for adding custom intents and training the model
- Web interface for chatting with the assistant
- Admin panel for managing the assistant

## Running the Application

To run the application, use the following command:

```bash
python app.py
```

The application will be available at http://localhost:8080

## Training the Model

The chatbot uses a simple neural network model for intent recognition. You can train the model using the provided training script:

```bash
python train_model.py train
```

You can customize the training parameters:

```bash
python train_model.py train --epochs 2000 --batch-size 16 --learning-rate 0.01 --hidden-size 16
```

Parameters:
- `--epochs`: Number of training epochs (default: 1000)
- `--batch-size`: Batch size for training (default: 8)
- `--learning-rate`: Learning rate (default: 0.01)
- `--hidden-size`: Size of hidden layer (default: 8)

## Adding New Intents

### Using JSON

You can add new intents using a JSON file with the following structure:

```json
{
  "intents": [
    {
      "tag": "intent_name",
      "patterns": [
        "Question 1?",
        "Question 2?",
        "Alternative question?"
      ],
      "responses": [
        "Response 1",
        "Response 2"
      ],
      "context_set": ""
    }
  ]
}
```

Use the provided template in `templates/intent_template.json` as a reference.

To add intents from a JSON file:

```bash
python train_model.py add path/to/your/file.json
```

### Using CSV

You can also add intents using a CSV file with the following columns:
- `tag`: The intent name
- `pattern`: A question/pattern for the intent
- `response`: A response for the intent
- `context`: (Optional) The context for the intent

Use the provided template in `templates/intent_template.csv` as a reference.

To add intents from a CSV file:

```bash
python train_model.py add path/to/your/file.csv --type csv
```

## Example Intents to Add

Here are examples of intents you might want to add to your banking assistant:

1. **Fee Information**
   - Tag: `fee_information`
   - Patterns: Questions about account fees, service charges, ATM fees, etc.
   - Responses: Information about the bank's fee structure

2. **Security Information**
   - Tag: `security_info`
   - Patterns: Questions about account security, fraud protection, online security
   - Responses: Information about the bank's security measures

3. **International Banking**
   - Tag: `international_banking`
   - Patterns: Questions about international transfers, foreign transactions, etc.
   - Responses: Information about international banking services

4. **Student Banking**
   - Tag: `student_banking`
   - Patterns: Questions about student accounts, student loans, etc.
   - Responses: Information about banking services for students

## Configuring the Assistant

You can configure various aspects of the assistant by editing the configuration values in `src/utils/config.py`. Some key configuration values:

- `CONFIDENCE_THRESHOLD`: The minimum confidence threshold for intent recognition
- `PRODUCTION_MODE`: Whether the assistant is in production mode or learning mode
- `DEBUG`: Whether to run in debug mode

## Banking Q&A Database

The assistant includes a specialized database for banking questions and answers. This allows the system to:

- Store and retrieve detailed banking information
- Match user questions to the most relevant stored answers
- Provide accurate responses to specific banking queries

For more information on how to use and extend the banking Q&A database, see the [Banking Q&A Documentation](docs/BANKING_QA.md).

## Testing the Assistant

You can test the assistant's ability to answer banking questions using the test script:

```bash
python test_database_query.py
```

This will run a series of banking-related questions against the database and check if the assistant finds the correct answers.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 