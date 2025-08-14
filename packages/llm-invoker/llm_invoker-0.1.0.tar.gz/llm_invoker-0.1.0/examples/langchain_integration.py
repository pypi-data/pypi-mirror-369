"""
LangChain Integration Example

This example shows how to integrate the llmInvoker library
with LangChain, LangGraph, and other multi-agent frameworks.
"""

import asyncio
from typing import List, Dict, Any

from llmInvoker import llmInvoker, invoke_failover


class LangChainWrapper:
    """
    Wrapper class to integrate llmInvoker with LangChain workflows.
    This allows you to use the failover functionality within LangChain chains.
    """
    
    def __init__(self, strategy: str = "failover", **kwargs):
        self.invoker = llmInvoker(strategy=strategy, **kwargs)
        self.configured = False
    
    def configure_providers(self, **provider_configs):
        """Configure providers for the wrapper."""
        self.invoker.configure_providers(**provider_configs)
        self.configured = True
        return self
    
    def use_defaults(self):
        """Use default provider configurations."""
        self.invoker.use_defaults()
        self.configured = True
        return self
    
    async def __call__(self, prompt: str, **kwargs) -> str:
        """Make the wrapper callable like a LangChain LLM."""
        if not self.configured:
            self.use_defaults()
        
        response = await self.invoker.invoke(prompt, **kwargs)
        
        if response['success']:
            # Extract content from response
            if 'response' in response:
                content = self._extract_content(response['response'])
                return content
            return str(response.get('response', ''))
        else:
            raise Exception(f"All providers failed: {response.get('error', 'Unknown error')}")
    
    def _extract_content(self, response) -> str:
        """Extract text content from various response formats."""
        if isinstance(response, str):
            return response
        
        if isinstance(response, dict):
            # OpenAI format
            if 'choices' in response and len(response['choices']) > 0:
                choice = response['choices'][0]
                if 'message' in choice:
                    return choice['message'].get('content', '')
                elif 'text' in choice:
                    return choice['text']
            
            # Anthropic format
            if 'content' in response:
                if isinstance(response['content'], list) and len(response['content']) > 0:
                    return response['content'][0].get('text', '')
                elif isinstance(response['content'], str):
                    return response['content']
        
        return str(response)


async def example_1_basic_integration():
    """Basic integration example."""
    print("=== Example 1: Basic LangChain Integration ===")
    
    # Create wrapper
    llm_wrapper = LangChainWrapper(strategy="failover")
    llm_wrapper.configure_providers(
        github=["gpt-4o"],
        google=["gemini-2.0-flash-exp"],
        openrouter=["deepseek/deepseek-r1"]
    )
    
    # Use like a regular LangChain LLM
    prompt = "Explain the concept of prompt engineering in 2 sentences."
    response = await llm_wrapper(prompt, temperature=0.7)
    
    print(f"Response: {response}")


async def example_2_multi_step_workflow():
    """Multi-step workflow with failover at each step."""
    print("\n=== Example 2: Multi-Step Workflow ===")
    
    llm = LangChainWrapper(strategy="failover")
    llm.use_defaults()
    
    # Step 1: Generate topic ideas
    print("Step 1: Generating topic ideas...")
    topics_prompt = "Generate 3 blog post topics about sustainable technology."
    topics_response = await llm(topics_prompt)
    print(f"Topics: {topics_response}")
    
    # Step 2: Expand on first topic
    print("\nStep 2: Expanding on first topic...")
    expansion_prompt = f"Based on this topic idea: '{topics_response.split('1.')[1].split('2.')[0].strip() if '1.' in topics_response else topics_response[:100]}', write a detailed outline."
    outline_response = await llm(expansion_prompt)
    print(f"Outline: {outline_response}")
    
    # Step 3: Write introduction
    print("\nStep 3: Writing introduction...")
    intro_prompt = f"Write an engaging introduction paragraph for this outline: {outline_response[:200]}..."
    intro_response = await llm(intro_prompt)
    print(f"Introduction: {intro_response}")


async def example_3_agent_simulation():
    """Simulate different agents with different configurations."""
    print("\n=== Example 3: Multi-Agent Simulation ===")
    
    # Creative Agent - uses models good for creativity
    creative_agent = LangChainWrapper(strategy="failover")
    creative_agent.configure_providers(
        github=["gpt-4o"],
        openrouter=["deepseek/deepseek-r1"]
    )
    
    # Analytical Agent - uses models good for analysis
    analytical_agent = LangChainWrapper(strategy="failover")
    analytical_agent.configure_providers(
        google=["gemini-2.0-flash-exp"],
        github=["gpt-4o"]
    )
    
    # Technical Agent - uses models good for code
    technical_agent = LangChainWrapper(strategy="failover")
    technical_agent.configure_providers(
        github=["gpt-4o"],
        openrouter=["deepseek/deepseek-r1"]
    )
    
    topic = "Building a recommendation system"
    
    # Get responses from different "agents"
    creative_response = await creative_agent(
        f"Brainstorm creative features for {topic}",
        temperature=0.9
    )
    
    analytical_response = await analytical_agent(
        f"Analyze the technical challenges of {topic}",
        temperature=0.3
    )
    
    technical_response = await technical_agent(
        f"Outline the technical architecture for {topic}",
        temperature=0.5
    )
    
    print(f"Creative Agent: {creative_response}")
    print(f"\nAnalytical Agent: {analytical_response}")
    print(f"\nTechnical Agent: {technical_response}")


async def example_4_crewai_style():
    """Example mimicking CrewAI-style agent interactions."""
    print("\n=== Example 4: CrewAI-Style Agent Interaction ===")
    
    # Define agent roles
    agents = {
        "researcher": LangChainWrapper(strategy="failover").use_defaults(),
        "writer": LangChainWrapper(strategy="failover").use_defaults(),
        "reviewer": LangChainWrapper(strategy="failover").use_defaults()
    }
    
    task = "Create a brief report on the impact of AI on job markets"
    
    # Researcher phase
    print("Researcher working...")
    research_prompt = f"Research and gather key facts about: {task}"
    research_result = await agents["researcher"](research_prompt)
    print(f"Research: {research_result[:200]}...")
    
    # Writer phase
    print("\nWriter working...")
    writing_prompt = f"Based on this research: {research_result}, write a concise report about {task}"
    writing_result = await agents["writer"](writing_prompt)
    print(f"Draft: {writing_result[:200]}...")
    
    # Reviewer phase
    print("\nReviewer working...")
    review_prompt = f"Review and improve this report: {writing_result}. Focus on clarity and accuracy."
    final_result = await agents["reviewer"](review_prompt)
    print(f"Final Report: {final_result}")


async def example_5_conversation_memory():
    """Example with persistent conversation memory."""
    print("\n=== Example 5: Conversation Memory ===")
    
    # Agent with memory
    agent = LangChainWrapper(strategy="failover", enable_history=True)
    agent.use_defaults()
    
    # Conversation simulation
    conversation = [
        "Hi, I'm working on a Python project about data analysis.",
        "What libraries would you recommend for data visualization?",
        "Can you show me a simple example using one of those libraries?",
        "How would I modify that code to handle missing data?"
    ]
    
    print("Conversation with memory:")
    for i, message in enumerate(conversation, 1):
        print(f"\nUser {i}: {message}")
        response = await agent(message)
        print(f"Agent {i}: {response}")
    
    # Show conversation history
    history = agent.invoker.get_history()
    if history:
        summary = history.get_summary()
        print(f"\nConversation Summary: {summary}")


def main():
    """Run all integration examples."""
    print("MultiAgent Failover Invoke - LangChain Integration Examples")
    print("=" * 65)
    
    try:
        loop = asyncio.get_running_loop()
        print("Running in async context...")
    except RuntimeError:
        asyncio.run(run_examples())


async def run_examples():
    """Run all async examples."""
    await example_1_basic_integration()
    await example_2_multi_step_workflow()
    await example_3_agent_simulation()
    await example_4_crewai_style()
    await example_5_conversation_memory()
    
    print("\n" + "=" * 65)
    print("Integration examples completed!")
    print("\nKey Integration Benefits:")
    print("- Seamless failover within existing LangChain workflows")
    print("- Automatic provider switching without workflow interruption")
    print("- Maintained conversation context across provider switches")
    print("- Compatible with multi-agent frameworks like CrewAI")


if __name__ == "__main__":
    main()
