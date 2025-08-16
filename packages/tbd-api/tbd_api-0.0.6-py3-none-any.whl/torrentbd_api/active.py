import re
from typing import List

from bs4 import BeautifulSoup, Tag

from .login import check_login_status, login, session
from .schema import Badge, User

headers = {
    "Host": "www.torrentbd.net",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Sec-Ch-Ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Sec-Ch-Ua-Mobile": "?0",
    "Origin": "https://www.torrentbd.net",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://www.torrentbd.net/",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9,bn;q=0.8",
    "Priority": "u=1, i",
}


class UserParser:
    def __init__(self, html: str):
        self.soup = BeautifulSoup(html, "html.parser")

    def parse_users(self) -> List[User]:
        users: List[User] = []
        for user_tag in self.soup.select("span.dl-sc-trg"):
            if not isinstance(user_tag, Tag):
                continue
            user = self._parse_single_user(user_tag)
            if user:
                users.append(user)
        return users

    def _parse_single_user(self, user_tag: Tag) -> User | None:
        """Extract a User from a single tag. Returns None if invalid."""
        a_tag = user_tag.find("a", href=True)
        if not isinstance(a_tag, Tag):
            return None

        profile_url = a_tag.get("href")
        if not isinstance(profile_url, str):
            return None

        user_id_match = re.search(r"id=(\d+)", profile_url)
        if not user_id_match:
            return None
        user_id = int(user_id_match.group(1))

        span_rank = a_tag.find("span", class_=re.compile(r"^tbdrank"))
        if not isinstance(span_rank, Tag):
            return None

        class_list = span_rank.get("class", [])
        if not isinstance(class_list, list):
            class_list = []
        rank_class = next((c for c in class_list if c != "tbdrank"), "unknown")

        name = span_rank.get_text(strip=True).split()[0]

        badges: List[Badge] = []
        for img in span_rank.find_all("img"):
            if not isinstance(img, Tag):
                continue
            title = img.get("title")
            src = img.get("src")
            if title and src:
                badges.append(Badge(title=str(title), image_url=str(src)))

        return User(
            user_id=user_id,
            name=name,
            profile_url=profile_url,
            rank=rank_class,
            badges=badges,
        )


def get_online_users() -> List[User]:
    if not check_login_status():
        print("❌ Not logged in. Attempting login...")
        login()
    url = "https://www.torrentbd.net/ajscripts.php"
    data = "task=getOnlineUsers"
    response = session.post(url, headers=headers, data=data)
    html = response.text
    parser = UserParser(html)
    return parser.parse_users()
