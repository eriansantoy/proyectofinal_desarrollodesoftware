from flask import Flask, request, jsonify
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mi_clave_secreta_super_segura'

# Base de datos
usuarios_db = {
    "admin": {"password": "123", "rol": "administrador"},
    "juan": {"password": "abc", "rol": "usuario"}
}
donantes_db = []

# Decorador para proteger rutas con JWT
def requiere_token(f):
    @wraps(f)
    def decorador(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"mensaje": "Falta el token"}), 403
        try:
            # Quitamos la palabra "Bearer " del token
            token_limpio = token.split(" ")[1]
            data = jwt.decode(token_limpio, app.config['SECRET_KEY'], algorithms=["HS256"])
        except Exception as e:
            return jsonify({"mensaje": "Token inválido"}), 403
        return f(data, *args, **kwargs)
    return decorador

@app.route('/login', methods=['POST'])
def login():
    datos = request.get_json()
    usuario = datos.get('usuario')
    password = datos.get('password')

    if usuario in usuarios_db and usuarios_db[usuario]['password'] == password:
        # Generador JWT con el rol del usuario
        token = jwt.encode({
            'usuario': usuario,
            'rol': usuarios_db[usuario]['rol'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({"token": token})
    return jsonify({"mensaje": "Credenciales inválidas"}), 401

@app.route('/registro_donante', methods=['POST'])
@requiere_token
def registro_donante(usuario_actual):
    # Verificamos los roles
    if usuario_actual['rol'] != 'administrador':
        return jsonify({"mensaje": "No tienes permisos de administrador"}), 401
    
    datos = request.get_json()
    nuevo_donante = {"nombre": datos.get("nombre"), "recurso": datos.get("recurso")}
    donantes_db.append(nuevo_donante)
    
    return jsonify({"mensaje": "Donante registrado exitosamente", "donante": nuevo_donante}), 201

if __name__ == '__main__':
    app.run(debug=True)