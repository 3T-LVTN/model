from app.adapter.file_service.file_service_adapter import file_service
from app.internal.util.file_util.csv_reader import


def daily_sync_data_from_file_service():
    list_file = file_service.get_list_file()
