import pytest
from app import app, donantes_db

@pytest.fixture
def cliente():
    app.config['TESTING'] = True
    with app.test_client() as client:
        donantes_db.clear() # Limpiamos la BD simulada antes de cada prueba
        yield client

def test_login_exitoso(cliente):
    respuesta = cliente.post('/login', json={"usuario": "admin", "password": "123"})
    assert respuesta.status_code == 200
    assert "token" in respuesta.get_json()

def test_login_fallido(cliente):
    respuesta = cliente.post('/login', json={"usuario": "admin", "password": "mal"})
    assert respuesta.status_code == 401

def test_registro_donante_sin_token(cliente):
    respuesta = cliente.post('/registro_donante', json={"nombre": "Empresa X", "recurso": "Comida"})
    assert respuesta.status_code == 403

def test_registro_donante_con_admin(cliente):
    # 1. Hacemos login para obtener el token
    res_login = cliente.post('/login', json={"usuario": "admin", "password": "123"})
    token = res_login.get_json()["token"]
    
    # 2. Usamos el token para registrar un donante
    headers = {"Authorization": f"Bearer {token}"}
    respuesta = cliente.post('/registro_donante', json={"nombre": "Empresa X", "recurso": "Comida"}, headers=headers)
    
    assert respuesta.status_code == 201
    assert respuesta.get_json()["mensaje"] == "Donante registrado exitosamente"

def test_registro_donante_con_usuario_normal(cliente):
    # Hacemos login con "juan" que es un usuario normal
    res_login = cliente.post('/login', json={"usuario": "juan", "password": "abc"})
    token = res_login.get_json()["token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    respuesta = cliente.post('/registro_donante', json={"nombre": "Empresa Y", "recurso": "Ropa"}, headers=headers)
    
    # Debe fallar porque no es administrador
    assert respuesta.status_code == 401