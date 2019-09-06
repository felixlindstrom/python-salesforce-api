import io
import csv
from typing import List
from .. import exceptions


class FilePreparer:
    def __init__(self, entries: List[dict]):
        self.entries = entries

    def _has_entries(self) -> bool:
        return len(self.entries) > 0

    def _check_headers(self) -> bool:
        headers = [':'.join(x.keys()) for x in self.entries]
        headers = list(set(headers))
        return len(headers) == 1

    def _check_empty_rows(self) -> bool:
        for row in self.entries:
            if ''.join(str(x) for x in row.values() if x is not None).strip() == '':
                return False
        return True

    def get_csv_file(self) -> io.StringIO:
        if not self._has_entries():
            raise exceptions.NoEntriesError

        if not self._check_headers():
            raise exceptions.MultipleDifferentHeadersError('Multiple different data-structures found. Only supports one.')

        if not self._check_empty_rows():
            raise exceptions.BulkEmptyRowsError

        file_handle = io.StringIO()
        writer = csv.writer(file_handle, delimiter=',', lineterminator='\n')
        writer.writerow(self.entries[0].keys())
        writer.writerows([
            entry.values()
            for entry in self.entries
            if ''.join([str(x) for x in entry.values() if x is not None]) != ''
        ])
        return file_handle

    def get_csv_string(self) -> str:
        return self.get_csv_file().getvalue().strip()
