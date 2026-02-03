import re
from typing import Any, Dict, List


class BasePrompt:
    """
    Simple string template helper used to format prompt text.

    This is the foundation for creating dynamic prompts in RAG systems.
    Prompts are the instructions we give to LLMs, and they often need
    to include variable content like retrieved document chunks.

    Key RAG Concepts:
    - Prompt Templates: Reusable prompt structures with placeholders
    - Dynamic Content: Inserting retrieved chunks or user queries into prompts
    - Prompt Engineering: Crafting effective instructions for LLMs

    Python Concepts:
    - String templating: Using {placeholder} syntax for variable substitution
    - Regular expressions: Finding placeholder patterns in text
    - Keyword arguments: Flexible parameter passing with **kwargs
    """

    def __init__(self, prompt: str):
        """
        Initialize the prompt template.

        Args:
            prompt (str): Template string with {placeholder} markers

        Example:
            prompt = BasePrompt("Hello {name}, today is {day}")
        """
        self.prompt = prompt
        self._pattern = re.compile(
            r"\{([^}]+)\}"
        )  # Regex to find {placeholder} patterns

    def format_prompt(self, **kwargs: Any) -> str:
        """
        Return the prompt with kwargs substituted for placeholders.

        Args:
            **kwargs: Key-value pairs where keys match placeholder names

        Returns:
            str: Formatted prompt with placeholders replaced

        Example:
            prompt.format_prompt(name="Alice", day="Monday")
            # Returns: "Hello Alice, today is Monday"

        Python Concepts:
        - **kwargs: Accepts any number of keyword arguments
        - Dictionary comprehension: Building replacements dict efficiently
        - String.format(): Python's built-in string formatting
        """
        matches = self._pattern.findall(self.prompt)
        replacements = {match: kwargs.get(match, "") for match in matches}
        return self.prompt.format(**replacements)

    def get_input_variables(self) -> List[str]:
        """
        Return the placeholder names used by this prompt.

        Returns:
            List[str]: List of placeholder names found in the template

        This is useful for validation - you can check what variables
        a prompt needs before trying to format it.
        """
        return self._pattern.findall(self.prompt)


class RolePrompt(BasePrompt):
    """
    Prompt template that also captures an accompanying chat role.

    OpenAI's chat models expect messages in a specific format with roles
    like "system", "user", or "assistant". This class combines a prompt
    template with its intended role.

    Key RAG Concepts:
    - Chat Roles: Different types of messages in a conversation
    - System Messages: Instructions for how the AI should behave
    - User Messages: Questions or inputs from the user
    - Assistant Messages: Responses from the AI

    This is especially important in RAG because you often want to give
    the AI system-level instructions about how to use retrieved documents.
    """

    def __init__(self, prompt: str, role: str):
        """
        Initialize the role-based prompt template.

        Args:
            prompt (str): Template string with {placeholder} markers
            role (str): Chat role ("system", "user", or "assistant")

        Python Concepts:
        - Inheritance: RolePrompt extends BasePrompt functionality
        - super(): Call parent class constructor
        """
        super().__init__(prompt)
        self.role = role

    def create_message(
        self, apply_format: bool = True, **kwargs: Any
    ) -> Dict[str, str]:
        """
        Build an OpenAI chat message dictionary for this prompt.

        Args:
            apply_format (bool): Whether to substitute placeholders with kwargs
            **kwargs: Values to substitute into the template

        Returns:
            Dict[str, str]: OpenAI-compatible message dictionary
                Format: {"role": "system", "content": "formatted prompt text"}

        This creates the exact format that OpenAI's chat API expects:
        [
            {"role": "system", "content": "You are a helpful assistant..."},
            {"role": "user", "content": "What is machine learning?"},
            {"role": "assistant", "content": "Machine learning is..."}
        ]

        RAG Concepts:
        - Message Formatting: Converting templates to API-ready format
        - Dynamic Content: Inserting retrieved chunks into system messages
        - Conversation Structure: Building proper chat conversations
        """
        content = self.format_prompt(**kwargs) if apply_format else self.prompt
        return {"role": self.role, "content": content}


class SystemRolePrompt(RolePrompt):
    """
    Prompt template specifically for system messages.

    System messages are instructions that tell the AI how to behave.
    In RAG systems, this is where you typically include:
    - Instructions on how to use retrieved documents
    - Guidelines for answering questions
    - Formatting requirements for responses

    Example RAG system prompt:
    "You are a helpful assistant. Use the following documents to answer
    the user's question. If the answer is not in the documents, say so.

    Documents: {retrieved_chunks}"
    """

    def __init__(self, prompt: str):
        """Initialize a system role prompt template."""
        super().__init__(prompt, "system")


class UserRolePrompt(RolePrompt):
    """
    Prompt template specifically for user messages.

    User messages represent input from the person asking questions.
    In RAG systems, this is typically the user's question that needs
    to be answered using the retrieved documents.

    Example:
    "What is the capital of France?"
    """

    def __init__(self, prompt: str):
        """Initialize a user role prompt template."""
        super().__init__(prompt, "user")


class AssistantRolePrompt(RolePrompt):
    """
    Prompt template specifically for assistant messages.

    Assistant messages represent AI responses. These are less commonly
    used as templates since the AI generates its own responses, but
    they can be useful for few-shot prompting (showing examples).

    Example few-shot prompting:
    System: "Answer questions about animals"
    User: "What do cats eat?"
    Assistant: "Cats are carnivores and primarily eat meat..."
    User: "What about dogs?" (new question)
    """

    def __init__(self, prompt: str):
        """Initialize an assistant role prompt template."""
        super().__init__(prompt, "assistant")


if __name__ == "__main__":
    """
    Example usage demonstrating prompt templating and role-based messages.
    
    This shows how to:
    1. Create basic prompt templates
    2. Format templates with variables
    3. Create role-specific prompts for OpenAI chat format
    4. Extract template variables for validation
    """
    # Basic prompt templating
    prompt = BasePrompt("Hello {name}, you are {age} years old")
    formatted = prompt.format_prompt(name="John", age=30)
    print("Basic prompt:", formatted)

    # Role-based prompt for OpenAI chat format
    system_prompt = SystemRolePrompt("Hello {name}, you are {age} years old")
    message = system_prompt.create_message(name="John", age=30)
    print("System message:", message)

    # Check what variables the template needs
    variables = prompt.get_input_variables()
    print("Required variables:", variables)

    # Example RAG system prompt
    rag_prompt = SystemRolePrompt(
        "You are a helpful assistant. Use the following context to answer the user's question.\n\n"
        "Context: {context}\n\n"
        "Question: {question}\n\n"
        "Answer based on the context above:"
    )

    rag_message = rag_prompt.create_message(
        context="Machine learning is a subset of artificial intelligence.",
        question="What is machine learning?",
    )
    print("RAG system message:", rag_message)
