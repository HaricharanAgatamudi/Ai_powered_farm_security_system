import cv2
import numpy as np
import time
from ultralytics import YOLO
import pygame
import os
from datetime import datetime
import face_recognition
import pickle

class EnhancedFarmSecuritySystem:
    def __init__(self):
        # Initialize pygame for sound
        pygame.mixer.init()
        
        # Load alert sounds
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.human_alert = pygame.mixer.Sound(os.path.join(current_dir, 'human_alert.wav'))
        self.animal_alert = pygame.mixer.Sound(os.path.join(current_dir, 'animal_alert.wav'))
        self.bird_alert = pygame.mixer.Sound(os.path.join(current_dir, 'bird_alert.wav'))
        
        # Initialize the webcam (0 is usually the default camera)
        self.cap = cv2.VideoCapture(0)
        
        # Check if camera opened successfully
        if not self.cap.isOpened():
            print("Error: Could not open camera.")
            exit()
            
        # Set the resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Load YOLOv8 model
        self.model = YOLO('yolov8n.pt')  # Using the nano model for faster inference
        
        # Define classes of interest (based on COCO dataset used by YOLOv8)
        self.target_classes = {
            0: {'name': 'person', 'type': 'human'},  # Humans
            14: {'name': 'bird', 'type': 'bird'},   # Birds
            15: {'name': 'cat', 'type': 'animal'},    # Cats
            16: {'name': 'dog', 'type': 'animal'},    # Dogs
            17: {'name': 'horse', 'type': 'animal'},  # Horse 
            18: {'name': 'sheep', 'type': 'animal'},  # Sheep
            19: {'name': 'cow', 'type': 'animal'},    # Cow
            20: {'name': 'elephant', 'type': 'animal'}, # Elephant
            21: {'name': 'bear', 'type': 'animal'},   # Bear
            22: {'name': 'zebra', 'type': 'animal'},  # Zebra
            23: {'name': 'giraffe', 'type': 'animal'} # Giraffe
        }
        
        # Cooldown time between alerts (in seconds)
        self.cooldown = 5
        self.last_alert_time = time.time() - self.cooldown
        
        # Create directories
        self.save_dir = os.path.join(current_dir, 'detected_images')
        self.authorized_dir = os.path.join(current_dir, 'authorized_users')
        os.makedirs(self.save_dir, exist_ok=True)
        os.makedirs(self.authorized_dir, exist_ok=True)
        
        # Load authorized users
        self.known_face_encodings = []
        self.known_face_names = []
        self.load_authorized_users()
        
        # Face recognition parameters
        self.face_recognition_enabled = True
        self.face_recognition_cooldown = 1.0  # Check faces every second to save CPU
        self.last_face_check_time = 0
        
    def load_authorized_users(self):
        """Load authorized users' face encodings from files"""
        encodings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'authorized_users.pkl')
        
        if os.path.exists(encodings_file):
            try:
                with open(encodings_file, 'rb') as f:
                    data = pickle.load(f)
                    self.known_face_encodings = data['encodings']
                    self.known_face_names = data['names']
                print(f"Loaded {len(self.known_face_encodings)} authorized users")
            except Exception as e:
                print(f"Error loading authorized users: {e}")
                # Initialize empty if there's an error
                self.known_face_encodings = []
                self.known_face_names = []
        else:
            print("No authorized users file found. Starting with empty authorized list.")
    
    def save_authorized_users(self):
        """Save authorized users' face encodings to file"""
        data = {
            'encodings': self.known_face_encodings,
            'names': self.known_face_names
        }
        encodings_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'authorized_users.pkl')
        
        with open(encodings_file, 'wb') as f:
            pickle.dump(data, f)
        print(f"Saved {len(self.known_face_encodings)} authorized users")
    
    def add_authorized_user(self, name, face_encoding):
        """Add a new authorized user"""
        self.known_face_encodings.append(face_encoding)
        self.known_face_names.append(name)
        self.save_authorized_users()
        print(f"Added authorized user: {name}")
        
    def play_alert(self, detected_type, detected_class):
        """Play appropriate alert sound based on the type of detection"""
        current_time = time.time()
        if current_time - self.last_alert_time > self.cooldown:
            print(f"⚠️ ALERT! Detected: {detected_class}")
            
            if detected_type == 'human':
                self.human_alert.play()
            elif detected_type == 'animal':
                self.animal_alert.play()
            elif detected_type == 'bird':
                self.bird_alert.play()
                
            self.last_alert_time = current_time
    
    def save_detection(self, frame, detected_class):
        """Save the frame with detection for record keeping"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{detected_class}_{timestamp}.jpg"
        save_path = os.path.join(self.save_dir, filename)
        cv2.imwrite(save_path, frame)
        print(f"Detection saved to {save_path}")
    
    def add_new_user_mode(self):
        """Enter interactive mode to add a new authorized user"""
        print("\nEntering New User Registration Mode")
        print("Please position your face in the camera")
        print("Press 'c' to capture, 'q' to cancel")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab frame")
                break
                
            # Mirror the frame (flip horizontally for more natural view)
            frame = cv2.flip(frame, 1)
            
            # Draw a face positioning guide
            height, width = frame.shape[:2]
            center_x, center_y = width // 2, height // 2
            cv2.rectangle(frame, (center_x - 100, center_y - 125), 
                          (center_x + 100, center_y + 125), (0, 255, 0), 2)
            
            # Add instructions to the frame
            cv2.putText(frame, "Position face in the green box", 
                      (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, "Press 'c' to capture, 'q' to cancel", 
                      (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Display the frame
            cv2.imshow('New User Registration', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("User registration cancelled")
                cv2.destroyWindow('New User Registration')
                return False
                
            elif key == ord('c'):
                # Try to find a face in the current frame
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                face_locations = face_recognition.face_locations(rgb_frame)
                
                if not face_locations:
                    print("No face detected. Please position your face clearly in the green box.")
                    continue
                    
                # Take one face encoding (the first one found)
                face_encoding = face_recognition.face_encodings(rgb_frame, face_locations)[0]
                
                # Ask for a name for this user
                cv2.destroyWindow('New User Registration')
                name = input("Enter name for this authorized user: ")
                
                # Save user image
                user_image_path = os.path.join(self.authorized_dir, f"{name}.jpg")
                top, right, bottom, left = face_locations[0]
                # Expand the face region slightly
                padding = 30
                top = max(0, top - padding)
                left = max(0, left - padding)
                bottom = min(frame.shape[0], bottom + padding)
                right = min(frame.shape[1], right + padding)
                face_image = frame[top:bottom, left:right]
                cv2.imwrite(user_image_path, face_image)
                
                # Add the user to authorized list
                self.add_authorized_user(name, face_encoding)
                print(f"User {name} added successfully!")
                return True
    
    def is_authorized(self, frame):
        """Check if there are any authorized users in the frame"""
        current_time = time.time()
        
        # Only process face recognition periodically to save CPU
        if current_time - self.last_face_check_time < self.face_recognition_cooldown:
            return False
            
        self.last_face_check_time = current_time
        
        # If no authorized users are registered yet, no one can be authorized
        if len(self.known_face_encodings) == 0:
            return False
            
        # Convert the image from BGR to RGB (face_recognition uses RGB)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Find all faces in the current frame
        face_locations = face_recognition.face_locations(rgb_frame)
        
        if not face_locations:
            return False
            
        # Get face encodings for all faces in the frame
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        for face_encoding in face_encodings:
            # Compare with known faces
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.6)
            
            # If any match is found, the person is authorized
            if True in matches:
                name_index = matches.index(True)
                name = self.known_face_names[name_index]
                
                # Draw a green box around authorized face
                top, right, bottom, left = face_locations[face_encodings.index(face_encoding)]
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, f"Authorized: {name}", (left, top - 10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                return True
        
        return False
    
    def run(self):
        """Main function to run the detection system"""
        print("Starting Enhanced Farm Security System...")
        print("Press 'a' to add authorized user")
        print("Press 'q' to quit")
        
        try:
            while True:
                # Capture frame-by-frame
                ret, frame = self.cap.read()
                
                if not ret:
                    print("Failed to grab frame")
                    break
                
                # Mirror the frame (flip horizontally for more natural view)
                frame = cv2.flip(frame, 1)
                
                # Check for authorized users
                authorized_person_present = False
                if self.face_recognition_enabled:
                    authorized_person_present = self.is_authorized(frame)
                
                # Run YOLOv8 inference on the frame
                results = self.model(frame)
                
                # Process detections
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        # Get class and confidence
                        cls_id = int(box.cls[0].item())
                        conf = box.conf[0].item()
                        
                        # Check if detected class is in our target list and confidence is high enough
                        if cls_id in self.target_classes and conf > 0.5:
                            # Get coordinates and draw bounding box
                            x1, y1, x2, y2 = box.xyxy[0].tolist()
                            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                            
                            detected_info = self.target_classes[cls_id]
                            detected_class = detected_info['name']
                            detected_type = detected_info['type']
                            
                            # Draw bounding box with class name
                            color = (0, 255, 0) if (detected_type == 'human' and authorized_person_present) else (0, 0, 255)
                            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                            cv2.putText(frame, f"{detected_class} {conf:.2f}", 
                                      (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                            
                            # Only trigger alert if it's not an authorized person
                            # For humans, check authorization
                            # For animals and birds, always alert
                            if not (detected_type == 'human' and authorized_person_present):
                                self.play_alert(detected_type, detected_class)
                                self.save_detection(frame, detected_class)
                
                # Add title and instructions to the frame
                cv2.putText(frame, "Enhanced Farm Security System", 
                          (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                
                auth_status = "Authorized User: YES" if authorized_person_present else "Authorized User: NO"
                cv2.putText(frame, auth_status, 
                          (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                          
                cv2.putText(frame, "Press 'a' to add authorized user, 'q' to quit", 
                          (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                
                # Display the resulting frame
                cv2.imshow('Farm Security System', frame)
                
                # Check for key press
                key = cv2.waitKey(1) & 0xFF
                
                # Add authorized user
                if key == ord('a'):
                    self.add_new_user_mode()
                
                # Exit on 'q' press
                elif key == ord('q'):
                    break
                    
        finally:
            # Release the camera and close windows
            self.cap.release()
            cv2.destroyAllWindows()
            print("Farm Security System stopped")
    
    def __del__(self):
        # Ensure resources are released
        if hasattr(self, 'cap'):
            self.cap.release()


if __name__ == "__main__":
    security_system = EnhancedFarmSecuritySystem()
    security_system.run()