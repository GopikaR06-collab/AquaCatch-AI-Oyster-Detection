import cv2
import numpy as np
from tensorflow.keras.models import load_model

model = load_model("oyster_model.keras")
cap = cv2.VideoCapture(0)

IMG_SIZE = 150  # your training size
REAL_WIDTH_CM = 8
FOCAL_LENGTH = 750  # <-- replace with your calculated value

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # ---------------- CLASSIFICATION ----------------
    resized = cv2.resize(frame, (IMG_SIZE, IMG_SIZE))
    normalized = resized / 255.0
    input_data = np.expand_dims(normalized, axis=0)
    prediction = model.predict(input_data, verbose=0)[0][0]

    if prediction > 0.5:
        label = "OYSTER"
        color = (0, 255, 0)
        confidence = prediction
    else:
        label = "NOT OYSTER"
        color = (0, 0, 255)
        confidence = 1 - prediction

    # ---------------- CONTOUR DETECTION ----------------
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    size_value = "No object"
    distance_cm = 0
    grade = "N/A"

    if contours:
        largest = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest)

        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 3)

        # Distance estimation
        distance_cm = (REAL_WIDTH_CM * FOCAL_LENGTH) / w

        # Size grading
        if w < 120:
            grade = "SMALL"
        elif w < 200:
            grade = "MEDIUM"
        else:
            grade = "LARGE"

        size_value = f"{w}px"
        cv2.putText(frame, f"Grade: {grade}", (x, y-40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        cv2.putText(frame, f"Distance: {distance_cm:.2f} cm", (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    # Show classification
    cv2.putText(frame,
                f"{label} ({confidence*100:.2f}%)",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                color,
                2)

    # Save all data for MATLAB
    with open("prediction.txt", "w") as f:
        f.write(f"{label},{confidence*100:.2f},{size_value},{distance_cm:.2f},{grade}")

    cv2.imshow("Advanced Oyster Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()