from flask import Flask, request, jsonify, render_template
import pandas as pd
from datetime import datetime
import pickle
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, text
import io
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


engine = create_engine("sqlite:///mydb.db")

with open("pipe_model.pkl",  "rb") as f:
    loaded_model = pickle.load(f)


app = Flask(__name__)

@app.route("/", methods=["GET"])
def guello():
    return """<h1>Flask app pa lo del vino</h1>
('color_intensity' -> color, 
('flavanoids' -> flav,
('alcohol' -> alc,
('proline' -> prol
"""

@app.route("/predict", methods=["GET"])
def predict_args():
    
    color = request.get_json().get("color", None)
    flav = request.get_json().get("flav", None)
    alc = request.get_json().get("alc", None)
    prol = request.get_json().get("prol", None)
    
    data2pred = [color, flav, alc, prol]
    
    # IF ARGS MISSING, ERROR 0
    if None in data2pred:
        return {"results": 0}

    # IF ANY VALUE NOT FLOAT, ERROR 1
    if len(data2pred) != len([float(s) for s in data2pred if not s.isalpha()]):
        return {"results": 1}
    
    # data2pred = [[5.0,2.0,13.0,746.0]]
    # loaded_model.predict(data2pred)


    inputs = str(data2pred)
    output = loaded_model.predict([data2pred])[0]
    fecha = str(datetime.now())[0:19]

    df = pd.DataFrame({
        "fecha": [fecha],
        "inputs": [inputs],
        "prediction": [output]
    })
    
    
    df.to_sql("predictions", con=engine, if_exists="append", index=None)
    
    return {"results": {"prediction": str(output)}}
    
@app.route("/check_logs", methods=["GET"])
def check_logs():
    
    filter = False
    start = request.args.get("start")
    end = request.args.get("end")
    filter = request.args.get("filter")
    
    # start = "2023-12-11 10:11:32"
    # end = "2023-12-11 10:11:34"
    if filter == True:

        query = f"""

            select * from predictions
            where fecha < "{end}"
            and fecha > "{start}";

        """
    else:
        query = f"""

            select * from predictions """
            
    return pd.read_sql(query, con=engine).to_html()

@app.route("/fi")
def fi():
    datos_graph = pd.DataFrame(loaded_model["rfc"].feature_importances_, columns=["importance"], index=["color", "flav", "alc", "prol"]).sort_values("importance", ascending=False)
    
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.bar([x for x in datos_graph.index], [x[0] for x in datos_graph.values])
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')


@app.route("/predict_form", methods=["GET", "POST"])
def predict_form():
    if request.method == "POST":
        color = request.form.get("color", None)
        flav = request.form.get("flav", None)
        alc = request.form.get("alc", None)
        prol = request.form.get("prol", None)
        
        data2pred = [color, flav, alc, prol]
        
        # IF ARGS MISSING, ERROR 0
        if None in data2pred:
            return {"results": 0}

        # IF ANY VALUE NOT FLOAT, ERROR 1
        if len(data2pred) != len([float(s) for s in data2pred if not s.isalpha()]):
            return {"results": 1}
        
        # data2pred = [[5.0,2.0,13.0,746.0]]
        # loaded_model.predict(data2pred)


        inputs = str(data2pred)
        output = loaded_model.predict([data2pred])[0]
        fecha = str(datetime.now())[0:19]

        df = pd.DataFrame({
            "fecha": [fecha],
            "inputs": [inputs],
            "prediction": [output]
        })
        
        
        df.to_sql("predictions", con=engine, if_exists="append", index=None)
    
        return render_template("form.html", prediction = output)
    
    
    return render_template("form.html", prediction = "N/A")
    
if __name__ == "__main__":
    app.run(debug=True, port=8080)
