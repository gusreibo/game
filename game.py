import random

class Living:
    def __init__(self, name, stats):
        self.name = name
        self.stats = stats
        self.isDead = False
        self.lastKilled = None
        self.equipped = {}

    def __str__(self):
        return self.name + '\n' + str(self.stats)

    def __cmp__(self, other):
        return cmp((self.stats, self.name), (other.stats, other.name))

    def damage(self, points):
        if self.stats.HP <= points:
            damageDone = self.stats.HP
            self.stats.HP = 0
            self.isDead = True
        else:
            damageDone = points
            self.stats.HP -= points
        return damageDone

    def attack(self, target):
        damage = self.stats.ATK - target.stats.DEF
        if damage <= 0:
            damage = 1
        damageDone = target.damage(damage)
        if target.isDead:
            self.lastKilled = target
        return damageDone

    def __hash__(self):
        return hash((self.name, self.stats))

class Player(Living):
    def __init__(self, name):
        Living.__init__(self, name, Stats(10, 2, 2, 2))
        self.exp = 0
        self.level = 1

    def __str__(self):
        return self.name + ' Lv.' + str(self.level) + '\n' + str(self.stats)

    def __cmp__(self, other):
        if isinstance(other, Player):
            return cmp((self.level, self.exp, self.stats, self.name), (other.level, other.exp, other.stats, other.name))
        elif isinstance(other, Living):
            return Living.__cmp__(self, other)

    def levelUp(self):
        self.level += 1
        for i in ['maxHP', 'ATK', 'DEF', 'SPD']:
            self.stats.__dict__[i] += random.choice([1, 1, 2, 2, 2, 3])
            self.stats.HP = self.stats.maxHP

    def equip(self, thing):
        if self.equipped.get(thing.loc):
            other = self.equipped[self.loc]
            self.equipped[thing.loc] = thing
        else:
            other = None
            self.equipped[thing.loc] = thing
        if isinstance(thing, Weapon):
            self.stats.ATK += thing.strength
        if isinstance(other, Weapon):
            self.stats.ATK -= other.strength

    def getExp(self, exp):
        self.exp += exp
        if self.exp >= self.level*10:
            self.exp -= self.level*10
            self.level += 1
            print "Levelled up!", self.name, "is now level", str(self.level)

class Game:
    def __init__(self, players=[], locations=[]):
        self.players = players
        self.locations = locations

    def addPlayer(self, player):
        self.players.append(player)

    def addLocation(self, location):
        self.locations.append(location)

    def nextTurn(self):
        for i in self.locations:
            i.nextTurn()

class Location:
    def __init__(self, name, typ):
        self.name = name
        self.type = typ
        self.battles = []

    def __str__(self):
        return self.type + ' of ' + self.name

    def addBattle(self, side1, side2):
        self.battles.append(Battle(side1, side2, self))

    def nextTurn(self):
        for i in self.battles:
            i.nextTurn()

class Battle:
    def __init__(self, side1, side2, location):
        self.side1 = side1
        self.side2 = side2
        self.location = location
        self.lastTurns = {}

    def __str__(self):
        names1 = [i.name for i in self.side1]
        names2 = [i.name for i in self.side2]
        return ', '.join(names1) + ' battling ' + ', '.join(names2) + ' at ' + str(self.location)

    def nextTurn(self):
        battlers = self.side1 + self.side2
        battlers2 = sorted(battlers, key=lambda battler: battler.stats.SPD)
        battlers2.reverse()
        for i in battlers2:
            if i.isDead:
                continue
            otherSide = self.side1 if i in self.side2 else self.side2
            if isinstance(i, Player):
                print [[j.name, j.stats.HP] for j in otherSide]
                print "What will " + i.name + " do?",
                action = raw_input().split(' ')
                if action == [''] and self.lastTurns.get(i):
                    action = self.lastTurns[i]
                if action[0] == 'attack':
                    target = otherSide[int(action[1])]
                    print "Dealt", i.attack(target), "damage to", target.name
                self.lastTurns[i] = action
            elif isinstance(i, Monster):
                target = random.choice(otherSide)
                print i.name, 'dealt', i.attack(target), 'damage to', target.name
            if target.isDead:
                otherSide.remove(target)
                print "Killed " + target.name
                if isinstance(i, Player) and isinstance(target, Monster):
                    i.getExp(target.exp)
        print [j for j in [[[i.name, i.stats.HP] for i in self.side1], [[i.name, i.stats.HP] for i in self.side2]]]

class Stats:
    def __init__(self, HP, ATK, DEF, SPD):
        self.HP = HP
        self.maxHP = HP
        self.ATK = ATK
        self.DEF = DEF
        self.SPD = SPD

    def __str__(self):
        return 'HP: ' + str(self.HP) + ', ATK: ' + str(self.ATK) + ', DEF: ' + str(self.DEF) + ', SPD: ' + str(self.SPD)

class Monster(Living):
    def __init__(self, name, stats, exp):
        Living.__init__(self, name, stats)
        self.exp = exp

    @classmethod
    def slime(cls):
        return cls("Slime", Stats(5, 1, 1, 1), 2)

    @classmethod
    def goblin(cls):
        return cls("Goblin", Stats(10, 3, 2, 2), 5)

    @classmethod
    def troll(cls):
        return cls("Troll", Stats(20, 5, 0, 1), 20)

class Item:
    def __init__(self, name, typ):
        self.name = name
        self.type = typ

    def __str__(self):
        return self.name

class Consumable(Item):
    def __init__(self, name, effect, effArgs=None):
        Item.__init__(self, name, "Consumable")
        self.effect = effect
        self.effArgs = effArgs

    def use(self, target):
        if self.effArgs:
            self.effect(target, self.effArgs)
        else:
            self.effect(target)

class Potion(Consumable):
    def __init__(self, points=5, typ=""):
        if typ:
            Consumable.__init__(self, typ+" Potion", heal, points)
        else:
            Consumable.__init__(self, "Potion", heal, points)

    @classmethod
    def large(cls, points=10):
        return cls(points, "Large")

def heal(target, points):
    target.stats.HP = min(target.stats.HP + points, target.stats.maxHP)

class Equipment(Item):
    def __init__(self, name, loc):
        Item.__init__(self, name, "Equipment")
        self.loc = loc

class Weapon(Equipment):
    def __init__(self, kind, strength=2, typ=""):
        if typ:
            Equipment.__init__(self, typ+" "+kind, "Hand")
        else:
            Equipment.__init__(self, kind, "Hand")
        self.strength = strength
        self.typ = typ

    @classmethod
    def sword(cls, strength=2, typ=""):
        return cls("Sword", strength, typ)

def testGame():
    p1 = Player("Davion")
    p2 = Player("Maron")
    
    wiFe = Location("Winterfell", "Castle")
    saBu = Location("Salzburg", "Town")
    
    s1 = Monster.slime()
    s2 = Monster.slime()
    
    wiFe.addBattle([p1, p2], [s1, s2])
    
    g = Game([p1], [wiFe, saBu])
    
    p = Potion()
    lp = Potion.large()
    
    s = Weapon.sword()
    i = Weapon("Mace", 4, "Iron")
    
    p1.equip(i)
    p2.equip(s)
    
    p1.exp = 9
    
    g.nextTurn()

testGame()