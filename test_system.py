#!/usr/bin/env python3
"""
Simple test script to verify the RAG Chatbot system is working correctly.
Run this after starting the system with docker-compose.
"""

import asyncio
import json
import sys
from datetime import datetime
import httpx

# API base URL
BASE_URL = "http://localhost:8000"

async def test_health():
    """Test the health endpoint."""
    print("🏥 Testing health endpoint...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("✅ Health check passed")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False

async def test_query_generate():
    """Test the query generation endpoint."""
    print("🔍 Testing query generation...")
    async with httpx.AsyncClient() as client:
        try:
            data = {
                "user_query": "What are your business hours?",
                "conversation_history": []
            }
            response = await client.post(f"{BASE_URL}/query_generate", json=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Query generation successful")
                print(f"   Original: {result['original_query']}")
                print(f"   Refined:  {result['refined_query']}")
                return result
            else:
                print(f"❌ Query generation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Query generation failed: {e}")
            return None

async def test_answer_generate(refined_query="What are the business hours for customer support?"):
    """Test the answer generation endpoint."""
    print("💡 Testing answer generation...")
    async with httpx.AsyncClient() as client:
        try:
            data = {
                "refined_query": refined_query,
                "original_query": "What are your business hours?",
                "conversation_history": []
            }
            response = await client.post(f"{BASE_URL}/answer_generate", json=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Answer generation successful")
                print(f"   Answer: {result['answer'][:100]}...")
                return result
            else:
                print(f"❌ Answer generation failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Answer generation failed: {e}")
            return None

async def test_chat():
    """Test the complete chat pipeline."""
    print("💬 Testing complete chat pipeline...")
    async with httpx.AsyncClient() as client:
        try:
            data = {
                "user_query": "Do you offer free trials?",
                "conversation_history": []
            }
            response = await client.post(f"{BASE_URL}/chat", json=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Chat pipeline successful")
                print(f"   Original: {result['original_query']}")
                print(f"   Refined:  {result['refined_query']}")
                print(f"   Answer:   {result['answer'][:100]}...")
                print(f"   Conv ID:  {result['conversation_id']}")
                return result
            else:
                print(f"❌ Chat pipeline failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Chat pipeline failed: {e}")
            return None

async def test_messages():
    """Test the messages retrieval endpoint."""
    print("📝 Testing messages retrieval...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/messages?limit=5")
            
            if response.status_code == 200:
                messages = response.json()
                print(f"✅ Messages retrieval successful")
                print(f"   Retrieved {len(messages)} messages")
                return messages
            else:
                print(f"❌ Messages retrieval failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Messages retrieval failed: {e}")
            return None

async def test_message_count():
    """Test the message count endpoint."""
    print("🔢 Testing message count...")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/messages/count")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Message count successful: {result['count']} messages")
                return result
            else:
                print(f"❌ Message count failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Message count failed: {e}")
            return None

async def main():
    """Run all tests."""
    print("🚀 Starting RAG Chatbot System Tests")
    print("=" * 50)
    
    success_count = 0
    total_tests = 6
    
    # Test 1: Health check
    if await test_health():
        success_count += 1
    print()
    
    # Test 2: Query generation
    query_result = await test_query_generate()
    if query_result:
        success_count += 1
    print()
    
    # Test 3: Answer generation
    refined_query = query_result.get('refined_query') if query_result else None
    answer_result = await test_answer_generate(refined_query)
    if answer_result:
        success_count += 1
    print()
    
    # Test 4: Complete chat pipeline
    if await test_chat():
        success_count += 1
    print()
    
    # Test 5: Messages retrieval
    if await test_messages():
        success_count += 1
    print()
    
    # Test 6: Message count
    if await test_message_count():
        success_count += 1
    print()
    
    # Summary
    print("=" * 50)
    print(f"📊 Test Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All tests passed! Your RAG Chatbot system is working correctly.")
        print("\n🌐 You can now access:")
        print("   - Frontend Dashboard: http://localhost:3000")
        print("   - API Documentation: http://localhost:8000/docs")
        print("   - pgAdmin: http://localhost:5050")
        return 0
    else:
        print("❌ Some tests failed. Please check the logs and configuration.")
        print("\n🔧 Troubleshooting:")
        print("   - Ensure all services are running: docker-compose ps")
        print("   - Check logs: docker-compose logs [service_name]")
        print("   - Verify OPENAI_API_KEY is set in .env")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        sys.exit(1)