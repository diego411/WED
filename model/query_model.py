import tensorflow as tf
from tensorflow import keras

image_size = (180, 180)
model = keras.models.load_model('./model/save_at_49.h5')


def get_weeb_score(path):
    img = keras.preprocessing.image.load_img(
        path, target_size=image_size
    )
    img_array = keras.preprocessing.image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)  # Create batch axis

    predictions = model.predict(img_array)
    score = predictions[0]

    return score[0]
