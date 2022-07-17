from flask import Flask, request
import numpy as np
from io import BytesIO
import pydub as pd
from tensorflow import keras
import base64
import json
import requests as req

app = Flask(__name__)
model = keras.models.load_model('model2212.h5')

ALLOWED_EXTENSIONS = ["mp3", "wav", "m4a"]
def allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def index():
    return "INDEX PAGE"

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == "POST":

        if "chinchin" in request.form:
            return request.form["chinchin"]

        if "base64" in request.form:
            file = base64.b64decode(request.form["base64"])
            decoded = pd.AudioSegment(BytesIO(file))
            # arr = np.array(decoded.get_array_of_samples())
        else:
            if "audio" not in request.files:
                return 0
            audio = request.files["audio"]
            if audio.filename == "":
                return 0
            if audio and allowed(audio.filename):
                decoded = pd.AudioSegment(BytesIO(audio.read()))
                # arr = np.array(decoded.get_array_of_samples())

        chunks = pd.silence.split_on_silence(decoded, min_silence_len = 100, silence_thresh = decoded.dBFS - 12)
        audioChunks = []
        for i, chunk in enumerate(chunks):
            audioChunks.append(chunk)

        newAudio = pd.AudioSegment.empty()
        for segment in audioChunks:
            newAudio += segment

        arr = np.array(newAudio.get_array_of_samples())

        # process audio data
        prediction = model.predict(np.reshape(arr[:arr.size - (arr.size % 255)], (arr.size // 255, 255)))
        maxVals = np.fromiter([np.where(x == np.amax(x))[0] for x in prediction], dtype=np.int16)
        check = np.bincount(maxVals)

        temp = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        for i in range(len(check)):
            temp[i] = check[i]

        a = temp[1] + temp[2] + temp[3]
        i = temp[4] + temp[5] + temp[6]
        u = temp[7] + temp[8] + temp[9]

        if a > i and a > u:
            return "a"
        elif i > a and i > u:
            return "i"
        elif u > a and u > i:
            return "u"
        return "a"
    return "UPLOAD THROUGH POST ONLY"



@app.route("/todb", methods=["POST"])
def todb():
    if "json" in request.form:
        json_data = json.loads(request.form["json"], strict=False)
        guid = json_data["uid"]
        data = json_data["data"]
        
        for item in data:
            if item["audio"] != "null":
                file = BytesIO(base64.b64decode(item["audio"]))
                decoded = pd.AudioSegment(file)
                exported = BytesIO()
                exported = decoded.export(exported, format="wav")
                # temp_name = f"temp/{uuid.uuid4()}.wav"
                # decoded.export(temp_name, format="wav")
                chunks = pd.silence.split_on_silence(decoded, min_silence_len = 100, silence_thresh = decoded.dBFS - 12)
                audioChunks = []
                for i, chunk in enumerate(chunks):
                    audioChunks.append(chunk)

                newAudio = pd.AudioSegment.empty()
                for segment in audioChunks:
                    newAudio += segment

                arr = np.array(newAudio.get_array_of_samples())

                # process audio data
                prediction = model.predict(np.reshape(arr[:arr.size - (arr.size % 255)], (arr.size // 255, 255)))
                maxVals = np.fromiter([np.where(x == np.amax(x))[0] for x in prediction], dtype=np.int16)
                check = np.bincount(maxVals)

                temp = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
                for i in range(len(check)):
                    temp[i] = check[i]

                a = temp[1] + temp[2] + temp[3]
                i = temp[4] + temp[5] + temp[6]
                u = temp[7] + temp[8] + temp[9]

                jb = ""
                js = ""
                if i > a and i > u:
                    jb = "b"
                    js = "i"
                elif u > a and u > i:
                    jb = "c"
                    js = "u"
                else:
                    jb = "a"
                    js = "a"

                new_data = {
                    "sid": item["sid"],
                    "guid": guid,
                    "jb": item[jb],
                    "wk": item["wk"],
                    "jreal": js
                }
                new_data = json.dumps(new_data)
                # res = req.post("https://projectquiz001.000webhostapp.com/record.php", data={"json": new_data}, files={"audio": open(temp_name, "rb")})
                # if os.path.exists(temp_name):
                #     os.remove(temp_name)
                # else:
                #     print("The file does not exist")

                res = req.post("https://projectquiz001.000webhostapp.com/record.php", data={"json": new_data}, files={"audio": exported})
                res = res.text

            else:
                jb, js = ["a", "a"]
                new_data = {
                    "sid": item["sid"],
                    "guid": guid,
                    "jb": item[jb],
                    "wk": item["wk"],
                    "jreal": js
                }
                new_data = json.dumps(new_data)
                res = req.post("https://projectquiz001.000webhostapp.com/record.php", data={"json": new_data})
                res = res.text
                
        return "1"

if __name__ == '__main__':
   app.run(host="0.0.0.0", debug=True)