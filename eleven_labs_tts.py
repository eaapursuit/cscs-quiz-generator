from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import play
import os
import json

import asyncio

class CSCSTTSGenerator:
    def __init__(self):

        print("\nDebugging Environment Setup:")
        print("---------------------------")

        #Print current working directory
        print(f"Current directory: {os.getcwd()}")

        # Try to load .env file
        load_dotenv()

        # Check if .env file exists
        if os.path.exists('.env'):
            print("✅ .env file found")
            with open('.env', 'r') as f:
                content = f.readlines()
            print("Content format:")
            for line in content:
                key = line.split('=')[0] if '=' in line else line
                print(f" {key}: {'*' * 10}")
        else:
            print("❌ .env file not found")

        # Try to get API Key
        self.api_key=os.getenv('ELEVENLABS_API_KEY')
        print(f"\nAPI Key status: {'✅ Found' if self.api_key else '❌ Not found'}")
        if self.api_key:
            print(f"API Key preview: {self.api_key[:4]}...")

        # Initialize client if key exists
        if self.api_key:
            self.client = ElevenLabs(api_key=self.api_key)
            print("✅ ElevenLabs client initialized")
        else:
            raise ValueError("ELEVENLABS_API_KEY not found in environment variables")
    
        
    def format_tts_text(self, question_data):
        """Format the text for TTS in an engaging way."""
        # Attention grabbers based on difficulty
        difficulty_intros = {
            "Easy": "Here's a basic CSCS concept everyone should know.",
            "Medium": "Let's test your CSCS knowledge with this one.",
            "Hard": "Here's a challenging CSCS question for you.",
            "Intense": "This is an advanced CSCS concept. Are you ready?"
        }
        
        intro = difficulty_intros.get(question_data['difficulty'], "Here's your CSCS trivia question.")
        
        # Format the question section with pauses
        tts_text = f"""{intro}
        
        <break time="500ms"/>
        {question_data['question']}
        
        <break time="800ms"/>
        Let's look at your options:
        <break time="500ms"/>
        
        A) {question_data['options']['A']}
        <break time="400ms"/>
        B) {question_data['options']['B']}
        <break time="400ms"/>
        C) {question_data['options']['C']}
        <break time="400ms"/>
        D) {question_data['options']['D']}
        
        <break time="5s"/>
        Time's up!
        <break time="500ms"/>
        
        The correct answer is {question_data['correct_answer']}.
        
        <break time="500ms"/>
        Here's why this is correct:
        <break time="300ms"/>
        {question_data['explanation']}"""
        
        return tts_text

    async def generate_audio_for_question(self, question_data, index, output_folder="audio_output", voice_id="21m00Tcm4TlvDq8ikWAM"):
        """Generate TTS audio for a CSCS trivia question."""
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        
        # Format text for TTS
        tts_text = self.format_tts_text(question_data)
        
        try:
            # Generate unique filename including difficulty level
            safe_filename = f"Question {index} - {question_data['difficulty']}.mp3"
            output_path = os.path.join(output_folder, safe_filename)
            
            # Generate audio
            audio_generator = await asyncio.to_thread(
                self.client.generate,
                text=tts_text,
                voice=voice_id,
                model="eleven_monolingual_v1"
            )
            
            #Convert generator to bytes
            audio_bytes = b"".join(audio_generator)

            # Save audio file
            async with asyncio.Lock():
                with open(output_path, 'wb') as f:
                    f.write(audio_bytes)
            
            print(f"✅ Generated audio: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Error generating audio: {str(e)}")
            return None

    async def process_questions(self, questions, output_folder="audio_output"):
        """Process all trivia questions and generate audio concurrently."""
        total_questions = len(questions)
        print(f"\nProcessing {total_questions} questions...")
        
        # Process questions concurrently
        tasks = []
        for i, question in enumerate(questions, 1):
            print(f"\nQueuing question {i}/{total_questions} | Difficulty: {question['difficulty']}")
            task = self.generate_audio_for_question(question, i, output_folder)
            tasks.append(task)
        
        # Wait for all audio generation tasks to complete
        audio_files = await asyncio.gather(*tasks)
        audio_files = [f for f in audio_files if f]  # Remove None values
        
        print(f"\n✅ Successfully generated {len(audio_files)}/{total_questions} audio files")
        return audio_files

async def main():
    try:
        # Check for API key
        if not os.getenv('ELEVENLABS_API_KEY'):
            print("❌ Error: ELEVENLABS_API_KEY not found in .env file")
            return
        
        # Load questions from JSON file
        json_file = "chapter1_questions.json"
        if not os.path.exists(json_file):
            print(f"❌ Error: Questions file {json_file} not found")
            return
            
        with open(json_file, 'r') as f:
            questions = json.load(f)
        
        if questions:
            # Initialize generator and process questions
            tts_gen = CSCSTTSGenerator()
            audio_files = await tts_gen.process_questions(questions)
            
            if audio_files:
                print("\nGenerated audio files:")
                for file in audio_files:
                    print(file)
        else:
            print("❌ No questions found in JSON file")
            
    except Exception as e:
        print(f"❌ Critical error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())