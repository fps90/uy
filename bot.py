from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped

# بيانات حساب المساعد (session string)
api_id = "8934899"
api_hash = "bf3e98d2c351e4ad06946b4897374a1e"
session_string = "BACIVfMATb0BpsmMaPEORGdSRUC7zt71hM2llM8JduJHCre9PsZyM9VpxQaFxcq0xppAb7CeQW4-GksJzmpguSOzfWebdjpJgmJwKKyYsLvaZZOapToKH_uHf_tB8fhqXcKqCFgz13LbXAiJEbcg-LKzvfo5_QilONL7X9FMvgO9l7qH5XgXcHQ0pno8X-JUuKz2GClkxbJJgzVQWkKoAIloMuZcheqzryVReW2PveG8I3lBhfb-0kGb1OryW9Av7W7cT1D-Jp7Yp6kw0hAAalV1FfpfQ2s7uOSZUbrvuhK11XopNXjX5Rkp5Hb3igmTv0VhT8rHszPnRSsVM1GihmiOyvroNgAAAAGTF-IEAA"

# توكن البوت
bot_token = "6604522716:AAFrs8QKqrQzLNWtXzM7Ts_Q2Ei1aV_3dJ8"

# إنشاء عميل البوت
bot = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# إنشاء عميل المساعد (Session String)
assistant = Client(session_string, api_id=api_id, api_hash=api_hash)
call_client = PyTgCalls(assistant)

# متغيرات لتخزين معرفات القنوات
source_channel_id = None  # القناة التي سيتم جلب الصوتيات منها
target_channel_id = None  # القناة التي سيتم البث فيها

# دالة لعرض لوحة الأزرار
def start_markup():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📌 اضف قناة مصدر", callback_data="add_source_channel")],
            [InlineKeyboardButton("📌 اضف قناة وجهة", callback_data="add_target_channel")],
            [InlineKeyboardButton("▶️ بدء الصوت", callback_data="start_audio")]
        ]
    )

# دالة بدء البوت
@bot.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("مرحبًا! اختر العملية:", reply_markup=start_markup())

# استقبال معرف القناة المصدر
@bot.on_callback_query(filters.regex("add_source_channel"))
async def add_source_channel(client, callback_query):
    await callback_query.message.reply("أرسل معرف القناة المصدر (يجب أن يبدأ بـ -100).")

# استقبال معرف القناة الوجهة
@bot.on_callback_query(filters.regex("add_target_channel"))
async def add_target_channel(client, callback_query):
    await callback_query.message.reply("أرسل معرف القناة الوجهة (يجب أن يبدأ بـ -100).")

# استقبال معرف القناة
@bot.on_message(filters.text & filters.private)
async def save_channel_id(client, message):
    global source_channel_id, target_channel_id
    if message.text.startswith("-100"):
        if "أرسل معرف القناة المصدر" in message.reply_to_message.text:
            source_channel_id = message.text
            await message.reply(f"تم حفظ معرف القناة المصدر: {source_channel_id}", reply_markup=start_markup())
        elif "أرسل معرف القناة الوجهة" in message.reply_to_message.text:
            target_channel_id = message.text
            await message.reply(f"تم حفظ معرف القناة الوجهة: {target_channel_id}", reply_markup=start_markup())
    else:
        await message.reply("الرجاء إرسال معرف قناة صالح يبدأ بـ -100.")

# عند الضغط على بدء الصوت
@bot.on_callback_query(filters.regex("start_audio"))
async def start_audio(client, callback_query):
    global source_channel_id, target_channel_id
    if source_channel_id and target_channel_id:
        try:
            # جلب أحدث ملف صوتي من القناة المصدر
            async for message in assistant.get_chat_history(source_channel_id, limit=1):
                if message.audio:
                    audio_file_id = message.audio.file_id
                    # تنزيل الملف الصوتي
                    audio_path = await assistant.download_media(audio_file_id)
                    
                    # انضمام المساعد إلى المكالمة الصوتية في القناة الوجهة وبث الصوت
                    await call_client.join_group_call(target_channel_id, AudioPiped(audio_path))
                    await callback_query.message.reply(f"تم تشغيل الصوت من القناة {source_channel_id} في المكالمة الصوتية للقناة {target_channel_id}.")
                else:
                    await callback_query.message.reply(f"لم يتم العثور على ملفات صوتية في القناة {source_channel_id}.")
        except Exception as e:
            await callback_query.message.reply(f"حدث خطأ: {str(e)}")
    else:
        await callback_query.message.reply("لم يتم تحديد معرف القناة المصدر أو القناة الوجهة بعد.")

# تشغيل البوت وحساب المساعد
async def main():
    await assistant.start()  # تشغيل حساب المساعد
    await bot.start()        # تشغيل البوت
    print("Bot and Assistant are running...")

# تشغيل الكود
import asyncio
asyncio.run(main())
