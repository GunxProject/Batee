import json
import os

import requests
from telegram import (
    ParseMode,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import CallbackContext, run_async
from GabiBraunRobot import dispatcher
from GabiBraunRobot.modules.disable import DisableAbleCommandHandler
from gpytranslate import SyncTranslator


trans = SyncTranslator()


@run_async
def translate(update: Update, context: CallbackContext) -> None:
    message = update.effective_message
    reply_msg = message.reply_to_message
    if not reply_msg:
        message.reply_text("Reply to a message to translate it!")
        return
    if reply_msg.caption:
        to_translate = reply_msg.caption
    elif reply_msg.text:
        to_translate = reply_msg.text
    try:
        args = message.text.split()[1].lower()
        if "//" in args:
            source = args.split("//")[0]
            dest = args.split("//")[1]
        else:
            source = trans.detect(to_translate)
            dest = args
    except IndexError:
        source = trans.detect(to_translate)
        dest = "en"
    translation = trans(to_translate, sourcelang=source, targetlang=dest)
    reply = (
        f"<b>Translated from {source} to {dest}</b>:\n"
        f"<code>{translation.text}</code>"
    )

    message.reply_text(reply, parse_mode=ParseMode.HTML)


@run_async
def languages(update: Update, context: CallbackContext) -> None:
    update.effective_message.reply_text(
        "Click on the button below to see the list of supported language codes.",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Language codes",
                        url="https://telegra.ph/Lang-Codes-03-19-3",
                    ),
                ],
            ],
            disable_web_page_preview=True,
        ),
    )


@send_action(ChatAction.RECORD_AUDIO)
def gtts(update: Update, context: CallbackContext):
    msg = update.effective_message
    reply = " ".join(context.args)
    if not reply:
        if msg.reply_to_message:
            reply = msg.reply_to_message.text
        else:
            return msg.reply_text(
                "Reply to some message or enter some text to convert it into audio format!"
            )
        for x in "\n":
            reply = reply.replace(x, "")
    try:
        tts = gTTS(reply)
        tts.save("oda.mp3")
        with open("oda.mp3", "rb") as speech:
            msg.reply_audio(speech)
    finally:
        if os.path.isfile("oda.mp3"):
            os.remove("oda.mp3")


# Open API key
API_KEY = "6ae0c3a0-afdc-4532-a810-82ded0054236"
URL = "http://services.gingersoftware.com/Ginger/correct/json/GingerTheText"


def spellcheck(update: Update, context: CallbackContext):
    if update.effective_message.reply_to_message:
        msg = update.effective_message.reply_to_message

        params = dict(lang="US", clientVersion="2.0", apiKey=API_KEY, text=msg.text)

        res = requests.get(URL, params=params)
        changes = json.loads(res.text).get("LightGingerTheTextResult")
        curr_string = ""
        prev_end = 0

        for change in changes:
            start = change.get("From")
            end = change.get("To") + 1
            suggestions = change.get("Suggestions")
            if suggestions:
                # should look at this list more
                sugg_str = suggestions[0].get("Text")
                curr_string += msg.text[prev_end:start] + sugg_str
                prev_end = end

        curr_string += msg.text[prev_end:]
        update.effective_message.reply_text(curr_string)
    else:
        update.effective_message.reply_text(
            "Reply to some message to get grammar corrected text!"
        )


TRANSLATE_HANDLER = DisableAbleCommandHandler(["tr", "tl"], translate)
LANGUAGE_HANDLER = DisableAbleCommandHandler(["lang", "langs"], languages)

dispatcher.add_handler(TRANSLATE_HANDLER)
dispatcher.add_handler(LANGUAGE_HANDLER)

__help__ = """ 
*──「 Help for the Translator module 」──*
Use this module to translate stuff!
*Commands:*
`/tl` (or `/tr`): as a reply to a message, translates it to English.
`/tl <lang>`: translates to <lang>
eg: `/tl ja`: translates to Japanese.
`/tl <source>//<dest>`: translates from <source> to <lang>.
eg: `/tl ja//en`: translates from Japanese to English.
• /langs*:* to get list language
"""

__mod_name__ = "Translator"
__command_list__ = ["tr", "tl"]
