class Scooter:
    def __init__(
        self,
        brand: str,
        model: str,
        serial_number: str,
        top_speed: float,
        battery_capacity: float,
        state_of_charge: float,
        target_range_soc: tuple,
        location: tuple,
        out_of_service: bool,
        mileage: float,
        last_maintenance_date: str,
    ):
        self.brand = brand
        self.model = model
        self.serial_number = serial_number
        self.top_speed = top_speed  # in km/h
        self.battery_capacity = battery_capacity  # in Wh
        self.state_of_charge = state_of_charge  # percentage (0-100)
        self.target_range_soc = target_range_soc  # (min%, max%) tuple
        self.location = location  # (latitude, longitude) tuple, 5 decimal places
        self.out_of_service = out_of_service
        self.mileage = mileage  # in km
        self.last_maintenance_date = last_maintenance_date  # ISO 8601: YYYY-MM-DD

    def __repr__(self):
        return (
            f"Scooter(brand={self.brand!r}, "
            f"model={self.model!r}, "
            f"serial_number={self.serial_number!r}, "
            f"top_speed={self.top_speed!r}, "
            f"battery_capacity={self.battery_capacity!r}, "
            f"state_of_charge={self.state_of_charge!r}, "
            f"target_range_soc={self.target_range_soc!r}, "
            f"location={self.location!r}, "
            f"out_of_service={self.out_of_service!r}, "
            f"mileage={self.mileage!r}, "
            f"last_maintenance_date={self.last_maintenance_date!r})"
        )