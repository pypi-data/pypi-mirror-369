import google.generativeai as genai
import json
import re

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
          }}
        ]
        Return ONLY JSON. No explanations, no markdown formatting.
        """

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        # Get text output
        output_text = getattr(response, "text", None)
        if not output_text and hasattr(response, "candidates"):
            # Fallback if .text is missing
            output_text = response.candidates[0].content.parts[0].text

        if not output_text:
            raise ValueError("Gemini returned no text.")

        # Remove markdown fences like ```json ... ```
        output_text = re.sub(r"^```json\s*|\s*```$", "", output_text.strip(), flags=re.DOTALL)

        try:
            self.questions_data = json.loads(output_text)
        except json.JSONDecodeError:
            print("DEBUG: Raw Gemini output:\n", output_text)  # Helps debug in development
            raise ValueError("Failed to parse Gemini's response as JSON.")

    def question(self, number: int) -> str:
        if 1 <= number <= len(self.questions_data):
            return self.questions_data[number - 1]["question"]
        raise IndexError("Question number out of range.")

    def options(self, number: int) -> list:
        if 1 <= number <= len(self.questions_data):
            return self.questions_data[number - 1]["options"]
        raise IndexError("Question number out of range.")

    def correct_answer(self, number: int) -> str:
        if 1 <= number <= len(self.questions_data):
            return self.questions_data[number - 1]["answer"]
        raise IndexError("Question number out of range.")
