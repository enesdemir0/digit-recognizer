from flask import Flask, request, jsonify, render_template
from PIL import Image, ImageOps, ImageEnhance
import numpy as np
import tensorflow as tf

app = Flask(__name__)
model = tf.keras.models.load_model('digit_model.h5')


def preprocess_image(image):
    # Convert to grayscale and invert
    image = image.convert('L')
    image = ImageOps.invert(image)

    # Enhance contrast
    image = ImageEnhance.Contrast(image).enhance(2.0)


    # Resize to 28x28 temporarily to extract the digit
    temp = image.resize((28, 28), Image.LANCZOS)
    img_array = np.array(temp)

    # Threshold to binary
    img_array = (img_array > 20).astype(np.uint8) * 255

    # Find bounding box of the digit
    coords = np.column_stack(np.where(img_array > 0))
    if coords.size == 0:
        return np.zeros((1, 28, 28, 1), dtype='float32')  # blank image fallback

    y0, x0 = coords.min(axis=0)
    y1, x1 = coords.max(axis=0)
    cropped = img_array[y0:y1+1, x0:x1+1]

    # Resize cropped digit to 20x20
    digit_img = Image.fromarray(cropped).resize((20, 20), Image.LANCZOS)

    # Paste into center of 28x28 black canvas
    final_img = Image.new('L', (28, 28), color=0)
    upper_left = ((28 - 20) // 2, (28 - 20) // 2)
    final_img.paste(digit_img, upper_left)

    # Normalize and reshape
    arr = np.array(final_img).astype('float32') / 255.0
    return arr.reshape(1, 28, 28, 1)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file found'}), 400

    file = request.files['image']
    image = Image.open(file)

    processed_image = preprocess_image(image)
    prediction = model.predict(processed_image)

    predicted_digit = int(np.argmax(prediction))
    print(f"Raw model output: {prediction}")
    print(f"Predicted digit: {predicted_digit}")

    # Just return the predicted digit, no image URL
    return jsonify({'digit': predicted_digit})


if __name__ == '__main__':
    app.run(debug=True)
