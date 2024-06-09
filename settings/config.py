import configparser
import os


def parse_bool_parameter(parameter: str) -> bool:
    return True if parameter == "True" else False


class Config:
    config = configparser.ConfigParser()
    config.read(os.path.dirname(__file__) + "/config.ini")

    FTB_QUESTS_DIR = config["Paths"]["ftb_quests_directory"]
    BETTER_QUESTING_JSON_PATH = config["Paths"]["better_questing_json_path"]
    LOG_FILE_PATH = config["Paths"]["log_file_path"]

    PARSE_RETRIEVAL_TASKS = parse_bool_parameter(config["BQ parsing rules"]["parse_optional_tasks_as_retrieval"])
    PARSE_HIDDEN_LINES = parse_bool_parameter(config["BQ parsing rules"]["parse_quest_lines_as_hidden"])

    LINE_LENGTH_MODIFIER = int(config["FTB settings"]["dependencies_lines_length_modifier"])
    QUEST_SIZE = int(config["FTB settings"]["quest_size"])
    SAFETY_UPLOADING = parse_bool_parameter(config["FTB settings"]["safety_uploading"])
