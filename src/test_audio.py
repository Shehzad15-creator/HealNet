import pygame
import time
import os  # Add this import

def play_meditation_audio():
    """Test function to play meditation audio."""
    audio_file = "assets/meditation.mp3"
    
    if not os.path.exists(audio_file):
        print("Error: Meditation audio file not found!")
        return

    pygame.mixer.init()
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()

    print("Playing meditation sound...")
    time.sleep(10)  # Play for 10 seconds
    pygame.mixer.music.stop()
    print("Meditation audio test complete.")

# Run the test
play_meditation_audio()
