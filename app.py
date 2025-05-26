from flask import Flask, request, jsonify
from statistics import mean
import importlib
import obtener_notas as on
from flask_cors import CORS
app = Flask(__name__)

CORS(app)
importlib.reload(on)


@app.route('/api/notas', methods=['POST'])
def obtener_notas():
    data = request.get_json()
    titulo = data.get('pelicula', '').strip()
    if not titulo:
        return jsonify({"error": "No se proporcionó título"}), 400
    
    peli = on.Peliculas(titulo)
    notas = peli.get_nota_todas()
    def safe_mean(values):
        filtered = [v for v in values if isinstance(v, (int, float))]
        if filtered:
            return mean(filtered)
        else:
            return None  
    media_criticas = safe_mean(notas['criticas'].values())
    media_audiencia = safe_mean(notas['audiencia'].values())
    notas = {**notas['audiencia'], **notas['criticas']}       
    return jsonify({
        "pelicula": titulo,
        "notas": notas,
        "media_criticas": media_criticas,
        "media_audiencia": media_audiencia
    })

if __name__ == "__main__":
    app.run()
