
import random
import json
from objs.job import Job
import time

count_id = 0
country_names = ["洛丹伦", "卡利姆多", "潘达利亚", "桃花岛", "白驼山", "青城派", "少林寺", "武当山"]


class Country:

    def __init__(self, world, name="", area=10, money=10, tex=1, manual=False, client=None):
        global count_id, country_names
        self.name = name  # 城市名称
        self.area = area  # 城市初始面积
        self.money = money  # 城市初始金钱
        self.tex = tex  # 城市初始税率
        self.world = world
        self.jobs = []
        self.history = []
        self.citizens = []
        self.id = count_id
        self.manual = manual
        self.client = client
        if name == "":
            if self.id < len(country_names):
                self.name = country_names[self.id]
            else:
                self.name = str(self.id)
        count_id += 1
        self.new_area = 0  # 根据工作需要增加的面积

    def publish_jobs(self):
        if self.world.room is not None:
            self.world.room.broadcast("turn", {
                "country": self.id,
            })
        if self.manual:
            return self.publish_jobs_manual()
        # 随机生成任务
        new_jobs = []
        total_pay = random.randint(0, self.money)
        remain_money = total_pay
        while remain_money > 0:
            job_pay = random.randint(0, remain_money)
            print("job_pay " + str(job_pay))
            if self.world.room is not None:
                self.world.room.broadcast("system", {
                    "info": "job_pay " + str(job_pay),
                })
            new_jobs.append(Job(self, money=job_pay))
            remain_money -= job_pay
        self.jobs = new_jobs
        # 随机赋税
        self.tex = random.randint(0, 5)
        print("{country.name}发布了{num}个任务,总支出{total_pay},税收 {tex}".format(
            country=self, num=len(new_jobs), total_pay=total_pay, tex=self.tex))
        if self.world.room is not None:
            self.world.room.broadcast("system", {
                "info": "{country.name}发布了{num}个任务,总支出{total_pay},税收 {tex}".format(
                    country=self, num=len(new_jobs), total_pay=total_pay, tex=self.tex),
            })
        return new_jobs

    def publish_jobs_manual(self):
        self.jobs = []
        while True:
            new_jobs = []
            print("当前城镇 {country.name}, 金钱: {country.money}, 人口: {num}, 面积: {country.area}".format(
                country=self, num=len(self.citizens)))
            print("{country.name} tex: ".format(country=self))
            if self.world.room is not None:
                self.world.room.broadcast("system", {
                    "info": "当前城镇 {country.name}, 金钱: {country.money}, 人口: {num}, 面积: {country.area}".format(
                        country=self, num=len(self.citizens)),
                })
                self.world.room.broadcast("system", {
                    "info": "等待 {country.name} 输入税收税收: ".format(country=self),
                })

            try:
                if self.client is None:
                    self.tex = (int)(input())
                else:
                    self.req_rec_flag = False
                    self.rec_tex = None
                    def process_tex(tex_msg):
                        self.rec_tex = tex_msg["tex"]
                        self.req_rec_flag = True
                    self.client.send_request({
                        "url": "set_tex",
                    }, process_tex)
                    while not self.req_rec_flag:
                        time.sleep(0.1)
                    self.tex = (int)(self.rec_tex)
            except Exception:
                print("无效税收数据")
                self.world.room.broadcast("system", {
                    "error": "无效税收数据",
                })
                continue
            
            self.world.room.broadcast("system", {
                "info": "{country.name} 税收: {country.tex}".format(country=self),
            })
            print("{country.name} jobs: ".format(country=self))
            self.world.room.broadcast("system", {
                "info": "{country.name} jobs: ".format(country=self),
            })
            total_pay = 0
            if self.client is None:
                for pay in input().split(" "):
                    if len(pay) == 0:
                        continue
                    new_jobs.append(Job(self, money=(int)(pay)))
                    total_pay += (int)(pay)
            else:
                self.req_rec_flag = False
                self.rec_job = None

                def process_job(job_msg):
                    self.rec_job = job_msg["jobs"]
                    self.req_rec_flag = True
                self.client.send_request({
                    "url": "set_jobs",
                }, process_job)
                while not self.req_rec_flag:
                    time.sleep(0.1)
                for pay in self.rec_job.split(" "):
                    if len(pay) == 0:
                        continue
                    new_jobs.append(Job(self, money=(int)(pay)))
                    total_pay += (int)(pay)
            if total_pay > self.money:
                print("预算不足，预算 {total_pay} 剩余金钱 {country.money}".format(
                    total_pay=total_pay, country=self))
                self.world.room.broadcast("system", {
                    "error": "预算不足，预算 {total_pay} 剩余金钱 {country.money}".format(
                        total_pay=total_pay, country=self),
                })
            else:
                break
        self.jobs = new_jobs
        return new_jobs

    def assign_job(self, job, person):
        person.job = job
        if self.money < job.money:
            return False
        self.money -= job.money
        person.money += job.money
        self.add_person(person)
        self.new_area += 1

    def get_tex(self):
        # 向居民收税
        for person in self.citizens:
            if person.money < self.tex:
                # 居民钱不够,则交其所有的钱
                self.money += person.money
                person.money = 0
            else:
                person.money -= self.tex
                self.money += self.tex

    def add_person(self, person):
        if person in self.citizens:
            return
        else:
            # 从之前城市离开
            if person.country != self and person.country is not None:
                person.country.remove_person(person)
            # 加入当前城市
            self.citizens.append(person)
            person.country = self

    def remove_person(self, person):
        if person not in self.citizens:
            return
        else:
            self.citizens.remove(person)
            person.country = None

    def update_area(self):
        self.area += self.new_area
        self.new_area = 0

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "area": self.area,
            "money": self.money,
            "tex": self.tex,
            "jobs": [job.to_json() for job in self.jobs],
            "citizens": [person.to_json() for person in self.citizens]
        }
