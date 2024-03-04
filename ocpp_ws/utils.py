import aiohttp


async def send_msg_cp_log(message):
    token = '6758742667:AAGWYLcppQAlSbhjGZS16QdpSb5lIgM1sT0'
    channel_id = -1002034772310
    user_id = 1260770782
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    params = {
        'chat_id': user_id,
        'text': message
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            await response.json()
