from telegram import Bot, CallbackQuery, ChatMember, ParseMode, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
import telegram
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    Handler
)
from telegram.error import TimedOut, NetworkError
import sqlite3
from random import choice, random
from time import sleep
import threading

token = "5467599780:AAGoOEG_p5cE34uVnmpKqQ0GvZrBe3XyehY"

updater = Updater(token)
dispatcher = updater.dispatcher
bot = Bot(token)

channelsUsername = ["@FIFA_TIPS"]
# channelsUsername = ["@testnimcchannel"]
# channelsLink = ["https://t.me/testnimcchannel"]
channelsLink = ["https://t.me/FIFA_TIPS"]
# botLink = "https://t.me/NIMCbot"
botLink = "https://t.me/FIFADRAW_bot"
isCheckUsersStillJoind = False
sumAllChance = 1
adminUsernames = ["NIMCNajafpour", "JusstinBiieber", "Mehdifcp"]

JOINCHANNEL, NUMBERLOTTERYWINNER, LOTTERYWINNER = range(3)

lock = threading.Lock()

sql = """
    CREATE TABLE IF NOT EXISTS user (
        chatID VARCHAR(60),
        username VARCHAR(60),
        chance VARCHAR(60),
        subsets text,
        isBaned VARCHAR(60),
        joindDate VARCHAR(60)
    );
"""
connection = sqlite3.connect("./myDatabase.db", check_same_thread=False)
cursor = connection.cursor()

cursor.execute(sql)
connection.commit()


def addUser(chatID, username):
    joinedTime = int(time.time())
    cursor.execute(f"""INSERT INTO user(chatID, username, chance, subsets, isBaned, joindDate) 
   VALUES('{chatID}', '{username}', '{1}', '{""}', '{"0"}', '{joinedTime}');""")
    connection.commit()


def checkIsUser(chatID):
    while(True):
        try:
            cursor.execute("SELECT chatID FROM user;")
            result = cursor.fetchall()
            connection.commit()
            if (str(chatID),) in result:
                return True
            else:
                return False
        except:
            sleep(0.01)
            pass


def checkJoined(chatID):
    while True:
        isError = False
        for channel in channelsUsername:
            try:
                status = bot.get_chat_member(channel, chatID)["status"]
                if status == "left":
                    return False
            except telegram.error.BadRequest:
                return False
            except telegram.error.TimedOut:
                isError = True
            except NetworkError:
                isError = True
        if(not isError):
            return True


def selectItem(chatID, item) -> str:
    while(True):
        try:
            cursor.execute(f"SELECT {item} FROM user WHERE chatID = {chatID};")
            result = cursor.fetchall()[0][0]
            connection.commit()
            return result
        except:
            sleep(0.01)
            pass


def updateItem(chatID, item, value):
    cursor.execute(
        f"UPDATE user SET {item} = '{value}' WHERE chatID = {chatID};")
    connection.commit()


def selectAllChatID():
    while(True):
        try:
            cursor.execute(f"SELECT chatID FROM user;")
            fusers = cursor.fetchall()
            connection.commit()
            users = []
            for user in fusers:
                users.append(user[0])
            return users
        except:
            sleep(0.01)
            pass


def addChance(chatID, subsetID):
    chance = int(selectItem(subsetID, "chance"))
    chance += 1
    subsetIDs = str(selectItem(subsetID, "subsets"))
    subsetIDs += f"{chatID} "
    cursor.execute(
        f"UPDATE user SET chance = {chance} WHERE chatID = {subsetID};")
    cursor.execute(
        f"UPDATE user SET subsets = '{subsetIDs}' WHERE chatID = {subsetID};")
    connection.commit()
    return chance


def removeChance(chatID=False, subsetID=False):
    if(chatID != False):
        chance = int(selectItem(chatID, "chance"))
        chance -= 1
        subsetIDs = selectItem(chatID, "subsets")
        subsetIDs = subsetIDs.replace(f"{subsetID} ", "")
        cursor.execute(
            f"UPDATE user SET chance = {chance} WHERE chatID = {chatID};")
        cursor.execute(
            f"UPDATE user SET subsets = '{subsetIDs}' WHERE chatID = {chatID};")
    cursor.execute(
        f"DELETE FROM user WHERE chatID={subsetID};")
    connection.commit()


def checkUsersStillJoind(context: CallbackContext):
    if(not isCheckUsersStillJoind):
        dispatcher.run_async(_checkUsersStillJoind)


def _checkUsersStillJoind():
    global isCheckUsersStillJoind
    global sumAllChance

    try:
        allChance = 0
        isCheckUsersStillJoind = True
        subsetIDs = []
        users = selectAllChatID()
        for user in users:
            if(checkIsUser(user)):
                subsets = selectItem(user, "subsets")
                subsets = subsets.split()
                for chatID in subsets:
                    subsetIDs.append(chatID)
                    if(not checkJoined(chatID)):
                        removeChance(user, chatID)
                        bot.send_message(
                            user, "یکی از افرادی که دعوت کردید دیگر عضو کانال نیست. بدین صورت یک شانس از شما کسر میگردد")
                        bot.send_message(
                            chatID, "شما دیگر عضو کانال نیستید!\nبرای شروع از /start استفاده کنید")
                    else:
                        allChance += int(selectItem(chatID, "chance"))
        users = selectAllChatID()
        for user in users:
            if(not user in subsetIDs and checkIsUser(user)):
                if(not checkJoined(user)):
                    removeChance(subsetID=user)
                    bot.send_message(
                        user, "شما دیگر عضو کانال نیستید!\nبرای شروع از /start استفاده کنید")
                else:
                    allChance += int(selectItem(user, "chance"))

        # users = selectAllChatID()
        # for user in users:
        #     subsets = selectItem(user, "subsets")
        #     subsets.split()
        #     shortAdded = [user]
        #     if(len(subsets) > 100):
        #         for num in range(len(subsets)):
        #             if((int(selectItem(subsets[num], "joindDate")) - int(selectItem(subsets[num+1], "joindDate"))) < 5):
        #                 shortAdded.append(subsets[num])

        #         if(len(shortAdded) > 100):
        #             for ban in shortAdded:
        #                 updateItem(ban, "isBaned", "1")
        #                 bot.send_message(
        #                     ban, "شما به دلیل نقض قوانین از ربات بن شدید!")

        isCheckUsersStillJoind = False
        sumAllChance = allChance
    except:
        isCheckUsersStillJoind = False
        current_jobs = updater.job_queue.get_jobs_by_name(
            "checkUsersStillJoind")

        for job in current_jobs:
            job.schedule_removal()

        updater.job_queue.run_repeating(
            checkUsersStillJoind, interval=3600, first=10, name="checkUsersStillJoind")


def start(update: Update, context: CallbackContext):
    chatID = update.effective_user.id

    if(not checkIsUser(chatID)):
        updateMessage = update.message.text
        name = update.effective_user.first_name
        text = f"""سلام ....

به قرعه کشی کانال <a href="https://t.me/FIFA_TIPS">FIFA TIPS</a> خوش اومدین 😍🔥🔥

قراره هر هفته قرعه کشی های خفن برای اعضای کانال برگزار کنیم پس از عضویت در کانال اطمینان حاصل کنید تا از اخبار جا نمونین 💪

    لطفا در کانال فیفا عضو شوید سپس روی عضو شدم✅ کلیک کنید."""
        buttons = [["عضو شدم✅"]]

        try:
            update.message.reply_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
            )
        except:
            pass

        if not updateMessage == "/start":
            updateMessage = updateMessage.split(" ")
            context.user_data["subsetID"] = updateMessage[1]
        else:
            context.user_data.pop("subsetID", None)

    else:
        getChanceAndSubsetlink(update, context)

    return JOINCHANNEL


def joinChannel(update: Update, context: CallbackContext):
    chatID = update.effective_user.id

    if(not checkJoined(chatID)):
        text = f"""لطفا از عضو شدن در کانال <a href="{channelsLink[0]}">فیفا</a> اطمینان حاصل فرمایید."""
        buttons = [["عضو شدم✅"]]

        try:
            update.message.reply_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
            )
        except:
            pass

        return JOINCHANNEL
    else:
        sunsetLink = f"{botLink}?start={chatID}"
        username = update.effective_user.username
        buttons = [["درصد شانس برد با توجه به امتیازات جامع شرکت کنندگان"], [
            "راهنمای قرعه کشی 🔥"]]

        try:
            subsetChatID = context.user_data["subsetID"]
            if(checkIsUser(subsetChatID)):
                isBanned = selectItem(subsetChatID, "isBaned")
                if(isBanned != "1"):
                    chance = addChance(chatID, subsetChatID)
                    text = f"""کاربر {username} با استفاده از لینک شما عضو کانال شد.
امتیاز کنونی شما : {chance}"""
                    context.bot.send_message(subsetChatID, text)
        except:
            pass
            # print(e)

        addUser(chatID, username)

        text = f"""عالی!
شما در حال حاضر 1 امتیاز در قرعه کشی دارید 
یادتون باشه هرچی امتیاز بیشتر، شانس بیشتر برای برنده شدن رو دارین 😁

برای افزایش شانس خود لینک زیر را برای دوست های خود ارسال کنید تا در کانال فیفا عضو شوند (هر نفر = 1 امتیاز)
لینک دعوت : {sunsetLink}"""
        try:
            update.message.reply_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
            )
        except:
            pass

        return JOINCHANNEL


def getChanceAndSubsetlink(update: Update, context: CallbackContext):
    chatID = update.effective_user.id
    if(checkIsUser(chatID)):
        isBanned = selectItem(chatID, "isBaned")
        if(isBanned != "1"):
            sunsetLink = f"{botLink}?start={chatID}"
            chance = selectItem(chatID, "chance")
            buttons = [["درصد شانس برد با توجه به امتیازات جامع شرکت کنندگان"], [
                "راهنمای قرعه کشی 🔥"]]
            text = f"""مجموع امتیازات : {chance} عدد
مجموع کل شانس های شرکت کنندگان : {sumAllChance} عدد
لینک دعوت : {sunsetLink}"""

            try:
                update.message.reply_text(
                    text=text,
                    reply_markup=ReplyKeyboardMarkup(
                        buttons, resize_keyboard=True)
                )
            except:
                pass
        else:
            return ConversationHandler.END

    return JOINCHANNEL


def help(update: Update, context: CallbackContext):
    chatID = update.effective_user.id
    if(checkIsUser(chatID)):
        isBanned = selectItem(chatID, "isBaned")
        if(isBanned != "1"):
            buttons = [["درصد شانس برد با توجه به امتیازات جامع شرکت کنندگان"], [
                "راهنمای قرعه کشی 🔥"]]
            text = """سلام دوست عزیز 😍
ممنون که توی قرعه کشی شرکت کردی و امیداوریم که برنده بشی 👌

قرعه کشی ما خیلی ساده هست🤌

🔰وقتی عضو ربات میشین، در مرحله اول باید عضو کانال بشید ، سپس ربات بهتون یک لینک اختصاصی میده

🔰با ارسال لینک به دوستات و عضویت اون ها در کانال به تو امتیاز تعلق میگیره

🔰هرچی امتیازت بیشتر باشه شانس برنده شدنت توی قرعه کشی بیشتر میشه

🔰اگر فردی که از طریق لینک شما در کانال عضو شده ، از کانال لفت بده امتیاز شما نیز کسر میشه

🔰میتونید از طریق گزینه ای که در ربات وجود داره تعداد نفراتی که از طریق لینک شما عضو شدن و درصد شانستون رو ببینید

🔰در پایان هر هفته جایزه فیفا و یا جایزه های مختلف به نفرات اول از لحاظ امتیاز تعلق خواهد گرفت

🔰اگرم برنده جایزه نشدی نگران نباش چون قراره هر چند وقت یکبار براتون قرعه کشی داشته باشیم 😉"""
            try:
                update.message.reply_text(
                    text=text,
                    reply_markup=ReplyKeyboardMarkup(
                        buttons, resize_keyboard=True)
                )
            except:
                pass
        else:
            return ConversationHandler.END

    return JOINCHANNEL


def cancel(update: Update, context: CallbackContext):
    try:
        update.message.reply_text(
            "Done",
            reply_markup=ReplyKeyboardRemove()
        )
    except:
        pass
    return ConversationHandler.END


def adminStart(update: Update, context: CallbackContext):
    username = update.effective_user.username
    if(username in adminUsernames):
        buttons = [["قرعه کشی"], ["حذف همه شانس ها"]]
        try:
            update.message.reply_text(
                text="لطفا یکی از گزینه های زیر را انتخاب کنید:",
                reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True)
            )
        except:
            pass
        return NUMBERLOTTERYWINNER
    else:
        try:
            update.message.reply_text(
                text="شما ادمین نیستید!",
                reply_markup=ReplyKeyboardRemove()
            )
        except:
            pass
        return ConversationHandler.END


def getNumberLotteryWinner(update: Update, context: CallbackContext):
    try:
        update.message.reply_text(
            text="لطفا تعداد برنده را بنویسید:",
            reply_markup=ReplyKeyboardRemove()
        )
    except:
        pass
    return LOTTERYWINNER


def lotteryWinner(update: Update, context: CallbackContext):
    numberOfWinner = update.message.text
    users = selectAllChatID()
    text = "ChatID | Username | Chance\n"
    isError = True

    while(isError):
        try:
            for a in range(int(numberOfWinner)):
                winners = []
                for user in users:
                    for b in range(int(selectItem(user, "chance"))):
                        winners.append(user)
                winner = choice(winners)
                users.remove(winner)
                winnerChatID = selectItem(winner, "chatID")
                winnerUsername = selectItem(winner, "username")
                winnerChane = selectItem(winner, "chance")
                text += f" {winnerChatID} | @{winnerUsername} | {winnerChane}\n"
            isError = False
        except:
            pass

    try:
        update.message.reply_text(
            text=text,
            reply_markup=ReplyKeyboardRemove()
        )
    except:
        pass
    return ConversationHandler.END


def deleteAllChance(update: Update, context: CallbackContext):
    users = selectAllChatID()
    for user in users:
        updateItem(user, "chance", 1)
    try:
        update.message.reply_text(
            text="Done!",
            reply_markup=ReplyKeyboardRemove()
        )
    except:
        pass
    return ConversationHandler.END


def main():
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            JOINCHANNEL: [MessageHandler(
                Filters.regex('^عضو شدم✅$'), joinChannel),
                MessageHandler(
                Filters.regex('^درصد شانس برد با توجه به امتیازات جامع شرکت کنندگان$'), getChanceAndSubsetlink),
                MessageHandler(
                Filters.regex('^راهنمای قرعه کشی 🔥$'), help),
                CommandHandler('start', start)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    admin_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('admin', adminStart)],
        states={
            NUMBERLOTTERYWINNER: [MessageHandler(
                Filters.regex('^قرعه کشی$'), getNumberLotteryWinner),
                MessageHandler(
                Filters.regex('^حذف همه شانس ها$'), deleteAllChance)],
            LOTTERYWINNER: [MessageHandler(Filters.text, lotteryWinner)]
        },
        fallbacks=[CommandHandler('cancelAdmin', cancel)]
    )

    dispatcher.add_handler(conv_handler)
    dispatcher.add_handler(admin_conv_handler)
    updater.job_queue.run_repeating(
        checkUsersStillJoind, interval=10, first=10, name="checkUsersStillJoind")
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
