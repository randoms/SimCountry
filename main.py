from objs.world import World
from objs.person import Person
from objs.country import Country
import time

if __name__ == "__main__":
    atlas = World("艾泽拉斯")
    luodanlun = atlas.create_country("洛丹伦", area=15, money=10)
    kalimuduo = atlas.create_country("卡利姆多", area=15, money=10)
    pandaliya = atlas.create_country("潘达利亚", area=15, money=10, manual=True)
    for i in range(0, 10):
        atlas.create_person(luodanlun)
    for i in range(0, 10):
        atlas.create_person(kalimuduo)
    for i in range(0, 10):
        atlas.create_person(pandaliya)
    while True:
        print("回合开始")
        atlas.play()
        input()
