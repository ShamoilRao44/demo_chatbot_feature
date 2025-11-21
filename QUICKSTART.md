# Quick Start Guide

Get the Restaurant Management Chatbot running in 5 minutes!

## Prerequisites Check

```bash
# Check Python version (need 3.11+)
python --version

# Check PostgreSQL
psql --version

# Check if Ollama is installed
ollama --version
```

## Step-by-Step Setup

### 1. Database Setup (2 minutes)

```bash
# Create database
createdb restaurant_agent

# Or using psql
psql -U postgres -c "CREATE DATABASE restaurant_agent;"
```

### 2. Python Environment (1 minute)

```bash
cd restaurant_agent

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Ollama Setup (2 minutes)

```bash
# Install Ollama (if not installed)
# macOS/Linux:
curl -fsSL https://ollama.com/install.sh | sh

# Windows: Download from https://ollama.com/download

# Pull LLaMA-3 model
ollama pull llama3

# Start Ollama server (in a separate terminal)
ollama serve
```

### 4. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit if needed (defaults should work)
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/restaurant_agent
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_MODEL=llama3
```

### 5. Initialize & Seed Database

```bash
# Run seed script to create test data
python seed_data.py
```

Expected output:
```
Database initialized
✓ Created restaurant: Demo Restaurant
✓ Created menu groups: Appetizers, Main Courses, Desserts, Beverages
✓ Created 10 menu items
```

### 6. Start the Server

```bash
# Start FastAPI server
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### 7. Test It!

Open a new terminal and run:

```bash
# Make test script executable
chmod +x test_requests.sh

# Run tests
./test_requests.sh
```

Or test manually:

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "quick-test",
    "owner_id": 1,
    "restaurant_id": 1,
    "message": "What can you help me with?"
  }'
```

## Common Issues

### "Database connection failed"
- Check if PostgreSQL is running: `sudo systemctl status postgresql`
- Verify database exists: `psql -l | grep restaurant_agent`

### "Ollama connection error"
- Check if Ollama is running: `curl http://localhost:11434/api/tags`
- Restart Ollama: `ollama serve`

### "Model not found"
- Pull the model: `ollama pull llama3`
- Verify: `ollama list`

### Port 8000 already in use
- Change port in command: `uvicorn app.main:app --port 8001`
- Or kill existing process: `lsof -ti:8000 | xargs kill`

## Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs for interactive API documentation
2. **View Functions**: `curl http://localhost:8000/functions` to see all 8 available functions
3. **Try Conversations**: Use the example conversations in README.md
4. **Add Your Own Functions**: Follow the guide in README.md to extend functionality

## Quick Commands Reference

```bash
# Start server
uvicorn app.main:app --reload

# Run in background
nohup uvicorn app.main:app > server.log 2>&1 &

# Stop background server
pkill -f "uvicorn app.main:app"

# View logs
tail -f server.log

# Reset database (WARNING: deletes all data)
python -c "from app.db import Base, engine; Base.metadata.drop_all(engine); Base.metadata.create_all(engine)"
python seed_data.py
```

## Demo Session Example

```bash
# Session 1: Update business hours (multi-turn)
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{
  "session_id": "demo1",
  "owner_id": 1,
  "restaurant_id": 1,
  "message": "I need to update my Monday hours"
}'
# Bot will ask for the hours

curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{
  "session_id": "demo1",
  "owner_id": 1,
  "restaurant_id": 1,
  "message": "09:00-22:00"
}'
# Bot will confirm the update

# Session 2: Create menu item (single turn)
curl -X POST http://localhost:8000/chat -H "Content-Type: application/json" -d '{
  "session_id": "demo2",
  "owner_id": 1,
  "restaurant_id": 1,
  "message": "Add Margherita Pizza for $14.99 to Main Courses"
}'
# Bot will create the item immediately
```

## Success Checklist

- [ ] PostgreSQL running
- [ ] Database created
- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] Ollama running with llama3 model
- [ ] Test data seeded
- [ ] Server started successfully
- [ ] Health check returns 200
- [ ] First chat request works

---

**Ready to build?** Start customizing by adding your own functions in `app/actions/`!

**Need help?** Check the full README.md for detailed documentation.
