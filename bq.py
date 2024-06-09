import json
from loguru import logger

from util.models import Tabs, Tab, ItemQuest, StandardTask, CheckBoxTask, HuntTask, LocationTask, LoggerData
from util.optional import get_hash
from settings.config import Config

logger.remove(0)
logger.add(Config.LOG_FILE_PATH, format="{time:MMMM-D-YYYY HH:mm:ss} | {level} | {message}", retention="5 minute")


class BetterQuestingParser:
    current_tab_info: LoggerData = None
    current_quest_info: LoggerData = None

    @staticmethod
    def tasks_loger(task_type: str):
        def hunt_tasks_loger(mob: str):
            if mob.isalpha():
                logger.success(f"Hunt-"
                               f"{BetterQuestingParser.current_tab_info.uid}-"
                               f"{BetterQuestingParser.current_tab_info.name}-"
                               f"{BetterQuestingParser.current_quest_info.uid}-"
                               f"{BetterQuestingParser.current_quest_info.name}-"
                               f"minecraft:{mob.lower()}")
            else:
                logger.error(f"Hunt-"
                             f"{BetterQuestingParser.current_tab_info.uid}-"
                             f"{BetterQuestingParser.current_tab_info.name}-"
                             f"{BetterQuestingParser.current_quest_info.uid}-"
                             f"{BetterQuestingParser.current_quest_info.name}-"
                             f"{mob}")

        def location_tasks_loger(dimension_id: str, dimension_name: str):
            logger.error(f"Location-"
                         f"{BetterQuestingParser.current_tab_info.uid}-"
                         f"{BetterQuestingParser.current_tab_info.name}-"
                         f"{BetterQuestingParser.current_quest_info.uid}-"
                         f"{BetterQuestingParser.current_quest_info.name}-"
                         f"{dimension_id}-"
                         f"{dimension_name}")

        def outer(function):
            def inner(*args, **kwargs):
                if task_type == "hunt":
                    hunt_tasks_loger(args[0]["target:8"])
                if task_type == "location":
                    location_tasks_loger(args[0]["dimension:3"], args[0]["name:8"])

                return function(*args, **kwargs)
            return inner
        return outer

    def get_tabs(self) -> Tabs:
        tabs = Tabs(tabs=[])
        with open(Config.BETTER_QUESTING_JSON_PATH, "r", encoding="utf8") as json_file:
            bq_json = json.load(json_file)
            bq_tabs = bq_json["questLines:9"]
            bq_quests = bq_json["questDatabase:9"]

            for tab_key in bq_tabs:
                tab_uid = get_hash()
                tab_name = bq_tabs[tab_key]["properties:10"]["betterquesting:10"]["name:8"]
                BetterQuestingParser.current_tab_info = LoggerData(uid=tab_uid, name=tab_name)

                tabs.tabs.append(
                    Tab(
                        uid=tab_uid,
                        name=tab_name,
                        description=desc if (
                            desc := bq_tabs[tab_key]["properties:10"]["betterquesting:10"]["desc:8"]) else "",
                        quests=self.get_quests(bq_tabs, bq_quests, tab_key)
                    )
                )
        return tabs

    def get_quests(self, bq_tabs: dict, bq_quests: dict, tab_key: str) -> list[ItemQuest]:
        quests = []
        for quest_key in bq_tabs[tab_key]["quests:9"]:
            x = bq_tabs[tab_key]["quests:9"][quest_key]["x:3"]
            y = bq_tabs[tab_key]["quests:9"][quest_key]["y:3"]
            quest_id = bq_tabs[tab_key]["quests:9"][quest_key]["id:3"]

            quests.append(self.get_quest(bq_quests, x, y, quest_id))

        return quests

    def get_quest(self, bq_quests: dict, x: float, y: float, quest_id: int) -> ItemQuest:
        for quest_key in bq_quests:
            if bq_quests[quest_key]["questID:3"] == quest_id:
                quest_uid = get_hash()
                quest_name = bq_quests[quest_key]["properties:10"]["betterquesting:10"]["name:8"]
                BetterQuestingParser.current_quest_info = LoggerData(uid=quest_uid, name=quest_name)

                return ItemQuest(
                    uid=quest_uid,
                    id=quest_id,
                    name=quest_name,
                    icon=bq_quests[quest_key]["properties:10"]["betterquesting:10"]["icon:10"]["id:8"],
                    hide_dependency_lines=True if bq_quests[quest_key].get("preRequisiteTypes:7") and Config.PARSE_HIDDEN_LINES else False,
                    text=bq_quests[quest_key]["properties:10"]["betterquesting:10"]["desc:8"],
                    x=x,
                    y=y,
                    dependencies=dependencies if (dependencies := bq_quests[quest_key]["preRequisites:11"]) else [],
                    tasks=self.get_tasks(bq_quests[quest_key]["tasks:9"])
                )

    def get_tasks(self, bq_tasks: dict) -> list[StandardTask | CheckBoxTask | HuntTask | LocationTask]:
        tasks = []
        for task_key in bq_tasks:
            if (task_type := bq_tasks[task_key]["taskID:8"].split(":")[1]) == "checkbox":
                tasks.append(CheckBoxTask(uid=get_hash(), type="checkbox"))
            if task_type == "hunt":
                tasks.append(self.generate_hunt_task(bq_tasks[task_key]))
            if task_type == "location":
                tasks.append(self.generate_location_task(bq_tasks[task_key]))
            if task_type == "retrieval":
                tasks.extend(self.generate_retrieval_tasks(bq_tasks[task_key]))
            if task_type in "optional_retrieval" and Config.PARSE_RETRIEVAL_TASKS:
                tasks.extend(self.generate_retrieval_tasks(bq_tasks[task_key]))

        return tasks

    @staticmethod
    @tasks_loger("hunt")
    def generate_hunt_task(task: dict) -> HuntTask:
        return HuntTask(
            uid=get_hash(),
            type="hunt",
            entity=f"minecraft:{mob.lower()}" if (mob := task["target:8"]).isalpha() else mob,
            count=task["required:3"]
        )

    @staticmethod
    @tasks_loger("location")
    def generate_location_task(task: dict) -> LocationTask:
        return LocationTask(
            uid=get_hash(),
            type="location",
            dimension=task["dimension:3"],
            dimension_name=task["name:8"],
            x=task["posX:3"],
            y=task["posY:3"],
            z=task["posZ:3"],
        )

    @staticmethod
    def generate_retrieval_tasks(task: dict) -> list[StandardTask]:
        return [
            StandardTask(
                uid=get_hash(),
                type="retrieval",
                icon=task["requiredItems:9"][item_key]["id:8"],
                item=task["requiredItems:9"][item_key]["id:8"],
                count=task["requiredItems:9"][item_key]["Count:3"],
                consume_items=True if task["consume:1"] else False,
                ignore_nbt=True if task["ignoreNBT:1"] else False
            ) for item_key in task["requiredItems:9"]
        ]


if __name__ == "__main__":
    BetterQuestingParser().get_tabs()
