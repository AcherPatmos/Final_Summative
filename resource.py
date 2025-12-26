class Resource:
    def __init__(self, resource_id: str, name: str, rtype: str, quantity: int):
        self.resource_id = resource_id.strip()
        self.name = name.strip()
        self.type = rtype.strip()
        self.quantity = int(quantity)

    def is_available(self) -> bool:
        return self.quantity > 0

    def borrow_one(self) -> bool:
        if self.quantity <= 0:
            return False
        self.quantity -= 1
        return True

    def return_one(self) -> None:
        self.quantity += 1

    def to_dict(self) -> dict:
        return {
            "resource_id": self.resource_id,
            "name": self.name,
            "type": self.type,
            "quantity": self.quantity
        }

    @staticmethod
    def from_dict(data: dict) -> "Resource":
        return Resource(
            data["resource_id"],
            data["name"],
            data["type"],
            data["quantity"]
        )
