
import os, traceback,requests,asyncio
import discord
from bs4 import BeautifulSoup
import aiohttp
from dotenv import load_dotenv
from discord import app_commands
from discord.ext import commands, tasks
from urllib.parse import unquote

# --- Bot Configuration ---
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True
intents.dm_messages = True
#bot = commands.Bot(command_prefix="!", intents=intents)
user_watchlists = {}  # keep track of user watchlists
last_statuses = {}  # keep track of last status for each user
# --- Config ---
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID= os.getenv("CHANNEL_ID")

  # Replace with your channel ID (integer)
CHECK_INTERVAL = 300  # in seconds (5 minutes)


Departments = {
    "AC ENG": "AC%20ENG",
    "AFAM": "AFAM",
    "ANATOMY": "ANATOMY",
    "ANESTH": "ANESTH",
    "ANTHRO": "ANTHRO",
    "ARABIC": "ARABIC",
    "ARMN": "ARMN",
    "ART": "ART",
    "ART HIS": "ART%20HIS",
    "ARTS": "ARTS",
    "ASIANAM": "ASIANAM",
    "ASL": "ASL",
    "BANA": "BANA",
    "BATS": "BATS",
    "BIO SCI": "BIO%20SCI",
    "BIOCHEM": "BIOCHEM",
    "BME": "BME",
    "CAMPREC": "CAMPREC",
    "CBE": "CBE",
    "CHC/LAT": "CHC%2FLAT",
    "CHEM": "CHEM",
    "CHINESE": "CHINESE",
    "CLASSIC": "CLASSIC",
    "CLT&THY": "CLT%26THY",
    "COGS": "COGS",
    "COM LIT": "COM%20LIT",
    "COMPSCI": "COMPSCI",
    "CRM/LAW": "CRM%2FLAW",
    "CSE": "CSE",
    "DANCE": "DANCE",
    "DATA": "DATA",
    "DERM": "DERM",
    "DEV BIO": "DEV%20BIO",
    "DRAMA": "DRAMA",
    "EARTHSS": "EARTHSS",
    "EAS": "EAS",
    "ECO EVO": "ECO%20EVO",
    "ECON": "ECON",
    "ECPS": "ECPS",
    "ED AFF": "ED%20AFF",
    "EDUC": "EDUC",
    "EECS": "EECS",
    "EHS": "EHS",
    "ENGLISH": "ENGLISH",
    "ENGR": "ENGR",
    "ENGRCEE": "ENGRCEE",
    "ENGRMAE": "ENGRMAE",
    "EPIDEM": "EPIDEM",
    "ER MED": "ER%20MED",
    "EURO ST": "EURO%20ST",
    "FAM MED": "FAM%20MED",
    "FIN": "FIN",
    "FLM&MDA": "FLM%26MDA",
    "FRENCH": "FRENCH",
    "GDIM": "GDIM",
    "GEN&SEX": "GEN%26SEX",
    "GERMAN": "GERMAN",
    "GLBLCLT": "GLBLCLT",
    "GREEK": "GREEK",
    "HISTORY": "HISTORY",
    "HUMAN": "HUMAN",
    "I&C SCI": "I%26C%20SCI",
    "IN4MATX": "IN4MATX",
    "INNO": "INNO",
    "INT MED": "INT%20MED",
    "INTL ST": "INTL%20ST",
    "IRAN": "IRAN",
    "ITALIAN": "ITALIAN",
    "JAPANSE": "JAPANSE",
    "KOREAN": "KOREAN",
    "LATIN": "LATIN",
    "LAW": "LAW",
    "LIT JRN": "LIT%20JRN",
    "LPS": "LPS",
    "LSCI": "LSCI",
    "M&MG": "M%26MG",
    "MATH": "MATH",
    "MED ED": "MED%20ED",
    "MED HUM": "MED%20HUM",
    "MGMT": "MGMT",
    "MGMT EP": "MGMT%20EP",
    "MGMT FE": "MGMT%20FE",
    "MGMTMBA": "MGMTMBA",
    "MGMTPHD": "MGMTPHD",
    "MIC BIO": "MIC%20BIO",
    "MNGE": "MNGE",
    "MOL BIO": "MOL%20BIO",
    "MPAC": "MPAC",
    "MSE": "MSE",
    "MUSIC": "MUSIC",
    "NET SYS": "NET%20SYS",
    "NEURBIO": "NEURBIO",
    "NEUROL": "NEUROL",
    "NUR SCI": "NUR%20SCI",
    "OB/GYN": "OB%2FGYN",
    "OPHTHAL": "OPHTHAL",
    "PATH": "PATH",
    "PED GEN": "PED%20GEN",
    "PEDS": "PEDS",
    "PERSIAN": "PERSIAN",
    "PHARM": "PHARM",
    "PHILOS": "PHILOS",
    "PHMD": "PHMD",
    "PHRMSCI": "PHRMSCI",
    "PHY SCI": "PHY%20SCI",
    "PHYSICS": "PHYSICS",
    "PHYSIO": "PHYSIO",
    "PM&R": "PM%26R",
    "POL SCI": "POL%20SCI",
    "PSCI": "PSCI",
    "PSYCH": "PSYCH",
    "PUBHLTH": "PUBHLTH",
    "RADIO": "RADIO",
    "REL STD": "REL%20STD",
    "ROTC": "ROTC",
    "RUSSIAN": "RUSSIAN",
    "SOC SCI": "SOC%20SCI",
    "SOCECOL": "SOCECOL",
    "SOCIOL": "SOCIOL",
    "SPANISH": "SPANISH",
    "SPPS": "SPPS",
    "STATS": "STATS",
    "SURGERY": "SURGERY",
    "SWE": "SWE",
    "UCDC": "UCDC",
    "UNI AFF": "UNI%20AFF",
    "UNI STU": "UNI%20STU",
    "UPPP": "UPPP",
    "VIETMSE": "VIETMSE",
    "VIS STD": "VIS%20STD",
    "WRITING": "WRITING",
}

# Reverse lookup for the Departments dictionary
DEPT_REVERSE_MAPPING = {v: k for k, v in Departments.items()}


quarters={
        "SUMMER":"Summer",
        "WINTER":"Winter",
        "SPRING":"Spring",
        "FALL":"Fall",
}

GUILD_ID = 751337060673257482   # ← your guild


async def course_exists(year: int, quarter_code: str,
                        dept: str, course_num: str,
                        sec_type: str, sec_code: str) -> bool:
    url = construct_url(year, quarter_code, dept, course_num)

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            html = await r.text()

    soup = BeautifulSoup(html, "html.parser")

    # quick check: any row whose <td> #2 and #3 match type / code?
    for row in soup.select("table tr"):
        cols = row.find_all("td")
        if len(cols) < 4:
            continue
        if (cols[1].get_text(strip=True).lower() == sec_type.lower() and
            cols[2].get_text(strip=True).lower() == sec_code.lower()):
            return True      # ✅ found

    return False             # ❌ not found

import aiohttp

async def fetch_page_text(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()  # Optional: raise if bad status
            return await response.text()


def handle_quarter(quarter):
    quarter = quarter.upper()
    if quarter == "SUMMER":
        return "20"
    elif quarter == "SPRING":
        return "10"
    elif quarter == "WINTER":
        return "03"
    elif quarter == "FALL":
        return "92"
    else:
        raise ValueError("Invalid quarter; use Winter, Spring, Summer, or Fall.")


def construct_url(year, quarter_code, dept, course_num):
    return f"https://www.reg.uci.edu/perl/WebSoc?YearTerm={year}-{quarter_code}&ShowFinals=1&ShowComments=1&Dept={dept}&CourseNum={course_num}"


def parse_int_from_string(s):
    s = s.strip()
    if "/" in s:
        s = s.split("/")[0].strip()
    return int(s)


def parse_enrollment_and_waitlist(html, section_type, section_code):
    soup = BeautifulSoup(html, "html.parser")

    tables = soup.find_all("table")
    print(f"Found {len(tables)} tables")

    target_table = None

    for i, table in enumerate(tables):
        headers = [th.text.strip() for th in table.find_all("th")]
        print(f"Table {i} headers: {headers}")

        if "Enr" in headers and "WL" in headers:
            target_table = table
            print(f"Selected table {i} for parsing")
            break

    if target_table is None:
        raise ValueError("No table with enrollment info found")

    rows = target_table.find_all("tr")

    print(f"Found {len(rows)} rows in target table")

    def parse_int_from_string(value, default=0):
        try:
            return int(value)
        except ValueError:
            return default

    for idx, row in enumerate(rows):
        cols = row.find_all("td")
        if len(cols) < 12:
            continue

        row_type = cols[1].text.strip().lower()
        row_sec = cols[2].text.strip().lower()

        print(f"Row {idx} type: '{row_type}', section: '{row_sec}'")

        if row_type == section_type.lower() and row_sec == section_code.lower():
            max_enrollment = parse_int_from_string(cols[9].text.strip())
            enrollment = parse_int_from_string(cols[10].text)
            waitlist_str = cols[11].text.strip()

            if waitlist_str.lower()=='n/a':
                waitlist=0
            else:
                waitlist=parse_int_from_string(waitlist_str)
            print(f"Match found! Enrollment: {enrollment}, Waitlist: {waitlist}")
            return enrollment, waitlist, max_enrollment

    raise ValueError(f"Could not find section {section_type} {section_code}")


@tasks.loop(seconds=CHECK_INTERVAL)
async def background_check():
    print(f"Starting background check for {len(user_watchlists)} users...")
    for user_id, watches in user_watchlists.items():
        print(f"Checking user {user_id} with {len(watches)} watches")
        user = await bot.fetch_user(user_id)
        if user is None:
            print(f"Could not fetch user {user_id}")
            continue

        dm_channel = user.dm_channel
        if dm_channel is None:
            dm_channel = await user.create_dm()

        for watch in watches:
            try:
                url = construct_url(
                    watch["Year"],
                    watch["Quarter"],
                    watch["Dept"],
                    watch["CourseNum"],
                )
                print(f"Fetching URL for {watch['Dept']} {watch['CourseNum']} - {url}")
                page_text = await fetch_page_text(url)


                enrollment, waitlist, max_enrollment = parse_enrollment_and_waitlist(
                    page_text, watch["SectionType"], watch["SectionCode"]
                )
                print(
                    f"Parsed Enrollment: {enrollment}, Waitlist: {waitlist}, Max Enrollment: {max_enrollment}"
                )

                seats_left = max_enrollment - enrollment

                key = f"{watch['Dept']}-{watch['CourseNum']}-{watch['SectionType']}-{watch['SectionCode']}-{watch['Year']}-{watch['Quarter']}"
                last_status = last_statuses.get(user_id, {}).get(key)

                current_status = (enrollment, waitlist, max_enrollment)

                if last_status != current_status:
                    messages = []
                    if last_status is None or (
                        last_status[0] < max_enrollment and seats_left > 0
                    ):
                        messages.append(
                            f"🚨 Class Alert! 🚨{seats_left} seat(s) available for {unquote(watch['Dept'])} {watch['CourseNum']} {watch['SectionType']} {watch['SectionCode']}."
                        )

                    if (
                        last_status
                        and waitlist < last_status[1]
                        and waitlist > 0
                    ):
                        messages.append(
                            f"🔼 The waitlist for {watch['Dept']} {watch['CourseNum']} has decreased. New waitlist: {waitlist}."
                        )

                    if (
                        last_status
                        and waitlist > last_status[1]
                        and waitlist > 0
                    ):
                        messages.append(
                            f"🔽 The waitlist for {watch['Dept']} {watch['CourseNum']} has increased. New waitlist: {waitlist}."
                        )

                    if (
                        waitlist == 0
                        and enrollment == max_enrollment
                        and (last_status is None or last_status[1] != 0)
                    ):
                        messages.append(
                            f"🚨 HURRY 🚨 the waitlist for {watch['Dept']} {watch['CourseNum']} is OPEN and NO-ONE is currently signed up!"
                        )

                    for msg in messages:
                        print(f"Sending DM to user {user_id}: {msg}")
                        await dm_channel.send(msg)

                    if user_id not in last_statuses:
                        last_statuses[user_id] = {}
                    last_statuses[user_id][key] = current_status

                    watch["WaitlistPos"] = waitlist

            except Exception as e:
                print(f"Error checking status for user {user_id}, watch {watch}: {e}")
                traceback.print_exc()


class MyBot(commands.Bot):
    def __init__(self):
        #intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        await self.tree.sync() 
        print("Tree contents:", [c.name for c in self.tree.get_commands()])
        await self.tree.sync(guild=discord.Object(id=GUILD_ID))
        print("Synced!")

        background_check.start()


bot = MyBot()

@bot.tree.command(name="hello", description="Say hello to the bot")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hello, {interaction.user.mention}!")


# 1️⃣  autocomplete helper
async def dept_autocomplete(
        interaction: discord.Interaction,
        current: str        # what the user has typed so far
) -> list[app_commands.Choice[str]]:
    current = current.upper()
    # filter keys or encoded values that contain the typed text
    matches = [
        app_commands.Choice(name=dept, value=encoded)
        for dept, encoded in Departments.items()
        if current in dept
    ]
    return matches[:25]     # Discord shows max 25

async def quarter_autocomplete(
        interaction: discord.Interaction,
        current:str
) -> list[app_commands.Choice[str]]:
    current = current.upper()

    matches=[
        app_commands.Choice(name=pretty.title(),value=pretty.upper())
        for pretty in ("winter","spring","summer","fall")
        if current in pretty.upper()
    ]
    return matches[:4]


@bot.tree.command(name="watch", description="Add a class to your watchlist!")
@app_commands.autocomplete(dept=dept_autocomplete,quarter=quarter_autocomplete)


    
@app_commands.describe(
    year="Year of the class",
    quarter="Quarter (Winter, Spring, Summer, Fall)",
    dept="Department code",
    course_num="Course number",
    section_type="Section type (Lec, Lab, etc.)",
    section_code="Section code (A, B, etc.)",
)

async def watch(
    interaction: discord.Interaction,
    year: int,
    quarter: str,
    dept: str,
    course_num: str,
    section_type: str,
    section_code: str,
):
    
    
    """Slash command /watch implementation."""

    # 1️⃣  validate quarter
    try:
        quarter_code = handle_quarter(quarter)
    except ValueError as e:
        await interaction.response.send_message(str(e), ephemeral=True)
        return
    
    # 1️⃣  validate course exists BEFORE saving
    if not await course_exists(year, quarter_code, dept, course_num,
                               section_type, section_code):
        await interaction.response.send_message(
            f"Sorry, I can’t find **{unquote(dept.upper())} {course_num} "
            f"{section_type.upper()} {section_code.upper()}** "
            f"in {quarter.title()} {year}. "
            "Double-check the number and section.",
            ephemeral=True
        )
        return

    # 2️⃣  build the watch-entry
    watch_entry = {
        "Year": year,
        "Quarter": quarter_code,
        "Dept": dept.upper(),
        "CourseNum": course_num,
        "SectionType": section_type,
        "SectionCode": section_code,
        "WaitlistPos": None,           # you’ll fill this in later
    }

    # 3️⃣  store it by user ID
    user_id = interaction.user.id
    user_watchlists.setdefault(user_id, []).append(watch_entry)

    # 4️⃣  reply to the user (first response must come from .response.*)
    await interaction.response.send_message(
        f'Added **{unquote(dept.upper())} {course_num} {section_type.upper()} {section_code.upper()}** '
        f'for **{quarter} {year}** to your watch-list!'
    )

    # 5️⃣  log to console (or anywhere else)
    print(
        f"User {user_id} added watch: {dept.upper()} {course_num} "
        f"{section_type}{section_code} ({quarter} {year})"
    )


#watchlist autocomplete classname
async def watchlist_autocomplete(
        interaction: discord.Interaction,
        current: str              # what the user has typed so far
) -> list[app_commands.Choice[str]]:
    
    uid      = interaction.user.id
    watches  = user_watchlists.get(uid, [])

    cur_up = current.upper()
    choices: list[app_commands.Choice[str]] = []

    for w in watches:
        unquoted_dept = unquote(w['Dept'])       # e.g. "AC ENG"
        code_dept  = w['Dept']                # e.g. "AC%20ENG"
        label = f"{unquoted_dept} {w['CourseNum']} {w['SectionType']} {w['SectionCode']}"
        value = f"{code_dept} {w['CourseNum']} {w['SectionType']} {w['SectionCode']}"
        
        if cur_up in label.upper():
            choices.append(app_commands.Choice(name=label, value=value))

    return choices[:25]

#STATUS BOT COMMAND
@bot.tree.command(name="status", description="Check status of a watched class")
@app_commands.autocomplete(wclass=watchlist_autocomplete)
async def status(interaction: discord.Interaction, wclass: str):
    await interaction.response.defer()  # Acknowledge early

    dept, cnum, stype, scode = wclass.split(maxsplit=3)
    watches = user_watchlists.get(interaction.user.id)
    watch = next(
        (w for w in watches if (
            w["Dept"].upper() == dept.upper() and
            str(w["CourseNum"]) == cnum and
            w["SectionType"].lower() == stype.lower() and
            w["SectionCode"].lower() == scode.lower()
        )),
        None
    )

    if not watch:
        await interaction.followup.send("That class is no longer on your watch-list.", ephemeral=True)
        return

    url = construct_url(watch["Year"], watch["Quarter"], watch["Dept"], watch["CourseNum"])
    
    # Ideally, use async HTTP client here, or run blocking in executor:
    page_text = await fetch_page_text(url)

    
    enrollment, waitlist, max_enrollment = parse_enrollment_and_waitlist(
        page_text, watch["SectionType"], watch["SectionCode"]
    )
    seats_left = max_enrollment - enrollment

    
    await interaction.followup.send(
        f"**{unquote(dept)} {cnum} {stype} {scode}**\n"
        f"Seats left: **{seats_left}**\n"
        f"Enrollment: {enrollment}/{max_enrollment}\n"
        f"Wait-list: {waitlist}"
    )


"""
@bot.command(name="watch", help="Add a class to your watchlist! Usage: !watch <Year> <Quarter> <Department> <CourseNum> <SectionType> <SectionCode>")
async def watch(ctx, year: int, quarter: str, dept: str, course_num: int, section_type: str, section_code: str, waitlist_pos: int):
    try:
        _ = handle_quarter(quarter)
    except ValueError as e:
        await ctx.send(str(e))
        return

    watch_entry = {
        "Year": year,
        "Quarter": quarter,
        "Dept": dept.upper(),
        "CourseNum": course_num,
        "SectionType": section_type,
        "SectionCode": section_code,
        "WaitlistPos": waitlist_pos,
    }

    if ctx.author.id not in user_watchlists:
        user_watchlists[ctx.author.id] = []

    user_watchlists[ctx.author.id].append(watch_entry)
    await ctx.send(f"{ctx.author.mention}, added {dept.upper()} {course_num} {section_type} {section_code} for {quarter} {year} to your watchlist!")
    print(f"User {ctx.author.id} added watch: {dept} {course_num} {section_type} {section_code} for {quarter} {year}")



@bot.command(name="watchlist", help="View your watchlist")
async def watchlist(ctx):
    if ctx.author.id not in user_watchlists or not user_watchlists[ctx.author.id]:
        await ctx.send("Your watchlist is empty!")
        return

    watch_entries = user_watchlists[ctx.author.id]
    msg_lines = [
        f"{entry['Dept']} {entry['CourseNum']} - {entry['SectionType']} {entry['SectionCode']} for {entry['Year']} {entry['Quarter']}"
        for entry in watch_entries
    ]
    await ctx.send("Your watchlist:\n" + "\n".join(msg_lines))


@bot.command(
    name="unwatch",
    help="Remove a class from your watchlist! Usage: !unwatch <Year> <Quarter> <Department> <CourseNum> <SectionType> <SectionCode>",
)
async def unwatch(
    ctx,
    year: int,
    quarter: str,
    dept: str,
    course_num: int,
    section_type: str,
    section_code: str,
):
    if ctx.author.id not in user_watchlists or not user_watchlists[ctx.author.id]:
        await ctx.send("Your watchlist is empty!")
        return

    watch_entry = {
        "Year": year,
        "Quarter": quarter,
        "Dept": dept.upper(),
        "CourseNum": course_num,
        "SectionType": section_type,
        "SectionCode": section_code,
    }

    if watch_entry in user_watchlists[ctx.author.id]:
        user_watchlists[ctx.author.id].remove(watch_entry)
        await ctx.send(
            f"{ctx.author.mention}, removed {dept.upper()} {course_num} {section_type} {section_code} for {quarter} {year} from your watchlist!"
        )
    else:
        await ctx.send(f"{ctx.author.mention}, that class is not in your watchlist!")


@bot.command(name="clear", help="Clear your watchlist")
async def clear(ctx):
    if ctx.author.id in user_watchlists:
        del user_watchlists[ctx.author.id]
        await ctx.send(f"{ctx.author.mention}, your watchlist has been cleared!")
    else:
        await ctx.send("Your watchlist is already empty!")


@bot.command(name="assist", help="Show this help message")
async def assist(ctx):
    help_text = (
        "!watch <Year> <Quarter> <Department> <CourseNum> <SectionType> <SectionCode> - Add a class to your watchlist\n"
        "!unwatch <Year> <Quarter> <Department> <CourseNum> <SectionType> <SectionCode> - Remove a class from your watchlist\n"
        "!watchlist - View your watchlist\n"
        "!clear - Clear your watchlist\n"
        "!help - Show this help message\n"
        "!status - <Year> <Quarter> <Department> <CourseNum> <SectionType> <SectionCode> - Check the status of a specific class\n"
    )
    await ctx.send(help_text)


@bot.command(
    name="status",
    help="Check status of a watched class by index (default is 1). Usage: !status [index]",
)
async def status(ctx, index: int = 1):
    watches = user_watchlists.get(ctx.author.id)
    if not watches:
        await ctx.send(
            f"{ctx.author.mention}, your watchlist is empty! Add a class with !watch."
        )
        return

    if index < 1 or index > len(watches):
        await ctx.send(
            f"{ctx.author.mention}, invalid index. You have {len(watches)} classes in your watchlist."
        )
        return

    watch = watches[index - 1]

    try:
        quarter_code = handle_quarter(watch["Quarter"])
        url = construct_url(
            watch["Year"], quarter_code, watch["Dept"], watch["CourseNum"]
        )
        response = requests.get(url)
        enrollment, waitlist, max_enrollment = parse_enrollment_and_waitlist(
            response.text, watch["SectionType"], watch["SectionCode"]
        )
        seats_left = max_enrollment - enrollment

        await ctx.send(
            f"{ctx.author.mention}, status for {watch['Dept']} {watch['CourseNum']} "
            f"{watch['SectionType']} {watch['SectionCode']} ({watch['Quarter']} {watch['Year']}):\n"
            f"Seats left: {seats_left}\n"
            f"Enrollment: {enrollment}\n"
            f"Waitlist position: {waitlist}\n"
            f"Max enrollment: {max_enrollment}"
        )
    except Exception as e:
        await ctx.send(f"Error retrieving status: {e}")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    background_check.start()



@bot.event #get guild id
async def on_ready():
    for g in bot.guilds:
        print(f"{g.name}: {g.id}")
"""
if __name__ == "__main__":
    bot.run(TOKEN)                           # 4️⃣ start bot
