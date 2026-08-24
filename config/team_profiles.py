from dataclasses import dataclass


@dataclass
class TeamProfile:

    full_name: str

    role: str

    chrome_profile: str

    gmail: str

    active: bool = True