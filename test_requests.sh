#!/bin/bash

# Test script for Restaurant Management Chatbot API
# Make sure the server is running before executing this script

BASE_URL="http://localhost:8000"

echo "=================================="
echo "Restaurant Chatbot API Test Suite"
echo "=================================="
echo ""

# Test 1: Health Check
echo "Test 1: Health Check"
echo "---"
curl -s "$BASE_URL/health" | python -m json.tool
echo ""
echo ""

# Test 2: List Available Functions
echo "Test 2: List Available Functions"
echo "---"
curl -s "$BASE_URL/functions" | python -m json.tool
echo ""
echo ""

# Test 3: Multi-turn conversation - Update Business Hours
echo "Test 3: Update Business Hours (Multi-turn)"
echo "---"
echo "Request 1: Initial request"
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session-1",
    "owner_id": 1,
    "restaurant_id": 1,
    "message": "I want to change my business hours"
  }' | python -m json.tool
echo ""
echo ""

echo "Request 2: Provide day"
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session-1",
    "owner_id": 1,
    "restaurant_id": 1,
    "message": "Monday"
  }' | python -m json.tool
echo ""
echo ""

echo "Request 3: Provide hours"
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session-1",
    "owner_id": 1,
    "restaurant_id": 1,
    "message": "10:00-20:00"
  }' | python -m json.tool
echo ""
echo ""

# Test 4: Single-turn conversation - Update Prep Time
echo "Test 4: Update Prep Time (Single-turn)"
echo "---"
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session-2",
    "owner_id": 1,
    "restaurant_id": 1,
    "message": "Set my prep time to 45 minutes"
  }' | python -m json.tool
echo ""
echo ""

# Test 5: Pause Restaurant
echo "Test 5: Pause Restaurant"
echo "---"
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session-3",
    "owner_id": 1,
    "restaurant_id": 1,
    "message": "Pause my restaurant"
  }' | python -m json.tool
echo ""
echo ""

# Test 6: Create Menu Item
echo "Test 6: Create Menu Item"
echo "---"
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session-4",
    "owner_id": 1,
    "restaurant_id": 1,
    "message": "Add a menu item called Pasta Carbonara for $16.99 in Main Courses"
  }' | python -m json.tool
echo ""
echo ""

# Test 7: Update Item Price
echo "Test 7: Update Menu Item Price"
echo "---"
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session-5",
    "owner_id": 1,
    "restaurant_id": 1,
    "message": "Change the price of Spring Rolls to $9.99"
  }' | python -m json.tool
echo ""
echo ""

# Test 8: Toggle Tag
echo "Test 8: Toggle Menu Item Tag"
echo "---"
curl -s -X POST "$BASE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-session-6",
    "owner_id": 1,
    "restaurant_id": 1,
    "message": "Add spicy tag to Buffalo Wings"
  }' | python -m json.tool
echo ""
echo ""

echo "=================================="
echo "Test Suite Completed"
echo "=================================="