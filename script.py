
import requests
from bs4 import BeautifulSoup
import asyncio
import discord
from discord import app_commands
from discord.ext import commands,tasks

# --- Bot Configuration ---
intents = discord.Intents.default()
intents.guilds = True
intents.messages = True
intents.message_content = True
intents.dm_messages = True
bot = commands.Bot(command_prefix="!",intents=intents)
user_watchlists = {} #keep track of user watchlists
last_statuses = {} #keep track of last status for each user
# --- Config ---

DISCORD_TOKEN = "MTM3NTAxODYxODUzMzgzODkxMA.GI4Hwu.O0_37BilZZ6fRy1eRv-Dhl1phuTHMf4EgPp9-I"
CHANNEL_ID = 1375024217405390973  # Replace with your channel ID (integer)
CHECK_INTERVAL = 300  # in seconds (5 minutes)


Departments = {

    "AC ENG":,
    "AFAM":,
    "ANATOMY":,
"ANESTH":,
"ANTHRO":,
"ARABIC":,
"ARMN":,
"ART":,
"ART HIS":,
"ARTS":,
"ARTSHUM":,
"ASIANAM":,
"ASL":,
"BANA":,
"BATS":,
"BIO SCI":,
"BIOCHEM":,
"BME":,
"CAMPREC":,
"CBE":,
"CEM":,
"CHC/LAT":,
"CHEM":,
"CHINESE":,
"CLASSIC":,
"CLT&THY":,
"COGS":,
"COM LIT":,
"COMPSCI":,
"CRITISM":,
"CRM/LAW":,
"CSE":,
"DANCE":,
"DATA":,
"DERM":,
"DEV BIO":,
"DRAMA":,
"EARTHSS":,
"EAS":,
"ECO EVO":,
"ECON":,
"ECPS":,
"ED AFF":,
"EDUC":,
"EECS":,
"EHS":,
"ENGLISH":,
"ENGR":,
"ENGRCEE":,
"ENGRMAE":,
"ENGRMSE":,
"EPIDEM":,
"ER MED":,
"EURO ST":,
"FAM MED":,
"FILIPNO":,
"FIN":,
"FLM&MDA":,
"FRENCH":,
"GDIM":,
"GEN&SEX":,
"GERMAN":,
"GLBL ME":,
"GLBLCLT":,
"GREEK":,
"HEBREW":,
"HINDI":,
"HISTORY":,
"HUMAN":,
"HUMARTS":,
"I&C SCI":,
"IN4MATX":,
"INNO":,
"INT MED":,
"INTL ST":,
"IRAN":,
"ITALIAN":,
"JAPANSE":,
"KOREAN":,
"LATIN":,
"LAW":,
"LIT JRN":,
"LPS":,
"LSCI":,
"M&MG":,
"MATH":,
"MED":,
"MED ED":,
"MED HUM":,
"MGMT":,
"MGMT EP":,
"MGMT FE":,
"MGMT HC":,
"MGMTMBA":,
"MGMTPHD":,
"MIC BIO":,
"MNGE":,
"MOL BIO":,
"MPAC":,
"MSE":,
"MUSIC":,
"NET SYS":,
"NEURBIO":,
"NEUROL":,
"NUR DNP":,
"NUR FNP":,
"NUR INF":,
"NUR SCI":,
"OB/GYN":,
"OPHTHAL":,
"PATH":,
"PED GEN":,
"PEDS":,
"PERSIAN":,
"PHARM":,
"PHILOS":,
"PHMD":,
"PHRMSCI":,
"PHY SCI":,
"PHYSICS":,
"PHYSIO":,
"PLASTIC":,
"PM&R":,
"POL SCI":,
"PORTUG":,
"PSCI":,
"PSYCH":,
"PUB POL":,
"PUBHLTH":,
"RADIO":,
"REL STD":,
"ROTC":,
"RUSSIAN":,
"SOC SCI":,
"SOCECOL":,
"SOCIOL":,
"SPANISH":,
"SPPS":,
"STATS":,
"SURGERY":,
"SWE":,
"TAGALOG":,
"TOX":,
"UCDC":,
"UNI AFF":,
    "UNI STU":,
    "UPPP":,
    "VIETMSE":,
    "VIS STD":,
    "WRITING":,
}


class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)
        
    
    async def setup_hook(self):
        # Sync commands globally or per guild here
        await self.tree.sync()  # Use await self.tree.sync(guild=discord.Object(id=YOUR_GUILD_ID)) to sync per guild faster

bot = MyBot()
""""
@bot.tree.command(name="hello", description="Say hello to the bot")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hello, {interaction.user.mention}!")

"""


@bot.tree.command(name="watch", description="Add a class to your watchlist")
@app_commands.describe(
    year="Year of the class",
    quarter="Quarter (Winter, Spring, Summer, Fall)",
    dept="Department code",
    course_num="Course number",
    section_type="Section type (Lec, Lab, etc.)",
    section_code="Section code (A, B, etc.)"
)
async def watch(
    interaction: discord.Interaction,
    year: int,
    quarter: str,
    dept: str,
    course_num: int,
    section_type: str,
    section_code: str,
):
    # Your logic to save watch here
    await interaction.response.send_message(
        f"Added {dept} {course_num} {section_type} {section_code} for {quarter} {year} to your watchlist!"
    )
bot.run(DISCORD_TOKEN)

def handle_quarter(quarter):
    quarter = quarter.lower()
    if quarter == "summer":
        return "20"
    elif quarter == "spring":
        return "10"
    elif quarter == "winter":
        return "03"
    elif quarter == "fall":
        return "92"
    else:
        raise ValueError("Invalid quarter; use Winter, Spring, Summer, or Fall.")

def construct_url(year, quarter_code, dept, course_num):
    return f"https://www.reg.uci.edu/perl/WebSoc?YearTerm={year}-{quarter_code}&ShowFinals=1&ShowComments=1&Dept={dept}&CourseNum={course_num}"

def parse_int_from_string(s):
    s = s.strip()
    if '/' in s:
        s = s.split('/')[0].strip()
    return int(s)

def parse_enrollment_and_waitlist(html, section_type, section_code):
    soup = BeautifulSoup(html, 'html.parser')

    tables = soup.find_all('table')
    print(f"Found {len(tables)} tables")

    target_table = None

    for i, table in enumerate(tables):
        headers = [th.text.strip() for th in table.find_all('th')]
        print(f"Table {i} headers: {headers}")

        if 'Enr' in headers and 'WL' in headers:
            target_table = table
            print(f"Selected table {i} for parsing")
            break

    if target_table is None:
        raise ValueError("No table with enrollment info found")

    rows = target_table.find_all('tr')

    print(f"Found {len(rows)} rows in target table")

    for idx, row in enumerate(rows):
        cols = row.find_all('td')
        if len(cols) < 12:
            continue

        row_type = cols[1].text.strip().lower()
        row_sec = cols[2].text.strip().lower()

        print(f"Row {idx} type: '{row_type}', section: '{row_sec}'")

        if row_type == section_type.lower() and row_sec == section_code.lower():
            max_enrollment = int(cols[9].text.strip())
            enrollment = parse_int_from_string(cols[10].text)
            waitlist = int(cols[11].text.strip())
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
                url = construct_url(watch["Year"], handle_quarter(watch["Quarter"]), watch["Dept"], watch["CourseNum"])
                print(f"Fetching URL for {watch['Dept']} {watch['CourseNum']} - {url}")
                page_text = requests.get(url).text

                enrollment, waitlist, max_enrollment = parse_enrollment_and_waitlist(page_text, watch["SectionType"], watch["SectionCode"])
                print(f"Parsed Enrollment: {enrollment}, Waitlist: {waitlist}, Max Enrollment: {max_enrollment}")

                seats_left = max_enrollment - enrollment

                key = f"{watch['Dept']}-{watch['CourseNum']}-{watch['SectionType']}-{watch['SectionCode']}-{watch['Year']}-{watch['Quarter']}"
                last_status = last_statuses.get(user_id, {}).get(key)

                current_status = (enrollment, waitlist, max_enrollment)

                if last_status != current_status:
                    messages = []
                    if last_status is None or (last_status[0] < max_enrollment and seats_left > 0):
                        messages.append(f"🚨 Class Alert! {seats_left} seat(s) available for {watch['Dept']} {watch['CourseNum']} {watch['SectionType']} {watch['SectionCode']}.")

                    if last_status and watch["WaitlistPos"] < last_status[1] and waitlist > 0:
                        messages.append(f"🔼 You moved up the waitlist for {watch['Dept']} {watch['CourseNum']}! New position: {waitlist}.")

                    if watch["WaitlistPos"] == 0 and enrollment == max_enrollment and (last_status is None or last_status[1] != 0):
                        messages.append(f"🎉 Congrats! You are off the waitlist for {watch['Dept']} {watch['CourseNum']}!")

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

"""""
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
"""

@bot.command(name="watchlist", help="View your watchlist")
async def watchlist(ctx):
    if ctx.author.id not in user_watchlists or not user_watchlists[ctx.author.id]:
        await ctx.send("Your watchlist is empty!")
        return

    watch_entries = user_watchlists[ctx.author.id]
    msg_lines = [f"{entry['Dept']} {entry['CourseNum']} - {entry['SectionType']} {entry['SectionCode']} for {entry['Year']} {entry['Quarter']}" for entry in watch_entries]
    await ctx.send(f"Your watchlist:\n" + "\n".join(msg_lines))

@bot.command(name="unwatch", help="Remove a class from your watchlist! Usage: !unwatch <Year> <Quarter> <Department> <CourseNum> <SectionType> <SectionCode>")
async def unwatch(ctx, year: int, quarter: str, dept: str, course_num: int, section_type: str, section_code: str):
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
        await ctx.send(f"{ctx.author.mention}, removed {dept.upper()} {course_num} {section_type} {section_code} for {quarter} {year} from your watchlist!")
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

@bot.command(name="status", help="Check status of a watched class by index (default is 1). Usage: !status [index]")
async def status(ctx, index: int = 1):
    watches = user_watchlists.get(ctx.author.id)
    if not watches:
        await ctx.send(f"{ctx.author.mention}, your watchlist is empty! Add a class with !watch.")
        return
    
    if index < 1 or index > len(watches):
        await ctx.send(f"{ctx.author.mention}, invalid index. You have {len(watches)} classes in your watchlist.")
        return

    watch = watches[index - 1]

    try:
        quarter_code = handle_quarter(watch["Quarter"])
        url = construct_url(watch["Year"], quarter_code, watch["Dept"], watch["CourseNum"])
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

bot.run(DISCORD_TOKEN)
