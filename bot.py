from threading import Thread
from flask import Flask
import discord
from discord.ext import commands
import asyncio
import random

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

BOT_TOKEN = "MTU0MDI3NjM0NTM2MjQ1NjYzNg.GizCWI.ysXYdGxb0II-FuMPC4Sh1GsFK-6VorQ8PRWQL8"
ACCESS_ROLE_ID = 1540280694079496244

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

user_tokens = {}

@bot.event
async def on_ready():
    print(f"Bot ready: {bot.user}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.guild is None:
        if message.content.startswith("MT") or message.content.startswith("mfa."):
            user_tokens[message.author.id] = message.content.strip()
            await message.channel.send("✅ Token saved. Now go to the server and type `.autoquest`")
        return

    if message.content == ".link":
        embed = discord.Embed(
            title="🔗 Token Required",
            description=(
                "You need to link your Discord token before using quest commands.\n\n"
                "### HOW TO FIND YOUR TOKEN\n"
                "Pick your platform below:"
            ),
            color=0x7FDBFF
        )

        view = discord.ui.View()

        js_button = discord.ui.Button(
            label="JAVASCRIPT",
            style=discord.ButtonStyle.primary,
            custom_id="js_token"
        )

        async def js_callback(interaction):
            js_code = (
                "javascript:(function(){try{let f=document.createElement('iframe');"
                "document.body.appendChild(f);"
                "let t=JSON.parse(f.contentWindow.localStorage.token);"
                "let ta=document.createElement('textarea');ta.value=t;"
                "document.body.appendChild(ta);ta.select();"
                "document.execCommand('copy');ta.remove();"
                "let n=document.createElement('div');"
                "n.innerHTML='<strong>Token Copied</strong><br>Your token has been copied to clipboard';"
                "n.style.cssText='position:fixed;top:20px;left:20px;background:#001f3f;color:#7FDBFF;"
                "padding:12px%2016px;border-radius:8px;box-shadow:0%204px%2012px%20rgba(0,0,0,0.4);"
                "font-family:-apple-system,BlinkMacSystemFont,Segoe%20UI,Roboto,sans-serif;font-size:14px;"
                "z-index:99999;opacity:0;transition:opacity%200.3s%20ease-in-out;';"
                "document.body.appendChild(n);setTimeout(()=>{n.style.opacity='1';},50);"
                "setTimeout(()=>{n.style.opacity='0';setTimeout(()=>n.remove(),500);},3500);"
                "}catch(e){alert('Error%20copying%20token');}})();"
            )

            embed_js = discord.Embed(
                title="📋 JavaScript — Token Linker",
                description=(
                    "**Copy the JavaScript below and run it in your browser console (or bookmark it):**\n\n"
                    "```js\n" + js_code + "\n```\n\n"
                    "After running, your token will be copied to clipboard.\n"
                    "Then **DM me the token** to activate auto-quest."
                ),
                color=0x001f3f
            )

            await interaction.response.send_message(embed=embed_js, ephemeral=True)

        js_button.callback = js_callback
        view.add_item(js_button)

        submit_button = discord.ui.Button(
            label="Submit Token",
            style=discord.ButtonStyle.success,
            custom_id="submit_token"
        )

        async def submit_callback(interaction):
            try:
                await interaction.user.send(
                    "**📝 Submit Your Token**\n\n"
                    "Paste your Discord token **here in DM**.\n\n"
                    "Format: `MT...` or `mfa...`"
                )
                await interaction.response.send_message(
                    "✅ Check your DMs to submit your token.",
                    ephemeral=True
                )
            except:
                await interaction.response.send_message(
                    "❌ I can't DM you. Enable DMs and try again.",
                    ephemeral=True
                )

        submit_button.callback = submit_callback
        view.add_item(submit_button)

        await message.channel.send(embed=embed, view=view)
        return

    if message.content == ".autoquest":
        user_id = message.author.id
        if user_id not in user_tokens:
            await message.channel.send("❌ Token not linked. First DM me your token.")
            return

        await message.channel.send("✅ **AutoQuest is enabled**")
        asyncio.create_task(run_autoquest(user_id, user_tokens[user_id]))
        return

    if message.content.startswith("MT") or message.content.startswith("mfa."):
        await message.delete()
        try:
            await message.author.send("❌ **Token blocked in server.**\nPaste your token **here in DM** instead.")
        except:
            pass
        return

async def run_autoquest(user_id, user_token):
    try:
        worker = commands.Bot(command_prefix="!", intents=discord.Intents.all(), self_bot=True)

        @worker.event
        async def on_ready():
            print(f"Worker ready for {user_id}")
            user = await worker.fetch_user(user_id)
            await complete_all_quests(worker, user)

        await worker.start(user_token)
    except Exception as e:
        print(f"Worker error: {e}")

async def complete_all_quests(worker, user):
    while True:
        quest_found = False

        for guild in worker.guilds:
            for channel in guild.text_channels:
                try:
                    async for msg in channel.history(limit=100):
                        if msg.author.bot:
                            if msg.components:
                                for comp in msg.components:
                                    for button in comp.children:
                                        if not button.disabled:
                                            try:
                                                await button.click()
                                                await user.send(f"✅ Bhai tera ye wala quest complete hogya: **{button.label}**")
                                                quest_found = True
                                                await asyncio.sleep(random.uniform(1,3))
                                            except:
                                                pass

                            content = msg.content.lower()
                            if any(k in content for k in ['quest', 'daily', 'task', 'challenge', 'adventure']):
                                try:
                                    await channel.send('/quest')
                                    await user.send("✅ Bhai tera ye wala quest complete hogya: **Slash Command Quest**")
                                    quest_found = True
                                    await asyncio.sleep(random.uniform(2,4))
                                except:
                                    pass
                except:
                    continue

        if not quest_found:
            await user.send("✅ Saare quests complete ho gaye. Naye quests aane pe main khud complete kar dunga.")
            break

        await asyncio.sleep(10)

keep_alive()
bot.run(BOT_TOKEN)
