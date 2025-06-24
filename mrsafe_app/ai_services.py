def generate_ai_quiz(topic, difficulty, num_questions=10):
    """Placeholder AI Quiz generation function"""
    return {
        "topic": topic,
        "difficulty": difficulty,
        "questions": [
            {"text": f"AI-generated Question {i+1}", "choices": ["A", "B", "C", "D"], "correct_answer": "A"}
            for i in range(num_questions)
        ]
    }

def generate_ai_questions(topic, difficulty, num_questions):
    """Mock AI question generator function."""
    return [
        {"question": f"Sample Question {i+1}", "choices": ["A", "B", "C", "D"], "correct_answer": "A"}
        for i in range(num_questions)
    ]
from openai import OpenAI
from django.conf import settings
import random

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generate_unique_question():
    prompts = [
        "Generate a unique general knowledge multiple-choice question.",
        "Create a new science-related quiz question with four answer choices.",
        "Provide an original math question with four options and a correct answer.",
        "Write a unique history question suitable for a quiz with four answer choices.",
        "Generate a distinct question about world geography with four possible answers."
    ]
    prompt = random.choice(prompts)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful AI that generates unique quiz questions."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("Error generating unique question:", e)
        return None
