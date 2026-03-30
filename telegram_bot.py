import asyncio
import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

BOT_TOKEN = "8790404618:AAFDtcSuS9hwZJ0eSCotGcUU2IJApP026_g"
ADMIN_ID = 1211718099 

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

print("✅ Бот запущен")
print(f"👤 Admin ID: {ADMIN_ID}")

def get_stats():
    try:
        conn = sqlite3.connect('emails.db')
        c = conn.cursor()
        
        # Проверяем, есть ли таблица
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='subscribers'")
        if not c.fetchone():
            conn.close()
            return 0, 0, []
        
        c.execute("SELECT COUNT(*) FROM subscribers")
        total = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM subscribers WHERE DATE(subscribed_at) = DATE('now')")
        today = c.fetchone()[0]
        
        c.execute("SELECT email, subscribed_at FROM subscribers ORDER BY subscribed_at DESC LIMIT 5")
        recent = c.fetchall()
        
        conn.close()
        return total, today, recent
    except:
        return 0, 0, []

@dp.message(Command("start"))
async def start(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔ Доступ запрещен")
        return
    
    await message.answer(
        "👋 *Бот для просмотра подписок*\n\n"
        "📊 `/stats` - статистика\n"
        "📋 `/list` - последние подписки\n"
        "📁 `/export` - скачать список",
        parse_mode="Markdown"
    )

@dp.message(Command("stats"))
async def stats(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    total, today, recent = get_stats()
    
    text = f"📊 *Статистика*\n\n"
    text += f"👥 Всего: *{total}*\n"
    text += f"📅 За сегодня: *{today}*\n\n"
    
    if recent:
        text += "*Последние:*\n"
        for email, date in recent:
            text += f"• {email} ({date[:10]})\n"
    else:
        text += "📭 Нет подписок"
    
    await message.answer(text, parse_mode="Markdown")

@dp.message(Command("list"))
async def list_subs(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        conn = sqlite3.connect('emails.db')
        c = conn.cursor()
        c.execute("SELECT email, subscribed_at FROM subscribers ORDER BY subscribed_at DESC LIMIT 10")
        subs = c.fetchall()
        conn.close()
        
        if not subs:
            await message.answer("📭 Нет подписок")
            return
        
        text = "📋 *Последние 10 подписок:*\n\n"
        for i, (email, date) in enumerate(subs, 1):
            text += f"{i}. `{email}`\n   📅 {date[:16]}\n\n"
        
        await message.answer(text, parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@dp.message(Command("export"))
async def export(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        conn = sqlite3.connect('emails.db')
        c = conn.cursor()
        c.execute("SELECT email FROM subscribers")
        emails = c.fetchall()
        conn.close()
        
        if not emails:
            await message.answer("📭 Нет подписок для экспорта")
            return
        
        filename = f"emails_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            for email in emails:
                f.write(email[0] + '\n')
        
        with open(filename, 'rb') as f:
            await message.answer_document(
                types.BufferedInputFile(f.read(), filename=filename),
                caption=f"📁 Экспортировано {len(emails)} email'ов"
            )
        
        import os
        os.remove(filename)
        
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@dp.message()
async def all_messages(message: types.Message):
    if message.from_user.id == ADMIN_ID:
        await message.answer("Используй команды: /start, /stats, /list, /export")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())