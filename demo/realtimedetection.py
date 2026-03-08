import cv2
from keras.models import model_from_json
import numpy as np
from keras.preprocessing.image import load_img

# Load model
json_file = open("emotiondetector.json", "r")
model_json = json_file.read()
json_file.close()
model = model_from_json(model_json)
model.load_weights("emotiondetector.h5")

# Load face detector
haar_file = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(haar_file)
def extract_features(img):
    feature = np.array(img)
    feature = feature.reshape(1, 48, 48, 1)
    return feature / 255.0



# Start webcam
webcam = cv2.VideoCapture(0)

# Emotion labels mapping
emotion_labels = {
    0: 'angry',
    1: 'contempt',
    2: 'disgust',
    3: 'fear',
    4: 'happy',
    5: 'neutral',
    6: 'sad',
    7: 'surprised',
    8: 'angry',
    9: 'contempt',
    10: 'disgust',
    11: 'fear',
    12: 'happy',
    13: 'neutral',
    14: 'sad',
    15: 'surprised',
    16: 'angry',
    17: 'contempt',
    18: 'disgust'
}

while True:
    i, im = webcam.read()

    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(im, 1.3, 5)

    try:
        for (p, q, r, s) in faces:
            image = gray[q:q+s, p:p+r]

            cv2.rectangle(im, (p, q), (p+r, q+s), (255, 0, 0), 2)

            image = cv2.resize(image, (48, 48))

            img = extract_features(image)

            pred = model.predict(img)
            emotion_index = int(pred.argmax())
            prediction_label = emotion_labels.get(emotion_index, 'unknown')

            print(f"Predicted Emotion: {prediction_label}")

            cv2.putText(
                im,
                f"Emotion: {prediction_label}",
                (p-10, q-10),
                cv2.FONT_HERSHEY_COMPLEX_SMALL,
                2,
                (0, 0, 255)
            )

        cv2.imshow("Output", im)

        if cv2.waitKey(27) == 27:
            break

    except cv2.error:
        pass
