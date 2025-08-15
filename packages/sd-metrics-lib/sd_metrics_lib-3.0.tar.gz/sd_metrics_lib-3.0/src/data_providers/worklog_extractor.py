from abc import ABC, abstractmethod
from typing import Dict


class WorklogExtractor(ABC):

    @abstractmethod
    def get_work_time_per_user(self, task) -> Dict[str, int]:
        pass


class TaskTotalSpentTimeExtractor(ABC):

    @abstractmethod
    def get_total_spent_time(self, task) -> int:
        pass


class ChainedWorklogExtractor(WorklogExtractor):

    def __init__(self, worklog_extractor_list: list[WorklogExtractor]) -> None:
        self.worklog_extractor_list = worklog_extractor_list

    def get_work_time_per_user(self, task):
        for worklog_extractor in self.worklog_extractor_list:
            work_time = worklog_extractor.get_work_time_per_user(task)
            if work_time is not None and len(work_time.keys()) != 0:
                return work_time
        return {}
