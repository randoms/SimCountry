
person_id = 0


class Person:

    def __init__(self, country, name="", money=10):
        global person_id
        self.name = name
        self.country = country
        self.money = money
        self.id = person_id
        if name == "":
            self.name = str(self.id)
        self.world = country.world
        person_id += 1
        self.health = 3

    def choose_job(self, jobs):
        # 找性价比最高的工作
        current_job = None
        choosed_country = self.choose_country()
        for job in jobs:
            if job.country.area <= len(job.country.citizens) and self.country != job.country:
                # 城市已经满了
                continue
            print("job.money - job.country.tex " +
                  str(job.money - job.country.tex))
            print("choosed_country.tex " + str(choosed_country.tex))
            if current_job is None and job.money - job.country.tex > - choosed_country.tex:
                current_job = job
            elif current_job is not None and job.money - job.country.tex > -choosed_country.tex and\
                    job.money - job.country.tex > current_job.money - current_job.country.tex:
                current_job = job

        return current_job

    def choose_country(self):
        current_country = self.country
        for country in self.world.countrys:
            if current_country is None:
                current_country = country
            if current_country.tex > country.tex:
                current_country = country
        return current_country

    def update_health(self):
        if self.money == 0:
            self.health -= 1
        if self.money > 10:
            self.health += (self.money - 10) / 2
        if self.health < 0:
            self.health = 0
