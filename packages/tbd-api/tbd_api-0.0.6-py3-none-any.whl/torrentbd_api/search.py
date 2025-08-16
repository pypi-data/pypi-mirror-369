from typing import Any, TypedDict, cast

from bs4 import BeautifulSoup, Tag

from .login import check_login_status, headers, login, session


class TorrentMetadata(TypedDict):
    total_results: int
    total_pages: int


class TorrentData(TypedDict):
    title: str
    torrent_id: str
    link: str
    download_link: str
    category: str
    size: str
    uploaded_by: str
    upload_time: str
    seeders: int
    leechers: int
    completed: int
    freeleech: bool


class SearchResponse(TypedDict):
    torrents: list[TorrentData]
    metadata: TorrentMetadata


def search_torrents(query: str, page: int = 1) -> SearchResponse:
    if not check_login_status():
        login()

    url = "https://www.torrentbd.net/ajsearch.php"
    data = {
        "page": str(page),
        "kuddus_searchtype": "torrents",
        "kuddus_searchkey": query,
        "searchParams[sortBy]": "",
        "searchParams[secondary_filters_extended]": "",
    }

    try:
        response = session.post(url, headers=headers, data=data)
        response.raise_for_status()

        return parse_torrents_from_html(response.text)

    except Exception:
        # Return error in the same structure as success
        empty_metadata: TorrentMetadata = {"total_results": 0, "total_pages": 0}
        return {
            "torrents": [],
            "metadata": empty_metadata,
        }


def parse_torrents_from_html(html: str) -> SearchResponse:
    try:
        soup = BeautifulSoup(html, "html.parser")
        results: list[TorrentData] = []

        # Base URL for constructing full links
        base_url = "https://www.torrentbd.net/"

        # Extract metadata from the page
        metadata = extract_search_metadata(soup)

        # Extract torrents from the page
        for torrent_row in soup.find_all("tr"):
            # Convert to Tag for proper typing
            torrent = cast(Tag, torrent_row)
            torrent_data = extract_torrent_data(torrent, base_url)
            if torrent_data:
                results.append(torrent_data)

        return {
            "torrents": results,
            "metadata": metadata,
        }

    except Exception:
        # Return error in the same structure as success but without error field
        empty_metadata: TorrentMetadata = {"total_results": 0, "total_pages": 0}
        return {"torrents": [], "metadata": empty_metadata}


def extract_search_metadata(soup: BeautifulSoup) -> TorrentMetadata:
    """Extract metadata like total results and pagination info from search results"""
    metadata: TorrentMetadata = {
        "total_results": 0,
        "total_pages": 0,
    }

    # Get total results count if available
    results_counter = soup.find("h6", class_="kuddus-results-counter")
    if results_counter and isinstance(results_counter, Tag):
        counter_text = results_counter.get_text(strip=True)
        import re

        count_match = re.search(r"(\d+)", counter_text)
        if count_match:
            metadata["total_results"] = int(count_match.group(1))

    # Extract pagination info
    pagination = soup.find("div", class_="pagination-block")
    if pagination and isinstance(pagination, Tag):
        pages = pagination.find_all("li", class_="aj-paginator")
        if pages:
            # Find the last page number
            page_numbers = [
                int(page.get_text(strip=True))
                for page in pages
                if isinstance(page, Tag) and page.get_text(strip=True).isdigit()
            ]
            if page_numbers:
                metadata["total_pages"] = max(page_numbers)

    return metadata


def extract_torrent_data(torrent: Tag, base_url: str) -> TorrentData | None:
    """Extract data for a single torrent from its row"""
    # Skip rows without title
    title_tag = torrent.find("a", class_="ttorr-title")
    if not title_tag:
        return None

    # Ensure title_tag is a Tag
    title_tag = cast(Tag, title_tag)

    # Initialize the torrent data dictionary with basic info
    torrent_data: TorrentData = {
        "title": title_tag.text.strip(),
        "torrent_id": "",
        "link": "",
        "download_link": "",
        "category": "Unknown",
        "size": "N/A",
        "uploaded_by": "Unknown",
        "upload_time": "Unknown",
        "seeders": 0,
        "leechers": 0,
        "completed": 0,
        "freeleech": False,
    }

    # Extract links and ID
    extract_links_and_id(title_tag, torrent, torrent_data, base_url)

    # Extract category and freeleech status
    extract_category_and_freeleech(torrent, torrent_data)

    # Extract size
    extract_size(torrent, torrent_data)

    # Extract uploader information
    extract_uploader_info(torrent, torrent_data)

    # Extract stats (seeders, leechers, completed)
    extract_searcher_stats(torrent, torrent_data)

    return torrent_data


def extract_links_and_id(
    title_tag: Tag, torrent: Tag, torrent_data: TorrentData, base_url: str
) -> None:
    """Extract torrent links and ID"""
    # Extract torrent link
    link = title_tag.get("href", "")
    if link and isinstance(link, str) and not link.startswith("http"):
        link = base_url + link
    torrent_data["link"] = link if isinstance(link, str) else ""

    # Extract torrent ID from the link
    if link and isinstance(link, str):
        import re

        id_match = re.search(r"id=(\d+)", link)
        if id_match:
            torrent_data["torrent_id"] = id_match.group(1)

    # Extract download link
    download_tag = torrent.find(
        "a", href=lambda h: h and isinstance(h, str) and h.startswith("download.php")
    )
    if download_tag and isinstance(download_tag, Tag):
        download_link = download_tag.get("href", "")
        if (
            download_link
            and isinstance(download_link, str)
            and not download_link.startswith("http")
        ):
            download_link = base_url + download_link
        torrent_data["download_link"] = (
            download_link if isinstance(download_link, str) else ""
        )


def extract_category_and_freeleech(torrent: Tag, torrent_data: TorrentData) -> None:
    """Extract category and check if torrent is freeleech"""
    # Extract category
    category_img = torrent.find("img", class_="cat-pic-img")
    if category_img and isinstance(category_img, Tag):
        category = category_img.get("title", "")
        if isinstance(category, str):
            torrent_data["category"] = category

    # Check if it's a freeleech torrent
    # Define a function that returns bool for type checking
    def title_contains_freeleech(t: Any) -> bool:
        return bool(t and isinstance(t, str) and "FreeLeech" in t)

    torrent_data["freeleech"] = bool(
        torrent.find(
            "img",
            class_="rel-icon",
            attrs={"title": title_contains_freeleech},
        )
    )


def extract_size(torrent: Tag, torrent_data: TorrentData) -> None:
    """Extract torrent size"""
    size_tag = torrent.find("div", class_="blue100")
    if size_tag:
        size = size_tag.get_text(strip=True)
        torrent_data["size"] = size.replace("insert_drive_file", "").strip()


def extract_uploader_info(torrent: Tag, torrent_data: TorrentData) -> None:
    """Extract uploader information and upload time"""
    uploaded_by_div = torrent.find("div", class_="uploaded-by")
    if uploaded_by_div and isinstance(uploaded_by_div, Tag):
        # Check if it's an anonymous upload
        if "Anonymous" in uploaded_by_div.get_text():
            torrent_data["uploaded_by"] = "Anonymous"
        else:
            uploader_tag = uploaded_by_div.find("a")
            if uploader_tag and isinstance(uploader_tag, Tag):
                span = uploader_tag.find("span")
                if span and isinstance(span, Tag):
                    torrent_data["uploaded_by"] = span.get_text(strip=True)

        # Extract upload time
        # Define a function that returns bool for type checking
        def title_contains_time(t: Any) -> bool:
            return bool(t and isinstance(t, str) and any(x in t for x in ["PM", "AM"]))

        time_span = uploaded_by_div.find(
            "span",
            attrs={"title": title_contains_time},
        )
        if time_span and isinstance(time_span, Tag):
            torrent_data["upload_time"] = time_span.get_text(strip=True)


def extract_searcher_stats(torrent: Tag, torrent_data: TorrentData) -> None:
    """Extract seeders, leechers, and completed counts"""
    # First approach: Try finding the stats divs and extract their content
    try:
        extract_stats_approach_1(torrent, torrent_data)
    except (AttributeError, TypeError):
        # Set default values if extraction fails
        torrent_data["seeders"] = torrent_data.get("seeders", 0)
        torrent_data["leechers"] = torrent_data.get("leechers", 0)
        torrent_data["completed"] = torrent_data.get("completed", 0)

    # If first approach didn't work, try second approach
    if (
        torrent_data["seeders"] == 0
        and torrent_data["leechers"] == 0
        and torrent_data["completed"] == 0
    ):
        try:
            extract_stats_approach_2(torrent, torrent_data)
        except (IndexError, AttributeError):
            # Ensure default values are set if second approach also fails
            torrent_data["seeders"] = torrent_data.get("seeders", 0)
            torrent_data["leechers"] = torrent_data.get("leechers", 0)
            torrent_data["completed"] = torrent_data.get("completed", 0)


def extract_stats_approach_1(torrent: Tag, torrent_data: TorrentData) -> None:
    """First approach to extract seeders, leechers, completed stats"""
    extract_seeders(torrent, torrent_data)
    extract_leechers(torrent, torrent_data)
    extract_completed(torrent, torrent_data)


def extract_seeders(torrent: Tag, torrent_data: TorrentData) -> None:
    """Extract seeders count from torrent row"""
    seeders_tag = torrent.find("div", class_="thc seed")
    if seeders_tag and isinstance(seeders_tag, Tag):
        try:
            # Try to find the icon and get its next sibling text
            icon = seeders_tag.find("i", class_="material-icons")
            if icon and isinstance(icon, Tag):
                next_text = str(icon.next_sibling).strip()
                if next_text:
                    try:
                        torrent_data["seeders"] = int(next_text)
                    except ValueError:
                        torrent_data["seeders"] = 0
            # If that didn't work, try the full text
            if torrent_data["seeders"] == 0:
                seeders_text = seeders_tag.get_text(strip=True)
                # Remove known icon text and get remaining digits
                seeders_text = seeders_text.replace("file_upload", "").strip()
                if seeders_text:
                    try:
                        torrent_data["seeders"] = int(
                            "".join(filter(str.isdigit, seeders_text)) or "0"
                        )
                    except ValueError:
                        torrent_data["seeders"] = 0
        except Exception:
            # Fallback to 0 if anything goes wrong
            torrent_data["seeders"] = 0


def extract_leechers(torrent: Tag, torrent_data: TorrentData) -> None:
    """Extract leechers count from torrent row"""
    leechers_tag = torrent.find("div", class_="thc leech")
    if leechers_tag and isinstance(leechers_tag, Tag):
        try:
            # Try to find the icon and get its next sibling text
            icon = leechers_tag.find("i", class_="material-icons")
            if icon and isinstance(icon, Tag):
                next_text = str(icon.next_sibling).strip()
                if next_text:
                    try:
                        torrent_data["leechers"] = int(next_text)
                    except ValueError:
                        torrent_data["leechers"] = 0
            # If that didn't work, try the full text
            if torrent_data["leechers"] == 0:
                leechers_text = leechers_tag.get_text(strip=True)
                # Remove known icon text and get remaining digits
                leechers_text = leechers_text.replace("file_download", "").strip()
                if leechers_text:
                    try:
                        torrent_data["leechers"] = int(
                            "".join(filter(str.isdigit, leechers_text)) or "0"
                        )
                    except ValueError:
                        torrent_data["leechers"] = 0
        except Exception:
            # Fallback to 0 if anything goes wrong
            torrent_data["leechers"] = 0


def extract_completed(torrent: Tag, torrent_data: TorrentData) -> None:
    """Extract completed downloads count from torrent row"""
    completed_tag = torrent.find("div", class_="thc completed")
    if completed_tag and isinstance(completed_tag, Tag):
        try:
            # Try to find the icon and get its next sibling text
            icon = completed_tag.find("i", class_="material-icons")
            if icon and isinstance(icon, Tag):
                next_text = str(icon.next_sibling).strip()
                if next_text:
                    try:
                        torrent_data["completed"] = int(next_text)
                    except ValueError:
                        torrent_data["completed"] = 0
            # If that didn't work, try the full text
            if torrent_data["completed"] == 0:
                completed_text = completed_tag.get_text(strip=True)
                # Remove known icon text and get remaining digits
                completed_text = completed_text.replace("done_all", "").strip()
                if completed_text:
                    try:
                        torrent_data["completed"] = int(
                            "".join(filter(str.isdigit, completed_text)) or "0"
                        )
                    except ValueError:
                        torrent_data["completed"] = 0
        except Exception:
            # Fallback to 0 if anything goes wrong
            torrent_data["completed"] = 0


def extract_stats_approach_2(torrent: Tag, torrent_data: TorrentData) -> None:
    """Alternative approach to extract torrent stats (seeders, leechers, completed)"""
    try:
        # Use a safer approach to find the container
        # First, find all divs that might contain our stats
        potential_containers = torrent.find_all("div")
        stats_container = None

        # Check each potential container for thc class divs
        for container in potential_containers:
            if isinstance(container, Tag) and container.find_all(
                "div", class_="thc", recursive=False
            ):
                stats_container = container
                break

        if stats_container and isinstance(stats_container, Tag):
            # Get all the thc divs in order
            thc_divs = stats_container.find_all("div", class_="thc")
            if len(thc_divs) >= 3:
                # Extract text from each div
                seeders_div = cast(Tag, thc_divs[0])
                seeders_text = seeders_div.get_text(strip=True)
                try:
                    torrent_data["seeders"] = int(
                        "".join(filter(str.isdigit, seeders_text)) or "0"
                    )
                except ValueError:
                    torrent_data["seeders"] = 0

                leechers_div = cast(Tag, thc_divs[1])
                leechers_text = leechers_div.get_text(strip=True)
                try:
                    torrent_data["leechers"] = int(
                        "".join(filter(str.isdigit, leechers_text)) or "0"
                    )
                except ValueError:
                    torrent_data["leechers"] = 0

                completed_div = cast(Tag, thc_divs[2])
                completed_text = completed_div.get_text(strip=True)
                try:
                    torrent_data["completed"] = int(
                        "".join(filter(str.isdigit, completed_text)) or "0"
                    )
                except ValueError:
                    torrent_data["completed"] = 0
    except Exception:
        # Log the error or handle it more explicitly
        torrent_data["seeders"] = torrent_data.get("seeders", 0)
        torrent_data["leechers"] = torrent_data.get("leechers", 0)
        torrent_data["completed"] = torrent_data.get("completed", 0)
