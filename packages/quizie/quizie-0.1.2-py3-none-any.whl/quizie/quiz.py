import google.generativeai as genai
import json
import re
import os

# Your static Gemini API key
GEMINI_API_KEY = "AIzaSyCYlzNIT7xse2DwErxQsYC9fi4Ts2iy_Sc"

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

class QuizGenerator:
    def __init__(self, storage_file="quiz_data.json"):
        self.storage_file = storage_file
        self.questions_data = []
        self._load_storage()

    def _load_storage(self):
        """Load existing quiz data from JSON file."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, "r", encoding="utf-8") as f:
                    self.storage = json.load(f)
            except json.JSONDecodeError:
                self.storage = {}
        else:
            self.storage = {}

    def _save_storage(self):
        """Save updated quiz data to JSON file."""
        with open(self.storage_file, "w", encoding="utf-8") as f:
            json.dump(self.storage, f, indent=2, ensure_ascii=False)

    def _generate_from_gemini(self, topic: str, num_questions: int):
        """Helper: Call Gemini to generate quiz questions."""
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

        # Extract text
        output_text = getattr(response, "text", None)
        if not output_text and hasattr(response, "candidates"):
            output_text = response.candidates[0].content.parts[0].text

        if not output_text:
            raise ValueError("Gemini returned no text.")

        # Remove markdown fences
        output_text = re.sub(r"^```json\s*|\s*```$", "", output_text.strip(), flags=re.DOTALL)

        try:
            return json.loads(output_text)
        except json.JSONDecodeError:
            print("DEBUG: Raw Gemini output:\n", output_text)
            raise ValueError("Failed to parse Gemini's response as JSON.")

    def generate_quiz(self, topic: str, num_questions: int):
        """
        If quiz for topic exists → load from storage.
        Else → generate with Gemini and save.
        """
        if topic in self.storage:
            self.questions_data = self.storage[topic]
        else:
            self.questions_data = self._generate_from_gemini(topic, num_questions)
            self.storage[topic] = self.questions_data
            self._save_storage()
        return self.questions_data

    def generate_quiz_new(self, topic: str, num_questions: int):
        """
        Always generate new questions with Gemini and overwrite stored ones.
        """
        self.questions_data = self._generate_from_gemini(topic, num_questions)
        self.storage[topic] = self.questions_data
        self._save_storage()
        return self.questions_data

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
