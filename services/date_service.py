from datetime import datetime


class DateService:
    @staticmethod
    def from_timestamp(timestamp):
        return datetime.fromtimestamp(timestamp)
