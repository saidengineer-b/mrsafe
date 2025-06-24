import openai
from PyPDF2 import PdfReader
from PIL import Image
import pytesseract
import os
import re

# Initialize pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Ensure the OpenAI API key is set
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Initialize OpenAI Client Globally
client = openai.OpenAI(api_key=openai.api_key)

# Function to normalize questions to avoid repetitions
def normalize_text(text):
    return " ".join(re.sub(r'\s+', ' ', text.strip().lower()).split())

# Function to parse the raw quiz text into structured format
def parse_quiz_text(quiz_text):
    questions = []
    question_pattern = r"Q: (.*?)\nA\) (.*?)\nB\) (.*?)\nC\) (.*?)\nD\) (.*?)\nAnswer: (.)"
    matches = re.findall(question_pattern, quiz_text, re.DOTALL)

    for match in matches:
        question_data = {
            "question": match[0].strip(),
            "options": {
                "A": match[1].strip(),
                "B": match[2].strip(),
                "C": match[3].strip(),
                "D": match[4].strip(),
            },
            "correct_answer": match[5].strip()
        }
        questions.append(question_data)

    return {"questions": questions}
def generate_quiz(topic, num_questions=10, difficulty="medium"):
    prompt = (
        f"You are an expert quiz generator. Your task is to create exactly {num_questions} unique, non-repetitive "
        f"{difficulty}-level multiple-choice questions based on the following content.\n\n"
        f"If the content is in Arabic, write the questions and choices in Arabic. Otherwise, use English.\n"
        f"Each question must be clear, concise, and cover a distinct aspect of the content.\n\n"
        f"📘 Content:\n{topic[:1000]}\n\n"
        f"🎯 Format (strictly follow this structure and repeat it for each question):\n"
        f"Q: [Question text]\n"
        f"A) [Option A]\n"
        f"B) [Option B]\n"
        f"C) [Option C]\n"
        f"D) [Option D]\n"
        f"Answer: [Correct option letter only: A, B, C, or D]\n\n"
        f"🛑 No numbering, no explanations, no duplicates."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a quiz generator."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=3000,
            temperature=0.3
        )

        quiz_text = response.choices[0].message.content
        parsed_questions = parse_quiz_text(quiz_text)["questions"]

        seen_questions = set()
        unique_questions = []

        for q in parsed_questions:
            norm = normalize_text(q["question"])
            if norm not in seen_questions:
                unique_questions.append(q)
                seen_questions.add(norm)

        # Ensure we return only the number requested
        return {"questions": unique_questions[:num_questions]}

    except Exception as e:
        print(f"❌ API Error: {e}")
        return {"error": str(e)}



# ✅ Enhanced Quiz Text Parsing
def parse_quiz_text(quiz_text):
    questions = []
    pattern = re.compile(
        r"(?:Q\d*[:.]?\s*)?(.*?)\n"         # Matches the question (with or without Q1, Q2)
        r"(?:A\)|A\.|A\s*-)\s*(.*?)\n"       # Matches option A with different formats
        r"(?:B\)|B\.|B\s*-)\s*(.*?)\n"       # Matches option B
        r"(?:C\)|C\.|C\s*-)\s*(.*?)\n"       # Matches option C
        r"(?:D\)|D\.|D\s*-)\s*(.*?)\n"       # Matches option D
        r"Answer[:.]?\s*([A-D])",            # Matches the answer
        re.DOTALL
    )

    matches = pattern.findall(quiz_text)
    print(f"✅ Found {len(matches)} questions via regex.")

    for match in matches:
        question_text, option_a, option_b, option_c, option_d, correct_answer = match
        question_data = {
            "question": question_text.strip(),
            "options": {
                "A": option_a.strip(),
                "B": option_b.strip(),
                "C": option_c.strip(),
                "D": option_d.strip(),
            },
            "correct_answer": correct_answer.strip()
        }
        questions.append(question_data)

    print(f"✅ Parsed {len(questions)} questions.")
    return {"questions": questions}




# ✅ Parse Quiz Text
import re

def parse_quiz_text(quiz_text):
    questions = []
    
    # ✅ Use regex to identify question blocks more flexibly
    pattern = re.compile(r"Q\d*[:.]?\s*(.*?)(?:\n|$)"  # Matches question
                         r"(?:A\)|A\.\s*)(.*?)\n"      # Matches option A
                         r"(?:B\)|B\.\s*)(.*?)\n"      # Matches option B
                         r"(?:C\)|C\.\s*)(.*?)\n"      # Matches option C
                         r"(?:D\)|D\.\s*)(.*?)\n"      # Matches option D
                         r"(?:Answer[:.]?\s*)([A-D])", # Matches answer
                         re.DOTALL)

    matches = pattern.findall(quiz_text)
    print(f"✅ Found {len(matches)} questions via regex.")

    for match in matches:
        question_text, option_a, option_b, option_c, option_d, correct_answer = match

        question_data = {
            "question": question_text.strip(),
            "options": {
                "A": option_a.strip(),
                "B": option_b.strip(),
                "C": option_c.strip(),
                "D": option_d.strip(),
            },
            "correct_answer": correct_answer.strip()
        }

        questions.append(question_data)

    print(f"✅ Parsed {len(questions)} questions.")
    return {"questions": questions}



