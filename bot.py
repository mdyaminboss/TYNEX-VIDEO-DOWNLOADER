import os
import asyncio
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import yt_dlp

# লগিং সেটআপ
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# --- বটের টোকেন (অটো-ইনপুট করা) ---
BOT_TOKEN = "8255561320:AAEJC_Y_vqwi_j09iOCMbxsHZq6i8cYKmLY"

# --- অফিসিয়াল চ্যানেল ইউজারনেম (Force Subscribe-এর জন্য) ---
CHANNEL_USERNAME = "@MrTripleR_YT0"  # আপনার চ্যানেল ইউজারনেম এখানে থাকবে

# ইউজার চ্যানেলে জয়েন করেছে কি না তা চেক করার ফাংশন
async def check_user_subscription(bot, user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ['left', 'kicked']:
            return False
        return True
    except Exception as e:
        logger.error(f"Subscription Check Error: {e}")
        return False

# ১. ফোর্স সাবস্ক্রাইব পেজ (চ্যানেলে জয়েন করার নির্দেশিকা ও Verify বাটন)
async def send_force_sub_message(update_obj, context, is_callback=False):
    join_text = (
        "<b>🔒 Access Restricted!</b>\n\n"
        "╭──────────────────────────╮\n"
        "│  To use <b>TYNEX VIDEO DOWNLOADER</b>,\n"
        "│  you must join our official channel first.\n"
        "╰──────────────────────────╯\n\n"
        "👉 <b>Step 1:</b> Join our channel below.\n"
        "👉 <b>Step 2:</b> Click on <b>'Verify'</b> to unlock the bot."
    )
    keyboard = [
        [InlineKeyboardButton("📢 Join Official Channel", url="https://t.me/MrTripleR_YT0")],
        [InlineKeyboardButton("⚡ Verify Subscription", callback_data="verify_sub")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if is_callback:
        await update_obj.edit_message_text(join_text, reply_markup=reply_markup, parse_mode="HTML")
    else:
        await update_obj.message.reply_text(join_text, reply_markup=reply_markup, parse_mode="HTML")

# ২. /start কমান্ড হ্যান্ডলার
async def start_command(update: Update, context):
    user = update.effective_user
    is_subscribed = await check_user_subscription(context.bot, user.id)
    
    if not is_subscribed:
        await send_force_sub_message(update, context, is_callback=False)
        return

    await show_main_menu(update, context, edit=False)

# ৩. মূল প্রিমিয়াম মেনু (TYNEX VIDEO DOWNLOADER Dashboard)
async def show_main_menu(update: Update, context, edit=False):
    user_name = update.effective_user.first_name if update.effective_user else "User"
    
    menu_text = (
        f"🔥 <b>Welcome, {user_name} to TYNEX VIDEO DOWNLOADER!</b> 🔥\n\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "┃  ⚡ <b>ULTIMATE MEDIA ENGINE</b> ⚡\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        "🎯 <b>Supported Platforms:</b>\n"
        " ├ 🎵 <b>TikTok</b> (No Watermark)\n"
        " ├ 📘 <b>Facebook</b> (HD Quality)\n"
        " ├ 📸 <b>Instagram</b> (Reels & Posts)\n"
        " └ 🎬 <b>YouTube & Others</b>\n\n"
        "💡 <i>Just copy any video link and paste it here. High-speed downloading will start instantly!</i> 🚀"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("📥 Video Download Guide", callback_data="video_download"),
            InlineKeyboardButton("👨‍💻 Developer Info", callback_data="dev_info")
        ],
        [
            InlineKeyboardButton("🤖 Bot Information", callback_data="bot_info"),
            InlineKeyboardButton("📢 Official Channel", url="https://t.me/MrTripleR_YT0")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if edit and update.callback_query:
        await update.callback_query.message.edit_text(menu_text, reply_markup=reply_markup, parse_mode="HTML")
    else:
        if update.message:
            await update.message.reply_text(menu_text, reply_markup=reply_markup, parse_mode="HTML")

# ৪. প্রফেশনাল ইনলাইন বাটন হ্যান্ডলার
async def button_callback(update: Update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    
    if data == "verify_sub":
        is_subscribed = await check_user_subscription(context.bot, user_id)
        if is_subscribed:
            await show_main_menu(update, context, edit=True)
            await context.bot.send_message(
                chat_id=user_id, 
                text="🎉 <b>Verification Successful!</b> Welcome to <b>TYNEX VIDEO DOWNLOADER</b>. Enjoy unlimited downloads! 🔥", 
                parse_mode="HTML"
            )
        else:
            await query.answer("❌ You haven't joined the channel yet! Please join first.", show_alert=True)
            
    elif data == "video_download":
        keyboard = [[InlineKeyboardButton("« Back to Main Menu", callback_data="go_home")]]
        guide_text = (
            "📥 <b>Video Download Instructions:</b>\n\n"
            "1️⃣ Go to TikTok, Facebook, Instagram, or YouTube.\n"
            "2️⃣ Copy the video <b>Share Link</b>.\n"
            "3️⃣ Simply <b>Paste & Send</b> the link right here in this chat.\n\n"
            "✨ <i>Our server will process and send you the clean, watermark-free HD video in seconds!</i>"
        )
        await query.edit_message_text(guide_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
        
    elif data == "dev_info":
        keyboard = [
            [InlineKeyboardButton("💬 Contact Developer", url="https://t.me/YaminOnFire07")],
            [InlineKeyboardButton("« Back to Main Menu", callback_data="go_home")]
        ]
        dev_text = (
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "🔥         <b>DEVELOPER PROFILE</b>         🔥\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            "👑 <b>Developer:</b> 𝐓𝐘 𝐘𝐀𝐌𝐈𝐍\n"
            "🤝 <b>Partner:</b> @MrTripleR_YT\n"
            "🏆 <b>Sponsor:</b> TYNEX OFFICIAL\n"
            "🌐 <b>Telegram Username:</b> <code>@YaminOnFire07</code>\n\n"
            "💡 <i>Proudly engineered for high performance and lightning-fast speed.</i>"
        )
        await query.edit_message_text(dev_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")

    elif data == "bot_info":
        keyboard = [[InlineKeyboardButton("« Back to Main Menu", callback_data="go_home")]]
        info_text = (
            "┏━━━━━━━━━━━━━━━━━━━━━━━━━━┓\n"
            "🤖           <b>BOT INFORMATION</b>           🤖\n"
            "┗━━━━━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
            "📌 <b>Name:</b> TYNEX VIDEO DOWNLOADER\n"
            "⚡ <b>Version:</b> v7.0 Professional Pro\n"
            "🛡️ <b>Security:</b> Force-Subscribe Enabled\n"
            "🚀 <b>Engine:</b> Cloud-Connected Async Downloader\n\n"
            "✨ <i>Designed to provide seamless, watermark-free media downloading experience.</i>"
        )
        await query.edit_message_text(info_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="HTML")
        
    elif data == "go_home":
        await show_main_menu(update, context, edit=True)

# ৫. হাই-স্পিড ভিডিও ডাউনলোড প্রসেসিং ইঞ্জিন
async def process_and_download(update: Update, context):
    user_id = update.effective_user.id
    
    # সিকিউরিটি সাবস্ক্রিপশন চেক
    is_subscribed = await check_user_subscription(context.bot, user_id)
    if not is_subscribed:
        await send_force_sub_message(update, context, is_callback=False)
        return

    url = update.message.text.strip()
    if not url.startswith("http"):
        await update.message.reply_text("❌ <b>Invalid Link!</b> Please send a valid video URL.", parse_mode="HTML")
        return

    processing_msg = await update.message.reply_text(
        "⚡ <b>Processing Link...</b>\n"
        "⏳ <i>Fetching media from cloud servers, please hold on 🔄</i>", 
        parse_mode="HTML"
    )

    output_template = f"downloads/{user_id}.%(ext)s"
    file_path = None

    try:
        direct_video_url = None
        if "tiktok.com" in url:
            try:
                api_res = requests.post("https://www.tikwm.com/api/", data={"url": url}).json()
                if api_res.get("code") == 0:
                    direct_video_url = api_res["data"]["play"]
            except:
                pass

        loop = asyncio.get_running_loop()
        def download_task():
            nonlocal direct_video_url
            ydl_opts = {
                'format': 'best',
                'outtmpl': output_template,
                'quiet': True,
                'no_warnings': True,
                'geo_bypass': True,
                'nocheckcertificate': True,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
            }
            
            if direct_video_url:
                import urllib.request
                filename = f"downloads/{user_id}.mp4"
                urllib.request.urlretrieve(direct_video_url, filename)
                return filename, "TikTok (No Watermark)"

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                return filename, info.get('extractor', 'Media')

        file_path, platform_name = await loop.run_in_executor(None, download_task)
        
        await processing_msg.edit_text("🚀 <b>Uploading Video...</b> Almost done! ⚡", parse_mode="HTML")

        if file_path and os.path.exists(file_path):
            caption_text = (
                f"🎉 <b>Download Successful!</b>\n\n"
                f"🌐 <b>Platform:</b> <code>{platform_name.upper()}</code>\n"
                f"✨ <b>Quality:</b> HD (No Watermark)\n\n"
                f"👑 <b>Developer:</b> 𝚪𝐘 𝚼𝚫𝚳𝚰𝚴\n"
                f"🤝 <b>Partner:</b> @MrTripleR_YT\n"
                f"🏆 <b>Sponsor:</b> TYNEX OFFICIAL"
            )
            with open(file_path, 'rb') as video_file:
                await update.message.reply_video(
                    video=video_file,
                    caption=caption_text,
                    parse_mode="HTML"
                )
            os.remove(file_path)
            await processing_msg.delete()
        else:
            raise Exception("File download failed.")

    except Exception as e:
        logger.error(f"Download Error: {e}")
        if file_path and os.path.exists(file_path):
            try: os.remove(file_path)
            except: pass
                
        error_text = (
            "❌ <b>Download Failed!</b>\n\n"
            "🔍 <b>Possible Reasons:</b>\n"
            "• The link might be private or restricted.\n"
            "• The video has been removed by the creator.\n\n"
            "👉 <i>Please try again with another public link.</i>"
        )
        await processing_msg.edit_text(error_text, parse_mode="HTML")

# ৬. মেইন রান ফাংশন
def main():
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
        
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), process_and_download))

    print("🔥 TYNEX VIDEO DOWNLOADER Bot is running smoothly...")
    application.run_polling()

if __name__ == "__main__":
    main()