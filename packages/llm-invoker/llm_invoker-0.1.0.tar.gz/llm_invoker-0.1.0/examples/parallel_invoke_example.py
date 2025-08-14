"""
Parallel Strategy Example

This example demonstrates how to use the parallel strategy to invoke multiple
providers/models simultaneously and compare their responses.
"""

import asyncio
from llmInvoker import llmInvoker, invoke_parallel


async def example_1_basic_parallel():
    """Basic parallel invocation example."""
    print("=== Example 1: Basic Parallel Invocation ===")
    
    # Initialize the invoker with parallel strategy
    invoker = llmInvoker(strategy="parallel", timeout=30)
    
    # Configure multiple providers
    invoker.configure_providers(
        github=["gpt-4o", "gpt-4o-mini"],
        google=["gemini-2.0-flash-exp"],
        openrouter=["deepseek/deepseek-r1", "meta-llama/llama-3.2-3b-instruct:free"],
        openai=["gpt-4o-mini"]  # If configured
    )
    
    # Ask the same question to all models
    message = "What are the top 3 programming languages for data science and why?"
    
    response = await invoker.invoke(message, temperature=0.7, max_tokens=200)
    
    if response['success']:
        print(f"Successfully got {len(response['successful_responses'])} responses out of {response['total_providers']} providers")
        
        # Display each response
        for i, result in enumerate(response['successful_responses'], 1):
            print(f"\n--- Response {i} from {result['provider']}:{result['model']} ---")
            print(result['response'])
            print("-" * 50)
    else:
        print("All providers failed!")


def example_2_convenience_parallel():
    """Using convenience function for parallel invocation."""
    print("\n=== Example 2: Convenience Parallel Function ===")
    
    # Quick parallel invocation
    response = invoke_parallel(
        message="Explain the difference between AI, ML, and Deep Learning in one sentence each.",
        providers={
            "github": ["gpt-4o"],
            "google": ["gemini-2.0-flash-exp"],
            "openrouter": ["deepseek/deepseek-r1"]
        },
        temperature=0.5,
        max_tokens=100
    )
    
    if response['success']:
        print(f"Got {len(response['successful_responses'])} responses:")
        
        for result in response['successful_responses']:
            print(f"\n{result['provider']}:{result['model']}: {result['response']}")
    else:
        print("No successful responses received")


async def example_3_compare_models():
    """Compare different models on the same creative task."""
    print("\n=== Example 3: Creative Writing Comparison ===")
    
    invoker = llmInvoker(strategy="parallel")
    invoker.use_defaults()  # Use all available configured providers
    
    creative_prompt = "Write a haiku about artificial intelligence."
    
    response = await invoker.invoke(creative_prompt, temperature=0.9)
    
    if response['success']:
        print("Creative responses from different models:")
        print("=" * 50)
        
        for result in response['successful_responses']:
            print(f"\n{result['provider']} ({result['model']}):")
            print(result['response'])
            print("-" * 30)
    
    # Show detailed results including failures
    print(f"\nDetailed Results:")
    for provider_model, result in response['results'].items():
        status = "✓" if result['success'] else "✗"
        message = result.get('response', result.get('error', 'Unknown error'))
        print(f"{status} {provider_model}: {message[:100]}...")


async def example_4_analysis_task():
    """Use parallel invocation for analysis tasks."""
    print("\n=== Example 4: Analysis Task ===")
    
    invoker = llmInvoker(strategy="parallel", timeout=45)
    
    invoker.configure_providers(
        github=["gpt-4o"],
        google=["gemini-2.0-flash-exp"],
        openrouter=["deepseek/deepseek-r1"]
    )
    
    analysis_prompt = """
    Analyze the following business scenario and provide 3 key recommendations:
    
    A small tech startup wants to expand internationally but has limited budget.
    They currently have 50 employees and their main product is a SaaS platform.
    """
    
    response = await invoker.invoke(
        analysis_prompt,
        temperature=0.3,  # Lower temperature for more focused analysis
        max_tokens=300
    )
    
    if response['success']:
        print("Business Analysis from Multiple AI Models:")
        print("=" * 50)
        
        # Create a comparison table
        recommendations = {}
        for i, result in enumerate(response['successful_responses'], 1):
            provider = f"{result['provider']}:{result['model']}"
            recommendations[provider] = result['response']
            print(f"\nModel {i} ({provider}):")
            print(result['response'])
            print("-" * 40)
        
        # Summary
        print(f"\nSummary: Received {len(response['successful_responses'])} different analyses")
        print("You can now compare and synthesize the recommendations from different models.")


async def example_5_with_history():
    """Parallel invocation with conversation history."""
    print("\n=== Example 5: Parallel with History ===")
    
    invoker = llmInvoker(strategy="parallel", enable_history=True)
    invoker.use_defaults()
    
    # First round
    response1 = await invoker.invoke("I'm learning Python. What's the most important concept to master first?")
    
    if response1['success']:
        print("First question responses:")
        for result in response1['successful_responses']:
            print(f"- {result['provider']}: {result['response'][:100]}...")
    
    # Second round with context
    response2 = await invoker.invoke("Can you give me a simple code example for that concept?")
    
    if response2['success']:
        print("\nFollow-up question responses (with context):")
        for result in response2['successful_responses']:
            print(f"\n{result['provider']}:{result['model']}:")
            print(result['response'])
            print("-" * 30)
    
    # Show conversation history
    history = invoker.get_history()
    if history:
        stats = history.get_provider_usage_stats()
        print(f"\nProvider usage stats: {stats}")


def main():
    """Run all parallel examples."""
    print("MultiAgent Failover Invoke - Parallel Strategy Examples")
    print("=" * 60)
    
    try:
        loop = asyncio.get_running_loop()
        print("Running in async context...")
    except RuntimeError:
        asyncio.run(run_examples())


async def run_examples():
    """Run all async examples."""
    await example_1_basic_parallel()
    example_2_convenience_parallel()
    await example_3_compare_models()
    await example_4_analysis_task()
    await example_5_with_history()
    
    print("\n" + "=" * 60)
    print("All parallel examples completed!")
    print("\nKey Benefits of Parallel Strategy:")
    print("- Compare responses from multiple models")
    print("- Get diverse perspectives on the same question")
    print("- Identify consensus or interesting differences")
    print("- Choose the best response for your use case")


if __name__ == "__main__":
    main()
