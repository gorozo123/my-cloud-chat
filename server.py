import asyncio
import websockets
import os
import sys

CONNECTED = set()

# Храним историю сообщений прямо в оперативной памяти сервера
# Чтобы она не забивала бесплатный тариф, мы ограничим её 100 сообщениями
HISTORY = []

async def handler(websocket):
    CONNECTED.add(websocket)
    print("[ПОДКЛЮЧЕНИЕ] Новый пользователь зашел в чат.")
    try:
        # Как только ты или друг зашли — сервер сразу высылает всю сохраненную историю
        for past_msg in HISTORY:
            await websocket.send(past_msg)
            
        async def for_each_message():
            async_iterable = websocket
            async_iterator = async_iterable.__aiter__()
            while True:
                try:
                    message = await async_iterator.__anext__()
                except StopAsyncIteration:
                    break
                
                # Добавляем сообщение в историю
                HISTORY.append(message)
                if len(HISTORY) > 100:
                    HISTORY.pop(0)
                
                # Мгновенно пересылаем сообщение всем участникам
                for user_socket in CONNECTED.copy():
                    try:
                        await user_socket.send(message)
                    except:
                        if user_socket in CONNECTED:
                            CONNECTED.remove(user_socket)
        await for_each_message()
    except Exception as e:
        print(f"[ОШИБКА КЛИЕНТА]: {e}")
    finally:
        if websocket in CONNECTED:
            CONNECTED.remove(websocket)
        print("[ОТКЛЮЧЕНИЕ] Пользователь вышел из чата.")

async def main():
    port = int(os.environ.get("PORT", 10000))
    print(f"[ОБЛАКО] Запуск стабильного чат-сервера на порту {port}...")
    async with websockets.serve(handler, "0.0.0.0", port):
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        sys.exit(0)
