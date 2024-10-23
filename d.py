import telebot
import requests
from datetime import datetime

TOKEN = '7553033910:AAEGCBIdWwPH3_-NzhbW2Q-TIzfdDtBtJXA'
bot = telebot.TeleBot(TOKEN)

# ID của nhóm được phép sử dụng bot
ALLOWED_GROUP_ID = -1002225888416

def format_time(timestamp):
    try:
        dt_object = datetime.fromtimestamp(int(timestamp))
        return dt_object.strftime('%d/%m/%Y %H:%M:%S')
    except ValueError:
        return None

def get_freefire_info(uid):
    url = f'https://hasaki.io.vn/freefire/view/info.php?uid={uid}'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if 'error' in data:
                return {'error': True}
            return data
        else:
            return None
    except Exception as e:
        print(f"Lỗi khi gọi API: {e}")
        return None

@bot.message_handler(commands=['ff'])
def handle_ff(message):
    chat_id = message.chat.id

    if chat_id != ALLOWED_GROUP_ID:
        bot.send_message(chat_id, "Không được phép sử dụng bot trong nhóm này. Vui lòng sử dụng trong nhóm hỗ trợ.")
        return

    try:
        command, uid = message.text.split()
    except ValueError:
        bot.send_message(chat_id, "Vui lòng nhập UID hợp lệ. Ví dụ: /ff 12345678")
        return

    msg = bot.send_message(chat_id, "🔮")

    try:
        data = get_freefire_info(uid)

        if data and 'error' in data:
            bot.edit_message_text("Lỗi: ID game này không tồn tại.", chat_id=chat_id, message_id=msg.message_id)
        elif data:
            if 'AccountName' not in data:
                bot.edit_message_text("Acc không tồn tại trên hệ thống hoặc hệ thống bot đang quá tải.", chat_id=chat_id, message_id=msg.message_id)
                return

            account_create_time = format_time(data.get('AccountCreateTime'))
            account_last_login = format_time(data.get('AccountLastLogin'))

            cs_rank_point = data.get('CsRank', 0)
            br_rank_point = data.get('BrRank', 0)
            account_bp_badges = data.get('AccountBPBadges', 0)
            account_likes = data.get('AccountLikes', 0) 

            guild_info = data.get('Guild Information', {})
            leader_info = guild_info.get('LeaderInfo', {})
            guild_create_time = format_time(leader_info.get('CreateTime', 0))
            leader_last_login = format_time(leader_info.get('LastLogin', 0))

            badge_info = data.get('HistoryBooyahPassInfo', [{}])
            latest_badge_info = badge_info[0] if isinstance(badge_info, list) else {}
            badge_count = latest_badge_info.get('BadgeCount', 0)
            badge_id = latest_badge_info.get('BadgeId', 0)

            pet_info = data.get('Pet Information', {})
            pet_name = pet_info.get('PetName')
            pet_level = pet_info.get('PetLevel')
            pet_exp = pet_info.get('PetEXP')
            equipped_pet = pet_info.get('Equipped?', "Không Trang Bị")

            if equipped_pet == 1:
                equipped_pet = "Đã Trang Bị"
            elif equipped_pet == 0 or equipped_pet == "Không Trang Bị":
                equipped_pet = "Không Trang Bị"

            
            result_message = f"➠ ID Game: {data.get('AccountUID')}\n"
            result_message += "<blockquote>\n"

            if 'AccountName' in data:
                result_message += f"Tên game: {data['AccountName']}\n"
            if 'AccountRegion' in data:
                result_message += f"Quốc Gia: {data['AccountRegion']}\n"
            if 'AccountLevel' in data:
                result_message += f"Cấp Độ: {data['AccountLevel']}\n"
            if 'AccountEXP' in data:
                result_message += f"Exp: {data['AccountEXP']}\n"
            if 'AccountSignature' in data:
                result_message += f"Tiểu Sử: {data['AccountSignature']}\n"     
            result_message += f"Số Like: {account_likes}\n"  # Hiển thị số Like

            result_message += "━━━━━━━━━━━━━━━━\n"

            if 'AccountCreateTime' in data:
                result_message += f"Ngày Tạo: {data['AccountCreateTime']}\n"     
            if 'AccountLastLogin' in data:
                result_message += f"Login Lần Cuối: {data['AccountLastLogin']}\n" 

            result_message += "━━━━━━━━━━━━━━━━\n"
            result_message += f"Rank Sinh Tồn: {br_rank_point}\n"
            result_message += f"Rank Tử Chiến: {cs_rank_point}\n"
            result_message += "━━━━━━━━━━━━━━━━\n"

            result_message += f"Số Booyah Mùa Trước: {badge_count} Huy Hiệu\n"
            result_message += f"Số Booyah Mùa Này: {account_bp_badges} Huy Hiệu\n"

            result_message += "━━━━━━━━━━━━━━━━\n"

            if 'GuildName' in guild_info:
                result_message += f"Tên Quân Đoàn: {guild_info['GuildName']}\n"
            else:
                result_message += "Người Chơi Không Tham Gia Quân Đoàn\n"
            
            if guild_info:
                if guild_info.get('GuildLevel'):
                    result_message += f"Cấp độ: {guild_info['GuildLevel']}\n"
                if guild_info.get('GuildMember') and guild_info.get('GuildCapacity'):
                    result_message += f"Thành Viên: {guild_info['GuildMember']}/{guild_info['GuildCapacity']}\n"
            
            if leader_info:
                if leader_info.get('LeaderName'):
                    result_message += f"➤ Info Chủ Quân Đoàn ♛\n"
                    result_message += f"Tên Game: {leader_info['LeaderName']}\n"
                if leader_info.get('LeaderLevel'):
                    result_message += f"Cấp Độ: {leader_info['LeaderLevel']}\n"
                if leader_info.get('LeaderEXP'):
                    result_message += f"Exp: {leader_info['LeaderEXP']}\n"
                if leader_info.get('LeaderUID'):
                    result_message += f"ID Game: {leader_info['LeaderUID']}\n"
                if guild_create_time:
                    result_message += f"Ngày Tạo: {guild_create_time}\n"
                if leader_last_login:
                    result_message += f"Login Lần Cuối: {leader_last_login}\n"

            result_message += "━━━━━━━━━━━━━━━━\n"

            if equipped_pet:
                result_message += f"Thú Cưng: {equipped_pet}\n"
            if pet_level:
                result_message += f"Level: {pet_level}\n"
            if pet_exp:
                result_message += f"Exp: {pet_exp}\n"
            if pet_name:
                result_message += f"Tên Pet: {pet_name}\n"

            result_message += "━━━━━━━━━━━━━━━━\n"

            if 'ReleaseVersion' in data:
                result_message += f"Phiên Bản Game: {data['ReleaseVersion']}\n"

            result_message += "</blockquote>"

            bot.edit_message_text(result_message, chat_id=chat_id, message_id=msg.message_id, parse_mode='HTML')
        else:
            bot.edit_message_text("Lỗi: Không thể lấy thông tin từ API.", chat_id=chat_id, message_id=msg.message_id)
    except Exception as e:
        bot.edit_message_text(f"Đã xảy ra lỗi: {e}", chat_id=chat_id, message_id=msg.message_id)

bot.polling()
