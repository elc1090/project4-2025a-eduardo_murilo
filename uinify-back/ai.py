from pydantic import BaseModel
from os import environ
import instructor
from groq import Groq


class Component(BaseModel):
    title: str
    description: str
    framework: str
    category: str
    tags: str
    input_type: str
    include_tailwind: bool
    code: str


client = instructor.from_groq(
    Groq(api_key=environ.get("GROQ_API_KEY")), mode=instructor.Mode.JSON
)

META_PROMPT = """Given the following code snippet, analyze its structure and functionality. Then, generate a JSON object representing the component using the following schema:

{
    "title": "<short descriptive title>",
    "description": "<what the component does>",
    "framework": "<one of: Vue 3, React, HTML/CSS/JS>",
    "category": "<one of: UI Elements, Forms, Navigation, Cards, Data Display, Layout>",
    "tags": "<comma-separated list of lowercase keywords without spaces between>",
    "input_type": "<either: HTML or Vue SFC>",
    "include_tailwind": <true or false>,
    "code": "<the original code snippet>"
}

Guidelines:
    Identify if the code uses Tailwind CSS (based on class names like bg-gray-100, p-4, etc.) and set include_tailwind accordingly.
    Use "Vue 3" or "Vue SFC" only if <script setup> or single-file component structure is detected.
    Use "React" if JSX or hooks are used.
    Use "HTML/CSS/JS" for plain HTML, CSS, or vanilla JavaScript.
    Choose the most appropriate category and include meaningful tags.
    Output strictly valid JSON with no additional text.

Respond with only a valid JSON object matching the schema above. Do not include any explanation, formatting, or code blocks."""


def generate_component_info(code: str):
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": META_PROMPT,
                },
                {
                    "role": "user",
                    "content": "Here's the code:\n" + code,
                },
            ],
            response_model=Component,
            temperature=0.5,
            max_retries=10,
        )

        return response.model_dump()
    except Exception as e:
        print(e)
        return {}
