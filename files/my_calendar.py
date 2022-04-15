import datetime
import json

from discord_webhook import DiscordEmbed, DiscordWebhook
from requests_html import HTMLSession


def isExpired(event_date):
    """returns True if event_date has passed.
    returns False if event_date has not passed yet."""
    today = datetime.datetime.today()
    event = datetime.datetime.strptime(event_date, "%d-%m-%Y")
    return today > event


class myCalendar:
    def __init__(self):
        with open("files/bdd/events.json", "r+", encoding="utf8") as file:
            self.events_db = json.load(file)

        self.session = HTMLSession()

    def save(self):
        with open("files/bdd/events.json", "r+", encoding="utf8") as file:
            file.seek(0)
            json.dump(self.events_db, file, indent=4)
            file.truncate()

    ######################################################################################

    def create_calendar(self, calendar):
        calendar = calendar.upper()
        if calendar not in self.events_db:
            self.events_db[calendar.upper()] = {}
            self.save()
            return f'"{calendar}" calendar successfully created.  :white_check_mark:'
        elif calendar in self.events_db:
            return f'"{calendar}" already exists.  :x:'

    def get_calendar(self, calendar):
        try:
            if self.events_db[calendar.upper()]:
                calendar_events = self.events_db[calendar.upper()]
                events = ""
                for count, (event, value) in enumerate(calendar_events.items()):
                    events += f"\n{count + 1} - {event} :arrow_forward: {value}\n"

                return f"**{calendar.upper()}** :calendar:\n\n**{events}**"
            elif not self.events_db[calendar.upper()]:
                return f'No event saved in "{calendar.upper()}" yet.'
        except KeyError:
            return f'Could not find "{calendar}"  :x: Try again.'

    def delete_calendar(self, calendar):
        try:
            del self.events_db[calendar.upper()]
            self.save()
            return f'"{calendar.upper()}" successfully deleted.  :white_check_mark:'
        except KeyError:
            return f'Could not find "{calendar}".  :x: Try again.'

    def get_all_calendars(self):
        if self.events_db:
            return "\n\n".join(
                [f":arrow_forward: {calendar}" for calendar in self.events_db]
            )
        elif not self.events_db:
            return "No calendar saved yet !  :x:"

    def create_event(self, calendar="global", title="no title", date="01-02"):
        calendar = calendar.upper()
        try:
            if title not in self.events_db[calendar]:
                for char in [",", "/", "."]:
                    date = date.replace(char, "-")
                if isExpired(date + "-2022"):
                    return "Wrong date !  :x: Try again !"

                self.events_db[calendar][title] = date + "-2022"

                self.save()

                return f'"{title}" created in "{calendar}".  :white_check_mark:'

            elif title in self.events_db[calendar]:
                return f'"{title}" already in "{calendar}".  :x:'

        except KeyError:
            return f'"{calendar}" does not exist.  :x: Please create it with **!addCalendar** first.'

    def delete_event(self, calendar, index):
        try:
            target = list(self.events_db[calendar.upper()])[index - 1]
            del self.events_db[calendar.upper()][target]
            self.save()

            return f'"{target}" has been successfully deleted.  :white_check_mark:'

        except IndexError:
            return f'Could not find this event in "{calendar}"  :x: Try again.'

        except KeyError:
            return f'"{calendar}" does not exist.  :x: Please create it with **!addCalendar** first.'

    def get_all_events(self):
        def prettify_events(calendars):
            all_events = ""
            for calendar, events in calendars.items():
                if events:
                    all_events += f"\n**{calendar}**  :calendar:\n\n"
                for title, date in events.items():
                    all_events += f"**- {title}** :arrow_forward: **{date}**\n\n"
            return all_events

        return (
            prettify_events(self.events_db)
            if prettify_events(self.events_db)
            else "No event saved yet !"
        )

    def checkEvents(self):
        """checking if an event is outdated and
        deleting it"""

        to_del = []
        for calendar, entry in self.events_db.items():
            for event, date in entry.items():
                if datetime.datetime.today() > datetime.datetime.strptime(
                    date, "%d-%m-%Y"
                ) + datetime.timedelta(days=1):
                    to_del.append((calendar, event))
        for calendar, event in to_del:
            del self.events_db[calendar][event]

        self.save()

        if to_del:
            print(f"{len(to_del)} event(s) deleted.")

    def send_daily_events(self):
        """sending daily events list"""

        # GETTING DAILY EVENTS
        today = 0
        all_events = ""
        for calendar, events in self.events_db.items():
            if events:
                for title, date in events.items():
                    if (
                        datetime.datetime.strptime(date, "%d-%m-%Y").date()
                        == datetime.datetime.today().date()
                    ):
                        all_events += f"\n*{calendar}*\n"
                        all_events += f"*~ {title}*\n"
                        today += 1

        # GETTING MARKET PRICES
        all_events += f'**{"-"* 24}**\n'
        cryptos = {
            "bitcoin": "BTC",
            "ethereum": "ETH",
            "terra-luna": "LUNA",
            "cosmos": "ATOM",
        }
        for crypto in cryptos:
            r = self.session.get(
                f"https://api.coingecko.com/api/v3/simple/price?ids={crypto}&vs_currencies=usd"
            ).json()

            all_events += f"{cryptos[crypto]} :arrow_forward: {r[crypto]['usd']} $\n"

        # SENDING MESSAGE ON DISCORD
        if today:
            webhook = DiscordWebhook(
                (
                    "WEBHOOK LINK"
                ),
                rate_limit_retry=True,
            )
            msg = all_events

            embed = DiscordEmbed(
                title=f"EVENTS OF THE DAY  :calendar:\n\n",
                description=msg,
                color="2D36FF",
            )

            webhook.add_embed(embed)

            webhook.execute()
            print(today, "events today.")
        elif not today:
            print("No event today.")
