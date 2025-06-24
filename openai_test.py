import openai

# Replace with your actual API key

try:
    client = openai.OpenAI(api_key=openai.api_key)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a quiz generator."},
            {"role": "user", "content": "Generate 3 medium-level multiple-choice questions on Physics. Format:\nQ: [Question]\nOptions:\nA) Option A\nB) Option B\nC) Option C\nD) Option D\nAnswer: [Correct Option Letter]"}
        ]
    )

    print(response.choices[0].message.content)

except Exception as e:
    print(f"Error: {e}")

