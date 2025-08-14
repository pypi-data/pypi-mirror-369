"""
Conversation History Example

This example demonstrates all features related to conversation history management
including import/export, analysis, and advanced usage patterns.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from llmInvoker import llmInvoker


async def example_1_basic_history():
    """Basic conversation history usage."""
    print("=== Example 1: Basic History Management ===")
    
    # Initialize with history enabled (default)
    invoker = llmInvoker(strategy="failover", enable_history=True)
    invoker.use_defaults()
    
    # Have a conversation
    print("\n📝 Starting conversation...")
    response1 = await invoker.invoke("Hello, my name is Alice. What's your name?")
    if response1['success']:
        print(f"Assistant: {response1['response']}")
    
    response2 = await invoker.invoke("What did I just tell you my name was?")
    if response2['success']:
        print(f"Assistant: {response2['response']}")
    
    # Check history
    history = invoker.get_history()
    print(f"\n📊 Conversation entries: {len(history.entries)}")
    
    return invoker


async def example_2_history_analysis():
    """Analyze conversation history and get statistics."""
    print("\n=== Example 2: History Analysis ===")
    
    invoker = llmInvoker(strategy="failover", enable_history=True)
    invoker.configure_providers(
        github=["gpt-4o", "gpt-4o-mini"],
        google=["gemini-2.0-flash-exp"]
    )
    
    # Have multiple conversations
    messages = [
        "What is machine learning?",
        "Can you give me a simple example?",
        "How is it different from traditional programming?",
        "What are the main types of machine learning?",
        "Thank you for the explanation!"
    ]
    
    print("\n💬 Having extended conversation...")
    for i, message in enumerate(messages, 1):
        print(f"User ({i}): {message}")
        response = await invoker.invoke(message)
        if response['success']:
            print(f"Assistant: {response['response'][:100]}...")
        else:
            print(f"Failed: {response['error']}")
    
    # Get detailed history analysis
    history = invoker.get_history()
    summary = history.get_summary()
    
    print(f"\n📈 History Summary:")
    print(f"  • Total entries: {summary['total_entries']}")
    print(f"  • Providers used: {summary['providers_used']}")
    print(f"  • Models used: {summary['models_used']}")
    if summary['first_interaction']:
        print(f"  • First interaction: {summary['first_interaction']}")
    if summary['last_interaction']:
        print(f"  • Last interaction: {summary['last_interaction']}")
    
    # Provider statistics
    provider_stats = history.get_provider_usage_stats()
    print(f"\n🔄 Provider Statistics:")
    for provider, models in provider_stats.items():
        for model, count in models.items():
            print(f"  • {provider}/{model}: {count} calls")
    
    return invoker


async def example_3_export_import():
    """Export and import conversation history."""
    print("\n=== Example 3: Export/Import History ===")
    
    # Create a conversation
    invoker1 = llmInvoker(strategy="failover", enable_history=True)
    invoker1.use_defaults()
    
    print("\n📝 Creating conversation for export...")
    await invoker1.invoke("Hello, I'm working on a Python project.")
    await invoker1.invoke("Can you help me with error handling?")
    await invoker1.invoke("What's the difference between try/except and if/else?")
    
    # Export history to file
    export_file = "conversation_export.json"
    history1 = invoker1.get_history()
    
    print(f"\n💾 Exporting {len(history1.entries)} entries to {export_file}")
    history1.export_to_json(export_file)
    
    # Create new invoker and import history
    invoker2 = llmInvoker(strategy="failover", enable_history=True)
    invoker2.use_defaults()
    
    print(f"\n📥 Importing history to new invoker...")
    history2 = invoker2.get_history()
    history2.import_from_json(export_file)
    
    print(f"✅ Imported {len(history2.entries)} entries")
    
    # Continue conversation with imported context
    print(f"\n🔄 Continuing conversation with imported context...")
    response = await invoker2.invoke("Can you summarize what we discussed so far?")
    if response['success']:
        print(f"Assistant: {response['response']}")
    
    # Cleanup
    import os
    if os.path.exists(export_file):
        os.remove(export_file)
        print(f"\n🧹 Cleaned up {export_file}")
    
    return invoker2


async def example_4_context_management():
    """Demonstrate conversation context management."""
    print("\n=== Example 4: Context Management ===")
    
    invoker = llmInvoker(strategy="failover", enable_history=True)
    invoker.configure_providers(
        github=["gpt-4o"],
        google=["gemini-2.0-flash-exp"]
    )
    
    # Create conversation
    topics = [
        "How do I create a list in Python?",
        "What's the difference between lists and tuples?", 
        "How do I handle exceptions in Python?",
        "What are Python decorators?",
        "Can you explain list comprehensions?"
    ]
    
    print("\n💬 Creating conversation...")
    for i, message in enumerate(topics, 1):
        print(f"[{i}] User: {message}")
        response = await invoker.invoke(message)
        if response['success']:
            print(f"[{i}] Assistant: {response['response'][:80]}...")
    
    history = invoker.get_history()
    
    # Show context messages
    print(f"\n🧠 Getting conversation context...")
    context_messages = history.get_context_messages(include_last_n=3)
    
    print(f"Recent context ({len(context_messages)} messages):")
    for i, msg in enumerate(context_messages[-6:], 1):  # Show last 6 messages
        role = msg['role'].title()
        content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
        print(f"  {i}. {role}: {content}")
    
    # Test with new message using context
    print(f"\n🔄 Testing context awareness...")
    response = await invoker.invoke("Can you summarize what we've covered so far?")
    if response['success']:
        print(f"Summary: {response['response']}")
    
    return invoker


async def example_5_history_without_context():
    """Compare behavior with and without history."""
    print("\n=== Example 5: With vs Without History ===")
    
    # Invoker with history
    invoker_with_history = llmInvoker(strategy="failover", enable_history=True)
    invoker_with_history.use_defaults()
    
    # Invoker without history
    invoker_without_history = llmInvoker(strategy="failover", enable_history=False)
    invoker_without_history.use_defaults()
    
    print("\n🧠 Testing with history:")
    await invoker_with_history.invoke("My favorite color is blue.")
    response1 = await invoker_with_history.invoke("What's my favorite color?")
    if response1['success']:
        print(f"With history: {response1['response']}")
    
    print("\n🚫 Testing without history:")
    await invoker_without_history.invoke("My favorite color is blue.")
    response2 = await invoker_without_history.invoke("What's my favorite color?")
    if response2['success']:
        print(f"Without history: {response2['response']}")
    
    print(f"\n📊 History comparison:")
    print(f"  • With history entries: {len(invoker_with_history.get_history().entries)}")
    print(f"  • Without history entries: {len(invoker_without_history.get_history().entries)}")


async def example_6_custom_history_management():
    """Advanced history management techniques."""
    print("\n=== Example 6: Advanced History Management ===")
    
    invoker = llmInvoker(strategy="failover", enable_history=True)
    invoker.use_defaults()
    
    # Set up conversation
    print("\n📝 Setting up conversation...")
    await invoker.invoke("I'm planning a trip to Japan.")
    await invoker.invoke("What are the best places to visit in Tokyo?")
    await invoker.invoke("What about traditional food recommendations?")
    
    history = invoker.get_history()
    print(f"Initial entries: {len(history.entries)}")
    
    # Show conversation entries
    print(f"\n� Current conversation entries:")
    for i, entry in enumerate(history.entries, 1):
        print(f"  {i}. User: {entry.user_message[:60]}...")
        assistant_msg = str(entry.assistant_response)[:60] + "..." if len(str(entry.assistant_response)) > 60 else str(entry.assistant_response)
        print(f"     Assistant ({entry.provider}/{entry.model}): {assistant_msg}")
    
    # Clear and restart
    print(f"\n🧹 Clearing history...")
    history.clear()
    print(f"After clear: {len(history.entries)} entries")
    
    # Start new conversation
    print(f"\n� Starting fresh conversation...")
    await invoker.invoke("Hello, I need help with Python programming.")
    await invoker.invoke("How do I read a CSV file?")
    print(f"New conversation: {len(history.entries)} entries")


async def example_7_history_export_formats():
    """Export history in different formats."""
    print("\n=== Example 7: Export Formats ===")
    
    invoker = llmInvoker(strategy="failover", enable_history=True)
    invoker.use_defaults()
    
    # Create sample conversation
    conversation = [
        "Hello, I need help with Python programming.",
        "How do I read a file in Python?",
        "What about writing to a file?",
        "Can you show me error handling for file operations?",
        "Thank you for the help!"
    ]
    
    print("\n💬 Creating sample conversation...")
    for message in conversation:
        response = await invoker.invoke(message)
        if response['success']:
            print(f"✓ {message[:50]}...")
    
    history = invoker.get_history()
    
    # Export using built-in method
    print(f"\n💾 Exporting using built-in method...")
    history.export_to_json("history_export.json")
    print("✓ JSON export: history_export.json")
    
    # Create custom text export
    print(f"\n📝 Creating custom text export...")
    with open("conversation.txt", 'w', encoding='utf-8') as f:
        f.write(f"Conversation History - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")
        
        for i, entry in enumerate(history.entries, 1):
            f.write(f"[{i}] {entry.timestamp.strftime('%H:%M:%S')}\n")
            f.write(f"User: {entry.user_message}\n")
            
            # Handle different response formats
            if hasattr(entry, 'assistant_response'):
                response_text = str(entry.assistant_response)
                if len(response_text) > 200:
                    response_text = response_text[:200] + "..."
                f.write(f"Assistant ({entry.provider}/{entry.model}): {response_text}\n")
            
            f.write("-" * 40 + "\n\n")
    
    print("✓ Text format: conversation.txt")
    
    # Show export summary
    print(f"\n📋 Export Summary:")
    print(f"  • Total entries exported: {len(history.entries)}")
    print(f"  • Export formats: JSON, TXT")
    
    # Cleanup
    import os
    for file in ["history_export.json", "conversation.txt"]:
        if os.path.exists(file):
            os.remove(file)
    print("\n🧹 Cleaned up export files")


async def main():
    """Run all conversation history examples."""
    print("🗨️  Conversation History Feature Examples")
    print("=" * 50)
    
    try:
        await example_1_basic_history()
        await example_2_history_analysis()
        await example_3_export_import()
        await example_4_context_management()
        await example_5_history_without_context()
        await example_6_custom_history_management()
        await example_7_history_export_formats()
        
        print("\n✅ All conversation history examples completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️  Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print(__doc__)
    asyncio.run(main())
