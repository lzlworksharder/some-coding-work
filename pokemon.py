import sys
import tkinter 
import random as rd
from tkinter.constants import ANCHOR, CENTER, E, LEFT, N, NE, RAISED, RIGHT, TOP, W, X
from PIL import ImageTk
from tkinter import messagebox

def yes_or_no(precision): # 判定函数,参数为成功的概率(百分制)
    a = rd.random() # 利用random库,判断一个0-1随机数是否位于成功区间以说明是否判定成功
    if a <= precision/100:
        return True
    else:
        return False

counter_d = {'一般':[] , '水':['火'] , '格斗':['一般','钢','冰'] , '超能':['格斗','毒'] , 
'龙':['龙'] , '飞行':['格斗'] , '钢':['冰'] , '火':['钢','冰'] , '电':['水','飞行'] , 
'鬼':['鬼','超能'] ,'冰':['飞行','龙']}
notsogood_d = {'一般':['钢'] , '水':['龙','水'] , '格斗':['超能'] , '超能':['钢','超能'],
'龙':['钢'] , '飞行':['钢'] , '火':['水','龙','火'] , '电':['龙','电'] , '毒':['鬼'],'冰':['水','冰','火','钢'],
'钢':['水','火','电','钢']}

notwork_d = {'一般':['鬼'] , '格斗':['鬼'] , '毒':['钢'] , '鬼':['一般']}


class Pokemon:
    def __init__(self,name,values,property,skills,level,image_path):
        self.name = name
        self.values = values[0:5]+((level*(values[5]+15)/50)+110,) # 参数为元组,6个值  0物攻 1特攻 2物防 3特防 4速度 5生命
        self.property = property # 列表,1-2个值,精灵属性
        self.skills = skills # 传入技能类对象
        self.skpp = {skills[0]:skills[0].pp,skills[1]:skills[1].pp,skills[2]:skills[2].pp,skills[3]:skills[3].pp} # 记录精灵pp
        self.state = [0,0,0,0,0,values[5]] # 战斗状态,6个值 0物攻 1特攻 2物防 3特防 4速度 5生命
        self.battlestate = [values[i] for i in range(5)] + [(level*(values[5]+15)/50)+110] # 战斗中精灵能力值参数
        self.level = level # 整数
        self.image_path = image_path # 精灵图像的路径
        self.unusual = 0 # 异常状态标记,0无,1睡眠,2麻痹,3烧伤,4中毒
        self.poison_count = 0 # 中毒回合数
        self.strug = 0 # 挣扎判定参数
        self.sleep_count = 0 # 睡眠回合
        self.fskill = 9 # 即将释放的技能
        self.owner = 0 # 主人
    def death_judge(self): # 判定精灵是否死亡
        if self.battlestate[5] < 1:
            self.battlestate[5] = 0
            return 1
        else:
            return 0


class skill: # 技能类(父类)
    def __init__(self,name,property,cl,pp,power,precision,special=None):
        self.property = property # 技能属性
        self.cl = cl # 技能分类: 攻击类:特攻1/物攻0 变化类:1睡眠,2麻痹,3烧伤,4中毒
        self.pp = pp # pp值,为一正整数
        self.power = power # 威力
        self.precision = precision # 命中率
        self.name = name # 姓名
        self.special = special # 特殊效果

class Attack_skill(skill): # 攻击技能类(子类)
    def __init__(self, name, property, cl, pp, power, precision, special=None): # cl为0:物攻 1是特攻
        super().__init__(name, property, cl, pp, power, precision, special)
    def cal(self,attacker,defender): # 技能的伤害计算函数
        modi = 1 # 修正值:要害 技能属性 精灵属性克制 能力与异常状态 
        basic_cal = ((2*attacker.level+10)/250*attacker.battlestate[self.cl]/defender.battlestate[2+self.cl]*self.power+2) # 基础伤害
        tip = 1 # 记录效果 0没用 1正常 >0<1不佳 >=2效果拔群
        weak_tip = 0 # 记录要害
        if self.property in attacker.property: # 技能属性加成
            modi *= 1.5
        for j in defender.property: # 双方属性克制加成
            try:
                if j in notwork_d[self.property]:
                    modi *= 0
                    tip *= 0
            except:
                pass
            try:
                if j in notsogood_d[self.property]:
                    modi *= 0.5
                    tip *= 0.5
            except:
                pass
            try:
                if j in counter_d[self.property]:
                    modi *= 2
                    tip *= 2
            except:
                pass

        if yes_or_no(attacker.values[4]/512*100):
            modi *= 1.5
            weak_tip = 1
        if tip == 0:
            l = 0
            print(f'{attacker.name}的技能好像没有什么作用')
        elif tip == 1:
            l = basic_cal*modi
        elif 1> tip >0:
            l =  basic_cal*modi
            print(f'{attacker.name}的技能效果不佳')
        elif tip >= 2:
            l = basic_cal*modi
            print(f'{attacker.name}的技能效果拔群')
        if weak_tip:
            print(f'{attacker.name}的技能击中要害')
        return l 
    def exertion(self,attacker,defender): # 技能的施放函数
        if self in attacker.skpp:
            attacker.skpp[self] -= 1
        damage= self.cal(attacker,defender)
        defender.battlestate[5] -= damage
        if self.special != None:
            self.special(attacker,defender) # 特殊效果为一个函数!
        if damage != 0:
            print(f'{attacker.name}的{self.name}, 对{defender.name}造成了{damage:.0f}点伤害.')
        attacker.fskill = 9

def changestate(changer,cl,power): # 能力变化函数,用来计算能力变化后精灵能力值
    if abs(changer.state[cl] + power) <= 6: # 讨论能力值是否超过6,不超过正常计算,超过按6算
        changer.state[cl] += power
        if changer.state[cl] != 0:
            changer.battlestate[cl] = changer.values[cl]*((2+abs(changer.state[cl]))/2)**(changer.state[cl]//abs(changer.state[cl]))
        else:
            changer.battlestate[cl] = changer.values[cl]
    else:
        if abs(changer.state[cl])<6:
            changer.state[cl] = 6*(changer.state[cl]//abs(changer.state[cl]))
        else:
            l = {0:'物攻',1:'特攻',2:'物防',3:'特防',4:'速度',5:'生命'}
            print(f'{l[cl]}已达上限,无法变化')
            return 0

class Alter_skill(skill): # 变化技能类(子类)
    def __init__(self, name, property, cl, pp, power, precision): # cl为012345:对应能力改变,0-5为自己7-12为对手 可以为一个列表 cl为6:状态改变 
        super().__init__(name, property, cl, pp, power, precision) # power:能力改变量或异常状态
    def exertion(self,attacker,defender): # 技能释放函数
        if  defender.unusual != 0 and self.cl == 6:
            print(f'{self.name}使用失败了')
        else:
            if self.cl == 6:
                if self.power == 4:
                    if '钢' in defender.property: # 考虑毒对钢无效
                        print(f'毒对{defender.name}好像没什么作用')
                    else:
                        print(f'{attacker.name}施放了{self.name}')
                        print(f'{defender.name}中剧毒了!')
                        defender.unusual = 4
                        attacker.skpp[self] -= 1
                elif self.power == 1:
                    print(f'{attacker.name}施放了{self.name}')
                    defender.unusual = 1
                    a = rd.randint(1,3) # 睡眠需要生成一个1-3的随机数表示睡眠回合
                    defender.sleep_count = a
                    attacker.skpp[self] -= 1
                    print(f'{defender.name}睡着了!')
                elif self.power == 2:
                    print(f'{attacker.name}施放了{self.name}')
                    print(f'{defender.name}麻痹了!')
                    defender.unusual = self.power
                    attacker.skpp[self] -= 1
                elif self.power == 3:
                    if '火' in defender.property: # 烧伤对火无效
                        print(f'烧伤对{defender.name}好像没什么作用')
                    else:
                        print(f'{attacker.name}施放了{self.name}') 
                        print(f'{defender.name}烧伤了!')
                        defender.unusual = self.power
                        attacker.skpp[self] -= 1
            else:
                attacker.skpp[self] -= 1
                flag = 0
                for i in range(len(self.cl)):
                    if self.cl[i] <= 5:
                        a = changestate(attacker,self.cl[i],self.power[i])
                        if a != 0 and flag == 0:
                            flag = 1
                            print(f'{attacker.name}施放了{self.name},能力值提高了')
                    else:
                        a = changestate(defender,self.cl[i]-7,self.power[i])
                        if a!=0:
                            print(f'{attacker.name}施放了{self.name},对方能力值下降了')
        attacker.fskill = 9
      


class user: # 用户类
    def __init__(self,pokemons,name): 
        self.medicine = [['恢复药',2] , ['元气块',2] , ['烧伤药',1] , ['麻痹药',1] , ['解睡药',1] , ['解毒药',1]] # 开始拥有的药
        self.pokemons = pokemons # 持有精灵
        self.name = name # 用户名
        self.turn = 0 # 当前控制的精灵
    def breakfree(self,pokemon,num): # 复活精灵使用使精灵能力值变为初始值
        if pokemon.state[num] != 0:
            pokemon.battlestate[num] = pokemon.values[num]*(((2+abs(pokemon.state[num]))/2)**(pokemon.state[num]//abs(pokemon.state[num])))
        else:
            pokemon.battlestate[num] = pokemon.values[num]

    def use_medicine(self,med,pokemon):  # 异常状态标记,0无,1睡眠,2麻痹,3烧伤,4中毒,给精灵用药,返回值为0时使用失败,重新选择,否则使用成功
        pokemon.fskill = 9
        if self.medicine[med][1] >= 1:
            if self.medicine[med][0] == '恢复药':
                if pokemon.battlestate[5] == 0:
                    print(f'失败, {pokemon.name}已死亡,请重新输入')
                else:
                    pokemon.battlestate[5] = pokemon.values[5]
                    self.medicine[med][1] -= 1
                    print(f'{pokemon.name}的HP恢复了')
                    return 1
            elif self.medicine[med][0] == '元气块':
                if pokemon.battlestate[5] > 0:
                    print(f'{pokemon.name}并未死亡,请重新输入')
                else:
                    pokemon.battlestate = list(pokemon.values)
                    pokemon.unusual = 0
                    self.breakfree(pokemon,4)
                    self.breakfree(pokemon,0)
                    self.medicine[med][1] -= 1
                    print(f'{pokemon.name}复活了!')
                    return 1
            elif self.medicine[med][0] == '烧伤药':
                if pokemon.unusual != 3:
                    print(f'{pokemon.name}并未烧伤,请重新输入')
                else:
                    pokemon.unusual = 0
                    self.medicine[med][1] -= 1
                    self.breakfree(pokemon,0)
                    print(f'{pokemon.name}的烧伤痊愈了')
                    return 1
            elif self.medicine[med][0] == '麻痹药':
                if pokemon.unusual != 2:
                    print(f'{pokemon.name}并未麻痹,请重新输入')
                else:
                    pokemon.unusual = 0
                    self.breakfree(pokemon,4)
                    self.medicine[med][1] -= 1
                    print(f'{pokemon.name}的麻痹痊愈了')
                    return 1
            elif self.medicine[med][0] == '解睡药':
                if pokemon.unusual != 1:
                    print(f'{pokemon.name}并未睡着,请重新输入')
                else:
                    pokemon.unusual = 0
                    self.medicine[med][1] -= 1
                    print(f'{pokemon.name}醒来了!')
                    return 1
            elif self.medicine[med][0] == '解毒药':
                if pokemon.unusual != 4:
                    print(f'{pokemon.name}并未中毒,请重新输入')
                else:
                    pokemon.unusual = 0
                    print(f'{pokemon.name}的中毒痊愈了!')
                    self.medicine[med][1] -= 1
                    return 1
            return 0
        else:
            print('此药已用完')
            return 0



bulkup = Alter_skill('健美','格斗',[0,2],20,[1,1],100)
calmmind = Alter_skill('冥想','超能',[1,3],20,[1,1],100)
dragondance = Alter_skill('龙舞','龙',[0,4],20,[1,1],100)
toxic = Alter_skill('剧毒','毒',6,10,4,90)
thunderwave = Alter_skill('电磁波','电',6,20,2,90)
hypnosis = Alter_skill('催眠术','超能',6,20,1,60)
willowisp = Alter_skill('鬼火','火',6,15,3,85)

hydropump = Attack_skill('水炮','水',1,5,110,80)
brickbreak = Attack_skill('瓦割','格斗',0,15,75,100)
def fbodyslam(attacker,defender):
    if yes_or_no(30):
        defender.unusual = 2
        print(f'{defender.name}麻痹了')
bodyslam = Attack_skill('泰山压顶','一般',0,15,85,100,special=fbodyslam)
def fthunderpunch(attacker,defender):
    if yes_or_no(10):
        defender.unusual = 2
        print(f'{defender.name}麻痹了')
thunderpunch = Attack_skill('雷电拳','电',0,15,75,100,special=fthunderpunch)
zenheadbutt = Attack_skill('意念头槌','超能',0,15,80,90)
ironhead = Attack_skill('铁头','钢',0,15,80,100)
def fpsychic(attacker,defender):
    if yes_or_no(10):
        changestate(defender,3,-1)
        print(f'{defender.name}的特防降低了')
psychic = Attack_skill('精神强念','超能',1,10,90,100,special=fpsychic)
def fshadowball(attacker,defender):
    if yes_or_no(20):
        changestate(defender,3,-1)
        print(f'{defender.name}的特防降低了')
shadowball = Attack_skill('暗影球','鬼',1,15,80,100,special=fshadowball)
outrage = Attack_skill('逆鳞','龙',0,10,120,100)
hurricane = Attack_skill('暴风','飞行',1,10,110,70)
def fflamethrower(attacker,defender):
    if yes_or_no(10) and '火' not in defender.property:
        defender.unusual = 3
        print(f'{defender.name}烧伤了')
flamethrower = Attack_skill('喷射火焰','火',1,15,90,100,special=fflamethrower)
flashcannon = Attack_skill('加农光炮','钢',1,10,80,100,special=fpsychic)
def fthunder(attacker,defender):
    if yes_or_no(30):
        defender.unusual = 2
        print(f'{defender.name}麻痹了')
thunder = Attack_skill('打雷','电',1,10,110,70,special=fthunder)
def ffirepunch(attacker,defender):
    if yes_or_no(10) and '火' not in defender.property:
        defender.unusual = 3
        print(f'{defender.name}烧伤了')
firepunch = Attack_skill('火焰拳','火',0,15,75,100,special=ffirepunch)
icebeam = Attack_skill('急冻光线','冰',1,10,90,100)
blizzard = Attack_skill('暴风雪','冰',1,5,110,70)
thunderbolt = Attack_skill('十万伏特','电',1,15,90,100,special=fthunderpunch)
def fstruggle(attacker,defender):
    attacker.battlestate[5] -= attacker.battlestate[5]*0.25
struggle = Attack_skill('挣扎','无',0,100000,50,100,special=fstruggle)
# value: 
n241 = Pokemon('大奶罐',(80,40,105,70,100,95),['一般'],(bodyslam,thunderpunch,zenheadbutt,ironhead),50,r'.\pokemonpic\Pictures\241-大奶罐_big.png')
n062 = Pokemon('快泳蛙',(95,70,95,90,70,90),['水','格斗'],(bulkup,hydropump,brickbreak,bodyslam),49,r'.\pokemonpic\Pictures\062-快泳蛙_big.png') 
n282 = Pokemon('沙奈朵',(65,125,65,115,80,68),['超能'],(hypnosis,psychic,calmmind,shadowball),50,r'.\pokemonpic\Pictures\282-超能女皇_big.png')
n149 = Pokemon('快龙',(134,100,95,100,80,91),['龙','飞行'],(dragondance,outrage,hurricane,thunderpunch),48,r'.\pokemonpic\Pictures\149-快龙_big.png')
n376 = Pokemon('巨金怪',(135,95,130,90,70,80),['钢','超能'],(zenheadbutt,bodyslam,shadowball,ironhead),47,r'.\pokemonpic\Pictures\376-钢铁螃蟹_big.png')
n059 = Pokemon('风速狗',(110,100,80,80,95,90),['火'],(flamethrower,willowisp,bodyslam,outrage),49,r'.\pokemonpic\Pictures\059-风速狗_big.png')
n082 = Pokemon('三合一磁怪',(60,120,95,70,70,50),['电','钢'],(thunder,thunderbolt,flashcannon,thunderwave),50,r'.\pokemonpic\Pictures\082-三磁怪_big.png')
n094 = Pokemon('耿鬼',(65,130,60,75,110,60),['鬼','毒'],(shadowball,toxic,psychic,hypnosis),47,r'.\pokemonpic\Pictures\094-耿鬼_big.png')
n006 = Pokemon('喷火龙',(84,109,78,85,100,78),['火','飞行'],(flamethrower,outrage,dragondance,willowisp),47,r'.\pokemonpic\Pictures\006-喷火龙_big.png')
n230 = Pokemon('刺龙王',(95,95,95,95,85,75),['水','龙'],(hydropump,hurricane,icebeam,flashcannon),50,r'.\pokemonpic\Pictures\230-海马龙_big.png')
n125 = Pokemon('电击兽',(83,95,57,85,105,65),['电'],(thunderpunch,firepunch,thunderwave,brickbreak),48,r'.\pokemonpic\Pictures\125-电击兽_big.png')
n362 = Pokemon('冰鬼护',(80,80,80,80,80,80),['冰'],(icebeam,ironhead,shadowball,blizzard),50,r'.\pokemonpic\Pictures\362-冰鬼护_big.png')

def rgb(n): # 颜色系统
    if n>255:
        n = 255
    elif n<0:
        n = 0
    x = hex(n)
    x = x[2:]
    if len(x)<2:
        x = '0'+x
    return x.upper()

def trancolor(r,g,b):
    rc = rgb(r)
    gc = rgb(g)
    bc = rgb(b)
    return f'#{rc}{gc}{bc}'

user1,user2 = 0,0
root = tkinter.Tk()
root.title('请选择你的6只出战精灵,剩下的6只将作为AI或玩家2的精灵')
root.geometry('575x700')

var241 = tkinter.IntVar()
image241 = ImageTk.PhotoImage(file=n241.image_path)
c241 = tkinter.Checkbutton(root,variable=var241,image=image241,command=lambda:pickcount())
c241.grid(row=4,column=0,ipadx=50,ipady=20)

var062 = tkinter.IntVar()
image062 = ImageTk.PhotoImage(file=n062.image_path)
c062 = tkinter.Checkbutton(root,variable=var062,image=image062,command=lambda:pickcount())
c062.grid(row=4,column=1,ipadx=50,ipady=20)

var282 = tkinter.IntVar()
image282 = ImageTk.PhotoImage(file=n282.image_path)
c282 = tkinter.Checkbutton(root,variable=var282,image=image282,command=lambda:pickcount())
c282.grid(row=4,column=2,ipadx=50,ipady=20)

var149 = tkinter.IntVar()
image149 = ImageTk.PhotoImage(file=n149.image_path)
c149 = tkinter.Checkbutton(root,variable=var149,image=image149,command=lambda:pickcount())
c149.grid(row=1,column=0,ipadx=50,ipady=20)
    
var376 = tkinter.IntVar()
image376 = ImageTk.PhotoImage(file=n376.image_path)
c376 = tkinter.Checkbutton(root,variable=var376,image=image376,command=lambda:pickcount())
c376.grid(row=1,column=1,ipadx=50,ipady=20)

var059 = tkinter.IntVar()
image059 = ImageTk.PhotoImage(file=n059.image_path)
c059 = tkinter.Checkbutton(root,variable=var059,image=image059,command=lambda:pickcount())
c059.grid(row=1,column=2,ipadx=50,ipady=20)

var082 = tkinter.IntVar()
image082 = ImageTk.PhotoImage(file=n082.image_path)
c082 = tkinter.Checkbutton(root,variable=var082,image=image082,command=lambda:pickcount())
c082.grid(row=2,column=0,ipadx=50,ipady=20)

var094 = tkinter.IntVar()
image094 = ImageTk.PhotoImage(file=n094.image_path)
c094 = tkinter.Checkbutton(root,variable=var094,image=image094,command=lambda:pickcount())
c094.grid(row=2,column=1,ipadx=50,ipady=20)

var006 = tkinter.IntVar()
image006 = ImageTk.PhotoImage(file=n006.image_path)
c006 = tkinter.Checkbutton(root,variable=var006,image=image006,command=lambda:pickcount())
c006.grid(row=2,column=2,ipadx=50,ipady=20)

var230 = tkinter.IntVar()
image230 = ImageTk.PhotoImage(file=n230.image_path)
c230 = tkinter.Checkbutton(root,variable=var230,image=image230,command=lambda:pickcount())
c230.grid(row=3,column=0,ipadx=50,ipady=20)

var125 = tkinter.IntVar()
image125 = ImageTk.PhotoImage(file=n125.image_path)
c125 = tkinter.Checkbutton(root,variable=var125,image=image125,command=lambda:pickcount())
c125.grid(row=3,column=1,ipadx=50,ipady=20)


var362 = tkinter.IntVar()
image362 = ImageTk.PhotoImage(file=n362.image_path)
c362 = tkinter.Checkbutton(root,variable=var362,image=image362,command=lambda:pickcount())
c362.grid(row=3,column=2,ipadx=50,ipady=20)


countl = [c241,c062,c282,c149,c376,c059,c082,c094,c006,c230,c125,c362]
l = [var241,var062,var282,var149,var376,var059,var082,var094,var006,var230,var125,var362]
nl = [n241,n062,n282,n149,n376,n059,n082,n094,n006,n230,n125,n362]
lt = []
for i in range(len(l)):
    lt.append((countl[i],l[i],nl[i]))
stack = []
count = 0
def pickcount():
    global count
    if count < 6: # 所选精灵数不足六只时
        for i in range(len(lt)): # 如果上一步操作是选中某一个精灵,则找到那个精灵的序号并赋值给a
            if lt[i][1].get() == 1:
                a = i
                break
        else: # 如果列表里没有精灵被选中,则说明上一步操作取消了某个选择,遍历stack找到取消的对象
            for i in range(len(stack)):
                if stack[i][1].get() == 0:
                    a = i
                    break
            lt.append(stack.pop(a)) # 将取消的还回lt,return none退出
            count -= 1
            return None
        stack.append(lt.pop(a)) # 没return则把选中的加到stack里
        count += 1 
    else: # 所选精灵已经不小于六只
        for i in range(len(lt)): # 记录选择对象,若有的话
            if lt[i][1].get() == 1:
                a = i
                break
        else: # 没有选择对象,则撤销了某个精灵,采用同样方法还回lt
            for i in range(len(stack)):
                if stack[i][1].get() == 0:
                    a = i
                    break
            lt.append(stack.pop(a))
            count -= 1
            return None
        stack[-1][0].deselect() # 将最后选择的取消,替换为最新的选择
        stack.append(lt.pop(a))
        lt.append(stack.pop(-2))

finishpick = tkinter.Button(root,bg=trancolor(255,193,37),height=2,width=9,text='选择完毕',command=lambda:retpick()).grid(row=6,column=1,sticky=W)
exit = tkinter.Button(root,bg=trancolor(30,144,255),text='退出',height=2,width=9,command= lambda:sys.exit(0)).grid(row=6,column=1,sticky=E)

def quit():
    root.destroy()
    sys.exit(0)
def retpick(): 
    global user1,user2
    if count == 6:
        root.destroy()
        user1,user2 = [stack[i][2] for i in range(6)] ,[lt[i][2] for i in range(6)] # 记录选择结果
    else:
        messagebox.showerror('error','选择数量未达6只')
root.protocol('WM_DELETE_WINDOW',lambda:sys.exit(0))
root.mainloop()



window1 = tkinter.Tk()
window1.geometry('300x200')
choose_label = tkinter.Label(window1,text='请选择对战模式').pack(side=TOP)

AI_button = tkinter.Button(window1,height=2,width=9,text='AI',command=lambda:AI(),bg=trancolor(0,245,255)).pack(side=LEFT,padx=35)
users_button = tkinter.Button(window1,height=2,width=9,text='双用户',command=lambda:users(),bg=trancolor(50,205,50)).pack(side=RIGHT,padx=35)

switch = 6

def AI():
    global switch
    switch = 0
    window1.destroy()
def users():
    global switch
    switch = 1
    window1.destroy()
window1.protocol('WM_DELETE_WINDOW',lambda:sys.exit(0))
window1.mainloop()



#battle begins

def startjudge(attacker): # 异常状态标记,0无,1睡眠,2麻痹,3烧伤,4中毒
    if attacker.unusual == 1:
        if attacker.sleep_count == 0:
            attacker.unusual = 0
            print(f'{attacker.name}醒来了!')
            return 0
        else:
            attacker.sleep_count -= 1
            return 1
        
    elif attacker.unusual == 2:
        attacker.owner.breakfree(attacker,4)
        attacker.battlestate[4] *= 3/4
        a = yes_or_no(25)
        if a:
            return 2
        else:
            return 0
    elif attacker.unusual == 3:
        attacker.owner.breakfree(attacker,0)
        attacker.battlestate[0] *= 1/2
        return 0
    else:
        return 0
def endminus(ender):
    if ender.unusual == 4:
        if ender.poison_count < 15:
            ender.poison_count += 1
        ender.battlestate[5] -= ender.values[5]*ender.poison_count/16
        print(f'{ender.name}中了剧毒!损失了生命')
    elif ender.unusual == 3:
        ender.battlestate[5] -= ender.values[5]/16
        print(f'{ender.name}烧伤了,损失了生命')
def numin_robust(start,end):
    while 1: # 鲁棒性
        try:
            first2 = int(input())
            if first2 >end or first2 <start:
                print(f'输入数字必须为{start}-{end},请重新输入')
            else:
                break
        except:
            print(f'必须输入位于{start}-{end}的正整数,请重新输入.')
    return first2




# 玩家与玩家的过程:
def choose_pokemon(user):
    print(f'{user.name}请决定出战精灵,输入一个数字.')
    print('精灵编号为:')
    for i in range(6):
        print(f'{i+1}: {user.pokemons[i].name}')
    while 1:
        poket = user.pokemons[numin_robust(1,6)-1]   
        if poket.death_judge():
            print('该精灵已死亡,无法选择')
        else:
            break
    return poket 


print('Battle begins!!!')
def speedjudge(poket1,poket2):
    if poket1.battlestate[4] > poket2.battlestate[4]:
        attacker = poket1
        defender = poket2
    elif poket1.battlestate[4] < poket2.battlestate[4]:
        attacker = poket2
        defender = poket1
    else:
        a = yes_or_no(50)
        if a:
            attacker = poket1
            defender = poket2
        else:
            attacker = poket2
            defender = poket1
    return [attacker,defender]


def choose_action(user):
    print(f'{user.name}请输入一个数字代表选择的行动:')
    print('行动代号:')
    print(f'1. 使用{user.turn.name}攻击, 2. 使用伤药, 3. 投降')
    choice = numin_robust(1,3)
    return choice



def choose_medicine(user):
    print('请输入两行数字,第一行代表所用药,第二行代表使用对象.任意一行输入为0时表示重新选择.')
    print('代号如下:')
    for i in range(len(user.medicine)):
        print(f'{i+1}: {user.medicine[i][0]}, 剩余{user.medicine[i][1]}个')
    print()
    for i in range(6):
        print(f'{i+1}: {user.pokemons[i].name}')
    while 1:
        med = numin_robust(0,len(user.medicine))
        pok = numin_robust(0,6)
        rechoose = 0
        if med == 0 or pok == 0:
            rechoose = 1
            break
        else:
            pok = user.pokemons[pok-1]
            result = user.use_medicine(med-1,pok)
            if result == 1:
                break
    return rechoose
def choose_skill(attacker):
    print('请输入你要使用的技能,输入为0时表示重新选择.')

    c = sum(list(attacker.skpp.values()))
    if c > 0:
        print(f'{attacker.name}选择技能:')
        for i in range(4):
            if type(attacker.skills[i]) == Attack_skill:
                print(f'{i+1}: {attacker.skills[i].name}  属性: {attacker.skills[i].property},  威力: {attacker.skills[i].power},  pp: {attacker.skpp[attacker.skills[i]]}/{attacker.skills[i].pp},  命中率: {attacker.skills[i].precision}')
            else:
                print(f'{i+1}: {attacker.skills[i].name}  属性: {attacker.skills[i].property},  威力: {0},  pp: {attacker.skpp[attacker.skills[i]]}/{attacker.skills[i].pp},  命中率: {attacker.skills[i].precision}')
        print('请选择:')
        skillchosen1 = numin_robust(0,4)
        while skillchosen1 > 0 and attacker.skpp[attacker.skills[skillchosen1-1]] <= 0 :
            print('失败,该技能pp已耗尽')
            skillchosen1 = numin_robust(0,4)
        return skillchosen1
    else:
        return -1
def lose_judge(pokemon):
    if pokemon.death_judge():
        a = 0
        for i in range(6):
            a += pokemon.owner.pokemons[i].death_judge()
        if a == 6:
            print(f'{pokemon.owner.name}失败,游戏结束.')
            sys.exit(0)

def replace_judge(pokemon):
    b = 0 # b代表是否真的替换了精灵,为0则原来精灵未死亡,返回原来精灵,为1则返回的是新的精灵
    if pokemon.death_judge():
        print(f'{pokemon.name}失去战斗能力')
        a = choose_pokemon(pokemon.owner)
        b = 1
        pokemon.owner.turn = a
    else:
        a = pokemon
    return [a,b]

def aical(attacker,defender):
    choice = -1
    l = -1
    for i in range(4):
        sk = attacker.skills[i]
        if attacker.skpp[sk] <= 0: # 技能pp为0不选
            continue
        elif type(sk) == Alter_skill and sk.cl == 6 and defender.unusual == 0 :
            choice = i # 满足施放异常状态技能的条件则优先释放
            break
        elif type(sk) == Alter_skill and sk.cl != 6 and max([i for i in attacker.state if i<7]) <= 1:
            choice = i # 且要进行必要的能力强化(最多两次)
            break
        else: # 以上条件均不满足时则要计算输出最佳技能
            modi = 1 # 修正值: 技能属性 精灵属性克制 能力与异常状态 
            try: # 
                basic_cal = ((2*attacker.level+10)/250*attacker.values[sk.cl]/defender.values[2+sk.cl]*sk.power+2)
            except:
                basic_cal = 0
            if sk.property in attacker.property:
                modi *= 1.5
            for j in defender.property:
                try:
                    if j in notwork_d[sk.property]:
                        modi *= 0
                except:
                    pass
                try:
                    if j in notsogood_d[sk.property]:
                        modi *= 0.5
                except:
                    pass
                try:
                    if j in counter_d[sk.property]:
                        modi *= 2
                except:
                    pass
            l1 = basic_cal*modi
            ex = l1*sk.precision/100 # 技能伤害期望=伤害值*命中率
            if ex >= l: # 进行逐项比较
                l = ex

                choice = i
    if choice == -1: # 没有可选的技能(所有pp均无,施放挣扎)
        real_user2.turn.strug = 1
    return choice  
    
def ai_lost_and_change(attacker,defender): 
    if real_user2.turn.battlestate[5] < 1:
        print(f'{real_user2.turn.name}失去战斗能力')
        if real_user2.pokemons.index(real_user2.turn)+1 < 5:
            real_user2.turn = real_user2.pokemons[real_user2.pokemons.index(real_user2.turn)+1]
            if attacker.owner == real_user2:
                a = real_user2.turn
                d = real_user1.turn
            else:
                d = real_user2.turn
                a = real_user1.turn
            return [1,a,d]
        else:
            print('AI失败,游戏结束.')
            sys.exit(0)
    else:
        return [0,attacker,defender]

def release(attacker,defender):
    al = startjudge(attacker)
    if al == 2: # 利用开局判定传来的参数判断精灵的行动
        print(f'{attacker.name}麻痹了,无法行动.')
    elif al == 1:
        print(f'{attacker.name}睡着了,无法行动.')
    elif al == 0:
        if attacker.strug == 1: # 拼命标识为1,则施放拼命(挣扎)
            print(f'没有技能可以使用,{attacker.name}拼命了.')
            struggle.exertion(attacker,defender)
        else: # 否则根据是否技能使用无效以及是否命中判断技能释放函数是否被调用
            if '毒' in attacker.property and attacker.skills[attacker.fskill].name == '剧毒':
                attacker.skills[attacker.fskill].exertion(attacker,defender)
            elif yes_or_no(attacker.skills[attacker.fskill].precision):
                attacker.skills[attacker.fskill].exertion(attacker,defender)
            else:
                print(f'{attacker.name}的{attacker.skills[attacker.fskill].name}未命中')
                attacker.skpp[attacker.skills[attacker.fskill]] -= 1
print('20377173 李樟霖')
if switch == 1:
    real_user1 = user(user1,'玩家1')
    real_user2 = user(user2,'玩家2')   
    for i in range(6):
        user1[i].owner = real_user1
        user2[i].owner = real_user2
    poket1 = choose_pokemon(real_user1)
    poket2 = choose_pokemon(real_user2)
    attacker,defender = speedjudge(poket1,poket2)

    real_user1.turn = poket1
    real_user2.turn = poket2
    while 1:
        endminus(defender)
        lose_judge(defender)
        defender,f1 = replace_judge(defender)
        endminus(attacker)
        lose_judge(attacker)
        attacker,f2 = replace_judge(attacker)

        attacker,defender = speedjudge(attacker,defender)
        print(f'{real_user1.turn.name}的HP为: {real_user1.turn.battlestate[5]:.0f}/{real_user1.turn.values[5]:.0f}')
        print(f'{real_user2.turn.name}的HP为: {real_user2.turn.battlestate[5]:.0f}/{real_user2.turn.values[5]:.0f}')    
        op = {0:'正常',1:'睡眠',2:'麻痹',3:'烧伤',4:'中毒'}
        print(f'{real_user1.turn.name}的状态为: {op[real_user1.turn.unusual]}')
        print(f'{real_user2.turn.name}的状态为: {op[real_user2.turn.unusual]}')
        res1 = choose_action(real_user1)
        while 1:

            if res1 == 2:
                j1 = choose_medicine(real_user1)
                if j1 == 0:
                    real_user1.turn.fskill = 9
                    break
            elif res1 == 1:
                j1 = choose_skill(real_user1.turn)
                if j1 > 0:
                    real_user1.turn.fskill = j1-1
                    break
                elif j1 == -1:
                    real_user1.turn.strug = 1
                    break
            else:
                print(f'{real_user1.name}失败!!游戏结束.')
                sys.exit(0)
        while 1:
            res2 = choose_action(real_user2)
            if res2 == 2:
                j2 = choose_medicine(real_user2)
                if j2 == 0:
                    real_user2.turn.fskill = 9
                    break
            elif res2 == 1:
                j2 = choose_skill(real_user2.turn)
                if j2 > 0 :
                    real_user2.turn.fskill = j2-1
                    break
                elif j2 == -1:
                    real_user2.turn.strug = 1
                    break
            else:
                print(f'{real_user2.name}失败!!游戏结束.')
                sys.exit(0)

        if attacker.fskill != 9:
            release(attacker,defender)
            lose_judge(defender)
            lose_judge(attacker)
            defender,f1 = replace_judge(defender)
            attacker,f2 = replace_judge(attacker)
            if f1 == 1 or f2 == 1:
                continue
        else:
            pass

        if defender.fskill != 9:
            release(defender,attacker)
            lose_judge(attacker)
            lose_judge(defender)
            attacker,f2 = replace_judge(attacker)
            defender,f1 = replace_judge(defender)
            if f1 == 1 or f2 == 1:
                continue
        else:
            pass





elif switch == 0:
    real_user1 = user(user1,'玩家1')
    real_user2 = user(user2,'AI')
    for i in range(6):
        user1[i].owner = real_user1
        user2[i].owner = real_user2
    poket1 = choose_pokemon(real_user1)
    poket2 = user2[0]
    attacker,defender = speedjudge(poket1,poket2)
    # 开局初始状态
    real_user1.turn = poket1
    real_user2.turn = poket2
    while 1: # 进入循环
        endminus(defender) # 回合末判定
        endminus(attacker)
        lose_judge(defender)
        lose_judge(attacker)
        if defender.owner == real_user1:
            defender,f1 = replace_judge(defender)
        else:
            attacker,f1 = replace_judge(attacker)
        f2,attacker,defender = ai_lost_and_change(attacker,defender)
        attacker,defender = speedjudge(attacker,defender) # 速度判定
        print(f'{real_user1.turn.name}的HP为: {real_user1.turn.battlestate[5]:.0f}/{real_user1.turn.values[5]:.0f}') # 双方信息
        print(f'{real_user2.turn.name}的HP为: {real_user2.turn.battlestate[5]:.0f}/{real_user2.turn.values[5]:.0f}')    
        op = {0:'正常',1:'睡眠',2:'麻痹',3:'烧伤',4:'中毒'}
        print(f'{real_user1.turn.name}的状态为: {op[real_user1.turn.unusual]}')
        print(f'{real_user2.turn.name}的状态为: {op[real_user2.turn.unusual]}')
        while 1: # 玩家一选择行为
            res1 = choose_action(real_user1)
            if res1 == 2:
                j1 = choose_medicine(real_user1)
                if j1 == 0:
                    break
                elif j1 == 1:
                    continue
            elif res1 == 1:
                j1 = choose_skill(real_user1.turn)
                if j1 > 0:
                    real_user1.turn.fskill = j1-1
                    break
                elif j1 == -1:
                    real_user1.turn.strug = 1
                    break
            else:
                print(f'{real_user1.name}失败!!游戏结束.')
                sys.exit(0)
        real_user2.turn.fskill = aical(real_user2.turn,real_user1.turn) # AI选择行为

        if attacker.fskill != 9 or attacker.strug == 1: # 速度快者攻击
            release(attacker,defender)
            lose_judge(defender)
            lose_judge(attacker)
            if defender.owner == real_user1:
                defender,f1 = replace_judge(defender)
            else:
                attacker,f1 = replace_judge(attacker)
            f2,attacker,defender = ai_lost_and_change(attacker,defender)
            if f1 == 1 or f2 == 1:
                continue
        else:
            pass
        
        if defender.fskill != 9 or defender.strug == 1: # 慢者攻击
            release(defender,attacker)
            lose_judge(attacker)
            lose_judge(defender)
            if defender.owner == real_user1:
                defender,f1 = replace_judge(defender)
            else:
                attacker,f1 = replace_judge(attacker)
            f2,attacker,defender = ai_lost_and_change(attacker,defender)
            if f1 == 1 or f2 == 1:
                continue
        else:
            pass
