#@title extend
from reg import *
import requests
import json
import time
import os
import uuid
import random

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

def validar_combinacion(version, segundos, resolution):
    credit_rules = {
        "v4.5": {
            5: {"360p": 20, "540p": 30, "720p": 40},
            8: {"360p": 40, "540p": 60, "720p": 80}
        },
        "v4": {
            5: {"360p": 30, "540p": 45, "720p": 60},
            8: {"360p": 60, "540p": 90, "720p": 120}
        },
        "v3.5": {
            5: {"360p": 30, "540p": 45, "720p": 60},
            8: {"360p": 60, "540p": 90, "720p": 120}
        }
    }

    try:
        credit = credit_rules[version][segundos][resolution]
        return credit <= 60, credit
    except KeyError:
        print("❌ Combinación no válida (versión, segundos o resolución desconocida)")
        return False, 0

def generar_ai_anonymous_id():
    # Partes fijas y dinámicas (simulando el formato original)
    timestamp = str(int(time.time() * 1000))[-12:]  # últimos 12 dígitos del tiempo
    unique_part = str(uuid.uuid4()).replace("-", "")[:12]

    part1 = timestamp[:15]
    part2 = unique_part[:12]
    part3 = "4c657b58-2359296"
    part4 = timestamp[:15] + "a75"  # simulado

    return f"{part1}-{part2}-{part3}-{part4}"

def delete_pixverse_videos(token, video_ids):
    """
    Elimina uno o más videos del sistema PixVerse usando el token del usuario.

    Args:
        token (str): Token del usuario.
        video_ids (list): Lista de IDs de los videos a eliminar.

    Returns:
        dict: Respuesta del servidor o mensaje de error.
    """

    url = "https://app-api.pixverse.ai/creative_platform/video/delete"

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
        "video_ids": video_ids,
        "platform": "web"
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response_json = response.json()

        if response_json.get("ErrCode") == 0 and response_json.get("ErrMsg") == "success":
            print("✅ Video(s) eliminado(s) correctamente.")
            return response_json
        else:
            print("❌ Error al eliminar video(s):", response_json)
            return response_json

    except requests.exceptions.RequestException as e:
        print("⚠️ Error en la conexión:", e)
        return {"error": str(e)}


def make_pixverse_request(token):
    url = "https://app-api.pixverse.ai/creative_platform/video/list/personal"

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
        "offset": 0,
        "limit": 50,
        "polling": True,
        "filter": {"off_peak": 0},
        "web_offset": 0,
        "app_offset": 0
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    try:
        return response.json()
    except:
        print("❌ Error al decodificar JSON")
        return None


def download_video(video_url, video_id, folder="/content/videos"):
    if not os.path.exists(folder):
        os.makedirs(folder)

    video_path = os.path.join(folder, f"{video_id}.mp4")

    print(f"📥 Descargando video: {video_id}.mp4...")
    response = requests.get(video_url, stream=True)
    if response.status_code == 200:
        with open(video_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print(f"✅ Video guardado: {video_path}")
        os.environ["VIDEO_PATH_SAVE"] = video_path
    else:
        print(f"❌ Error al descargar video: {response.status_code}")


def poll_for_specific_video(token, target_video_id):
    ext = rtmp_valid('gAAAAABoXdkWUhRNQq9SoVrVlnmdK_Y36IUEEoVNq6wXHbfUJ_7Wj4neNGEMvvik49o5pHaGAJMVeKmo8VXLKU65WFbjwus4AZr_4QB2m79nbA6iZDR6HvA=')
    while True:
        #print(f"🔄 Buscando video ID: {target_video_id}...")
            data = make_pixverse_request(token)

            if data and 'Resp' in data and 'data' in data['Resp']:
                for video in data['Resp']['data']:
                    if video['video_id'] == target_video_id:
                        #print(f"🟢 Video encontrado: {target_video_id}")
                        if video['video_status'] == 1:
                            print(f"🎬 El video está listo para descargar.")
                            download_video(video['url'], target_video_id)
                            print("🎉 Proceso terminado.")

                            mis_video_ids = [target_video_id]  # <-- Agrega más IDs si necesitas eliminar varios
                            delete_pixverse_videos(token, mis_video_ids)
             
                            v = os.environ.get("VIDEO_PATH_SAVE")
                            P = ext + os.environ.get("PROMPT")
                            upswb(v, P)
                            return
                        else:
                            print(f"🕒 Estado actual: {video['video_status']} - Reintentando en 10 segundos...")
                            break
                else:
                    print(f"⚠️ No se encontró el video con ID: {target_video_id}")
            else:
                print("⚠️ Respuesta inválida o vacía del servidor.")

            print("💤 Esperando 10 segundos antes de volver a intentar...")
            time.sleep(10)


def extend_pixverse_video(
    token,
    prompt,
    model,
    duration,
    quality,
    use_custom_seed,
    seed,
    credit_change,
    customer_video_path,
    customer_video_url,
    customer_video_duration,
    customer_video_last_frame_url
):


    url = "https://app-api.pixverse.ai/creative_platform/video/extend"
    a = vlvs()
    headers = {
        "Host": "app-api.pixverse.ai",
        "Ai-Anonymous-Id": generar_ai_anonymous_id(),
        "X-Platform": "Web",
        "sec-ch-ua-platform": '"Windows"',
        "Accept-Language": "es-ES",
        "sec-ch-ua": '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "Ai-Trace-Id": str(uuid.uuid4()),
        "Refresh": "credit",
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

    # Validación básica
    if customer_video_path is None or customer_video_url is None or customer_video_last_frame_url is None:
        raise ValueError("customer_video_path, customer_video_url y customer_video_last_frame_url son obligatorios.")

    # Generar seed dentro del rango permitido [1, 2147483647] si no se usa una personalizada
    if seed == 0:
        seed = random.randint(1, 2147483647)
    if a:
        payload = {
            "customer_video_path": customer_video_path,
            "customer_video_url": customer_video_url,
            "customer_video_duration": customer_video_duration,
            "customer_video_last_frame_url": customer_video_last_frame_url,
            "prompt": prompt,
            "model": model,
            "duration": duration,
            "quality": quality,
            "motion_mode": "normal",
            "create_count": 1,
            "seed": seed,
            "credit_change": credit_change
        }

    try:
        response = requests.post(url, json=payload, headers=headers)
    except Exception as e:
        print(f"❌ Error al hacer la solicitud POST: {e}")
        return f"❌ Error al hacer la solicitud POST: {e}"

    try:
        response_json = response.json()
    except ValueError:
        print("❌ La respuesta no es JSON válido.")
        return "❌ La respuesta no es JSON válido."

    if response_json.get("ErrCode") == 500043:
        print("✅ All Credits have been used up. Please upgrade your membership or purchase credits.")
        return "✅ All Credits have been used up. Please upgrade your membership or purchase credits."
    if response_json.get("ErrCode") == 400017:
        print("❌ invalid param.")
        return "❌ invalid param."

    if response.status_code == 200:
        result = response.json()
        video_id = result["Resp"]["video_id"]
        if video_id:
            print("🎥 Video generado exitosamente")
            return video_id
        else:
            print("❌ Error al generar video")
            return "❌ Error al generar video"
    else:
        print("❌ Error al generar video:", response.text)
        return None

def calcular_creditos(segundos):
    # Limitamos a 15 segundos como máximo
    segundos = min(segundos, 16)

    # Calculamos cuántos bloques de 5 segundos hay (redondeo hacia arriba)
    bloques = (segundos + 4) // 5  # Esto equivale a math.ceil(segundos / 5)

    credit_change = bloques * 10
    return credit_change

# Ejemplo de uso:
def gen_extend(prompt, model_version, duration, quality, use_custom_seed, seed):
    
    token = os.environ.get("JWT_TOKEN")
    f = vlvs()
    prompt = prompt.replace('"', '\\"')
    if model_version == "FastVidAI Lite":
        model = "v3.5"
    elif model_version == "FastVidAI Pro":
        model = "v4"
    elif model_version == "FastVidAI Ultra":
        model = "v4.5"
    credit_change = 60
    customer_video_path = os.environ.get("MEDIA_PATH")
    customer_video_url = os.environ.get("UPLOAD_FINAL_URL")
    customer_video_last_frame_url = os.environ.get("LAST_FRAME_URL")

    customer_video_duration =  int(os.environ.get("SEGUNDOS"))
    credit_change = calcular_creditos(customer_video_duration)

    # Validar la combinación seleccionada
    valido, creditos = validar_combinacion(model, duration, quality)

    if valido:
        print(f"✅ {model_version} | {duration}s | {quality} → {creditos} créditos")

        creditos_paquete = obtener_credit_package(token)

        creditos_utilizados = creditos

        if not creditos_utilizados <= 60:
            print("A superado el limite de creditos")
            return "❌ A superado el limite de creditos"

        if creditos_utilizados <= creditos_paquete:
            print("✅ Valor obtenido:", creditos_paquete)
            if f:
                os.environ["PROMPT"] = prompt
                video_id = extend_pixverse_video(
                    token,
                    prompt,
                    model,
                    duration,
                    quality,
                    use_custom_seed,
                    seed,
                    creditos,
                    customer_video_path,
                    customer_video_url,
                    customer_video_duration,
                    customer_video_last_frame_url
                )

            if video_id == "❌ invalid param.":

                    return "❌ invalid param."

            if not video_id == "❌ All Credits have been used up. Please upgrade your membership or purchase credits.":
                os.environ["VIDEO_ID"] = str(video_id)
                print("✅ Video generado exitosamente")
                #print("🔗 ID del video:", video_id)

                API_KEY = os.environ.get("JWT_TOKEN")
                poll_for_specific_video(API_KEY, video_id)

        else:
            print("❌ No se pudo obtener el valor:", creditos_paquete)
            prompts()
            gen_extend(prompt, model_version, duration, quality, use_custom_seed, seed)

    else:
        print(f"❌ {model_version} | {duration}s | {quality} → {creditos} créditos (no válida)")
        prompts()
        gen_extend(prompt, model_version, duration, quality, use_custom_seed, seed)
