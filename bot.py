import discord, os, asyncio, requests, whisper
from gtts import gTTS

TOKEN = os.getenv("DISCORD_TOKEN")
GROQ = os.getenv("GROQ_KEY")

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

client = discord.Client(intents=intents)
model = whisper.load_model("base")

def ask_ai(text):
    r = requests.post(
      "https://api.groq.com/openai/v1/chat/completions",
      headers={
        "Authorization": f"Bearer {GROQ}",
        "Content-Type": "application/json"
      },
      json={
        "model": "llama-3.3-70b-versatile",
        "messages": [
          {"role": "system","content":"You are Zeno. Short natural replies."},
          {"role": "user","content":text}
        ]
      })
    return r.json()["choices"][0]["message"]["content"]

async def listen_once(vc):
    await asyncio.sleep(1)

    audio = await vc.recv_audio()

    with open("input.wav","wb") as f:
        f.write(audio)

    text = model.transcribe("input.wav")["text"]

    reply = ask_ai(text)

    gTTS(reply).save("reply.mp3")

    vc.play(discord.FFmpegPCMAudio("reply.mp3"))

    while vc.is_playing():
        await asyncio.sleep(1)

@client.event
async def on_message(msg):

    if msg.content == "/joincall":

        if not msg.author.voice:
            await msg.channel.send("Join VC first")
            return

        vc = await msg.author.voice.channel.connect()

        await msg.channel.send("Listening... speak now")

        await listen_once(vc)

        await vc.disconnect()

client.run(TOKEN)
