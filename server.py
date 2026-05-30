import asyncio
import websockets
import os
import urllib.request
import urllib.parse
import threading

CONNECTED = set()
HISTORY = []
PASTE_URL = None  # Сюда автоматически сохранится ссылка на облачный текст

def save_to_cloud(text_data):
    """Абсолютно бесплатно и без регистраций сохраняет переписку в текстовый буфер dpaste"""
    global PASTE_URL
    try:
        url = "https://dpaste.org"
        data = urllib.parse.urlencode({"content": text_data, "expiry_days": 30}).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req) as response:
            PASTE_URL = response.read().decode("utf-8").strip()
    except Exception as e:
        print(f"Ошибка сохранения истории: {e}")

# Пишем базовую строчку в историю при старте
save_to_cloud("Система: Чат успешно запущен.")

async def handler(websocket):
    CONNECTED.add(websocket)
    try:
        # Как только ты или друг зашли — сервер сразу высылает всю сохраненную историю
        for past_msg in HISTORY:
            await websocket.send(past_msg)
            
        async def for_each_message():
            global HISTORY
            async for message in websocket:
                HISTORY.append(message)
                
                # Храним последние 100 сообщений, чтобы чат не тормозил
                if len(HISTORY) > 100:
                    HISTORY.pop(0)
                
                # В отдельном фоновом потоке тихо обновляем архив в облаке dpaste
                full_text = "\n".join(HISTORY)
                threading.Thread(target=save_to_cloud, args=(full_text,), daemon=True).start()
                
                # Мгновенно пересылаем сообщение всем, кто в чате
                for user_socket in CONNECTED.copy():
                    try:
                        await user_socket.send(message)
                    except:
                        CONNECTED.remove(user_socket)
        await for_each_message()
    except:
        pass
    finally:
        if websocket in CONNECTED:
            CONNECTED.remove(websocket)

async def main():
    port = int(os.environ.get("PORT", 10000))
    print(f"[ОБЛАКО] Стабильный сервер запущен на порту {port}...")
    async with websockets.serve(handler, "0.0.0.0", port):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
