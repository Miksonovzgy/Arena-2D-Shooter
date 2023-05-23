class generalServerInfo():
    def __init__(self, protocolMessage, playerList: list, objectList, weaponList, bulletList):
        self.protocol = protocolMessage#* #THIS IS A LIST OF INFOOBJECTS FOR THE PLAYERS THAT ARE IN
        self.playerList = playerList
        self.objectList = objectList #AGAIN, LIST OF "OBJECT" OBJECTS
        self.weaponList = weaponList #I THINK YOU GET IT BY THIS POINT
        self.bulletList = bulletList #ITS GETTING KINDA OBVIOUS AT THIS POINT

#* WE WILL ONLY BE SENDING OBJECTS WITH OUR CLIENTS AND SERVER (NOTE: EVEN WHEN ESTABLISHING CONNECTION YOU SHOULD SEND AN OBJECT FOR THIS TO WORK FULLY)
#THEREFORE, TO DISTINGUISH THE PROTOCOL EXECTUION WE ONLY NEED TO DO 1 SIMPLE THING
#GIVE THE PROTOCOL VALUE TO EACH OBJECT, THEN BASED ON THE STRING DO DIFFERENT ACTIONS

#THE CLIENT NEEDS TO USE A SIMILLIAR BIG CLASS FOR SENDING THE INFO TO THE SERVER (WITH INFO FOR EACH OBJECT DEPENDENT ON THAT CLIENT)
#FOR EXAMPLE, CLIENT1 SENDS A BIG INFO OBJECT (NOT THE SAME AS THE ONE ABOVE) WHICH HOLDS A INFOPLAYEROBJECT, INFOWEAPONOBJECT
#INFOBULLETSOBJECT. THEN THE SERVER TAKES THAT OBJECT, IT UNPICKLES IT AND DOES STUFF THAT IT NEEDS TO DO WITH THE VALUES ONE BY ONE

#I WOULD LOVE TO DO IT FOR YOU BUT I DONT REALLY KNOW THE TECHNICHALITIES AND WHAT EXACLTY IS SUPPOSED TO BE THERE
#ALL I KNOW IS THAT I NEED INFO FOR EVERYTHING NEW THAT USUALLY YOU WOULD UPDATE IN THE GAME, BUT INSTEAD OF COMPUTING IT
#MANUALLY YOU WILL SEND IT TO THE SERVER, EXAMPLE: YOU SHOOT AND BULLETS ARE CREATED, THEN YOU SEND IN THE BIG INFO OBJECT
#A LIST OF BULLET OBJECTS, WHICH THE SERVER WILL STORE IN ITS OWN LIST OF BULLETS, WHICH IT WILL THEN SEND TO THE PLAYERS

class generalClientInfo():
    def __init__(self, protocolMessage, positionVector,pos, nickname, bulletsShot, weaponOwnedId, angle_pointing): ##The moue position is optional
        self.protocol = protocolMessage
        self.positionVector = positionVector
        self.pos = pos
        self.nickname = nickname
        self.bulletsShot = bulletsShot
        self.weaponOwnedId = weaponOwnedId
        self.angle_pointing = angle_pointing


class infoPlayerObject(): 
    def __init__(self, pos, group, nickname, protocol, positionVector, angle_pointing): #ALL OF THESE VALUES GET UPDATED WHENEVER THE CLIENT SENDS A MESSAGE TO THE SERVER
        self.protocol = protocol
        self.positionVector = positionVector
        self.pos = pos
        self.group = group
        self.nickname = nickname
        self.angle_pointing = angle_pointing

class infoObjectObject():
    def __init__(self, pos, group):
        self.pos = pos
        self.group = group

class infoWeaponObject(): #I NEED SOME ASSISTANCE HERE AND FOR THE BULLETS, AS I DONT REALLY KNOW AGAIN WHAT SHOULD BE EXACTLY SEND TO THE PLAYER WHEN HE JOINS AND WHEN THE PICTURE IS DRAWN EVERYTIME
    def __init__(self, posX, posY, group, id, owner, angle):
        self.posX = posX
        self.posY = posY
        self.group = group
        self.id = id
        self.owner = owner
        self.angle = angle

class infoBulletsObject():
    def __init__(self, posX, posY, shooter, id, angle, protocol = ""):        ##SO that we can send it as a separate message to the GeneralClientInfo
        self.posX = posX
        self.posY = posY
        #self.group = group
        self.shooter = shooter
        self.id = id
        self.bullet_speed = 10
        self.angle = angle
        self.protocol = protocol

class destroyBulletInfoObject():
    def __init__(self, protocol, id):
        self.protocol = protocol
        self.id = id


class disconnectionObject():
    def __init__(self, nickname, protocolMessage):
        self.protocol = protocolMessage #IMPORTANT, HERE THE MESSAGE WILL BE EITHER DISCONNECT OR CONNECT AND WE WILL HANDLE CONNECTIONS WITH THIS OBJECT ()
        self.nickname = nickname

class pingObject():
    def __init__(self, protocol, nickname = ""):
        self.protocol = protocol
        self.nickname = nickname

#IM TRULLY SORRY FOR THIS LAST MINUTE CHANGE, THE IDEA CAME TO ME WHEN I STARTED WORKING RIGHT AFTER YOU WENT TO SLEEP
#I AM TRULLY CONFIDENT THAT THIS IDEA IS GENIUS EVEN IF IT IS A SMALL OVERALL IMPROVEMENT AND THE FINALL RESULT WILL BE BETTER BECAUSE OF THIS

#P.S. FUCK DICTIONARIES, THIS IS THE TRUE WAY TO DO IT!!!!