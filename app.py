# Importing the necessary libraries
from keras.applications import ResNet50
from keras.preprocessing.image import img_to_array
from keras.applications import imagenet_utils
from PIL import Image
import numpy as np
import flask
import io
import tensorflow as tf

# Initialize the Flask app
app = flask.Flask(__name__)
model = None

# Loading the model
def load_model():
    global model
    model = ResNet50(weights="imagenet")
    global graph
    graph = tf.get_default_graph()


# Preprocessing the image
def prepare_image(image, target):
    # If the image is not of the RGB format, convert it
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Resize the image and preprocess it
    image = image.resize(target)
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)
    image = imagenet_utils.preprocess_input(image)

    return image


# Building the predict API endpoint
@app.route("/predict", methods=["POST"])
def predict():
    # Initialize the data dict that will be returned from the view
    data = {"success": False}

    # Ensure that the image was loaded properly on our endpoint
    if flask.request.method == "POST":
        if flask.request.files.get("image"):
            # Read image in PIL format
            image = flask.request.files["image"].read()
            image = Image.open(io.BytesIO(image))
            # Preprocess the image for classification
            image = prepare_image(image, target=(224, 224))
            # Classify the input image and then initialize the list of predictions to return to the client
            with graph.as_default():
                preds = model.predict(image)
                results = imagenet_utils.decode_predictions(preds)
                data["predictions"] = []

                # Loop through the results and add them to the list of returned predictions
                for (imagenetID, label, prob) in results[0]:
                    r = {"label": label, "probability": float(prob)}
                    data["predictions"].append(r)

                data["success"] = True

    return flask.jsonify(data)

# If this is the main thread of execution first load the model and then start the server
if __name__ == "__main__":
    print(("* Loading Keras model and starting Flask server..."
        "please wait until server has fully started"))
    load_model()
    app.run(host='0.0.0.0')
