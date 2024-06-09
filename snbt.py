import snbtlib
import os

from util.models import ItemQuest, StandardTask, CheckBoxTask, HuntTask, LocationTask
from settings.config import Config


class SnbtManager:

    def get_quest(self, quest: ItemQuest, dependencies: list[str] | list) -> str:
        return '{\n' \
               f'\t title: "{self.replace_symbols(quest.name)}",\n' \
               f'\t icon: "{self.replace_symbols(quest.icon)}",\n' \
               f'\t x: {quest.x // Config.LINE_LENGTH_MODIFIER}d,\n' \
               f'\t y: {quest.y // Config.LINE_LENGTH_MODIFIER}d,\n' \
               f'\t description: "{self.replace_symbols(quest.name)}",\n' \
               '\t text: [\n' \
               f'\t\t "{self.replace_symbols(quest.text)}"\n' \
               '\t ],\n' \
               f'\t dependencies: {snbtlib.dumps(dependencies, compact=True)},\n' \
               f'\t hide_dependency_lines: {quest.hide_dependency_lines},\n' \
               f'\t size: {Config.QUEST_SIZE}d,\n' \
               f'\t tasks: {self.get_tasks(quest.tasks, quest.uid)}' \
               '}'

    def get_tab(self, tab_name: str) -> str:
        return '{\n' \
               f'\t title: "{self.replace_symbols(tab_name)}",\n' \
               '\t always_invisible: False,\n' \
               '\t default_quest_shape: ""\n' \
               '}'

    def get_index(self, tabs: list[str]) -> str:
        try:
            with open(Config.FTB_QUESTS_DIR + "\index.snbt", "r") as file:
                index_file = snbtlib.loads(file.read())
                if index_file:
                    return snbtlib.dumps(self.create_index(index_file, tabs), compact=True)
                else:
                    return snbtlib.dumps({"index": tabs}, compact=True)

        except FileNotFoundError:
            print(f"File {Config.FTB_QUESTS_DIR}/index.snbt doesn't exists. Clear ftb chapters directory and create"
                  f"an empty index.snbt file in it. Then, restart the program")

    @staticmethod
    def create_index(index_file: dict, tabs: list[str]) -> dict:
        if Config.SAFETY_UPLOADING:
            index_file["index"].extend(tabs)
        else:
            index_file["index"] = tabs
        return index_file

    def get_tasks(self, tasks: list[StandardTask | CheckBoxTask | HuntTask | LocationTask], quest_uid: str) -> str:
        a = ""
        for task in tasks:
            if task.type == "checkbox":
                a += self.get_checkbox_task(task)
            elif task.type == "retrieval":
                a += self.get_standard_task(task)
            elif task.type == "hunt":
                a += self.get_hunt_task(task)
            elif task.type == "location":
                a += self.get_location_task(task)

        return f'[{a[:-2]}\n]'

    @staticmethod
    def get_checkbox_task(task: CheckBoxTask) -> str:
        return '\t{\n' \
               f'\t\t uid: "{task.uid}",\n' \
               '\t\t type: "checkmark"\n' \
               '\t},\n'

    @staticmethod
    def get_standard_task(task: StandardTask) -> str:
        return '\t{\n' \
               f'\t\t uid: "{task.uid}",\n' \
               '\t\t type: "item",\n' \
               f'\t\t icon: "{task.icon}",\n' \
               f'\t\t item: "{task.item}",\n' \
               f'\t\t count: {task.count}L,\n' \
               f'\t\t consume_items: {task.consume_items},\n' \
               f'\t\t ignore_nbt: {task.ignore_nbt}\n' \
               '\t},\n'

    @staticmethod
    def get_hunt_task(task: HuntTask) -> str:
        return '\t{\n' \
               f'\t\t uid: "{task.uid}",\n' \
               '\t\t type: "kill",\n' \
               f'\t\t entity: "{task.entity}",\n' \
               f'\t\t value: {task.count}L\n' \
               '\t},\n'

    @staticmethod
    def get_location_task(task: LocationTask) -> str:
        return '\t{\n' \
               f'\t\t uid: "{task.uid}",\n' \
               f'\t\t title: "{task.dimension_name}",\n' \
               '\t\t type: "location",\n' \
               f'\t\t location: [I;\n' \
               f'\t\t\t {task.dimension},\n' \
               f'\t\t\t {task.x},\n' \
               f'\t\t\t {task.y},\n' \
               f'\t\t\t {task.z},\n' \
               f'\t\t\t 1,\n' \
               f'\t\t\t 1,\n' \
               f'\t\t\t 1\n' \
               '\t\t]\n' \
               '\t},\n'

    @staticmethod
    def replace_symbols(text: str | None) -> str:
        if not text:
            return ""
        text = text.replace('\"', ' ').replace('"', ' ')
        return " ".join(text.split()).replace("\\", " ")
