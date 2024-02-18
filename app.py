import requests
import tensorflow as tf
from flask import Flask, render_template, request

app = Flask(__name__)


def get_data(city):
    BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"
    API_KEY = "87ce6387cccc97c824ed350534e68fb2"
    url = BASE_URL + "appid=" + API_KEY + "&q=" + city
    response = requests.get(url).json()
    if response.get('cod') != 200:
        return None  # If response indicates an error, return None
    return response


def predict_cloud_burst(city):
    result = get_data(city)
    if result:
        # Extract relevant features from JSON data
        feature_names = ['coord.lat', 'coord.lon', 'main.temp', 'main.feels_like',
                         'main.pressure', 'main.humidity', 'wind.speed', 'wind.deg']

        extracted_features = [get_nested_value(
            result, name) for name in feature_names]

        # Load the model outside the function to avoid loading it with every prediction
        if 'model' not in app.config:
            app.config['model'] = tf.keras.models.load_model('api_model')

        model = app.config['model']

        # Make the prediction
        pred = model.predict([extracted_features])
        pred[0] /= 3
        return pred[0][0]
    else:
        return None


def get_nested_value(obj, key):
    keys = key.split('.')
    for k in keys:
        if isinstance(obj, dict) and k in obj:
            obj = obj[k]
        elif isinstance(obj, list) and len(obj) > 0:
            obj = obj[int(k)]
        else:
            return None
    return obj


@app.route('/', methods=['GET', 'POST'])
def home():
    prediction = None
    city_name = None  # Initialize city_name variable
    invalid_input = False
    if request.method == 'POST':
        city_name = request.form['city']  # Retrieve city name from form input
        try:
            prediction = predict_cloud_burst(city_name)
            if prediction is None:
                invalid_input = True
        except:
            invalid_input = True
    return render_template('index.html', city=city_name, prediction=prediction, invalid_input=invalid_input)


if __name__ == '__main__':
    app.run(debug=True)
