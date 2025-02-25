from dotenv import load_dotenv
import os

def check_api_keys():
    """Check both ElevenLabs and Anthropic API keys."""
    # Load .env file
    load_dotenv()
    
    print("\n🔍 Checking API Keys Setup")
    print("========================")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found in current directory")
        print(f"Current directory: {os.getcwd()}")
        return False
        
    print("✅ .env file found")
    
    # Read and display .env format
    with open('.env', 'r') as f:
        content = f.readlines()
    
    print("\n📄 Current .env format:")
    print("------------------------")
    for line in content:
        # Show format while hiding actual keys
        if "=" in line:
            key, value = line.strip().split('=', 1)
            print(f"{key}=[{'*' * len(value)}]")
    
    # Check individual keys
    print("\n🔑 API Keys Status:")
    print("------------------------")
    
    # Check ElevenLabs API Key
    elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')
    if elevenlabs_key:
        print("\nElevenLabs API Key:")
        print(f"✅ Found")
        print(f"✅ Length: {len(elevenlabs_key)} characters")
        print(f"✅ Starts with: {elevenlabs_key[:4]}...")
    else:
        print("\n❌ ElevenLabs API Key not found")
        print("Should be in format: ELEVENLABS_API_KEY=your_key_here")
    
    # Check Anthropic API Key
    anthropic_key = os.getenv('ANTHROPIC_API_KEY')
    if anthropic_key:
        print("\nAnthropic API Key:")
        print(f"✅ Found")
        print(f"✅ Length: {len(anthropic_key)} characters")
        print(f"✅ Starts with: {anthropic_key[:4]}...")
    else:
        print("\n❌ Anthropic API Key not found")
        print("Should be in format: ANTHROPIC_API_KEY=your_key_here")
    
    print("\n📋 Required .env format:")
    print("------------------------")
    print("ELEVENLABS_API_KEY=your_elevenlabs_key_here")
    print("ANTHROPIC_API_KEY=your_anthropic_key_here")
    
    return bool(elevenlabs_key and anthropic_key)

if __name__ == "__main__":
    if check_api_keys():
        print("\n✅ All API keys are set up correctly!")
    else:
        print("\n❌ Some API keys are missing or incorrect. Please check the format above.")