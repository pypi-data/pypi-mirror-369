from typing import TypedDict, Union

from bs4 import BeautifulSoup, Tag

from .login import check_login_status, headers, login, session


class ProfileStats(TypedDict):
    upload: str
    download: str
    ratio: str
    seedbonus: str
    referrals: str
    fl_tokens: str
    last_seen: str
    torrent_uploads: str
    upload_rep: str
    forum_rep: str
    activity: dict[str, str]
    seed_to_go: str | None
    seeding_now: str | None


class AdditionalInfo(TypedDict):
    privacy_level: str
    ip_address: str
    invited_by: str
    client: str
    country: str
    joined: str
    age: str
    gender: str


class SuccessfulProfileData(TypedDict):
    success: bool
    username: str
    rank: str
    avatar: str
    stats: ProfileStats
    additional_info: AdditionalInfo


class ErrorProfileData(TypedDict):
    success: bool
    error: str


ProfileData = Union[SuccessfulProfileData, ErrorProfileData]


class ProfileResponse(TypedDict):
    result: ProfileData


def get_user_profile() -> ProfileResponse:
    if not check_login_status():
        login()

    url = "https://www.torrentbd.net/account-details.php"

    try:
        response = session.get(url, headers=headers)
        response.raise_for_status()
        return {"result": parse_profile_from_html(response.text)}
    except Exception as e:
        return {"result": {"success": False, "error": str(e)}}


def parse_profile_from_html(html: str) -> ProfileData:
    try:
        soup = BeautifulSoup(html, "html.parser")

        # Check for error page
        error_div = soup.find("div", class_="error")
        if error_div and "Invalid user" in error_div.text:
            return {"success": False, "error": "Invalid user or not logged in"}

        # Extract all profile data
        profile_data = extract_profile_data(soup)

        # Format the data for response
        return format_profile_data(profile_data)

    except Exception as e:
        return {"success": False, "error": f"Error parsing profile: {str(e)}"}


def extract_profile_data(soup: BeautifulSoup) -> dict[str, str]:
    """Extract all profile data from the BeautifulSoup object"""
    profile_data: dict[str, str] = {}

    # Extract basic profile info
    extract_username_and_rank(soup, profile_data)
    extract_avatar(soup, profile_data)

    # Extract stats from different parts of the page
    extract_crc_wrapper_data(soup, profile_data)
    extract_short_links_data(soup, profile_data)
    extract_profile_info_table(soup, profile_data)
    extract_card_reveal_data(soup, profile_data)
    extract_cr_wrapper_data(soup, profile_data)
    extract_activity_data(soup, profile_data)

    return profile_data


def extract_username_and_rank(
    soup: BeautifulSoup, profile_data: dict[str, str]
) -> None:
    """Extract username and rank information"""
    username_span = soup.find("span", class_="tbdrank")
    if username_span and isinstance(username_span, Tag):
        profile_data["username"] = username_span.text.strip()
        class_attr = username_span.get("class")
        if class_attr and len(class_attr) > 1:
            profile_data["rank"] = class_attr[1]
        else:
            profile_data["rank"] = "Unknown"

    # Find the small element with rank text (more reliable)
    rank_span = soup.find("small", class_="u-rank-text")
    if rank_span and isinstance(rank_span, Tag):
        profile_data["rank"] = rank_span.text.strip()


def extract_avatar(soup: BeautifulSoup, profile_data: dict[str, str]) -> None:
    """Extract avatar URL"""
    avatar_img = soup.find("img", class_="up-avatar")
    if avatar_img and isinstance(avatar_img, Tag):
        avatar_url = avatar_img.get("data-src-og", "")
        if (
            avatar_url
            and isinstance(avatar_url, str)
            and avatar_url != "https://www.torrentbd.net/images/transparent-sq.png"
        ):
            profile_data["avatar"] = avatar_url


def extract_crc_wrapper_data(soup: BeautifulSoup, profile_data: dict[str, str]) -> None:
    """Extract data from crc-wrapper divs"""
    crc_wrappers = soup.find_all("div", class_="crc-wrapper")
    for wrapper in crc_wrappers:
        if isinstance(wrapper, Tag):
            title = wrapper.get("title", "")
            value_div = wrapper.find("div", class_="cr-value")
            if not (value_div and isinstance(value_div, Tag)):
                continue

            value = value_div.text.strip()

            if isinstance(title, str):
                if "Upload:" in title:
                    profile_data["upload"] = value
                elif "Download:" in title:
                    profile_data["download"] = value
                elif "Ratio:" in title:
                    profile_data["ratio"] = value
                elif "Seedbonus:" in title:
                    profile_data["seedbonus"] = value
                elif "Last Seen" in title:
                    profile_data["last_seen"] = value


def extract_short_links_data(soup: BeautifulSoup, profile_data: dict[str, str]) -> None:
    """Extract data from short links"""
    short_links = soup.find_all("div", class_="short-links")
    for link in short_links:
        if isinstance(link, Tag):
            text = link.text.strip()
            counter = link.find("span", class_="short-link-counter")
            if counter and isinstance(counter, Tag):
                value = counter.text.strip()
                if "Torrent Uploads" in text:
                    profile_data["torrent_uploads"] = value
                elif "Upload Rep" in text:
                    profile_data["upload_rep"] = value
                elif "Forum Rep" in text:
                    profile_data["forum_rep"] = value


def extract_profile_info_table(
    soup: BeautifulSoup, profile_data: dict[str, str]
) -> None:
    """Extract data from profile info table"""
    profile_info_table = soup.find("table", class_="profile-info-table")
    if profile_info_table and isinstance(profile_info_table, Tag):
        rows = profile_info_table.find_all("tr")
        for row in rows:
            if isinstance(row, Tag):
                cols = row.find_all("td")
                if (
                    len(cols) == 2
                    and isinstance(cols[0], Tag)
                    and isinstance(cols[1], Tag)
                ):
                    key = cols[0].text.strip().lower()
                    value = cols[1].text.strip()

                    # Clean up values that have links
                    link = cols[1].find("a")
                    if link and isinstance(link, Tag):
                        value = link.text.strip()

                    profile_data[key] = value


def extract_card_reveal_data(soup: BeautifulSoup, profile_data: dict[str, str]) -> None:
    """Extract data from card reveal section"""
    card_reveal = soup.find("div", class_="card-reveal")
    if card_reveal and isinstance(card_reveal, Tag):
        p_tags = card_reveal.find_all("p")
        for p in p_tags:
            if isinstance(p, Tag) and ":" in p.text:
                key, value = p.text.split(":", 1)
                profile_data[key.strip().lower()] = value.strip()


def extract_cr_wrapper_data(soup: BeautifulSoup, profile_data: dict[str, str]) -> None:
    """Extract data from cr-wrapper divs"""
    cr_wrappers = soup.find_all("div", class_="cr-wrapper")
    for wrapper in cr_wrappers:
        if isinstance(wrapper, Tag):
            label_div = wrapper.find("div", class_="cr-label")
            value_div = wrapper.find("div", class_="cr-value")

            if not (
                label_div
                and isinstance(label_div, Tag)
                and value_div
                and isinstance(value_div, Tag)
            ):
                continue

            key = label_div.text.strip().lower()
            value = value_div.text.strip()

            # Clean colon from start of values
            if value.startswith(":"):
                value = value[1:].strip()

            # Clean up values that have links
            link = value_div.find("a")
            if link and isinstance(link, Tag):
                value = link.text.strip()

            profile_data[key] = value


def extract_activity_data(soup: BeautifulSoup, profile_data: dict[str, str]) -> None:
    """Extract activity data (seeding/leeching)"""
    activity_row = find_activity_row(soup)

    if activity_row and isinstance(activity_row, Tag):
        td_cells = activity_row.find_all("td")
        if len(td_cells) > 1:
            # Ensure activity_td is a Tag
            activity_td = td_cells[1]
            if isinstance(activity_td, Tag):
                extract_seeding_leeching_data(soup, activity_td, profile_data)


def find_activity_row(soup: BeautifulSoup) -> Tag | None:
    """Find the row containing activity information"""
    activity_rows = soup.find_all("tr")

    # Find the activity row
    for row in activity_rows:
        if isinstance(row, Tag):
            first_cell = row.find("td")
            if (
                first_cell
                and isinstance(first_cell, Tag)
                and first_cell.text.strip() == "Activity"
            ):
                return row

    return None


def extract_seeding_leeching_data(
    soup: BeautifulSoup, activity_td: Tag, profile_data: dict[str, str]
) -> None:
    """Extract seeding and leeching data from activity cell"""
    # Try to extract seeding and leeching from spans
    seeding_span = activity_td.find("span", class_="uc-seeding")
    leeching_span = activity_td.find("span", class_="uc-leeching")

    if (
        seeding_span
        and isinstance(seeding_span, Tag)
        and leeching_span
        and isinstance(leeching_span, Tag)
    ):
        # If spans contain ..., look for actual values elsewhere
        seeding_text = seeding_span.text.strip()
        leeching_text = leeching_span.text.strip()

        if seeding_text == "..." or not seeding_text:
            seeding_text = find_seeding_count_elsewhere(soup)

        # Update the activity data
        profile_data["seeding"] = seeding_text
        profile_data["leeching"] = leeching_text


def find_seeding_count_elsewhere(soup: BeautifulSoup) -> str:
    """Look for seeding count in other parts of the page when not available
    in the activity row.
    """
    seeding_divs = soup.find_all("div")
    for div in seeding_divs:
        if isinstance(div, Tag):
            label_div = div.find("div", class_="cr-label")
            if (
                label_div
                and isinstance(label_div, Tag)
                and label_div.text.strip() == "Seeding now"
            ):
                seeding_value_div = div.find("div", class_="cr-value")
                if seeding_value_div and isinstance(seeding_value_div, Tag):
                    seeding_link = seeding_value_div.find("a")
                    if seeding_link and isinstance(seeding_link, Tag):
                        return seeding_link.text.strip()

    return "0"


def format_profile_data(profile_data: dict[str, str]) -> SuccessfulProfileData:
    """Format the extracted profile data into a structured response"""
    activity_data: dict[str, str] = {
        "seeding": profile_data.get("seeding", "0"),
        "leeching": profile_data.get("leeching", "0"),
    }

    stats: ProfileStats = {
        "upload": profile_data.get("upload", "0 B"),
        "download": profile_data.get("download", "0 B"),
        "ratio": profile_data.get("ratio", "0"),
        "seedbonus": profile_data.get("seedbonus", "0"),
        "referrals": profile_data.get("referrals", "0"),
        "fl_tokens": profile_data.get("fl tokens", "0"),
        "last_seen": profile_data.get("last_seen", "Unknown"),
        "torrent_uploads": profile_data.get("torrent_uploads", "0"),
        "upload_rep": profile_data.get("upload_rep", "0"),
        "forum_rep": profile_data.get("forum_rep", "0"),
        "activity": activity_data,
        "seed_to_go": None,
        "seeding_now": None,
    }

    # Add seed to go if it exists
    if "seed to go" in profile_data:
        stats["seed_to_go"] = profile_data["seed to go"]

    # Add seeding now if it exists
    if "seeding now" in profile_data:
        stats["seeding_now"] = profile_data["seeding now"]

    additional_info: AdditionalInfo = {
        "privacy_level": profile_data.get("privacy level", "Unknown"),
        "ip_address": profile_data.get("ip address", "Unknown"),
        "invited_by": profile_data.get("invited by", "Unknown"),
        "client": profile_data.get("torrent clients", "Unknown"),
        "country": profile_data.get("country", "Unknown"),
        "joined": profile_data.get("joined", "Unknown"),
        "age": profile_data.get("age", "Unknown"),
        "gender": profile_data.get("gender", "Unknown"),
    }

    formatted_data: SuccessfulProfileData = {
        "success": True,
        "username": profile_data.get("username", "Unknown"),
        "rank": profile_data.get("rank", "Unknown"),
        "avatar": profile_data.get("avatar", ""),
        "stats": stats,
        "additional_info": additional_info,
    }

    return formatted_data


def extract_number(text: str, prefix: str) -> str:
    """Extract number after a prefix like ↑ or ↓."""
    try:
        parts = text.split(prefix)
        if len(parts) > 1:
            num_str = "".join(
                filter(lambda x: x.isdigit() or x == ".", parts[1].split()[0])
            )
            return num_str
        return "0"
    except Exception:
        return "0"
