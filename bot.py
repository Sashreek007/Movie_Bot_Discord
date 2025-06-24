import os
import discord
from dotenv import load_dotenv
import requests

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


# -------------------------------
# Helpers for streaming providers
# -------------------------------
def get_movie_watch_providers(id, country="IN"):
    url = f"https://api.themoviedb.org/3/movie/{id}/watch/providers?api_key={TMDB_API_KEY}"
    data = requests.get(url).json()
    results = data.get("results", {})
    if country in results:
        flatrate = results[country].get("flatrate", [])
        providers = [p["provider_name"] for p in flatrate]
        return ", ".join(providers) if providers else "No streaming info"
    else:
        return "No streaming info"


def get_tv_watch_providers(id, country="IN"):
    url = f"https://api.themoviedb.org/3/tv/{id}/watch/providers?api_key={TMDB_API_KEY}"
    data = requests.get(url).json()
    results = data.get("results", {})
    if country in results:
        flatrate = results[country].get("flatrate", [])
        providers = [p["provider_name"] for p in flatrate]
        return ", ".join(providers) if providers else "No streaming info"
    else:
        return "No streaming info"


# -------------------------------
# Ready event
# -------------------------------
@client.event
async def on_ready():
    print(f"✅ Bot is online as {client.user}")


# -------------------------------
# Commands
# -------------------------------
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # ----------------------------------------
    # !movie (Movie Info)
    # ----------------------------------------
    if message.content.startswith("!movie"):
        query = message.content[len("!movie") :].strip()
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"
        data = requests.get(url).json()
        if data["results"]:
            movie = data["results"][0]
            id = movie["id"]
            title = movie["title"]
            overview = movie["overview"]
            date = movie["release_date"]
            poster = (
                f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"
                if movie["poster_path"]
                else None
            )
            details = requests.get(
                f"https://api.themoviedb.org/3/movie/{id}?api_key={TMDB_API_KEY}"
            ).json()
            genres = ", ".join([g["name"] for g in details.get("genres", [])]) or "N/A"
            rating = details.get("vote_average", "N/A")
            providers = get_movie_watch_providers(id)

            embed = discord.Embed(
                title=f"{title} ({date})", description=overview, color=0x00FF00
            )
            embed.add_field(name="Genres", value=genres, inline=True)
            embed.add_field(name="Rating", value=str(rating), inline=True)
            embed.add_field(name="Available on", value=providers, inline=False)
            if poster:
                embed.set_image(url=poster)
            await message.channel.send(embed=embed)
        else:
            await message.channel.send("Movie not found!")

    # ----------------------------------------
    # !tv (TV Show Info)
    # ----------------------------------------
    elif message.content.startswith("!tv"):
        query = message.content[len("!tv") :].strip()
        url = f"https://api.themoviedb.org/3/search/tv?api_key={TMDB_API_KEY}&query={query}"
        data = requests.get(url).json()
        if data["results"]:
            show = data["results"][0]
            id = show["id"]
            name = show["name"]
            overview = show["overview"]
            date = show["first_air_date"]
            poster = (
                f"https://image.tmdb.org/t/p/w500{show['poster_path']}"
                if show["poster_path"]
                else None
            )
            details = requests.get(
                f"https://api.themoviedb.org/3/tv/{id}?api_key={TMDB_API_KEY}"
            ).json()
            genres = ", ".join([g["name"] for g in details.get("genres", [])]) or "N/A"
            rating = details.get("vote_average", "N/A")
            providers = get_tv_watch_providers(id)

            embed = discord.Embed(
                title=f"{name} ({date})", description=overview, color=0x1E90FF
            )
            embed.add_field(name="Genres", value=genres, inline=True)
            embed.add_field(name="Rating", value=str(rating), inline=True)
            embed.add_field(name="Available on", value=providers, inline=False)
            if poster:
                embed.set_image(url=poster)
            await message.channel.send(embed=embed)
        else:
            await message.channel.send("TV show not found!")

    # ----------------------------------------
    # !movietrailer
    # ----------------------------------------
    elif message.content.startswith("!mt"):
        query = message.content[len("!mt") :].strip()
        search = requests.get(
            f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"
        ).json()
        if search["results"]:
            id = search["results"][0]["id"]
            videos = requests.get(
                f"https://api.themoviedb.org/3/movie/{id}/videos?api_key={TMDB_API_KEY}"
            ).json()
            for v in videos["results"]:
                if v["type"] == "Trailer" and v["site"] == "YouTube":
                    await message.channel.send(
                        f"https://www.youtube.com/watch?v={v['key']}"
                    )
                    break
            else:
                await message.channel.send("Trailer not found!")
        else:
            await message.channel.send("Movie not found!")

    # ----------------------------------------
    # !tvtrailer
    # ----------------------------------------
    elif message.content.startswith("!tt"):
        query = message.content[len("!tt") :].strip()
        search = requests.get(
            f"https://api.themoviedb.org/3/search/tv?api_key={TMDB_API_KEY}&query={query}"
        ).json()
        if search["results"]:
            id = search["results"][0]["id"]
            videos = requests.get(
                f"https://api.themoviedb.org/3/tv/{id}/videos?api_key={TMDB_API_KEY}"
            ).json()
            for v in videos["results"]:
                if v["type"] == "Trailer" and v["site"] == "YouTube":
                    await message.channel.send(
                        f"https://www.youtube.com/watch?v={v['key']}"
                    )
                    break
            else:
                await message.channel.send("Trailer not found!")
        else:
            await message.channel.send("TV show not found!")

    # ----------------------------------------
    # !moviecast
    # ----------------------------------------
    elif message.content.startswith("!mc"):
        query = message.content[len("!mc") :].strip()
        search = requests.get(
            f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"
        ).json()
        if search["results"]:
            id = search["results"][0]["id"]
            credits = requests.get(
                f"https://api.themoviedb.org/3/movie/{id}/credits?api_key={TMDB_API_KEY}"
            ).json()
            for a in credits.get("cast", [])[:5]:
                name = a["name"]
                char = a.get("character", "Unknown Role")
                pic = (
                    f"https://image.tmdb.org/t/p/w300{a['profile_path']}"
                    if a["profile_path"]
                    else "https://upload.wikimedia.org/wikipedia/commons/8/89/Portrait_Placeholder.png"
                )
                embed = discord.Embed(
                    title=name, description=f"Role: {char}", color=0xFFD700
                )
                embed.set_image(url=pic)
                await message.channel.send(embed=embed)
        else:
            await message.channel.send("Movie not found!")

    # ----------------------------------------
    # !tvcast
    # ----------------------------------------
    elif message.content.startswith("!tc"):
        query = message.content[len("!tc") :].strip()
        search = requests.get(
            f"https://api.themoviedb.org/3/search/tv?api_key={TMDB_API_KEY}&query={query}"
        ).json()
        if search["results"]:
            id = search["results"][0]["id"]
            credits = requests.get(
                f"https://api.themoviedb.org/3/tv/{id}/credits?api_key={TMDB_API_KEY}"
            ).json()
            for a in credits.get("cast", [])[:5]:
                name = a["name"]
                char = a.get("character", "Unknown Role")
                pic = (
                    f"https://image.tmdb.org/t/p/w300{a['profile_path']}"
                    if a["profile_path"]
                    else "https://upload.wikimedia.org/wikipedia/commons/8/89/Portrait_Placeholder.png"
                )
                embed = discord.Embed(
                    title=name, description=f"Role: {char}", color=0xFFD700
                )
                embed.set_image(url=pic)
                await message.channel.send(embed=embed)
        else:
            await message.channel.send("TV show not found!")

    # ----------------------------------------
    # !movierecommend
    # ----------------------------------------
    elif message.content.startswith("!rcm"):
        query = message.content[len("!rcm") :].strip()
        search = requests.get(
            f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"
        ).json()
        if search["results"]:
            id = search["results"][0]["id"]
            recs = requests.get(
                f"https://api.themoviedb.org/3/movie/{id}/similar?api_key={TMDB_API_KEY}"
            ).json()
            titles = [r["title"] for r in recs.get("results", [])[:5]]
            if titles:
                await message.channel.send("Similar Movies:\n" + ", ".join(titles))
            else:
                await message.channel.send("No similar movies found!")
        else:
            await message.channel.send("Movie not found!")

    # ----------------------------------------
    # !tvrecommend
    # ----------------------------------------
    elif message.content.startswith("!rct"):
        query = message.content[len("!rct") :].strip()
        search = requests.get(
            f"https://api.themoviedb.org/3/search/tv?api_key={TMDB_API_KEY}&query={query}"
        ).json()
        if search["results"]:
            id = search["results"][0]["id"]
            recs = requests.get(
                f"https://api.themoviedb.org/3/tv/{id}/similar?api_key={TMDB_API_KEY}"
            ).json()
            titles = [r["name"] for r in recs.get("results", [])[:5]]
            if titles:
                await message.channel.send("Similar TV Shows:\n" + ", ".join(titles))
            else:
                await message.channel.send("No similar TV shows found!")
        else:
            await message.channel.send("TV show not found!")

    # ----------------------------------------
    # !moviesearch & !tvsearch
    # ----------------------------------------
    elif message.content.startswith("!sm"):
        query = message.content[len("!sm") :].strip()
        search = requests.get(
            f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"
        ).json()
        results = [m["title"] for m in search.get("results", [])[:5]]
        if results:
            await message.channel.send(
                "🎬 Movie Search Results:\n" + "\n".join(results)
            )
        else:
            await message.channel.send("No movies found!")

    elif message.content.startswith("!st"):
        query = message.content[len("!st") :].strip()
        search = requests.get(
            f"https://api.themoviedb.org/3/search/tv?api_key={TMDB_API_KEY}&query={query}"
        ).json()
        results = [t["name"] for t in search.get("results", [])[:5]]
        if results:
            await message.channel.send(
                "📺 TV Show Search Results:\n" + "\n".join(results)
            )
        else:
            await message.channel.send("No TV shows found!")

    # ----------------------------------------
    # !trending movies & !trending tv
    # ----------------------------------------
    elif message.content.startswith("!trending movie"):
        url = f"https://api.themoviedb.org/3/trending/movie/day?api_key={TMDB_API_KEY}"
        data = requests.get(url).json()
        titles = [r["title"] for r in data.get("results", [])[:5]]
        await message.channel.send("🔥 Trending Movies:\n" + "\n".join(titles))

    elif message.content.startswith("!trending tv"):
        url = f"https://api.themoviedb.org/3/trending/tv/day?api_key={TMDB_API_KEY}"
        data = requests.get(url).json()
        titles = [r["name"] for r in data.get("results", [])[:5]]
        await message.channel.send("🔥 Trending TV Shows:\n" + "\n".join(titles))

    # ----------------------------------------
    # !actor
    # ----------------------------------------
    elif message.content.startswith("!actor"):
        query = message.content[len("!actor") :].strip()
        search = requests.get(
            f"https://api.themoviedb.org/3/search/person?api_key={TMDB_API_KEY}&query={query}"
        ).json()
        if search["results"]:
            person = search["results"][0]
            name = person["name"]
            bio = person.get("biography", "No bio available.")
            known = ", ".join(
                [x.get("title") or x.get("name") for x in person.get("known_for", [])]
            )
            profile = (
                f"https://image.tmdb.org/t/p/w500{person['profile_path']}"
                if person["profile_path"]
                else None
            )
            embed = discord.Embed(
                title=name,
                description=bio[:500] + ("..." if len(bio) > 500 else ""),
                color=0xFF69B4,
            )
            embed.add_field(name="Known For", value=known or "N/A", inline=False)
            if profile:
                embed.set_image(url=profile)
            await message.channel.send(embed=embed)
        else:
            await message.channel.send("Actor not found!")

    # ----------------------------------------
    # !moviehelp
    # ----------------------------------------
    elif message.content.startswith("!helpmovie"):
        help_text = """
🎥 **Movie & TV Bot Commands**

**🎬 Movies**
- `!movie <name>` — Movie info
- `!mt <name>` — Movie trailer
- `!mc <name>` — Movie cast
- `!rcm <name>` — Similar movies
- `!sm <query>` — Search movies

**📺 TV Shows**
- `!tv <name>` — TV show info
- `!tt <name>` — TV show trailer
- `!tc <name>` — TV cast
- `!rct <name>` — Similar TV shows
- `!st <query>` — Search TV shows

**🔥 Trending**
- `!trending movies` — Trending movies
- `!trending tv` — Trending TV shows

**🎭 People**
- `!actor <name>` — Actor bio

✅ Use exact names for best results!
"""
        await message.channel.send(help_text)


client.run(DISCORD_TOKEN)
