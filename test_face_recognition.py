import os
import face_recognition

# Load the image of the person you want to recognize
known_image = face_recognition.load_image_file("c://Users//ted//CODE//TRAINING_DATA//0_14.jpg")
known_face_encoding = face_recognition.face_encodings(known_image)[0]

# Path to the folder containing the images to check
folder_path = "c://Users//ted//CODE//TRAINING_DATA//test"

# Iterate through each file in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        file_path = os.path.join(folder_path, filename)

        # Load the image in which you want to search for the person
        unknown_image = face_recognition.load_image_file(file_path)
        unknown_face_encodings = face_recognition.face_encodings(unknown_image)

        # Compare the known face encoding with the unknown face encodings
        results = face_recognition.compare_faces(unknown_face_encodings, known_face_encoding)

        # Check if the face is found in the unknown image
        if any(results):
            print(f"The person's face is in the picture: {filename}")
        else:
            print(f"The person's face is not in the picture: {filename}")