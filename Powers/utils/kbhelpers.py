from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def ikb(rows=None, back=False, todo="start_back"):
    if rows is None:
        rows = []
    lines = []
    try:
        for row in rows:
            line = []
            for button in row:
                btn_text = button.split(".")[1].capitalize()
                button = btn(btn_text, button)
                line.append(button)
            lines.append(line)
    except AttributeError:
        for row in rows:
            line = []
            for button in row:
                button = btn(*button)
                line.append(button)
            lines.append(line)
    except TypeError:
        line = []
        for button in rows:
            button = btn(*button)
            line.append(button)
        lines.append(line)
    if back: 
        back_btn = [(btn("ʙᴀᴄᴋ", todo))]
        lines.append(back_btn)
    return InlineKeyboardMarkup(inline_keyboard=lines)

def btn(text, value, type="callback_data"):
    return InlineKeyboardButton(text, **{type: value})
