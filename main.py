import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import ollama
load_dotenv() 

api_key = os.getenv("SERPAPI_API_KEY")
discord_token = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!",  intents=intents)

import requests

def web_search(query):
    url = "https://serpapi.com/search.json"

    params = {
        "q": query,
        "api_key": api_key,
        "engine": "google"
    }

    try:
        res = requests.get(url, params=params)
        data = res.json()

        if "organic_results" in data and len(data["organic_results"]) > 0:
            return data["organic_results"][0]["snippet"]

        return "No useful results found."

    except Exception as e:
        return f"Search error: {str(e)}"

def needs_search(question):
    response = ollama.chat(
        model='llama3',
        messages=[
            {
                "role": "system",
                "content": "Answer ONLY 'yes' or 'no'. Does this question require real-time or external data?"
            },
            {"role": "user", "content": question}
        ]
    )
    
    return "yes" in response['message']['content'].lower()

@bot.command()
async def hi(ctx):
    await ctx.send("Hi!")

@bot.command()
async def ask(ctx, *, question):
    async with ctx.typing():
        if needs_search(question):
            result = web_search(question)

            response = ollama.chat(
                model='llama3',
                messages=[
                    {"role": "system", "content": "Use this data to answer."},
                    {"role": "system", "content": f"Use this real-time data:\n{result}"},
                    {"role": "user", "content": question}
                ]
            )
        else:
            response = ollama.chat(
                model='llama3',
                messages=[
                    {"role": "user", "content": question}
                ]
            )
        reply = response['message']['content']
        print(reply)
        await ctx.send(reply)

bot.run(discord_token)