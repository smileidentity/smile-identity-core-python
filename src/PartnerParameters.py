class PartnerParameters:
    def __init__(self, user_id, job_id, job_type):
        if not user_id or not job_id or not job_type:
            raise ValueError("Partner Parameter Arguments may not be null or empty")

        self.partner_params = {
            "user_id": user_id,
            "job_id": job_id,
            "job_type": job_type,
        }

    def add(self, key, value):
        if self.partner_params is None:
            self.partner_params = {
                key: value
            }
        else:
            self.partner_params[key] = value

    def get(self, key):
        if key in self.partner_params:
            return self.partner_params[key]
        else:
            None

    def get_params(self):
        return self.partner_params
