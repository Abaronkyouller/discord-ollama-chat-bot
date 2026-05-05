import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import ollama
load_dotenv()

import asyncio
from bs4 import BeautifulSoup
import requests

api_key = os.getenv("SERPAPI_API_KEY")
discord_token = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!",  intents=intents)

def access_another_link(url):
    try:
        res = requests.get(url=url, headers={"User-Agent": "Mozilla/5.0"})
        html = res.text
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style"]):
            tag.decompose()
        text = soup.get_text(separator=" ")
        text = " ".join(text.split())[:1000]
        return text

    except Exception as e:
        print("error")
        return ""

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
            results = data["organic_results"][0]
            snippets = results["snippet"] if "snippet" in results else ""
            links = results["link"] if "link" in results else ""
            links_access_results = access_another_link(links)

            return snippets+links_access_results

        return "No useful results found."

    except Exception as e:
        return f"Search error: {str(e)}"

@bot.command()
async def hi(ctx):
    await ctx.send("Hi!")

@bot.command()
# async def ask(ctx, *, question):
#     async with ctx.typing():
#         response = ollama.chat(
#             model='llama3',
#             messages=[
#                 {"role": "user", "content": question}
#             ]
#         )
#         reply = response['message']['content']
#         await ctx.send(reply)
async def ask(ctx, *, question):
    async with ctx.typing():
        response = await asyncio.to_thread(
            ollama.chat,
            model="llama3",
            messages=[
                {"role": "system", "content":"summarize to be less than 2000 characters"},
                {"role": "user", "content": question}
            ]
        )
        try:
            await ctx.send(response['message']['content'])
        except Exception as e:
            if "2000 or fewer" in str(e):
                await ctx.send("Answer exceed 2000 characters")

@bot.command()
async def search(ctx, *, question):
    async with ctx.typing():
        result = await asyncio.to_thread(web_search, question)
        context = "\n\n".join(result)
        response = await asyncio.to_thread(
            ollama.chat,
            model='llama3',
            messages=[
                {"role": "system", "content":"summarize to be less than 2000 characters"},
                {"role": "system", "content": "Use this data to answer."},
                {"role": "system", "content": f"Use this real-time data:\n{context}"},
                {"role": "user", "content": question}
            ]
        )
        reply = response['message']['content']
        try: 
            await ctx.send(reply)
        except Exception as e:
            if "2000 or fewer" in str(e):
                await ctx.send("Answer exceed 2000 characters")

bot.run(discord_token)