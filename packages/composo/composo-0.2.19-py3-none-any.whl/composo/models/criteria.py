"""
Criteria definitions and management
"""


class CriteriaSet:
    """Predefined criteria sets for common evaluation scenarios"""

    # Note: Implementing without preset criteria as requested
    # This structure allows for future expansion

    # Basic evaluation criteria for general responses
    basic = [
        "Reward responses that provide a complete and comprehensive response to the question",
        "Reward responses that are clear and concise, avoiding unnecessary verbosity or repetition.",
        "Reward responses that present technical information in a logical, organised format that prioritises the most important details",
    ]

    # RAG (Retrieval-Augmented Generation) evaluation criteria
    rag = [
        "Reward responses that accurately reflect information explicitly stated in the provided user prompt without fabricating details.",
        "Reward responses where all information is accompanied with a helpful citation to the source from the context.",
        "Reward responses that provide a complete and comprehensive response to the question regardless of provided context.",
    ]

    # Tool call evaluation criteria
    tool_call = [
        "Reward responses that make relevant tool calls to address the user's prompt",
        "Reward responses that use sufficient tool calls to fully respond to the user's prompt",
    ]

    # Tool response evaluation criteria
    tool_response = [
        "Reward responses that effectively utilise the results of function calls",
        "Reward responses that complete tasks by gathering and correctly integrating all required information",
    ]
