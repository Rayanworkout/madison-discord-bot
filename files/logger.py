import json
import shutil
from uuid import uuid4

from discord_webhook import DiscordWebhook, DiscordEmbed
from requests_html import HTMLSession


def send_discord_alert(user, user_alert, chain, price):

    webhook = DiscordWebhook(
        (
            "WEBHOOK LINK"
        ),
        rate_limit_retry=True,
    )
    msg = (
        f"Your **{user_alert} gwei** alert on **{chain}** has been triggered.  :dart:"
        f"\n\n**Current gasPrice: {price} gwei**.  :dollar:"
    )

    embed = DiscordEmbed(
        title=f":rotating_light: :envelope_with_arrow: ",
        description=msg,
        color="2D36FF",
    )

    embed.set_timestamp()

    webhook.add_embed(embed)

    webhook.execute()

    webhook = DiscordWebhook(
        (
            "WEBHOOK LINK"
        ),
        rate_limit_retry=True,
        content=user,
    )
    webhook.execute()

    print(f"Alert sent to {user}. {user_alert} gwei on {chain}.")    


class Logger:
    def __init__(self):
        self.chains = [
            "AVAX",
            "ETH",
            "ARB",
            "BSC",
            "HECO",
            "MATIC",
            "MOVR",
            "CRO",
            "CELO",
            "XDAI",
        ]
        self.session = HTMLSession()

        with open("files/bdd/db.json", "r+", encoding="utf8") as file:
            self.db = json.load(file)

    def save(self):
        with open("files/bdd/db.json", "r+", encoding="utf8") as file:
            file.seek(0)
            json.dump(self.db, file, indent=4)
            file.truncate()

    def saveImage(self, url):
        try:
            if url[:26] == "https://cdn.discordapp.com" and url[-3:] in [
                "jpg",
                "png",
                "jpeg",
            ]:
                content = self.session.get(url, stream=True)
                title = f"files/photos/{str(uuid4())[:5]}.jpg"
                with open(f"{title}", "wb") as image:
                    shutil.copyfileobj(content.raw, image)

                    return "Picture added !  :fire:"
            elif url[-3:] not in ["jpg", "png", "jpeg"]:
                return "Wrong picture format. Please Try again."

        except Exception as err:
            print("Error saving picture: {}".format(err))
            return "Could not save picture. Try again.  :x:"

    def add_count(self, user):
        user = f"<@{user}>"
        if user not in self.db:
            self.db[user] = {
                "count": 0,
                "links": [],
                "gasAlerts": {
                    "AVAX": 0,
                    "ETH": 0,
                    "ARB": 0,
                    "BSC": 0,
                    "HECO": 0,
                    "MATIC": 0,
                    "MOVR": 0,
                    "CRO": 0,
                    "CELO": 0,
                    "XDAI": 0,
                },
            }
            print(f"{user} added to the database.")

        self.db[user]["count"] += 1
        self.save()
        return user

    def add_link(self, user, url):
        user = self.add_count(user)

        if url not in self.db[user]["links"]:
            self.db[user]["links"].append(url)
            self.save()
            print(f"{user} added an URL to his list.")
            return f"Your link has been saved. Use **!myLinks** to check all your saved links."
        else:
            return "URL already in your list !"

    def user_links(self, user):
        user = self.add_count(user)

        print(f"{user} asked for his URLs.")
        return self.db[user]["links"]

    def del_link(self, user, index):
        user = self.add_count(user)
        try:
            if index - 1 > 0:
                target = self.db[user]["links"][index - 1]
                del self.db[user]["links"][index - 1]
                self.save()

                print(f"{user} has deleted a link.")
                return "This link was removed from your list.  :white_check_mark:"
            elif index - 1 <= 0:
                return "Wrong index !  :x:"

        except IndexError:
            return "Could not find this URL in your list.  :x:"

    def add_gas_alert(self, user, chain, alert):

        try:
            alert = int(alert)
            if alert < 0:
                return "Please choose a positive number.  :x:"
        except Exception:
            return "Wrong format. Please try again.  :x:\n\nCommand example: **!gasAlert ETH 50**"

        chain = chain.upper()
        if chain in self.chains:
            user = self.add_count(user)

            self.db[user]["gasAlerts"][chain] = alert
            self.save()

            print(f"{user} added a {alert} gwei alert on {chain}.")
            return f"Alert successfully added.  :white_check_mark:\n\n:arrow_forward:  **{alert} gwei on {chain}.**"
        else:
            return "Wrong chain ! Use **!gasList** to check available chains."

    def check_gas_alerts(self):
        """Comparing user alert with last gasPrice and
    send him message on Discord with webhook.
    user = user to check alerts from."""

        headers = {
            "User-Agent": (
                "MY_USER_AGENT"
            )
        }
        current_gasPrices = {
            "AVAX": 0,
            "ETH": 0,
            "ARB": 0,
            "BSC": 0,
            "HECO": 0,
            "MATIC": 0,
            "MOVR": 0,
            "CRO": 0,
            "CELO": 0,
            "XDAI": 0,
        }
        try:
            for chain in current_gasPrices.keys():
                url = (
                    "GAS API URL"
                )
                r = self.session.get(url, headers=headers).json()
                gasPrice = round(r["data"]["normal"]["price"] * 0.000000001, 2)

                current_gasPrices[chain] = gasPrice
        
        except KeyError:
            return None
        
        for user in self.db:
            user_alerts = self.db[user]["gasAlerts"]

            # COMPARING USER ALERT WITH CURRENT PRICE
            if current_gasPrices:
                for chain in current_gasPrices.keys() & user_alerts.keys():
                    current_price = current_gasPrices[chain]
                    alert = user_alerts[chain]
                    if current_price <= alert:
                        send_discord_alert(user, alert, chain, current_price)
                        self.db[user]["gasAlerts"][chain] = 0
                        self.save()
                        print(f"{user} alert on {chain} reset.")
        
        
    def my_alerts(self, user):
        user = self.add_count(user)

        user_alerts = self.db[user]["gasAlerts"]
        alerts_list = []
        for entry in user_alerts:
            if user_alerts[entry] > 0:
                alerts_list.append(
                    f":arrow_forward:  **{entry}:  {user_alerts[entry]} gwei**\n\n"
                )
        if alerts_list:
            print(f"{user} asked for his gas alerts.")
            return f"Current alerts:\n\n{''.join(alerts_list)}"
        elif not alerts_list:
            return "No alert saved yet. Use **!gasAlert** command to save your first."

    def reset_gas_alerts(self, user):
        user = self.add_count(user)

        alerts = self.db[user]["gasAlerts"]
        for chain in alerts:
            alerts[chain] = 0
        self.save()
        print(f"{user} has reset his gas alerts.")
        return "All your gas alerts were reset.  :white_check_mark:"

    def add_response(self, user, answer):
        user = self.add_count(user)

        with open("files/bdd/responses.json", "r+", encoding="utf8") as file:
            responses = json.load(file)
            if answer not in responses["list"] and answer:
                responses["list"].append(answer)
                file.seek(0)
                json.dump(responses, file, indent=4)
                file.truncate()
                print(f"{user} added a response.")
                return f'"{answer}" added to responses list.  :pencil:'
            elif not answer:
                return "Empty response.  :x:"

            elif answer in responses["list"]:
                return f'"{answer}" is already in responses list.  :x:'

    def del_response(self, answer):
        with open("files/bdd/responses.json", "r+", encoding="utf8") as file:
            responses = json.load(file)
            if answer not in responses["list"]:
                return f'"{answer}" was not found in responses list.  :x:'

            responses["list"].remove(answer)
            file.seek(0)
            json.dump(responses, file, indent=4)
            file.truncate()
            return f'"{answer}" removed from responses list.  :white_check_mark:'

    def delete_last_response(self):
        with open("files/bdd/responses.json", "r+", encoding="utf8") as file:
            responses = json.load(file)
            if responses["list"]:
                last = responses["list"][-1]
                responses["list"].remove(last)
                file.seek(0)
                json.dump(responses, file, indent=4)
                file.truncate()
                return f'"{last}" removed from list.  :white_check_mark:'
            elif not responses["list"]:
                return "List is empty !  :x:"

    def allResponses(self):
        with open("files/bdd/responses.json", "r", encoding="utf8") as file:
            responses = json.load(file)
            return "\n\n".join(responses["list"])
