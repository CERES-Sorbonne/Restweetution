from typing import TYPE_CHECKING

# allows us to get type hinting without creating circular imports at runtime
if TYPE_CHECKING:
    from restweetution.models.linked.linked_bulk_data import LinkedBulkData


class Linked:
    def __init__(self, data):
        self.data: LinkedBulkData = data
