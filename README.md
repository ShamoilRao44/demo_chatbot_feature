# Restaurant Management Chatbot Backend

A production-quality demo implementation of an LLM-powered restaurant management chatbot backend using FastAPI, PostgreSQL, and Ollama (LLaMA-3).

## 🌟 Features

- **Multi-turn conversational interface** for restaurant management tasks
- **8 demo functions** for dashboard and menu management
- **Structured function calling** via prompt engineering
- **Chat session memory** stored in PostgreSQL
- **Modular function registry** - add new functions without modifying core logic
- **Local LLM** powered by Ollama (LLaMA-3)
- **Production-ready architecture** with FastAPI and SQLAlchemy

## 🏗 Architecture

```
restaurant_agent/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── db.py                   # Database setup
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── llm_client.py           # Ollama LLM client
│   ├── function_registry.py    # Function registration system
│   ├── utils.py                # Utility functions
│   ├── actions/
│   │   ├── __init__.py
│   │   ├── dashboard.py        # Dashboard functions
│   │   └── menu.py             # Menu functions
│   └── services/
│       ├── __init__.py
│       └── chat_session_service.py  # Chat orchestration
├── requirements.txt
└── README.md
```

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 12+
- Ollama with LLaMA-3 model

## 🚀 Installation

### 1. Clone and Setup Python Environment

```bash
cd restaurant_agent
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Setup PostgreSQL

Create a database for the application:

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE restaurant_agent;

# Exit psql
\q
```

### 3. Configure Environment

Create a `.env` file in the `restaurant_agent` directory:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/restaurant_agent
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

### 4. Install and Setup Ollama

#### Install Ollama

**macOS/Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from https://ollama.com/download

#### Pull LLaMA-3 Model

```bash
ollama pull llama3
```

#### Start Ollama Server

```bash
ollama serve
```

The server will start on `http://localhost:11434`

### 5. Initialize Database

The database tables will be automatically created on first run, but you can also initialize them manually:

```python
python -c "from app.db import init_db; init_db(); print('Database initialized')"
```

### 6. Seed Test Data (Optional)

Create a test restaurant with some data:

```python
from app.db import SessionLocal
from app.models import Restaurant, MenuGroup, MenuItem

db = SessionLocal()

# Create restaurant
restaurant = Restaurant(
    id=1,
    owner_id=1,
    name="Demo Restaurant",
    address="123 Main St, City, State",
    business_hours={
        "monday": "09:00-21:00",
        "tuesday": "09:00-21:00",
        "wednesday": "09:00-21:00",
        "thursday": "09:00-21:00",
        "friday": "09:00-22:00",
        "saturday": "10:00-22:00",
        "sunday": "10:00-20:00"
    },
    prep_time_minutes=30,
    is_paused=False
)
db.add(restaurant)

# Create menu groups
appetizers = MenuGroup(restaurant_id=1, name="Appetizers")
mains = MenuGroup(restaurant_id=1, name="Main Courses")
db.add_all([appetizers, mains])
db.commit()

# Create menu items
db.add(MenuItem(
    restaurant_id=1,
    group_id=appetizers.id,
    name="Spring Rolls",
    description="Fresh vegetables wrapped in rice paper",
    price=850,  # $8.50
    tags=["vegetarian"]
))
db.commit()
db.close()

print("Test data created!")
```

Save this as `seed_data.py` and run: `python seed_data.py`

## 🎯 Running the Application

### Start the FastAPI Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python
python -m app.main
```

The API will be available at `http://localhost:8000`

### Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📡 API Usage

### Chat Endpoint

**POST** `/chat`

#### Request Body

```json
{
  "session_id": "user123-session",
  "owner_id": 1,
  "restaurant_id": 1,
  "message": "I want to update my business hours"
}
```

#### Response Types

**When LLM needs more information:**
```json
{
  "reply": "Which day would you like to update?",
  "type": "ask_user",
  "function": null,
  "session_id": "user123-session"
}
```

**When function is executed:**
```json
{
  "reply": "Successfully updated Monday hours to 09:00-17:00 for Demo Restaurant",
  "type": "result",
  "function": "update_business_hours",
  "session_id": "user123-session"
}
```

## 💬 Example Conversations

### Example 1: Update Business Hours (Multi-turn)

```bash
# Request 1
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session1",
    "owner_id": 1,
    "restaurant_id": 1,
    "message": "I want to change my business hours"
  }'

# Response 1
{
  "reply": "Sure! Which day would you like to update?",
  "type": "ask_user",
  "session_id": "session1"
}

# Request 2
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session1",
    "owner_id": 1,
    "restaurant_id": 1,
    "message": "Monday"
  }'

# Response 2
{
  "reply": "What hours would you like to set for Monday? Please use the format HH:MM-HH:MM, like 09:00-17:00",
  "type": "ask_user",
  "session_id": "session1"
}

# Request 3
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session1",
    "owner_id": 1,
    "restaurant_id": 1,
    "message": "09:00-21:00"
  }'

# Response 3
{
  "reply": "Successfully updated Monday hours to 09:00-21:00 for Demo Restaurant",
  "type": "result",
  "function": "update_business_hours",
  "session_id": "session1"
}
```

### Example 2: Create Menu Item (Single turn with all info)

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session2",
    "owner_id": 1,
    "restaurant_id": 1,
    "message": "Add a new menu item called Caesar Salad for $12.99 in the Appetizers group"
  }'

# Response
{
  "reply": "Successfully created menu item 'Caesar Salad' at $12.99 in group 'Appetizers' for Demo Restaurant",
  "type": "result",
  "function": "create_menu_item",
  "session_id": "session2"
}
```

### Example 3: Pause Restaurant

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session3",
    "owner_id": 1,
    "restaurant_id": 1,
    "message": "Pause my restaurant temporarily"
  }'

# Response
{
  "reply": "Successfully paused Demo Restaurant. Orders are now stopped.",
  "type": "result",
  "function": "set_restaurant_pause_state",
  "session_id": "session3"
}
```

## 🔧 Available Functions

### Dashboard Functions

1. **update_business_hours** - Update hours for a specific day
2. **update_prep_time** - Update preparation time in minutes
3. **set_restaurant_pause_state** - Pause/unpause the restaurant
4. **update_restaurant_address** - Update restaurant address

### Menu Functions

5. **create_menu_group** - Create a new menu category
6. **create_menu_item** - Create a new menu item
7. **update_menu_item_price** - Update an item's price
8. **toggle_menu_item_tag** - Add/remove tags (vegetarian, spicy, etc.)

## 🔌 Adding New Functions

The system is designed to be easily extensible. To add a new function:

1. Create a new file or add to existing action files
2. Register the function spec and handler:

```python
from app.function_registry import register_function, register_handler

# Register function spec
register_function(
    "my_new_function",
    {
        "description": "Description of what this function does",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_id": {"type": "integer"},
                "param1": {"type": "string", "description": "Param description"}
            },
            "required": ["restaurant_id", "param1"]
        }
    }
)

# Register handler
@register_handler("my_new_function")
async def handle_my_new_function(db: Session, restaurant_id: int, param1: str) -> str:
    # Your implementation here
    return "Success message"
```

3. Import the module in `app/main.py` to ensure registration

## 🧪 Testing

### Test Function Listing

```bash
curl http://localhost:8000/functions
```

### Test Health Check

```bash
curl http://localhost:8000/health
```

## 📊 Database Schema

### Restaurant
- `id`, `owner_id`, `name`, `address`
- `business_hours` (JSON), `prep_time_minutes`, `is_paused`

### MenuGroup
- `id`, `restaurant_id`, `name`

### MenuItem
- `id`, `restaurant_id`, `group_id`
- `name`, `description`, `price` (in cents), `tags` (JSON array)

### ChatSession
- `id` (session_id), `owner_id`
- `current_function`, `collected_arguments` (JSON)
- `missing_fields` (JSON), `status`, `last_bot_message`

## 🛠 Troubleshooting

### Ollama Connection Issues

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
ollama serve
```

### Database Connection Issues

```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Or on macOS with Homebrew
brew services list
```

### LLM Not Responding Properly

- Ensure LLaMA-3 model is downloaded: `ollama pull llama3`
- Check Ollama logs for errors
- Increase timeout in `.env`: `OLLAMA_TIMEOUT=180`

## 📝 Notes

- Session state is maintained in the database for multi-turn conversations
- Each session tracks the current function being collected and partial arguments
- The LLM uses structured JSON output for reliable parsing
- All prices are stored in cents (integer) to avoid floating-point issues
- Function registry allows dynamic function addition without core changes

## 🤝 Contributing

To add new features:

1. Create new action handlers in `app/actions/`
2. Register functions using the decorator pattern
3. Update documentation

## 📄 License

This is a demo project for educational purposes.

---

**Built with**: FastAPI, PostgreSQL, SQLAlchemy, Ollama (LLaMA-3)