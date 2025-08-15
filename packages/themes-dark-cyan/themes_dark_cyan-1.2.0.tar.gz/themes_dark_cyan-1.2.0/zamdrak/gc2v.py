from reg import *
import requests
import json
import time
import os
import uuid
import random



def obtener_credit_package(token):
    """
    Obtiene el valor 'credit_package' del usuario desde la API de PixVerse.

    Args:
        token (str): El token del usuario para autenticar la solicitud.

    Returns:
        int: Valor de 'credit_package' si la solicitud es exitosa.
        None: Si ocurre un error o no se encuentra el campo.
    """

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
    c = rtmp_valid('gAAAAABoXdgN2-JRkM7c1cL4xz2sMpW1uvW-kfofI7dIXuweqHUZyeQswqA6W_r1UAPc-EIYmNGQiVrHkY5CUsoE9-VsFrqS9MJTwoBWMaSo3--Tzbvybqs=')
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
                            P = c + os.environ.get("PROMPT")
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

def create_video_from_asset(token, model, duration, asset_id, prompt, quality, aspect_ratio, seed, credit_change, style, camera_movement):

    url = "https://app-api.pixverse.ai/creative_platform/video/c2v" 
    a = vlvs()

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
    if a:
        # Si seed es None, generamos uno aleatorio
        if seed == 0:
            seed = random.randint(1, 2147483647)

        payload = {
            "asset_id": asset_id,
            "prompt": prompt,
            "model": model,
            "duration": duration,
            "quality": quality,
            "aspect_ratio": aspect_ratio,
            "motion_mode": "normal",
            "create_count": 1,
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






# Ejemplo de uso:
def get_c2v(prompt, model_version, duration, quality, aspect_ratio, seed, style_selected, camera_selected):

    

    token = os.environ.get("JWT_TOKEN")
    asset_id = int(os.environ.get("ASSET_ID"))
    f = vlvs()
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

    prompt = prompt.replace('"', '\\"')
    if model_version == "FastVidAI Lite":
        model = "v3.5"
    elif model_version == "FastVidAI Pro":
        model = "v4"
    elif model_version == "FastVidAI Ultra":
        model = "v4.5"


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
                video_id = create_video_from_asset(token, model, duration, asset_id, prompt, quality, aspect_ratio, seed, creditos, style, camera_movement)

            if video_id == "❌ invalid param.":

                return

            if not video_id == "✅ All Credits have been used up. Please upgrade your membership or purchase credits.":
                os.environ["VIDEO_ID"] = str(video_id)
                print("✅ Video generado exitosamente")
                #print("🔗 ID del video:", video_id)

                API_KEY = os.environ.get("JWT_TOKEN")
                poll_for_specific_video(API_KEY, video_id)

        else:
            print("❌ No se pudo obtener el valor:", creditos_paquete)
            prompts()
            get_c2v(prompt, model_version, duration, quality, aspect_ratio, seed, style_selected, camera_selected)

    else:
        print(f"❌ {model_version} | {duration}s | {quality} → {creditos} créditos (no válida)")
        prompts()
        get_c2v(prompt, model_version, duration, quality, aspect_ratio, seed, style_selected, camera_selected)