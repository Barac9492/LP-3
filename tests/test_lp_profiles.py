"""
Tests for LP profile manager
"""
import pytest
from pathlib import Path

from src.collectors.lp_profiles import LPProfileManager


class TestLPProfileManager:
    """Test LP profile manager"""

    @pytest.fixture
    def manager(self):
        """Create LP profile manager instance"""
        return LPProfileManager()

    def test_load_profiles(self, manager):
        """Test loading LP profiles"""
        assert len(manager.profiles) > 0
        assert 'GIC' in manager.profiles
        assert 'CalPERS' in manager.profiles

    def test_get_profile(self, manager):
        """Test getting a specific profile"""
        gic = manager.get_profile('GIC')

        assert gic.name == 'GIC'
        assert gic.full_name == 'GIC Private Limited'
        assert gic.country == 'Singapore'
        assert gic.korea_interest == 'high'

    def test_get_profile_not_found(self, manager):
        """Test getting non-existent profile"""
        with pytest.raises(ValueError):
            manager.get_profile('NonExistentLP')

    def test_get_all_profiles(self, manager):
        """Test getting all profiles"""
        all_profiles = manager.get_all_profiles()

        assert isinstance(all_profiles, dict)
        assert len(all_profiles) > 0

    def test_get_lp_names(self, manager):
        """Test getting LP names list"""
        names = manager.get_lp_names()

        assert isinstance(names, list)
        assert 'GIC' in names
        assert 'Temasek' in names

    def test_get_tier1_lps(self, manager):
        """Test getting tier 1 LPs"""
        tier1 = ['GIC', 'Temasek', 'CalPERS', 'CPPIB']
        result = manager.get_tier1_lps(tier1)

        assert isinstance(result, list)
        assert all(lp in manager.profiles for lp in result)

    def test_get_high_korea_interest_lps(self, manager):
        """Test getting high Korea interest LPs"""
        high_interest = manager.get_high_korea_interest_lps()

        assert isinstance(high_interest, list)
        assert 'GIC' in high_interest
        assert 'Temasek' in high_interest
        assert 'NPS' in high_interest

    def test_get_search_keywords(self, manager):
        """Test getting search keywords for LP"""
        keywords = manager.get_search_keywords('GIC')

        assert isinstance(keywords, list)
        assert len(keywords) > 0

    def test_get_profile_summary(self, manager):
        """Test getting profile summary"""
        summary = manager.get_profile_summary('GIC')

        assert isinstance(summary, str)
        assert 'GIC' in summary
        assert 'Singapore' in summary
