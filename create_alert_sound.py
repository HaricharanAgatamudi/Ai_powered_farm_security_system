import numpy as np
from scipy.io import wavfile

def create_alert_sound(filename="alert.wav", duration=1.0, freq=440.0, volume=0.5):
    """
    Create a simple alert sound and save it as a WAV file
    
    Parameters:
    - filename: output filename
    - duration: sound duration in seconds
    - freq: frequency of the tone in Hz
    - volume: volume of the sound (0.0 to 1.0)
    """
    # Sample rate (samples per second)
    sample_rate = 44100
    
    # Generate time array
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Generate sine wave
    tone = np.sin(freq * 2 * np.pi * t)
    
    # Apply volume
    tone = tone * volume
    
    # Ensure the values are within range [-1.0, 1.0]
    tone = np.clip(tone, -1.0, 1.0)
    
    # Convert to 16-bit PCM
    tone = (tone * 32767).astype(np.int16)
    
    # Save as WAV file
    wavfile.write(filename, sample_rate, tone)
    print(f"Alert sound saved as {filename}")

if __name__ == "__main__":
    create_alert_sound()    