class Options:
    def __init__(self, optional_callback=None, return_job_status=False, return_history=False, return_images=False):
        self.options = {
            "return_job_status": return_job_status,
            "return_history": return_history,
            "return_images": return_images,
        }
        if optional_callback is not None:
            self.options["optional_callback"] = optional_callback

    def add(self, key, value):
        if self.options is None:
            self.options = {
                key: value
            }
        else:
            self.options[key] = value

    def get(self, key):
        if key in self.options:
            return None
        else:
            return self.options[key]

    def get_params(self):
        return self.options
