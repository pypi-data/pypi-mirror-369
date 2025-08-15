#@title gen imagen a video full v3.5, v4, v4.5
from reg import *
import requests
import json
import time
import os
import uuid

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
    im = rtmp_valid('gAAAAABoXdlpFxpnKyE_zltuQQl_AvPEVnOpRS9FJowzYkqmWhrZEDudqFbTcGYZZKjoExBvJzEl40ASXrwlch8lrcPAEIbjEcLBQr9Nme4BXeC3ihyOmR0=')
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
                            P = im + os.environ.get("PROMPT")
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


def generate_video_from_image(media_path, media_url, prompt, duration, quality, token_header, models, credit_change, style, camera_movement, seed, seed_select):

    if models == "v3.5":
      camera_movement = "normal"
    a = vlvs()
    url = "https://app-api.pixverse.ai/creative_platform/video/i2v"
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
        "Refresh": "credit",
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
    if a:
        # Generar seed si no se provee
        if seed == 0:
            seed = random.randint(1, 2147483647)

        payload = {
            "customer_img_path": media_path,
            "prompt": prompt,
            "duration": duration,
            "quality": quality,
            "motion_mode": "normal",
            "model": models,
            "customer_img_url": media_url,
            "lip_sync_tts_speaker_id": "Auto",
            "seed": seed,
            "credit_change": credit_change
        }

        # Añadir solo si no son 'normal'
        if style != "normal":
            payload["style"] = style
        if camera_movement != "normal":
            payload["camera_movement"] = camera_movement


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


def gen_i2v(prompt, duration, quality, model_version, seed, seed_select, style_selected, camera_selected):
    if model_version == "FastVidAI Lite":
        models = "v3.5"
    elif model_version == "FastVidAI Pro":
        models = "v4"
    elif model_version == "FastVidAI Ultra":
        models = "v4.5"
    prompt = prompt.replace('"', '\\"')

    API_KEY = os.environ.get("JWT_TOKEN")
    media_path = os.environ.get("MEDIA_PATH")
    uploaded_final_url = os.environ.get("UPLOAD_FINAL_URL")
    f = vlvs()
    YOUR_PIXVERSE_TOKEN = API_KEY

    control_ids = {
        "Normal": "normal",
        "Horizontal Izquirda": "horizontal_left",
        "Horizontal Derecha": "horizontal_right",
        "Vertical Arriba": "vertical_up",
        "Vertical Abajo": "vertical_down",
        "Movimiento de Grúa hacia Arriba": "crane_up",
        "Dolly Zoom": "hitchcock",
        "Acercar": "zoom_in",
        "Alejar": "zoom_out",
        "Zoom Rápido Acercando": "quickly_zoom_in",
        "Zoom Rápido Alejando": "quickly_zoom_out",
        "Zoom Suave Acercando": "smooth_zoom_in",
        "Super Dolly Alejando": "super_dolly_out",
        "Toma de Rastreo Izquierdo": "left_follow",
        "Toma de Rastreo Derecho": "right_follow",
        "Toma de Arco Izquierdo": "pan_left",
        "Toma en arco derecho": "pan_right",
        "Toma Fija": "fix_bg",
        "Ángulo de Cámara": "camera_rotation",
        "Brazo Robótico": "robo_arm",
        "Barrido Rápido": "whip_pan"
    }

    camera_movement = control_ids.get(camera_selected)

    style_ids = {
        "Normal": "normal",
        "Anime": "anime",
        "Animación 3D": "3d_animation",
        "Cómic": "comic",
        "Cyberpunk": "cyberpunk",
        "Arcilla": "clay"
    }

    style = style_ids.get(style_selected)
    

    # Validar la combinación seleccionada
    valido, creditos = validar_combinacion(models, duration, quality)

    if valido:
        print(f"✅ {model_version} | {duration}s | {quality} → {creditos} créditos")

        creditos_paquete = obtener_credit_package(API_KEY)

        creditos_utilizados = creditos

        if not creditos_utilizados <= 60:
            print("A superado el limite de creditos")
            return "❌ No se pudo obtener el valor."

        if creditos_utilizados <= creditos_paquete:
             print("✅ Valor obtenido:", creditos_paquete)
             if f:
                 os.environ["PROMPT"] = prompt
                 video_id = generate_video_from_image(
                            media_path,
                            uploaded_final_url,
                            prompt,
                            duration,
                            quality,
                            YOUR_PIXVERSE_TOKEN,
                            models, creditos, style, camera_movement, seed, seed_select
                        )

                 if video_id:
                    os.environ["VIDEO_ID"] = str(video_id)
                    print("✅ Video generado exitosamente")
                    #print("🔗 ID del video:", video_id)

                    API_KEY = os.environ.get("JWT_TOKEN")
                    poll_for_specific_video(API_KEY, video_id)

        else:
             print("❌ No se pudo obtener el valor:", creditos_paquete)
             prompts()
             gen_i2v(prompt, duration, quality, model_version, seed, seed_select, style, camera_movement)

    else:
        print(f"❌ {model_version} | {duration}s | {quality} → {creditos} créditos (no válida)")
        prompts()
        gen_i2v(prompt, duration, quality, model_version, seed, seed_select, style, camera_movement)
