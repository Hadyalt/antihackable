from DbContext.crypto_utils import encrypt, decrypt


class Traveller:
    def __init__(
        self,
        first_name: str,
        last_name: str,
        birthday: str,
        gender: str,
        street_name: str,
        house_number: str,
        zip_code: str,
        city: str,
        email_address: str,
        mobile_phone: str,
        driving_license_number: str,
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.birthday = birthday
        self.gender = gender
        self.street_name = street_name
        self.house_number = house_number
        self.zip_code = zip_code
        self.city = city
        self.email_address = email_address
        self.mobile_phone = mobile_phone
        self.driving_license_number = driving_license_number

    def encrypt_fields(self):
        self.first_name = encrypt(self.first_name)
        self.last_name = encrypt(self.last_name)
        self.street_name = encrypt(self.street_name)
        self.house_number = encrypt(self.house_number)
        self.zip_code = encrypt(self.zip_code)
        self.city = encrypt(self.city)
        self.email_address = encrypt(self.email_address)
        self.mobile_phone = encrypt(self.mobile_phone)
        self.driving_license_number = encrypt(self.driving_license_number)

    def decrypt_fields(self):
        self.first_name = decrypt(self.first_name)
        self.last_name = decrypt(self.last_name)
        self.street_name = decrypt(self.street_name)
        self.house_number = decrypt(self.house_number)
        self.zip_code = decrypt(self.zip_code)
        self.city = decrypt(self.city)
        self.email_address = decrypt(self.email_address)
        self.mobile_phone = decrypt(self.mobile_phone)
        self.driving_license_number = decrypt(self.driving_license_number)

    def __repr__(self):
        return (
            f"Traveller(first_name={self.first_name!r}, "
            f"last_name={self.last_name!r}, "
            f"birthday={self.birthday!r}, "
            f"gender={self.gender!r}, "
            f"street_name={self.street_name!r}, "
            f"house_number={self.house_number!r}, "
            f"zip_code={self.zip_code!r}, "
            f"city={self.city!r}, "
            f"email_address={self.email_address!r}, "
            f"mobile_phone={self.mobile_phone!r}, "
            f"driving_license_number={self.driving_license_number!r})"
        )