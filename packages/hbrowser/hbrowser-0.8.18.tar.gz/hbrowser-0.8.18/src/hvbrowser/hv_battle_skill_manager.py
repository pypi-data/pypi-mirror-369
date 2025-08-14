from collections import defaultdict

from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException,
    ElementNotInteractableException,
)
from selenium.webdriver.remote.webdriver import WebDriver

from .hv import HVDriver
from .hv_battle_action_manager import ElementActionManager
from .hv_battle_observer_pattern import BattleDashboard


class SkillManager:
    def __init__(
        self,
        driver: HVDriver,
        battle_dashboard: BattleDashboard,
    ) -> None:
        self.hvdriver = driver
        self.battle_dashboard = battle_dashboard
        self.element_action_manager = ElementActionManager(
            self.hvdriver, self.battle_dashboard
        )
        self._checked_skills: dict[str, str] = defaultdict(lambda: "available")
        self.skills_cost: dict[str, int] = defaultdict(lambda: 1)

    @property
    def driver(self) -> WebDriver:
        return self.hvdriver.driver

    def _get_skill_xpath(self, key: str) -> str:
        return f"//div[not(@style)]/div/div[contains(text(), '{key}')]"

    def _click_skill_menu(self):
        button = self.driver.find_element(By.ID, "ckey_skill")
        button.click()

    def open_skills_menu(self):
        if "display: none;" == self.driver.find_element(
            By.ID, "pane_skill"
        ).get_attribute("style"):
            self._click_skill_menu()
            self.open_skills_menu()

    def open_spells_menu(self):
        if "display: none;" == self.driver.find_element(
            By.ID, "pane_magic"
        ).get_attribute("style"):
            self._click_skill_menu()
            self.open_spells_menu()

    def _click_skill(self, skill_xpath: str, iswait: bool):
        element = self.driver.find_element(By.XPATH, skill_xpath)
        if iswait:
            self.element_action_manager.click_and_wait_log(element)
        else:
            self.element_action_manager.click(element)

    def cast(self, key: str, iswait=True) -> bool:
        # 先檢查技能狀態
        if key not in self._checked_skills:
            self.get_skill_status(key)

        if self._checked_skills[key] == "missing":
            return False

        self.skills_cost[key] = max(
            self.get_skill_mp_cost_by_name(key), self.skills_cost[key]
        )

        match self._checked_skills[key]:
            case "missing":
                return False
            case "unavailable":
                return False
            case "available":
                if key in self.battle_dashboard.character_skillbook.skills:
                    self.open_skills_menu()
                if key in self.battle_dashboard.character_skillbook.spells:
                    self.open_spells_menu()
                skill_xpath = self._get_skill_xpath(key)
                self._click_skill(skill_xpath, iswait)
                return True
            case _:
                raise ValueError(f"Unknown skill status: {self._checked_skills[key]}")

    def get_skill_status(self, key: str) -> str:
        """
        回傳 'missing'（未擁有）、'available'（可用）、'unavailable'（不可用）
        """

        self._checked_skills[key] = (
            self.battle_dashboard.character_skillbook.skills_and_spells[key].status
            if key in self.battle_dashboard.character_skillbook.skills_and_spells
            else "missing"
        )
        return self._checked_skills[key]

    def get_skill_mp_cost_by_name(self, skill_name: str) -> int:
        """
        根據技能名稱（如 'Haste' 或 'Weaken'）從 HTML 片段中找出對應的數值。
        """

        if self.get_skill_status(skill_name) == "missing":
            raise ValueError(f"Skill '{skill_name}' is missing.")

        self.skills_cost[skill_name] = max(
            self.battle_dashboard.character_skillbook.skills_and_spells[
                skill_name
            ].cost,
            self.skills_cost[skill_name],
        )
        return self.skills_cost[skill_name]
