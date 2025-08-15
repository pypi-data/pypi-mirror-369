"""Settings for gbp-feeds"""

from dataclasses import dataclass

from gbpcli.settings import BaseSettings


@dataclass(frozen=True)
class Settings(BaseSettings):
    """gbp-feeds settings"""

    env_prefix = "GBP_FEEDS_"

    # pylint: disable=invalid-name

    # Title for the Feed
    TITLE: str = "Gentoo Build Publisher"

    # Description for the Feed
    DESCRIPTION: str = "Latest Gentoo Build Publisher builds" ""

    # Entries per feed
    ENTRIES_PER_FEED: int = 20

    EXT_CSS: str = (
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css"
    )
