class Resource:
    def __init__(self, resource_id: str, name: str, rtype: str, quantity: int):
        if not resource_id.strip():
            raise ValueError("resource_id cannot be empty")
        if not name.strip():
            raise ValueError("name cannot be empty")
        if not rtype.strip():
            raise ValueError("rtype cannot be empty")
        if not isinstance(quantity, int) or quantity < 0:
            raise ValueError("quantity must be an integer >= 0")

        self.resource_id = resource_id.strip()
        self.name = name.strip()
        self.rtype = rtype.strip()
        self.quantity = quantity

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
            "type": self.rtype,
            "quantity": self.quantity
        }

    @staticmethod
    def from_dict(data: dict) -> "Resource":
        return Resource(
            resource_id=data["resource_id"],
            name=data["name"],
            rtype=data.get("type", ""),
            quantity=int(data["quantity"])
        )
