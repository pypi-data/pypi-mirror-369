from reg import *
import requests
import os
import oss2
import uuid
from datetime import datetime
import uuid
import time
import random
import string

def verificar_imagen(token, img_id):

    url = "https://app-api.pixverse.ai/creative_platform/media/character_check_media" 
    
    headers = {
        "Host": "app-api.pixverse.ai",
        "Connection": "keep-alive",
        "Ai-Anonymous-Id": generar_ai_anonymous_id(),
        "X-Platform": "Web",
        "sec-ch-ua-platform": '"macOS"',
        "Accept-Language": "es-ES",
        "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="135", "Edge";v="135"',
        "sec-ch-ua-mobile": "?0",
        "Ai-Trace-Id": str(uuid.uuid4()),
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Token": token,
        "Origin": "https://app.pixverse.ai", 
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://app.pixverse.ai/", 
        "Accept-Encoding": "gzip, deflate"
    }
    
    payload = {
        "img_id": img_id
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("ErrMsg") == "success" and data.get("ErrCode") == 0:
            return {"success": True, "message": "La imagen es válida."}
        else:
            return {"success": False, "error": data.get("ErrMsg")}
    else:
        return {"success": False, "status_code": response.status_code, "response": response.text}


# Función para generar nombres aleatorios
def generar_nombre_aleatorio(longitud=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=longitud))

# Función principal
def crear_activo(token, img_ids):
    url = "https://app-api.pixverse.ai/creative_platform/asset/create" 
    
    headers = {
        "Host": "app-api.pixverse.ai",
        "Connection": "keep-alive",
        "Ai-Anonymous-Id": generar_ai_anonymous_id(),
        "X-Platform": "Web",
        "sec-ch-ua-platform": '"Windows"',
        "Accept-Language": "es-ES",
        "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "Ai-Trace-Id": str(uuid.uuid4()),
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Token": token,
        "Origin": "https://app.pixverse.ai", 
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://app.pixverse.ai/", 
        "Accept-Encoding": "gzip, deflate"
    }
    
    # Generar nombre aleatorio
    asset_name = generar_nombre_aleatorio()
    
    # Datos del cuerpo de la solicitud
    payload = {
        "AssetName": asset_name,
        "AssetType": 1,
        "ImgIds": img_ids
    }
    
    # Enviar solicitud POST
    response = requests.post(url, headers=headers, json=payload)
    
    # Verificar si la respuesta fue exitosa
    if response.status_code == 200:
        data = response.json()
        if data.get("ErrMsg") == "Success":
            asset_id = data["Resp"]["AssetId"]
            return asset_id
    
    return "Solicitud fallida o ErrMsg no es 'Success'"

def generar_ai_anonymous_id():
    # Partes fijas y dinámicas (simulando el formato original)
    timestamp = str(int(time.time() * 1000))[-12:]  # últimos 12 dígitos del tiempo
    unique_part = str(uuid.uuid4()).replace("-", "")[:12]

    part1 = timestamp[:15]
    part2 = unique_part[:12]
    part3 = "4c657b58-2359296"
    part4 = timestamp[:15] + "a75"  # simulado

    return f"{part1}-{part2}-{part3}-{part4}"

def obtener_credit_package(token):


    url = "https://app-api.pixverse.ai/creative_platform/user/credits"

    headers = {
        "Host": "app-api.pixverse.ai",
        "Connection": "keep-alive",
        "Ai-Anonymous-Id": generar_ai_anonymous_id(),
        "X-Platform": "Web",
        "sec-ch-ua-platform": '"Windows"',
        "Accept-Language": "es-ES",
        "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="137", "Edge";v="137"',
        "sec-ch-ua-mobile": "?0",
        "Ai-Trace-Id": str(uuid.uuid4()),
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0",
        "Accept": "application/json, text/plain, */*",
        "Token": token,
        "Origin": "https://app.pixverse.ai",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://app.pixverse.ai/",
        "Accept-Encoding": "gzip, deflate"
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        if data.get("ErrCode") == 0 and data.get("ErrMsg") == "Success":
            credit_package = data["Resp"].get("credit_package")
            return credit_package
        else:
            print("❌ Error en la respuesta de la API:", data.get("ErrMsg"))
            return 0

    except requests.exceptions.RequestException as e:
        print("⚠️ Error en la conexión:", e)
        return 0




# === 1. Función para obtener el token de carga ===
def get_upload_token(token_header, ai_anonymous_id, ai_trace_id):
    url = "https://app-api.pixverse.ai/creative_platform/getUploadToken"
    headers = {
        "Host": "app-api.pixverse.ai",
        "Connection": "keep-alive",
        "Ai-Anonymous-Id": generar_ai_anonymous_id(),
        "X-Platform": "Web",
        "sec-ch-ua-platform": '"Windows"',
        "Accept-Language": "es-ES",
        "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "Ai-Trace-Id": str(uuid.uuid4()),
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Token": token_header,
        "Origin": "https://app.pixverse.ai",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://app.pixverse.ai/",
        "Accept-Encoding": "gzip, deflate"
    }
    response = requests.post(url, headers=headers, data="")
    if response.status_code == 200:

        return response.json()["Resp"]
    else:
        print("❌ Error al obtener token:", response.text)
        return None


# === 2. Función para subir imagen usando OSS SDK (con nombre dinámico) ===
def upload_image_to_oss(image_path, token_data):
    access_key_id = token_data['Ak']
    access_key_secret = token_data['Sk']
    security_token = token_data['Token']
    endpoint = 'https://oss-accelerate.aliyuncs.com'
    bucket_name = 'pixverse-fe-upload'

    # Nombre de archivo dinámico
    file_ext = os.path.splitext(image_path)[1]  # Ej: .jpg
    dynamic_filename = f"{uuid.uuid4()}{file_ext}"
    object_name = f"upload/{dynamic_filename}"

    auth = oss2.StsAuth(access_key_id, access_key_secret, security_token)
    bucket = oss2.Bucket(auth, endpoint, bucket_name)

    try:
        with open(image_path, 'rb') as fileobj:
            result = bucket.put_object(object_name, fileobj)
        if result.status == 200:
            print("✅ Imagen subida correctamente")
            uploaded_url = f"https://{bucket_name}.{endpoint[8:]}/{object_name}"
            #print("🔗 URL:", uploaded_url)
            return object_name, uploaded_url
        else:
            print("❌ Error al subir imagen:", result.status, result.reason)
            return None, None
    except Exception as e:
        print("❌ Excepción al subir imagen:", str(e))
        return None, None


# === 3. Función para confirmar la carga en Pixverse ===
def confirm_upload_on_pixverse(path, url, name, size, token_header, ai_anonymous_id, ai_trace_id):
    confirm_url = "https://app-api.pixverse.ai/creative_platform/media/batch_upload_media"
    headers = {
        "Host": "app-api.pixverse.ai",
        "Connection": "keep-alive",
        "Ai-Anonymous-Id": generar_ai_anonymous_id(),
        "X-Platform": "Web",
        "sec-ch-ua-platform": '"Windows"',
        "Accept-Language": "es-ES",
        "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "Ai-Trace-Id": str(uuid.uuid4()),
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Token": token_header,
        "Origin": "https://app.pixverse.ai",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://app.pixverse.ai/",
        "Accept-Encoding": "gzip, deflate"
    }

    payload = {
        "images": [{
            "name": name,
            "size": size,
            "path": path
        }]
    }

    response = requests.post(confirm_url, json=payload, headers=headers)
    if response.status_code == 200:
        result = response.json()
        media_url = result["Resp"]["result"][0]["url"]
        media_id = result["Resp"]["result"][0]["id"]
        print("✅ Confirmación exitosa")
        #print("🔗 URL final:", media_url)
        return media_url, media_id
    else:
        print("❌ Error al confirmar carga:", response.text)
        return None, None


# === Ejemplo completo de uso ===
def upload_cimage(YOUR_IMAGE_PATH):
    os.environ["YOUR_IMAGE_PATH"] = YOUR_IMAGE_PATH
    API_KEY = os.environ.get("JWT_TOKEN")


    YOUR_PIXVERSE_TOKEN = API_KEY
    YOUR_AI_ANONYMOUS_ID = "196fa184746118d-0851d25932377c-26011f51-2304000-196fa184747179f"
    YOUR_AI_TRACE_ID = "e24b8004-8b6c-4215-a372-41c059efdc94"

    print("🔄 Obteniendo token de carga...")


    creditos_paquete = obtener_credit_package(API_KEY)
    print("creditos_paquete", creditos_paquete)

    if 20 <= creditos_paquete:
        print("✅ Valor obtenido:", creditos_paquete)

        token_data = get_upload_token(YOUR_PIXVERSE_TOKEN, YOUR_AI_ANONYMOUS_ID, YOUR_AI_TRACE_ID)

        if token_data:
            print("📤 Subiendo imagen a OSS...")
            image_name = os.path.basename(YOUR_IMAGE_PATH)
            media_path, media_url = upload_image_to_oss(YOUR_IMAGE_PATH, token_data)
            if media_path:
                os.environ["MEDIA_PATH"] = media_path
                print("✅ Confirmando carga...")
                uploaded_final_url, media_ids = confirm_upload_on_pixverse(
                    media_path,
                    media_url,
                    os.path.basename(media_path),
                    os.path.getsize(YOUR_IMAGE_PATH),
                    YOUR_PIXVERSE_TOKEN,
                    YOUR_AI_ANONYMOUS_ID,
                    YOUR_AI_TRACE_ID
                )

                if uploaded_final_url:
                  os.environ["UPLOAD_FINAL_URL"] = uploaded_final_url
                  os.environ["MEDIA_IDS"] = str(media_ids)
  
                
                  # Ejemplo de uso
                  API_KEY = os.environ.get("JWT_TOKEN")
                  resultado = verificar_imagen(API_KEY, media_ids)
                  print(resultado)

                  if resultado:
                    img_ids_usuario = [media_ids]
                    asset_id = crear_activo(API_KEY, img_ids_usuario)
                    print(asset_id)
                    if asset_id:
                      os.environ["ASSET_ID"] = str(asset_id)

    else:
        print("❌ No se pudo obtener el valor:", creditos_paquete)
        prompts()
        YOUR_IMAGE = os.environ.get("YOUR_IMAGE_PATH")
        upload_cimage(YOUR_IMAGE)
from reg import *
import requests
import os
import oss2
import uuid
from datetime import datetime
import uuid
import time
import random
import string

import requests

def verificar_imagen(token, img_id):

    url = "https://app-api.pixverse.ai/creative_platform/media/character_check_media" 
    
    headers = {
        "Host": "app-api.pixverse.ai",
        "Connection": "keep-alive",
        "Ai-Anonymous-Id": "196ad09e71a908-0e338d1936b62f8-26011c51-2304000-196ad09e71b121f",
        "X-Platform": "Web",
        "sec-ch-ua-platform": '"macOS"',
        "Accept-Language": "es-ES",
        "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="135", "Edge";v="135"',
        "sec-ch-ua-mobile": "?0",
        "Ai-Trace-Id": "44741b8a-4480-4356-a858-132cc080be56",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Token": token,
        "Origin": "https://app.pixverse.ai", 
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://app.pixverse.ai/", 
        "Accept-Encoding": "gzip, deflate"
    }
    
    payload = {
        "img_id": img_id
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("ErrMsg") == "success" and data.get("ErrCode") == 0:
            return {"success": True, "message": "La imagen es válida."}
        else:
            return {"success": False, "error": data.get("ErrMsg")}
    else:
        return {"success": False, "status_code": response.status_code, "response": response.text}


# Función para generar nombres aleatorios
def generar_nombre_aleatorio(longitud=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=longitud))

# Función principal
def crear_activo(token, img_ids):
    url = "https://app-api.pixverse.ai/creative_platform/asset/create" 
    
    headers = {
        "Host": "app-api.pixverse.ai",
        "Connection": "keep-alive",
        "Ai-Anonymous-Id": generar_ai_anonymous_id(),
        "X-Platform": "Web",
        "sec-ch-ua-platform": '"Windows"',
        "Accept-Language": "es-ES",
        "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "Ai-Trace-Id": str(uuid.uuid4()),
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Token": token,
        "Origin": "https://app.pixverse.ai", 
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://app.pixverse.ai/", 
        "Accept-Encoding": "gzip, deflate"
    }
    
    # Generar nombre aleatorio
    asset_name = generar_nombre_aleatorio()
    
    # Datos del cuerpo de la solicitud
    payload = {
        "AssetName": asset_name,
        "AssetType": 1,
        "ImgIds": img_ids
    }
    
    # Enviar solicitud POST
    response = requests.post(url, headers=headers, json=payload)
    
    # Verificar si la respuesta fue exitosa
    if response.status_code == 200:
        data = response.json()
        if data.get("ErrMsg") == "Success":
            asset_id = data["Resp"]["AssetId"]
            return asset_id
    
    return "Solicitud fallida o ErrMsg no es 'Success'"

def generar_ai_anonymous_id():
    # Partes fijas y dinámicas (simulando el formato original)
    timestamp = str(int(time.time() * 1000))[-12:]  # últimos 12 dígitos del tiempo
    unique_part = str(uuid.uuid4()).replace("-", "")[:12]

    part1 = timestamp[:15]
    part2 = unique_part[:12]
    part3 = "4c657b58-2359296"
    part4 = timestamp[:15] + "a75"  # simulado

    return f"{part1}-{part2}-{part3}-{part4}"

def obtener_credit_package(token):


    url = "https://app-api.pixverse.ai/creative_platform/user/credits"

    headers = {
        "Host": "app-api.pixverse.ai",
        "Connection": "keep-alive",
        "Ai-Anonymous-Id": generar_ai_anonymous_id(),
        "X-Platform": "Web",
        "sec-ch-ua-platform": '"Windows"',
        "Accept-Language": "es-ES",
        "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="137", "Edge";v="137"',
        "sec-ch-ua-mobile": "?0",
        "Ai-Trace-Id": str(uuid.uuid4()),
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0",
        "Accept": "application/json, text/plain, */*",
        "Token": token,
        "Origin": "https://app.pixverse.ai",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://app.pixverse.ai/",
        "Accept-Encoding": "gzip, deflate"
    }

    try:
        response = requests.get(url, headers=headers)
        data = response.json()

        if data.get("ErrCode") == 0 and data.get("ErrMsg") == "Success":
            credit_package = data["Resp"].get("credit_package")
            return credit_package
        else:
            print("❌ Error en la respuesta de la API:", data.get("ErrMsg"))
            return 0

    except requests.exceptions.RequestException as e:
        print("⚠️ Error en la conexión:", e)
        return 0




# === 1. Función para obtener el token de carga ===
def get_upload_token(token_header, ai_anonymous_id, ai_trace_id):
    url = "https://app-api.pixverse.ai/creative_platform/getUploadToken"
    headers = {
        "Host": "app-api.pixverse.ai",
        "Connection": "keep-alive",
        "Ai-Anonymous-Id": generar_ai_anonymous_id(),
        "X-Platform": "Web",
        "sec-ch-ua-platform": '"Windows"',
        "Accept-Language": "es-ES",
        "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "Ai-Trace-Id": str(uuid.uuid4()),
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Token": token_header,
        "Origin": "https://app.pixverse.ai",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://app.pixverse.ai/",
        "Accept-Encoding": "gzip, deflate"
    }
    response = requests.post(url, headers=headers, data="")
    if response.status_code == 200:

        return response.json()["Resp"]
    else:
        print("❌ Error al obtener token:", response.text)
        return None


# === 2. Función para subir imagen usando OSS SDK (con nombre dinámico) ===
def upload_image_to_oss(image_path, token_data):
    access_key_id = token_data['Ak']
    access_key_secret = token_data['Sk']
    security_token = token_data['Token']
    endpoint = 'https://oss-accelerate.aliyuncs.com'
    bucket_name = 'pixverse-fe-upload'

    # Nombre de archivo dinámico
    file_ext = os.path.splitext(image_path)[1]  # Ej: .jpg
    dynamic_filename = f"{uuid.uuid4()}{file_ext}"
    object_name = f"upload/{dynamic_filename}"

    auth = oss2.StsAuth(access_key_id, access_key_secret, security_token)
    bucket = oss2.Bucket(auth, endpoint, bucket_name)

    try:
        with open(image_path, 'rb') as fileobj:
            result = bucket.put_object(object_name, fileobj)
        if result.status == 200:
            print("✅ Imagen subida correctamente")
            uploaded_url = f"https://{bucket_name}.{endpoint[8:]}/{object_name}"
            #print("🔗 URL:", uploaded_url)
            return object_name, uploaded_url
        else:
            print("❌ Error al subir imagen:", result.status, result.reason)
            return None, None
    except Exception as e:
        print("❌ Excepción al subir imagen:", str(e))
        return None, None


# === 3. Función para confirmar la carga en Pixverse ===
def confirm_upload_on_pixverse(path, url, name, size, token_header, ai_anonymous_id, ai_trace_id):
    confirm_url = "https://app-api.pixverse.ai/creative_platform/media/batch_upload_media"
    headers = {
        "Host": "app-api.pixverse.ai",
        "Connection": "keep-alive",
        "Ai-Anonymous-Id": generar_ai_anonymous_id(),
        "X-Platform": "Web",
        "sec-ch-ua-platform": '"Windows"',
        "Accept-Language": "es-ES",
        "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "Ai-Trace-Id": str(uuid.uuid4()),
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "Token": token_header,
        "Origin": "https://app.pixverse.ai",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://app.pixverse.ai/",
        "Accept-Encoding": "gzip, deflate"
    }

    payload = {
        "images": [{
            "name": name,
            "size": size,
            "path": path
        }]
    }

    response = requests.post(confirm_url, json=payload, headers=headers)
    if response.status_code == 200:
        result = response.json()
        media_url = result["Resp"]["result"][0]["url"]
        media_id = result["Resp"]["result"][0]["id"]
        print("✅ Confirmación exitosa")
        #print("🔗 URL final:", media_url)
        return media_url, media_id
    else:
        print("❌ Error al confirmar carga:", response.text)
        return None, None


# === Ejemplo completo de uso ===
def upload_cimage(YOUR_IMAGE_PATH):
    os.environ["YOUR_IMAGE_PATH"] = YOUR_IMAGE_PATH
    API_KEY = os.environ.get("JWT_TOKEN")


    YOUR_PIXVERSE_TOKEN = API_KEY
    YOUR_AI_ANONYMOUS_ID = "196fa184746118d-0851d25932377c-26011f51-2304000-196fa184747179f"
    YOUR_AI_TRACE_ID = "e24b8004-8b6c-4215-a372-41c059efdc94"

    print("🔄 Obteniendo token de carga...")


    creditos_paquete = obtener_credit_package(API_KEY)
    print("creditos_paquete", creditos_paquete)

    if 20 <= creditos_paquete:
        print("✅ Valor obtenido:", creditos_paquete)

        token_data = get_upload_token(YOUR_PIXVERSE_TOKEN, YOUR_AI_ANONYMOUS_ID, YOUR_AI_TRACE_ID)

        if token_data:
            print("📤 Subiendo imagen a OSS...")
            image_name = os.path.basename(YOUR_IMAGE_PATH)
            media_path, media_url = upload_image_to_oss(YOUR_IMAGE_PATH, token_data)
            if media_path:
                os.environ["MEDIA_PATH"] = media_path
                print("✅ Confirmando carga...")
                uploaded_final_url, media_ids = confirm_upload_on_pixverse(
                    media_path,
                    media_url,
                    os.path.basename(media_path),
                    os.path.getsize(YOUR_IMAGE_PATH),
                    YOUR_PIXVERSE_TOKEN,
                    YOUR_AI_ANONYMOUS_ID,
                    YOUR_AI_TRACE_ID
                )

                if uploaded_final_url:
                  os.environ["UPLOAD_FINAL_URL"] = uploaded_final_url
                  os.environ["MEDIA_IDS"] = str(media_ids)
  
                
                  # Ejemplo de uso
                  API_KEY = os.environ.get("JWT_TOKEN")
                  resultado = verificar_imagen(API_KEY, media_ids)
                  #print(resultado)

                  if resultado:
                    img_ids_usuario = [media_ids]
                    asset_id = crear_activo(API_KEY, img_ids_usuario)
                    #print(asset_id)
                    if asset_id:
                      os.environ["ASSET_ID"] = str(asset_id)

    else:
        print("❌ No se pudo obtener el valor:", creditos_paquete)
        prompts()
        YOUR_IMAGE = os.environ.get("YOUR_IMAGE_PATH")
        upload_cimage(YOUR_IMAGE)
