import random
from objs.country import Country
from objs.person import Person


world_id = 0


class World:

    def __init__(self, name=""):
        global world_id
        self.id = world_id
        world_id += 1
        self.countrys = []
        self.persons = []
        self.jobs = []
        self.time = 0
        self.name = name

    def play(self):
        self.jobs = []
        # 城市发布任务
        for country in self.countrys:
            self.jobs += country.publish_jobs()

        # 随机工人顺序
        person_order = list(range(0, len(self.persons)))
        person_list = []
        while len(person_order) > 0:
            index = random.randint(0, len(person_order) - 1)
            person_list.append(self.persons[person_order[index]])
            person_order.remove(person_order[index])

        # 工人选择任务
        for person in person_list:
            job = person.choose_job(self.jobs)
            if job is None:
                print("{person.name} 没有获取到任务".format(person=person))
                choosed_country = person.choose_country()
                if choosed_country == person.country:
                    print("{person.name} 决定还是呆在 {country.name}".format(
                        person=person, country=choosed_country))
                    continue
                print("想要移动到{country.name}, 面积{country.area},人口{num}".format(country=choosed_country,num=len(choosed_country.citizens)))
                if choosed_country.area > len(choosed_country.citizens):
                    # 本城市尚有空间
                    choosed_country.add_person(person)
                    print("{person.name} 移动到了城市 {country.name}".format(
                        person=person, country=choosed_country))
                continue
            # 分配此任务
            if job.country.area <= len(job.country.citizens):
                continue
            job.country.assign_job(job, person)
            print("**")
            print("{person.name} 获取了 {country.name} 发布的任务 工资{job.money} 税收 ${country.tex}".format(
                person=person, country=job.country, job=job))

            # 删除任务
            self.jobs.remove(job)

        # 城市向工人收税
        for country in self.countrys:
            country.get_tex()

        # 根据工作增加城市面积
        for country in self.countrys:
            country.update_area()

        # 开始世界损耗
        # 每回合损耗1单位面积
        for country in self.countrys:
            country.area -= 2

        # 进行生命损耗，金钱为零生命降1
        for person in list(self.persons):
            person.update_health()
            if person.health == 0:
                self.remove_person(person)
                print("{person.name} 穷死了 ...".format(person=person))

        self.time += 1

        self.report()

        # 进行判定
        for country in self.countrys:
            if country.area <= 0:
                print("城镇 {country.name} 面积为零, 城镇死亡".format(country=country))
                self.remove_country(country)
        if len(self.countrys) == 0:
            print("所有国家都已灭亡，{name} 已经毁灭".format(name=self.name))
            exit(0)
                

    def report(self):
        print("时间: {time}".format(time=self.time))
        print("世界国家汇总: ")
        total_money = 0
        print("人口汇总： ")
        for person in self.persons:
            print("##")
            if person.country is not None:
                print("姓名: {person.name}, 金钱 {person.money}, 城市 {person.country.name}".format(
                    person=person))
            else:
                print("姓名: {person.name}, 金钱 {person.money}, 城市 无".format(
                    person=person))
            total_money += person.money
        for country in self.countrys:
            print("##")
            print("国家名称: {country.name}, 人口: {num}, 面积: {country.area}, 金钱: {country.money} 税收: {country.tex}".format(
                country=country, num=len(country.citizens)))
            total_money += country.money
        print("#######")
        print("世界总金钱: ${total_money}".format(total_money=total_money))

    def create_country(self, name, area=10, money=10, tex=1, manual=False):
        new_country = Country(self, name, area=area,
                              money=10, tex=1, manual=manual)
        self.countrys.append(new_country)
        return new_country

    def create_person(self, country, name="", money=10):
        new_person = Person(country, name, money)
        country.add_person(new_person)
        self.persons.append(new_person)
        return new_person

    def remove_person(self, person):
        self.persons.remove(person)
        for country in self.countrys:
            country.remove_person(person)

    def remove_country(self, country):
        for person in country.citizens:
            person.country = None
        self.countrys.remove(country)
