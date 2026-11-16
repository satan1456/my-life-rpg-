# MY LIFE RPG — Cloud Starter

ဤသည် Chapter 1 အတွက် စမ်းသပ် Cloud Starter ဖြစ်သည်။ Full game မဟုတ်သေးပါ။

## GitHub / Render ဖြင့် Deploy လုပ်ရန်

1. ဖိုင်အားလုံးကို GitHub repository root ထဲတင်ပါ။
2. Render Dashboard → New → Web Service → GitHub repository ကိုရွေးပါ။
3. Runtime: Python, Build Command: `pip install -r requirements.txt`, Start Command: `python bot.py`
4. Environment Variables ထဲတွင်:
   - `BOT_TOKEN` = BotFather မှရသော token (လျှို့ဝှက်ထားပါ)
   - `WEBHOOK_SECRET` = ခန့်မှန်းရခက်သော စကားလုံးတစ်ခု
   - `RENDER_EXTERNAL_URL` ကို Render က အလိုအလျောက်ပေးနိုင်ပါက ထည့်ရန်မလိုပါ။ မပေးပါက `https://သင့်-service.onrender.com` ထည့်ပါ။
5. Deploy ပြီး Telegram bot ကို `/start` ပို့ပါ။

## အရေးကြီးသော ကန့်သတ်ချက်များ

- Free web service သည် idle ဖြစ်လျှင် sleep ဖြစ်နိုင်သည်။
- ဤ starter သည် JSON file ဖြင့် save လုပ်ထားသောကြောင့် Render restart/redeploy လုပ်သည့်အခါ save data ပျောက်နိုင်သည်။
- Production အတွက် persistent database (ဥပမာ PostgreSQL) နှင့် error logging ထပ်ထည့်ရန်လိုသည်။
- Bot token ကို GitHub ထဲ မတင်ပါနှင့်။
