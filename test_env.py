from elevenlabs.client import ElevenLabs
from dotenv import load_dotenv
import os

def test_elevenlabs_connection():
    """Test ElevenLabs API connection and authentication."""
    print("🔍 Testing ElevenLabs Setup\n")
    
    # Step 1: Load environment variables
    print("Step 1: Checking Environment Variables")
    load_dotenv()
    api_key = os.getenv('ELEVENLABS_API_KEY')
    
    if not api_key:
        print("❌ ELEVENLABS_API_KEY not found in environment variables")
        if os.path.exists('.env'):
            print("✅ .env file found")
            print("⚠️  But ELEVENLABS_API_KEY is not set correctly in .env")
            print("Please add this line to your .env file:")
            print("ELEVENLABS_API_KEY=your_api_key_here")
        else:
            print("❌ .env file not found")
            print("Please create a .env file with your API key:")
            print("ELEVENLABS_API_KEY=your_api_key_here")
        return False
    
    # Step 2: Test API Connection
    print("\nStep 2: Testing API Connection")
    try:
        # Initialize client
        client = ElevenLabs(api_key=api_key)
        
        # Test voices
        print("Checking available voices...")
        voices = client.voices.get_all()
        print("✅ Successfully retrieved voices")
        
        print("\nAvailable voices:")
        for voice in voices.voices:
            print(f"- {voice.name} (ID: {voice.voice_id})")
            
        # Select first voice for testing
        if voices.voices:
            first_voice = voices.voices[0]
            
            # Test voice generation
            print(f"\nTesting voice generation with voice: {first_voice.name}")
            test_text = "This is a test of the ElevenLabs API connection."
            
            # Get the audio bytes from the generator
            audio_generator = client.generate(
                text=test_text,
                voice=first_voice.voice_id,
                model="eleven_monolingual_v1"
            )
            
            # Convert generator to bytes
            audio_bytes = b"".join(audio_generator)
            
            # Save test audio
            test_file = "test_audio.mp3"
            with open(test_file, 'wb') as f:
                f.write(audio_bytes)
            print(f"✅ Successfully generated test audio: {test_file}")
                
            return True
        else:
            print("❌ No voices available in your account")
            return False
        
    except Exception as e:
        print(f"❌ Error connecting to ElevenLabs: {str(e)}")
        return False

if __name__ == "__main__":
    if test_elevenlabs_connection():
        print("\n✅ All tests passed! You're ready to generate TTS audio.")
    else:
        print("\n❌ Some tests failed. Please fix the issues above.")