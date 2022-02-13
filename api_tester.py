"""ABCK API TESTER"""
import random
import json
from logging import basicConfig, INFO, ERROR, log
import requests

class Solver:
    """Solver object"""
    basicConfig(format="[Thread: %(thread_id)s] [%(asctime)s] [%(message)s]", level=INFO)

    def __init__(self, thread_id: int) -> None:
        self.s_validator, self.standard_sess = requests.Session(), requests.Session()
        self.abck = None
        self.thread_id = thread_id
        self.s_validator.headers = {
            "accept": "*/*",
            "user-agent": "",
            "accept-language": "en,pl-PL;q=0.9,pl;q=0.8,en-US;q=0.7",
            "content-type": "text/plain;charset=UTF-8",
            "origin": "https://sklep.sizeer.com",
            "referer": "https://sklep.sizeer.com/"
        }

        self.init_settings()
        self.solver_domain = self.setup["solver_domain"]
        self.page_to_bot = self.setup["page_to_bot"]
        self.validator = self.setup["validator_domain"]

        if self.setup["use_proxy"]:
            self.s_validator.proxies = Solver.randomize_proxy()


    def init_settings(self) -> None:
        """Initialize object based on settings from settings.json file"""
        with open("settings.json", encoding="utf-8") as settings_file:
            self.setup = json.loads(settings_file.read())


    def run(self) -> None:
        """Runs whole solver"""
        self.set_solver_session()
        self.get_invalid()
        if self.solve(1):
            if self.solve(2):
                self.solve(3)
        else:
            log(ERROR, "Process broke somwhere :|", extra={"thread_id": self.thread_id})


    def set_solver_session(self) -> None:
        """Set up `user-agent` header when using user-agent provided by API"""
        try:
            resp = self.standard_sess.get(self.solver_domain)
            resp = resp.json()
            self.s_validator.headers["user-agent"] = resp["userAgent"]
        except json.decoder.JSONDecodeError:
            log(ERROR, "Banned proxy", extra={"thread_id": self.thread_id})


    def get_invalid(self) -> None:
        """Method to get invaild abck cookie needed to gen good one"""
        try:
            self.abck = self.s_validator.get(self.page_to_bot).cookies["_abck"]
        except KeyError:
            self.get_invalid()


    def solve(self, step_id: int) -> bool:
        """Solver core logic"""

        try:
            solver_resp = self.standard_sess.post(self.solver_domain, json={
                "domain": self.page_to_bot,
                "oldCookie": self.abck
            })
            solver_resp = solver_resp.json()

            temp_cookie = self.s_validator.post(self.validator, json={
                "sensor_data": solver_resp["sensor"]
            }).cookies["_abck"]
            #making third sensor doesn't require new abck to send
            if step_id == 1:
                self.abck = temp_cookie
                log(INFO, f"Step [{step_id}]\nCookie [{len(self.abck)}\
]: {self.abck}", extra={"thread_id": self.thread_id})
            else:
                log(INFO, f"Step [{step_id}]\nCookie [{len(temp_cookie)}\
]: {temp_cookie}", extra={"thread_id": self.thread_id})

            return True

        except ConnectionError:
            log(ERROR ,"API SERVER CANNOT RESPOND [CRITICAL ERROR]")
            return False

        except Exception as unex_error:
            log(ERROR, f"[ERROR] {unex_error}", extra={"thread_id": self.thread_id})
            return False


    @staticmethod
    def randomize_proxy() -> None:
        """Gets random proxy from `proxy.txt` file"""

        random.seed()
        with open("proxy.txt", encoding="utf-8") as proxy_file:
            proxy_strings = [x.strip() for x in proxy_file.readlines()]

        picked = random.choice(proxy_strings)
        proxy_format = picked.split(":")

        return {"http": f"http://{proxy_format[2]}:{proxy_format[3]}@{proxy_format[0]}:\
    {proxy_format[1]}",
    "https": f"http://{proxy_format[2]}:{proxy_format[3]}@{proxy_format[0]}:{proxy_format[1]}"}
