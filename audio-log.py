import whisper
import os

def transcribe_audio(mp3_file):
    # Load Whisper model (use 'small', 'medium', or 'large' depending on your needs)
    model = whisper.load_model("small")
    
    # Transcribe the MP3 file
    result = model.transcribe(mp3_file)
    
    # Output file name
    base_name = os.path.splitext(os.path.basename(mp3_file))[0]
    output_file = f"{base_name}_transcription.txt"
    
    # Save transcription
    with open(output_file, "w") as f:
        f.write(result["text"])
    
    print(f"✅ Transcription saved to: {output_file}")

# Example Usage
mp3_file = "{path}}" 
transcribe_audio(mp3_file)
