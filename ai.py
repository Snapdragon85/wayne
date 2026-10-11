from ollama import chat
from tools import open_program


MODEL = "qwen3:4b"


tools = [
    {
        "type": "function",
        "function": {
            "name": "open_program",
            "description": "Open a program installed on the Windows computer.",
            "parameters": {
                "type": "object",
                "properties": {
                    "program_name": {
                        "type": "string",
                        "description": "The name of the program to open."
                    }
                },
                "required": ["program_name"]
            }
        }
    }
]


def ask_ai(prompt):

    messages = [
        {
            "role": "system",
            "content": (
                "You are Wayne, a local Windows desktop AI assistant. "
                "Give very short, direct responses. "
                "For simple questions, answer in one sentence. "
                "For commands, confirm the action in one short sentence. "
                "Do not use paragraphs, bullet points, numbered lists, "
                "Markdown, or unnecessary explanations unless the user asks "
                "for a detailed explanation. "
                "Your responses are spoken aloud, so prioritize natural speech "
                "and brevity."
            )
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    response = chat(
        model=MODEL,
        messages=messages,
        tools=tools,
        think=False
    )

    # Did Wayne decide to use a tool?
    if response["message"].get("tool_calls"):

        for tool_call in response["message"]["tool_calls"]:

            function_name = tool_call["function"]["name"]
            arguments = tool_call["function"]["arguments"]

            if function_name == "open_program":

                result = open_program(
                    arguments["program_name"]
                )

                messages.append(response["message"])

                messages.append({
                    "role": "tool",
                    "tool_name": "open_program",
                    "content": result
                })

        # Ask Wayne to respond after the tool ran
        final_response = chat(
            model=MODEL,
            messages=messages,
            think=False
        )

        return final_response["message"]["content"]

    return response["message"]["content"]
