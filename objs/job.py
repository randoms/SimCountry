
job_id = 0

class Job:

    def __init__(self, country, name="contruction", money=1):
        global job_id
        self.country = country
        self.name = name
        self.money = money
        self.id = job_id
        job_id += 1
        self.worker = None
