from dataclasses import dataclass, field
from dataclasses import asdict, replace


@dataclass
class Address:
    street: str = None
    city: str = None
    state: str = None
    zipcode: str = None


@dataclass
class Person:
    name: str = None
    age: int = None
    address: Address = field(default_factory=Address)
    phone: str = None


@dataclass
class Employee:
    id: str = None
    person: Person = field(default_factory=Person)
    salary: float = None
    department: str = None


employee_data = {
    "id": "E001",
    "person": {
        "name": "John Smith",
        "age": 30,
        "address": {
            "street": "1st Ave",
            "city": "NY",
            "state": "New York",
            "zipcode": "10001"
        },
        "phone": "555-555-5555"
    },
    "salary": 50000.0,
    "department": "IT"
}

employee = replace(Employee(), **employee_data)
print(employee)
