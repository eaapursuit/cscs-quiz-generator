import fitz
import anthropic
import os
import json
import asyncio
import aiohttp
from typing import List, Dict, Any
from dotenv import load_dotenv

class CSCSTrivia:
    def __init__(self):
        load_dotenv()
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.client = anthropic.Anthropic(api_key=self.anthropic_api_key)
        
    async def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract and clean text from PDF."""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text("text") + "\n\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error extracting PDF text: {str(e)}")

    async def generate_questions(self, chapter_text: str, chapter_name: str, 
                               num_questions: int = 7) -> List[Dict[str, Any]]:
        """Generate questions using Claude with improved JSON output."""
        prompt = f"""
        Based on this CSCS textbook content from {chapter_name}, create {num_questions} multiple-choice questions.
        Distribute the questions across these difficulty levels:
        - 2 Easy
        - 2 Medium
        - 2 Hard
        - 1 Intense

        Return the questions in this exact JSON format:
        {{
            "questions": [
                {{
                    "difficulty": "Easy/Medium/Hard/Intense",
                    "question": "The question text",
                    "options": {{
                        "A": "First option",
                        "B": "Second option",
                        "C": "Third option",
                        "D": "Fourth option"
                    }},
                    "correct_answer": "A/B/C/D",
                    "explanation": "Why this answer is correct"
                }}
            ]
        }}

        Textbook Content:
        {chapter_text}
        """

        try:
            response = await self._make_claude_request(prompt)
            # Parse JSON from Claude's response
            questions_data = json.loads(response.content[0].text)
            return questions_data["questions"]
        except json.JSONDecodeError:
            raise Exception("Failed to parse Claude's response as JSON")
        except Exception as e:
            raise Exception(f"Error generating questions: {str(e)}")

    async def _make_claude_request(self, prompt: str):
        """Make request to Claude with retry logic."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return await asyncio.to_thread(
                    self.client.messages.create,
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=2000,
                    temperature=0.7,
                    system="You are a CSCS expert creating accurate multiple choice questions. Always return responses in valid JSON format.",
                    messages=[{"role": "user", "content": prompt}]
                )
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

    async def process_chapter(self, chapter_path: str) -> List[Dict[str, Any]]:
        """Process a single chapter with error handling."""
        try:
            chapter_name = os.path.basename(chapter_path).replace(".pdf","").replace("_", " ")
            print(f"\n📚 Processing {chapter_name}...")
            
            text = await self.extract_text_from_pdf(chapter_path)
            if not text.strip():
                raise Exception("No text extracted from PDF")
                
            print(f"✅ Extracted {len(text.split())} words")
            questions = await self.generate_questions(text, chapter_name)
            print(f"✅ Generated {len(questions)} questions")
            
            # Add chapter info to each question
            for q in questions:
                q["chapter"] = chapter_name
                
            return questions
            
        except Exception as e:
            print(f"❌ Error processing {chapter_path}: {str(e)}")
            return []

async def main():
    try:
        trivia = CSCSTrivia()
        
        # Start with Chapter 1
        chapter_path = "chapters/chapter_1.pdf"
        questions = await trivia.process_chapter(chapter_path)
        
        if questions:
            # Save questions to JSON
            output_file = "chapter1_questions.json"
            with open(output_file, 'w') as f:
                json.dump(questions, f, indent=2)
            print(f"\n✅ Saved {len(questions)} questions to {output_file}")
            
            # Print sample question
            print("\n📝 Sample Question:")
            sample = questions[0]
            print(f"Difficulty: {sample['difficulty']}")
            print(f"Question: {sample['question']}")
            print("Options:")
            for letter, option in sample['options'].items():
                print(f"{letter}) {option}")
            print(f"Correct Answer: {sample['correct_answer']}")
            print(f"Explanation: {sample['explanation']}")
        else:
            print("\n❌ No questions were generated")
            
    except Exception as e:
        print(f"\n❌ Critical error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())