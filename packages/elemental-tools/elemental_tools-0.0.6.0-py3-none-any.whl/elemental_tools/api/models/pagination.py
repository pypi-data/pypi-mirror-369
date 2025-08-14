from pydantic import BaseModel


class PaginationRequestModel(BaseModel):
    page_size: int = 50
    page_num: int = 1
    page_count: int = 0
    row_count: int = 0

    def get_page(self, cursor):
        _result = []
        try:
            cursor = list(cursor)

            start_index = (self.page_num - 1) * self.page_size
            end_index = start_index + self.page_size

            self.row_count = len(cursor)
            if self.row_count:
                self.page_count = int(-(-self.row_count // self.page_size))
                _result = cursor[start_index:end_index]

        except Exception as e:
            print(e)

        return _result

    def headers(self):
        _result = {}
        for key, value in self.model_dump().items():
            _result[key] = str(value)

        return _result