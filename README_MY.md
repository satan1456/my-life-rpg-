# MY LIFE RPG — Cloud Starter (Android Browser Setup)

ဒီ Project ကို Termux မလိုဘဲ GitHub + Render ကနေ deploy လုပ်နိုင်ရန် ပြင်ဆင်ထားပါတယ်။

## 1) GitHub ထဲတင်ရန်
1. Chrome မှ https://github.com ကိုဖွင့်ပြီး account ဝင်ပါ။
2. New repository ကိုနှိပ်ပြီး `my-life-rpg` လို့နာမည်ပေးပါ။ Public သို့မဟုတ် Private ရွေးနိုင်ပါတယ်။
3. Add file → Upload files ကိုနှိပ်ပါ။ ZIP ကို အရင်ဖုန်းထဲ Extract လုပ်ပြီး အထဲက ဖိုင်/ဖိုလ်ဒါအားလုံးကို upload လုပ်ပါ။
4. Commit changes ကိုနှိပ်ပါ။

## 2) Telegram Bot Token
1. https://t.me/BotFather ကိုဖွင့်ပါ။
2. `/newbot` ပို့ပြီး Bot နာမည်နှင့် username သတ်မှတ်ပါ။
3. ရလာတဲ့ token ကို လျှို့ဝှက်ထားပါ။ GitHub ထဲ မတင်ပါနှင့်။

## 3) Render Deploy
1. https://render.com ကိုဖွင့်ပြီး GitHub ဖြင့် sign up / sign in လုပ်ပါ။
2. New → Blueprint ကိုရွေးပြီး `my-life-rpg` repository ကိုချိတ်ပါ။
3. Deploy လုပ်ပါ။ `render.yaml` က service ကိုဖန်တီးပေးပါမယ်။
4. Render Dashboard → my-life-rpg-bot → Environment ထဲဝင်ပါ။
5. Add Environment Variable: Key `BOT_TOKEN`, Value က BotFather token ဖြစ်ပါတယ်။ Save လုပ်ပြီး redeploy လုပ်ပါ။
6. Service Logs မှာ Telegram polling started ပေါ်လာရင် Telegram မှာ ကိုယ့် Bot ကို `/start` ပို့စမ်းပါ။

## အရေးကြီး
- Render Free Web Service သည် idle ဖြစ်လျှင် sleep ဖြစ်နိုင်ပြီး အမြဲတမ်း 24/7 uptime အာမမခံပါ။
- ဒီ starter သည် SQLite ကိုသုံးထားသည်။ Free instance ရဲ့ local filesystem သည် persistent မဖြစ်နိုင်သဖြင့် restart/redeploy ဖြစ်လျှင် player save များ ပျောက်နိုင်သည်။ အမြဲသိမ်းဆည်းရန် နောက်အဆင့်တွင် persistent PostgreSQL ချိတ်ဆက်ရမည်။
- BotFather token ကို ဘယ်သူ့ကိုမှ မပို့ပါနှင့်။ Screenshot ပို့လျှင် token ကို ဖုံးထားပါ။
- ယခု build သည် Chapter 1 demo ဖြစ်ပြီး Character portrait/images နှင့် romance/quest systems မပါသေးပါ။
