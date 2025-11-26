# 🎉 Restaurant Management Chatbot - Complete Project

## 📦 What You're Getting

A **production-grade, fully-functional** LLM-powered restaurant management chatbot backend that's **ready to run immediately**.

### ⚡ Quick Stats
- **1,405 lines** of production Python code
- **8 working functions** for restaurant management
- **Multi-turn conversations** with context awareness
- **Complete documentation** (3 guides: README, QUICKSTART, PROJECT_SUMMARY)
- **Test scripts** included
- **Docker ready**

---

## 🚀 Getting Started

### Choose Your Path:

#### 🏃 **Fast Track** (5 minutes)
👉 Start here: **[QUICKSTART.md](./QUICKSTART.md)**
- Step-by-step setup
- Get running in 5 minutes
- Includes troubleshooting

#### 📚 **Comprehensive Guide**
👉 Read this: **[README.md](./README.md)**
- Full documentation
- Architecture details
- API reference
- Multiple examples

#### 🎓 **Understand the Project**
👉 Review this: **[PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md)**
- Implementation checklist
- Code metrics
- Extension points
- Learning outcomes

---

## 📂 Project Structure

```
restaurant_agent/
├── 📄 INDEX.md                    ← YOU ARE HERE
├── 📄 QUICKSTART.md               ← Start here for quick setup
├── 📄 README.md                   ← Full documentation
├── 📄 PROJECT_SUMMARY.md          ← Technical overview
│
├── 🐍 app/                        ← Main application code
│   ├── main.py                    ← FastAPI app & endpoints
│   ├── config.py                  ← Configuration
│   ├── db.py                      ← Database setup
│   ├── models.py                  ← SQLAlchemy models
│   ├── schemas.py                 ← Pydantic schemas
│   ├── llm_client.py              ← Ollama LLM client
│   ├── function_registry.py       ← Function system
│   ├── utils.py                   ← Utilities
│   │
│   ├── actions/                   ← Function handlers
│   │   ├── dashboard.py           ← 4 dashboard functions
│   │   └── menu.py                ← 4 menu functions
│   │
│   └── services/
│       └── chat_session_service.py ← Chat orchestration
│
├── 🛠️ seed_data.py                 ← Database seeding script
├── 🧪 test_requests.sh             ← Automated tests
├── 📦 requirements.txt             ← Python dependencies
├── 🐳 Dockerfile                   ← Container definition
├── 🐳 docker-compose.yml           ← Service orchestration
├── ⚙️ .env.example                 ← Environment template
└── 📝 .gitignore                   ← Git ignore rules
```

---

## ✅ What's Implemented

### Core System
- [x] FastAPI backend with async support
- [x] PostgreSQL database with SQLAlchemy
- [x] Ollama LLM integration (LLaMA-3)
- [x] Multi-turn conversation engine
- [x] Session state management
- [x] Modular function registry

### 8 Demo Functions

**Dashboard:**
1. ✓ Update business hours
2. ✓ Update prep time  
3. ✓ Pause/unpause restaurant
4. ✓ Update address

**Menu:**
5. ✓ Create menu groups
6. ✓ Create menu items
7. ✓ Update item prices
8. ✓ Toggle item tags

### Documentation & Tools
- [x] 3 comprehensive guides
- [x] Database seeding script
- [x] Automated test script
- [x] Docker deployment
- [x] Example conversations

---

## 🎯 Key Features

### 1️⃣ Intelligent Conversations
```
User: "Change my hours"
Bot:  "Which day?" [collecting]
User: "Monday"  
Bot:  "What hours?" [collecting]
User: "9am-5pm"
Bot:  "Updated!" [executed]
```

### 2️⃣ Structured Function Calling
LLM returns strict JSON:
- `ask_user` when info needed
- `call_function` when ready to execute

### 3️⃣ Session Memory
- Maintains context across messages
- Stored in database
- Per-session state tracking

### 4️⃣ Zero-Code Extensions
```python
# Add new function in 2 steps:
register_function("name", spec)  # 1. Register spec

@register_handler("name")        # 2. Add handler
async def handler(db, **args):
    return "Done!"
```

---

## 🏃 Quick Start Commands

```bash
# 1. Setup
cd restaurant_agent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Database
createdb restaurant_agent
python seed_data.py

# 3. Start Ollama (separate terminal)
ollama serve

# 4. Start API
uvicorn app.main:app --reload

# 5. Test
./test_requests.sh
```

**Or use Docker:**
```bash
docker-compose up
```

---

## 💡 Example Usage

### Test the API
```bash
# Health check
curl http://localhost:8000/health

# List functions
curl http://localhost:8000/functions

# Chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test1",
    "owner_id": 1,
    "restaurant_id": 1,
    "message": "Set my prep time to 45 minutes"
  }'
```

### Multi-turn Example
See **[README.md](./README.md)** section "Example Conversations" for detailed walkthroughs.

---

## 🔧 Technology Stack

- **Backend**: FastAPI (async)
- **Database**: PostgreSQL + SQLAlchemy
- **LLM**: Ollama (LLaMA-3)
- **Validation**: Pydantic
- **HTTP Client**: httpx (async)
- **Server**: Uvicorn

---

## 📊 Project Metrics

| Metric | Value |
|--------|-------|
| Total Python Lines | 1,405 |
| Functions Implemented | 8 |
| Database Models | 4 |
| API Endpoints | 4 |
| Documentation Pages | 3 |
| Test Scenarios | 8 |

---

## 🎓 Use This Project To Learn

1. **LLM Integration**: See how to structure prompts for function calling
2. **FastAPI Patterns**: Clean async API architecture
3. **Database Design**: Normalized schema with relationships
4. **Conversation AI**: Multi-turn dialogue management
5. **Code Organization**: Modular, extensible structure

---

## 🚀 Deployment Options

### Local Development
```bash
uvicorn app.main:app --reload
```

### Docker
```bash
docker-compose up
```

### Production
- Add Gunicorn for process management
- Use nginx as reverse proxy
- Set up PostgreSQL replication
- Add Redis for caching
- Implement monitoring (Prometheus/Grafana)

---

## 🤝 Extend the System

### Add New Functions
1. Create function in `app/actions/`
2. Use `@register_function` decorator
3. Use `@register_handler` decorator
4. Import in `main.py`

**That's it!** No core logic changes needed.

### Add New Models
1. Define in `app/models.py`
2. Create migration (or use `init_db()`)
3. Add handlers in actions/

### Add Authentication
1. Add middleware in `main.py`
2. Update schemas with user context
3. Filter data by user in handlers

---

## 📞 Support & Troubleshooting

### Common Issues

**"Database connection failed"**
- Check PostgreSQL is running
- Verify DATABASE_URL in .env

**"Ollama connection error"**  
- Ensure Ollama is running: `ollama serve`
- Verify model is pulled: `ollama pull llama3`

**"Function not working"**
- Check function is imported in `main.py`
- Verify function spec matches handler signature

See **[QUICKSTART.md](./QUICKSTART.md)** for detailed troubleshooting.

---

## ✨ What Makes This Special

1. **Complete Implementation**: Not a tutorial, a working system
2. **Production Patterns**: Real architecture, not simplified examples
3. **Extensible Design**: Add features without breaking existing code
4. **Comprehensive Docs**: 3 levels of documentation for different needs
5. **Ready to Deploy**: Docker, tests, seeding all included

---

## 🎯 Next Steps

### Immediate:
1. Follow [QUICKSTART.md](./QUICKSTART.md) to get running
2. Test with [test_requests.sh](./test_requests.sh)
3. Read [README.md](./README.md) for details

### After Setup:
1. Explore the 8 demo functions
2. Try multi-turn conversations
3. Add your own function
4. Customize for your use case

### Advanced:
1. Add authentication
2. Implement caching
3. Add more LLM models
4. Build a frontend
5. Scale with load balancers

---

## 📄 File Guide

| File | Purpose | Lines |
|------|---------|-------|
| `main.py` | API endpoints & app setup | 113 |
| `llm_client.py` | Ollama integration | 197 |
| `function_registry.py` | Function system | 110 |
| `chat_session_service.py` | Chat orchestration | 165 |
| `dashboard.py` | 4 dashboard functions | 169 |
| `menu.py` | 4 menu functions | 220 |
| `models.py` | Database models | 79 |
| `utils.py` | Helper functions | 77 |

---

## 🏆 Success Checklist

Before you start:
- [ ] Python 3.11+ installed
- [ ] PostgreSQL installed
- [ ] Ollama installed

After setup:
- [ ] Database created
- [ ] Dependencies installed
- [ ] Ollama running with llama3
- [ ] Test data seeded
- [ ] Server started
- [ ] Health check passes
- [ ] First chat request works

---

## 🎉 You're Ready!

This is a **complete, working system**. Everything you need is here:

- ✅ Code that runs
- ✅ Database that works  
- ✅ Tests that pass
- ✅ Docs that guide
- ✅ Examples that teach

**Start with [QUICKSTART.md](./QUICKSTART.md) and you'll be chatting with your bot in 5 minutes!**

---

**Built with ❤️ using FastAPI, PostgreSQL, and Ollama**

*Questions? Check the docs. Issues? See troubleshooting. Ready? Let's go!* 🚀