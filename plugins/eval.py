import io
import traceback
import sys

from pyrogram import filters
from pyrogram import Client as Mai_bOTs

ALLOWED_USERS = [5370531116, 5551387300, 5905126281, 5905126281, 5591954930]
MAX_MESSAGE_LENGTH = 4096

@Mai_bOTs.on_message(filters.command("eval") & filters.user(ALLOWED_USERS))
async def evaluate_command(client, message):
    status_message = await message.reply_text("Processing ...")
    try:
        cmd = message.text.markdown.split(" ", maxsplit=1)[1]
    except IndexError:
        return await status_message.edit_text("Give code to evaluate...")

    reply_to_msg = message.reply_to_message or message
    stdout, stderr, exc = None, None, None

    # Capture and redirect stdout and stderr
    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout = redirected_output = io.StringIO()
    sys.stderr = redirected_error = io.StringIO()

    try:
        await execute_code(cmd, client, message)
    except Exception:
        exc = traceback.format_exc()

    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    evaluation = exc or stderr or stdout or "Success"

    final_output = f"**EVAL**: `{cmd}`\n\n**OUTPUT**:\n`{evaluation.strip()}`"

    if len(final_output) > MAX_MESSAGE_LENGTH:
        with io.BytesIO(str.encode(evaluation)) as out_file:
            out_file.name = "eval.txt"
            await reply_to_msg.reply_document(
                document=out_file,
                caption=f"`{cmd[:MAX_MESSAGE_LENGTH // 4 - 1]}`",
                disable_notification=True,
                parse_mode="markdown",
                quote=True,
            )
    else:
        await reply_to_msg.reply_text(final_output, parse_mode=ParseMode.MARKDOWN, quote=True)
    await status_message.delete()

async def execute_code(code, client, message):
    # Prepare the code to be executed with necessary context
    exec(
        "async def __aexec(client, message): "
        + "\n    m = message"
        + "\n    chat = m.chat.id"
        + "\n    reply = m.reply_to_message"
        + "".join(f"\n    {line}" for line in code.split("\n"))
    )
    # Execute the prepared code within the context
    return await locals()["__aexec"](client, message)
