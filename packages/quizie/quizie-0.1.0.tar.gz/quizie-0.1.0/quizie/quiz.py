import google.generativeai as genai
import json

# Your static Gemini API key
GEMINI_API_KEY = "AIzaSyCYlzNIT7xse2DwErxQsYC9fi4Ts2iy_Sc"

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

class QuizGenerator:
    def __init__(self):
        self.questions_data = []

    def generate_quiz(self, topic: str, num_questions: int):
        """
        Generate a quiz on a given topic with difficulty increasing from easy to hard.
        """
        prompt = f"""
        Create {num_questions} multiple-choice questions on the topic '{topic}'.
        The questions should gradually increase in difficulty from easy to medium to hard.
        For each question, provide:
        - Question text
        - 4 answer options (A, B, C, D)
        - The correct answer letter
        Format the output as a valid JSON list like this:
        [
          {{
            "question": "...",
            "options": ["...", "...", "...", "..."],
            "answer": "B"
          }},
          ...
        ]
        """

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        try:
            self.questions_data = json.loads(response.text.strip())
        except json.JSONDecodeError:
            raise ValueError("Failed to parse Gemini's response as JSON.")

    def question(self, number: int) -> str:
        """Return the question text for a given question number (1-based index)."""
        if 1 <= number <= len(self.questions_data):
            return self.questions_data[number - 1]["question"]
        raise IndexError("Question number out of range.")

    def options(self, number: int) -> list:
        """Return the options list for a given question number (1-based index)."""
        if 1 <= number <= len(self.questions_data):
            return self.questions_data[number - 1]["options"]
        raise IndexError("Question number out of range.")

    def correct_answer(self, number: int) -> str:
        """Return the correct answer letter for a given question number (1-based index)."""
        if 1 <= number <= len(self.questions_data):
            return self.questions_data[number - 1]["answer"]
        raise IndexError("Question number out of range.")
