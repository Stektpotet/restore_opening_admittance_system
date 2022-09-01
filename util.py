import csv
from typing import List, Dict, Any, TypeVar, Type

from form_data import Person

T = TypeVar('T')


def read_csv(entry_type: Type[T], file_path: str, table_specification: Dict[str, int]) -> List[T]:
    with open(file_path, encoding="utf-8") as registration_file:
        table_reader = csv.reader(registration_file)
        headers = next(table_reader)

        # find index of first empty header
        try:
            first_empty_header = headers.index('')
        except ValueError:
            first_empty_header = len(headers)

        for out_of_bounds, key, index in ((i >= first_empty_header, k, i) for k, i in table_specification.items()):
            if out_of_bounds:
                raise ValueError(f"table specification has a column index that is out of bounds: {key}: {index}")

        return [entry_type(**{k: row[v] for k, v in table_specification.items()}) for row in table_reader]


        # return [read_entry(*row) for row in reader]

