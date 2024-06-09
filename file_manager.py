import os

from util.models import Tabs, ItemQuest
from util.exceptions import TabsNameCollisionException
from settings.config import Config

from snbt import SnbtManager
from bq import BetterQuestingParser


from pathlib import Path


class FileManager:
    tabs: Tabs = None
    tabs_uid: list[str] = None

    def convert(self):
        self.tabs_uid = []

        self.tabs = bq_parser.get_tabs()
        self.create_tabs_folders()
        self.update_index_snbt()

    def create_tabs_folders(self) -> None:
        for tab in self.tabs.tabs:
            path = f"{Config.FTB_QUESTS_DIR}/{tab.uid}"
            if os.path.exists(path):
                raise TabsNameCollisionException

            os.makedirs(path)
            self.create_tab_snbt(tab.name, tab.description, path)
            self.create_quests_snbt(tab.quests, path)
            self.tabs_uid.append(tab.uid)

    def create_quests_snbt(self, quests: list[ItemQuest], path):
        for quest in quests:
            quest_dependencies = dependencies if (dependencies := self.get_dependencies(quest.dependencies)) else []
            snbt_pattern = snbt.get_quest(quest, quest_dependencies)
            Path(path + f"/{quest.uid}.snbt").write_text(snbt_pattern, encoding='utf-8')

    def update_index_snbt(self) -> None:
        snbt_pattern = snbt.get_index(self.tabs_uid)
        Path(Config.FTB_QUESTS_DIR + "/index.snbt").write_text(snbt_pattern, encoding='utf-8')

    def get_dependencies(self, dependencies: list[int]) -> list[str]:
        return [quest.uid for tab in self.tabs.tabs for quest in tab.quests if quest.id in dependencies]

    @staticmethod
    def create_tab_snbt(tab_name: str, tab_desc: str, path: str) -> None:
        snbt_pattern = snbt.get_tab(tab_name)
        Path(path + f"/chapter.snbt").write_text(snbt_pattern, encoding='utf-8')


if __name__ == '__main__':
    try:

        snbt = SnbtManager()
        bq_parser = BetterQuestingParser()
        converter = FileManager()
        converter.convert()
    except TabsNameCollisionException:
        print("Tab names duplication!")
