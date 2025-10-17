import requests
from bs4 import BeautifulSoup
import time

# Configuración del bot y producto
TOKEN = '7912465365:AAGjfaxheW_Zb2c4cdy0EFP8vMnuA-ohSHE'
chat_id = 916659859
url_producto = "https://www.mercadolibre.com.mx/nintendo-switch-oled-standard-heg-001-64-gb-blanco/p/MLM31000132?product_trigger_id=MLM18537258&picker=true&quantity=1"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"
}

ultimo_update_id = None
precio_anterior = None

def enviar_telegram(mensaje):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    params = {'chat_id': chat_id, 'text': mensaje}
    requests.get(url, params=params)

def obtener_precio_unico():
    respuesta = requests.get(url_producto, headers=headers)
    sopa = BeautifulSoup(respuesta.text, "html.parser")
    contenedor = sopa.find("div", class_="ui-pdp-price__second-line")
    if contenedor:
        precio_span = contenedor.find("span", class_="andes-money-amount__fraction")
        if precio_span:
            precio_texto = precio_span.text.strip().replace('.', '').replace(',', '')
            try:
                precio_numero = int(precio_texto)
                precio_formateado = "${:,}".format(precio_numero)
                print(f"Precio principal detectado: {precio_formateado}")  # debug
                return precio_formateado
            except:
                print(f"Precio principal detectado (sin formato): ${precio_texto}")  # debug
                return "$" + precio_texto
    print("No se encontró el precio principal.")
    return None

def responder_precio_si_hay_mensaje():
    global ultimo_update_id
    url_get = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    if ultimo_update_id:
        url_get += f"?offset={ultimo_update_id + 1}"
    response = requests.get(url_get)
    data = response.json()
    if 'result' in data:
        for mensaje_data in data['result']:
            update_id = mensaje_data['update_id']
            mensaje = mensaje_data.get('message')
            if not mensaje:
                continue
            text = mensaje.get('text', '').lower()
            chat = mensaje['chat']
            chat_id_msj = chat['id']
            print(f"Mensaje recibido: {text} de chat_id {chat_id_msj}")  # debug
            if chat_id_msj == chat_id and text == 'precio':
                precio_actual = obtener_precio_unico()
                enviar_telegram(f"Precio actual de tu Nintendo Switch: {precio_actual}")
            ultimo_update_id = update_id

while True:
    responder_precio_si_hay_mensaje()
    precio_actual = obtener_precio_unico()
    if precio_actual is None:
        print("No se encontró el precio en la página")
    elif precio_actual != precio_anterior:
        mensaje = f"¡El precio de Nintendo Switch cambió! Nuevo precio: {precio_actual}"
        print(mensaje)
        if precio_anterior is not None:
            enviar_telegram(mensaje)
        precio_anterior = precio_actual
    else:
        print(f"El precio sigue igual: {precio_actual}")
    time.sleep(900)
