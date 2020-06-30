import json


class IDParameters:

    def __init__(self, first_name, middle_name, last_name, country, id_type, id_number, dob, phone_number, entered):

        required_fields = IDParameters.get_required_params()

        if entered:
            for field in required_fields:
                if field is None:
                    raise Exception(field + " cannot be empty")

        self.id_info = {
            "first_name": first_name,
            "middle_name": middle_name,
            "last_name": last_name,
            "country": country,
            "id_type": id_type,
            "id_number": id_number,
            "dob": dob,
            "phone_number": phone_number,
            "entered": entered,
        }

    @staticmethod
    def get_required_params():
        return ["country", "id_type", "id_number"]

    def add(self, key, value):
        if self.id_info is None:
            self.id_info = {
                key: value
            }
        else:
            self.id_info[key] = value

    def get(self, key):
        if key in self.id_info:
            return None
        else:
            return self.id_info[key]

    def get_params(self):
        return self.id_info
