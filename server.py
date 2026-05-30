import asyncio
import websockets
import os

# Сюда хостинг сам подключит клиентов
CONNECTED = set()

async def handler(websocket):
    CONNECTED.add(websocket)
    try:
        async for message in websocket:
            # Рассылаем сообщение всем, кто в чате
            for user_socket in CONNECTED.copy():
                try:
                    await user_socket.send(message)
                except:
                    CONNECTED.remove(user_socket)
    except:
        pass
    finally:
        if websocket in CONNECTED:
            CONNECTED.remove(websocket)

async def main():
    # Хостинг Render сам выдает порт через переменную среды PORT
    port = int(os.environ.get("PORT", 10000))
    print(f"[ОБЛАКО] Сервер запускается на порту {port}...")
    async with websockets.serve(handler, "0.0.0.0", port):
        await asyncio.Future()  # Держит сервер включенным бесконечно

if __name__ == "__main__":
    asyncio.run(main())
