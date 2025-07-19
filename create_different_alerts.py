import os
import shutil
import requests
import pygame
import io
from scipy.io import wavfile
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox

def customize_alert_sounds():
    """Utility to customize alert sounds for the security system"""
    # Initialize pygame mixer for playing sounds
    pygame.mixer.init()
    
    # Dictionary of free sound effect URLs for each alert type
    sound_urls = {
        'human': [
            'https://freesound.org/data/previews/397/397354_5121236-lq.mp3',  # Alarm sound
            'https://freesound.org/data/previews/277/277021_1402315-lq.mp3',  # Siren
            'https://freesound.org/data/previews/181/181068_1284-lq.mp3'      # Alert
        ],
        'animal': [
            'https://freesound.org/data/previews/270/270528_5123851-lq.mp3',  # Animal alert
            'https://freesound.org/data/previews/411/411088_5121236-lq.mp3',  # Warning sound
            'https://freesound.org/data/previews/459/459146_9159316-lq.mp3'   # Animal detected
        ],
        'bird': [
            'https://freesound.org/data/previews/416/416434_5121236-lq.mp3',  # Chirp alert
            'https://freesound.org/data/previews/336/336899_1258513-lq.mp3',  # Bird sound
            'https://freesound.org/data/previews/156/156031_2703571-lq.mp3'   # Bird alert
        ]
    }
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    downloaded_sounds = {}
    
    print("====== Farm Security System Alert Sound Customizer ======")
    print("You can customize the alert sounds for different detection types")
    
    for detection_type in ['human', 'animal', 'bird']:
        print(f"\n== {detection_type.capitalize()} Alert Sound Customization ==")
        
        # Check if a custom sound already exists
        mp3_path = os.path.join(current_dir, f"{detection_type}_alert.mp3")
        wav_path = os.path.join(current_dir, f"{detection_type}_alert.wav")
        
        if os.path.exists(mp3_path) or os.path.exists(wav_path):
            existing_file = mp3_path if os.path.exists(mp3_path) else wav_path
            print(f"Found existing custom sound: {os.path.basename(existing_file)}")
            
            try:
                # Play the existing sound
                sound = pygame.mixer.Sound(existing_file)
                print("Playing current sound...")
                sound.play()
                pygame.time.wait(int(sound.get_length() * 1000))  # Wait for sound to finish
                
                # Ask if the user wants to keep this sound
                choice = input("Do you want to keep using this sound? (y/n): ")
                if choice.lower() == 'y':
                    downloaded_sounds[detection_type] = os.path.basename(existing_file)
                    continue
            except Exception as e:
                print(f"Error playing existing sound: {e}")
        
        # Ask the user to choose an option
        print("\nChoose an option for the alert sound:")
        print("1. Select from sample sounds")
        print("2. Use your own MP3 file")
        print("3. Create a basic default sound")
        
        option = input("Enter your choice (1-3): ")
        
        if option == '1':
            # Present sample sounds
            urls = sound_urls[detection_type]
            for i, url in enumerate(urls, 1):
                print(f"Downloading sample {i} for {detection_type}...")
                
                try:
                    response = requests.get(url, timeout=10)
                    if response.status_code == 200:
                        # Save to temporary file for pygame to play
                        temp_file = os.path.join(current_dir, f"temp_{detection_type}_{i}.mp3")
                        with open(temp_file, 'wb') as f:
                            f.write(response.content)
                        
                        # Play the sound for preview
                        print(f"Playing {detection_type} alert sound option {i}...")
                        sound = pygame.mixer.Sound(temp_file)
                        sound.play()
                        pygame.time.wait(int(sound.get_length() * 1000))  # Wait for sound to finish
                        
                        # Delete the temporary file
                        os.remove(temp_file)
                        
                        # Ask if the user likes this sound
                        choice = input(f"Do you want to use this sound for {detection_type} alerts? (y/n): ")
                        if choice.lower() == 'y':
                            # Save the chosen sound
                            filename = f"{detection_type}_alert.mp3"
                            filepath = os.path.join(current_dir, filename)
                            with open(filepath, 'wb') as f:
                                f.write(response.content)
                            print(f"Saved {detection_type} alert sound to {filepath}")
                            downloaded_sounds[detection_type] = filename
                            break
                    else:
                        print(f"Failed to download sound option {i} for {detection_type}")
                except Exception as e:
                    print(f"Error downloading or playing sound: {e}")
            
        elif option == '2':
            # Use a file browser to select an MP3 file
            print("Opening file dialog to select your MP3 file...")
            
            # Create a small GUI for file selection
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            
            file_path = filedialog.askopenfilename(
                title=f"Select MP3 or WAV file for {detection_type} alerts",
                filetypes=[("Audio files", "*.mp3 *.wav"), ("All files", "*.*")]
            )
            
            if file_path:
                if file_path.lower().endswith(('.mp3', '.wav')):
                    try:
                        # Test if the file is playable
                        sound = pygame.mixer.Sound(file_path)
                        print("Playing selected sound...")
                        sound.play()
                        pygame.time.wait(int(sound.get_length() * 1000))  # Wait for sound to finish
                        
                        # Ask for confirmation
                        confirm = input("Use this sound? (y/n): ")
                        if confirm.lower() == 'y':
                            # Copy the file to the application directory with the right name
                            ext = os.path.splitext(file_path)[1]
                            dest_filename = f"{detection_type}_alert{ext}"
                            dest_path = os.path.join(current_dir, dest_filename)
                            
                            shutil.copy2(file_path, dest_path)
                            print(f"Copied your custom sound to {dest_path}")
                            downloaded_sounds[detection_type] = dest_filename
                        else:
                            print("Sound selection cancelled.")
                    except Exception as e:
                        print(f"Error with selected file: {e}")
                        messagebox.showerror("Error", f"Could not use the selected file: {e}")
                else:
                    print("Selected file is not an MP3 or WAV file.")
                    messagebox.showerror("Invalid File", "Please select an MP3 or WAV file.")
            else:
                print("No file selected.")
        
        elif option == '3':
            print(f"Creating a basic sound for {detection_type} alerts...")
            create_basic_alert_sound(detection_type, current_dir)
            downloaded_sounds[detection_type] = f"{detection_type}_alert.wav"
        
        else:
            print("Invalid option. Creating a basic sound instead.")
            create_basic_alert_sound(detection_type, current_dir)
            downloaded_sounds[detection_type] = f"{detection_type}_alert.wav"
    
    print("\nAll alert sounds have been configured!")
    print("Your Farm Security System will use these sounds for different types of alerts.")
    
    # Summary of selected sounds
    print("\nSummary of configured alert sounds:")
    for detection_type, filename in downloaded_sounds.items():
        print(f"- {detection_type.capitalize()}: {filename}")

def create_basic_alert_sound(detection_type, directory):
    """Create a basic alert sound as fallback"""
    filename = f"{detection_type}_alert.wav"
    filepath = os.path.join(directory, filename)
    
    # Sample rate
    sample_rate = 44100
    
    # Parameters based on detection type
    if detection_type == 'human':
        duration = 1.5
        freq = 660.0
        volume = 0.8
    elif detection_type == 'animal':
        duration = 1.2
        freq = 440.0
        volume = 0.7
    else:  # bird
        duration = 0.8
        freq = 880.0
        volume = 0.6
        
    # Generate time array
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Generate sine wave with pulsing effect for more attention-grabbing sound
    tone = np.sin(freq * 2 * np.pi * t) * (0.7 + 0.3 * np.sin(8 * np.pi * t))
    
    # Apply volume
    tone = tone * volume
    
    # Ensure the values are within range [-1.0, 1.0]
    tone = np.clip(tone, -1.0, 1.0)
        
    # Convert to 16-bit PCM
    tone = (tone * 32767).astype(np.int16)
    
    # Save as WAV file
    wavfile.write(filepath, sample_rate, tone)
    print(f"Basic alert sound saved as {filepath}")

if __name__ == "__main__":
    customize_alert_sounds()