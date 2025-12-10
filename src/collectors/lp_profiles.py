"""
LP Profile management
Loads and manages LP institution profiles
"""
import json
import logging
from pathlib import Path
from typing import Dict, List

from ..database.models import LPProfile

logger = logging.getLogger(__name__)


class LPProfileManager:
    """Manages LP institution profiles"""

    def __init__(self, profiles_path: str = "data/lp_entities.json"):
        """Initialize LP profile manager"""
        self.profiles_path = Path(profiles_path)
        self.profiles: Dict[str, LPProfile] = {}
        self.load_profiles()

    def load_profiles(self):
        """Load LP profiles from JSON file"""
        try:
            with open(self.profiles_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for name, profile_data in data.items():
                self.profiles[name] = LPProfile.from_dict(name, profile_data)

            logger.info(f"Loaded {len(self.profiles)} LP profiles")

        except FileNotFoundError:
            logger.error(f"LP profiles file not found: {self.profiles_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing LP profiles JSON: {e}")
            raise

    def get_profile(self, lp_name: str) -> LPProfile:
        """Get a specific LP profile"""
        if lp_name not in self.profiles:
            raise ValueError(f"LP profile not found: {lp_name}")
        return self.profiles[lp_name]

    def get_all_profiles(self) -> Dict[str, LPProfile]:
        """Get all LP profiles"""
        return self.profiles

    def get_lp_names(self) -> List[str]:
        """Get list of all LP names"""
        return list(self.profiles.keys())

    def get_tier1_lps(self, tier1_list: List[str]) -> List[str]:
        """Get tier 1 LP names that exist in profiles"""
        return [lp for lp in tier1_list if lp in self.profiles]

    def get_high_korea_interest_lps(self) -> List[str]:
        """Get LPs with high or very high Korea interest"""
        return [
            name for name, profile in self.profiles.items()
            if profile.korea_interest in ['high', 'very_high']
        ]

    def get_search_keywords(self, lp_name: str) -> List[str]:
        """Get search keywords for a specific LP"""
        profile = self.get_profile(lp_name)
        return profile.search_keywords

    def get_profile_summary(self, lp_name: str) -> str:
        """Get a summary of an LP profile"""
        profile = self.get_profile(lp_name)
        aum_billions = profile.aum / 1_000_000_000

        return f"""
{profile.full_name} ({lp_name})
- Country: {profile.country}
- AUM: ${aum_billions:.1f}B
- PE Allocation: {profile.pe_allocation_pct}%
- Focus Regions: {', '.join(profile.focus_regions)}
- Korea Interest: {profile.korea_interest}
- Website: {profile.website}
        """.strip()
