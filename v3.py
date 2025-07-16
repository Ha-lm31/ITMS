simTime = 100
'''
1-Changer le valeur `simTime` selon le choix.
2- Inverser les valeurs de `x` et `y`: 
x['up'] <=> x['down']
y['right'] <=> y ['left'].
3- `signalCoods`, `signalTimerCoods`, `vehicleCountCoods` changer l'ordre des tuples, met le dernier en premier.
4- On ajouter un condition pour choisir le valeur de feux vert, si on prend la valeur par défault ou bien selon la formule,
ça aide à evalualer la simulation et faire une comparaison,
par example : 
par défault : 
`
Lane-wise Vehicle Counts
Lane 1 : 5
Lane 2 : 22
Lane 3 : 4
Lane 4 : 9
Total vehicles passed:  40
Total time passed:  100
No. of vehicles passed per unit time:  0.4
`
par la formule :
`
Lane-wise Vehicle Counts
Lane 1 : 40
Lane 2 : 28
Lane 3 : 4
Lane 4 : 9
Total vehicles passed:  81
Total time passed:  100
No. of vehicles passed per unit time:  0.81
`
5- ajouter les résultats de sumilation dans un fichier .csv.
'''

import random
import math
import time
import threading
# from vehicle_detection import detection
import pygame
import sys
import os

import csv

defaultRed = 150
defaultYellow = 5
defaultGreen = 20
defaultMinimum = 10
defaultMaximum = 60
signals = []
noOfSignals = 4
timeElapsed = 0
currentGreen = 0
nextGreen = (currentGreen + 1) % noOfSignals
currentYellow = 0
carTime = 2
bikeTime = 1
rickshawTime = 2.25
busTime = 2.5
truckTime = 2.5
noOfCars = 0
noOfBikes = 0
noOfBuses = 0
noOfTrucks = 0
noOfRickshaws = 0
noOfLanes = 2
detectionTime = 5
speeds = {
    'car':2.25,
    'bus':1.8,
    'truck':1.8,
    'rickshaw':2,
    'bike':2.5}
x = {
    'right':[0,0,0],
    'left':[1400,1400,1400],
    'up':[755,727,697],
    'down':[602,627,657]}
y = {
    'right':[498,466,436],
    'left':[348,370,398],
    'up':[800,800,800],
    'down':[0,0,0]}
vehicles = {
    'right': {0:[], 1:[], 2:[], 'crossed':0},
    'left': {0:[], 1:[], 2:[], 'crossed':0},
    'up': {0:[], 1:[], 2:[], 'crossed':0},
    'down': {0:[], 1:[], 2:[], 'crossed':0}}
vehicleTypes = {
    0:'car',
    1:'bus',
    2:'truck',
    3:'rickshaw',
    4:'bike'}
directionNumbers = {
    0:'right',
    2:'left',
    3:'up',
    1:'down'}
signalCoods = [(530,570),(530,230),(810,230),(810,570)]
signalTimerCoods = [(530,550),(530,210),(810,210),(810,550)]
vehicleCountCoods = [(480,550),(480,210),(880,210),(880,550)]
vehicleCountTexts = ["0", "0", "0", "0"]
stopLines = {
    'right': 590,
    'left': 800,
    'up': 535,
    'down': 330,}
defaultStop = {
    'right': 580,
    'left': 810,
    'up': 545,
    'down': 320,}
stops = {
    'right': [580,580,580],
    'left': [810,810,810],
    'up': [545,545,545],
    'down': [320,320,320],}
mid = {
    'right': {'x':705, 'y':445},
    'left': {'x':695, 'y':425},
    'up': {'x':695, 'y':400},
    'down': {'x':695, 'y':450}}
rotationAngle = 3
gap = 15
gap2 = 15
pygame.init()
simulation = pygame.sprite.Group()
class TrafficSignal:
    def __init__(self, red, yellow, green, minimum, maximum):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.minimum = minimum
        self.maximum = maximum
        self.signalText = "30"
        self.totalGreenTime = 0
class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction, will_turn):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = speeds[vehicleClass]
        self.direction_number = direction_number
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = 0
        self.willTurn = will_turn
        self.turned = 0
        self.rotateAngle = 0
        vehicles[direction][lane].append(self)
        # self.stop = stops[direction][lane]
        self.index = len(vehicles[direction][lane]) - 1
        path = "images/" + direction + "/" + vehicleClass + ".png"
        self.originalImage = pygame.image.load(path)
        self.currentImage = pygame.image.load(path)
        if(direction == 'right'):
            if(len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index-1].crossed == 0):
                self.stop = vehicles[direction][lane][self.index-1].stop - vehicles[direction][lane][self.index-1].currentImage.get_rect().width - gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().width + gap
            x[direction][lane] -= temp
            stops[direction][lane] -= temp
        elif(direction == 'left'):
            if(len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index-1].crossed == 0):
                self.stop = vehicles[direction][lane][self.index-1].stop + vehicles[direction][lane][self.index-1].currentImage.get_rect().width + gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().width + gap
            x[direction][lane] += temp
            stops[direction][lane] += temp
        elif(direction == 'down'):
            if(len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index-1].crossed == 0):
                self.stop = vehicles[direction][lane][self.index-1].stop - vehicles[direction][lane][self.index-1].currentImage.get_rect().height - gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().height + gap
            y[direction][lane] -= temp
            stops[direction][lane] -= temp
        elif(direction == 'up'):
            if(len(vehicles[direction][lane]) > 1 and vehicles[direction][lane][self.index-1].crossed == 0):
                self.stop = vehicles[direction][lane][self.index-1].stop + vehicles[direction][lane][self.index-1].currentImage.get_rect().height + gap
            else:
                self.stop = defaultStop[direction]
            temp = self.currentImage.get_rect().height + gap
            y[direction][lane] += temp
            stops[direction][lane] += temp
        simulation.add(self)
    def render(self, screen):
        screen.blit(self.currentImage, (self.x, self.y))
    def move(self):
        if(self.direction == 'right'):
            if(self.crossed == 0 and self.x + self.currentImage.get_rect().width > stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
            if(self.willTurn == 1):
                if(self.crossed == 0 or self.x + self.currentImage.get_rect().width < mid[self.direction]['x']):
                    if((self.x + self.currentImage.get_rect().width <= self.stop or (currentGreen == 0 and currentYellow == 0) or self.crossed == 1) and (self.index == 0 or self.x + self.currentImage.get_rect().width < (vehicles[self.direction][self.lane][self.index-1].x - gap2) or vehicles[self.direction][self.lane][self.index-1].turned == 1)):
                        self.x += self.speed
                else:
                    if(self.turned == 0):
                        self.rotateAngle += rotationAngle
                        self.currentImage = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                        self.x += 2
                        self.y += 1.8
                        if(self.rotateAngle == 90):
                            self.turned = 1
                            # path = "images/" + directionNumbers[((self.direction_number+1)%noOfSignals)] + "/" + self.vehicleClass + ".png"
                            # self.x = mid[self.direction]['x']
                            # self.y = mid[self.direction]['y']
                            # self.image = pygame.image.load(path)
                    else:
                        if(self.index == 0 or self.y + self.currentImage.get_rect().height < (vehicles[self.direction][self.lane][self.index-1].y - gap2) or self.x + self.currentImage.get_rect().width < (vehicles[self.direction][self.lane][self.index-1].x - gap2)):
                            self.y += self.speed
            else:
                if((self.x + self.currentImage.get_rect().width <= self.stop or self.crossed == 1 or (currentGreen == 0 and currentYellow == 0)) and (self.index == 0 or self.x + self.currentImage.get_rect().width < (vehicles[self.direction][self.lane][self.index-1].x - gap2) or (vehicles[self.direction][self.lane][self.index-1].turned == 1))):
                    self.x += self.speed
        elif(self.direction == 'down'):
            if(self.crossed == 0 and self.y + self.currentImage.get_rect().height > stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
            if(self.willTurn == 1):
                if(self.crossed == 0 or self.y + self.currentImage.get_rect().height < mid[self.direction]['y']):
                    if((self.y + self.currentImage.get_rect().height <= self.stop or (currentGreen == 1 and currentYellow == 0) or self.crossed == 1) and (self.index == 0 or self.y + self.currentImage.get_rect().height < (vehicles[self.direction][self.lane][self.index-1].y - gap2) or vehicles[self.direction][self.lane][self.index-1].turned == 1)):
                        self.y += self.speed
                else:
                    if(self.turned == 0):
                        self.rotateAngle += rotationAngle
                        self.currentImage = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                        self.x -= 2.5
                        self.y += 2
                        if(self.rotateAngle == 90):
                            self.turned = 1
                    else:
                        if(self.index == 0 or self.x > (vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().width + gap2) or self.y < (vehicles[self.direction][self.lane][self.index-1].y - gap2)):
                            self.x -= self.speed
            else:
                if((self.y + self.currentImage.get_rect().height <= self.stop or self.crossed == 1 or (currentGreen == 1 and currentYellow == 0)) and (self.index == 0 or self.y + self.currentImage.get_rect().height < (vehicles[self.direction][self.lane][self.index-1].y - gap2) or (vehicles[self.direction][self.lane][self.index-1].turned ==1 ))):
                    self.y += self.speed
        elif(self.direction == 'left'):
            if(self.crossed == 0 and self.x < stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
            if(self.willTurn == 1):
                if(self.crossed == 0 or self.x > mid[self.direction]['x']):
                    if((self.x >= self.stop or (currentGreen == 2 and currentYellow == 0) or self.crossed == 1) and (self.index == 0 or self.x > (vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().width + gap2) or vehicles[self.direction][self.lane][self.index-1].turned == 1)):
                        self.x -= self.speed
                else:
                    if(self.turned == 0):
                        self.rotateAngle += rotationAngle
                        self.currentImage = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                        self.x -= 1.8
                        self.y -= 2.5
                        if(self.rotateAngle == 90):
                            self.turned = 1
                            # path = "images/" + directionNumbers[((self.direction_number+1)%noOfSignals)] + "/" + self.vehicleClass + ".png"
                            # self.x = mid[self.direction]['x']
                            # self.y = mid[self.direction]['y']
                            # self.currentImage = pygame.image.load(path)
                    else:
                        if(self.index == 0 or self.y > (vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().height +  gap2) or self.x > (vehicles[self.direction][self.lane][self.index-1].x + gap2)):
                            self.y -= self.speed
            else:
                if((self.x >= self.stop or self.crossed == 1 or (currentGreen == 2 and currentYellow == 0)) and (self.index == 0 or self.x > (vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().width + gap2) or (vehicles[self.direction][self.lane][self.index-1].turned == 1))):
                    self.x -= self.speed
            # if((self.x>=self.stop or self.crossed == 1 or (currentGreen==2 and currentYellow==0)) and (self.index==0 or self.x>(vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().width + gap2))):
            #     self.x -= self.speed
        elif(self.direction == 'up'):
            if(self.crossed == 0 and self.y < stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
            if(self.willTurn == 1):
                if(self.crossed == 0 or self.y > mid[self.direction]['y']):
                    if((self.y >= self.stop or (currentGreen == 3 and currentYellow == 0) or self.crossed == 1) and (self.index == 0 or self.y > (vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().height +  gap2) or vehicles[self.direction][self.lane][self.index-1].turned == 1)):
                        self.y -= self.speed
                else:
                    if(self.turned == 0):
                        self.rotateAngle += rotationAngle
                        self.currentImage = pygame.transform.rotate(self.originalImage, -self.rotateAngle)
                        self.x += 1
                        self.y -= 1
                        if(self.rotateAngle == 90):
                            self.turned = 1
                    else:
                        if(self.index == 0 or self.x < (vehicles[self.direction][self.lane][self.index-1].x - vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().width - gap2) or self.y > (vehicles[self.direction][self.lane][self.index-1].y + gap2)):
                            self.x += self.speed
            else:
                if((self.y >= self.stop or self.crossed == 1 or (currentGreen == 3 and currentYellow == 0)) and (self.index == 0 or self.y > (vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].currentImage.get_rect().height + gap2) or (vehicles[self.direction][self.lane][self.index-1].turned == 1))):
                    self.y -= self.speed
def initialize():
    ts1 = TrafficSignal(0, defaultYellow, defaultGreen, defaultMinimum, defaultMaximum)
    signals.append(ts1)
    ts2 = TrafficSignal(ts1.red + ts1.yellow + ts1.green, defaultYellow, defaultGreen, defaultMinimum, defaultMaximum)
    signals.append(ts2)
    ts3 = TrafficSignal(defaultRed, defaultYellow, defaultGreen, defaultMinimum, defaultMaximum)
    signals.append(ts3)
    ts4 = TrafficSignal(defaultRed, defaultYellow, defaultGreen, defaultMinimum, defaultMaximum)
    signals.append(ts4)
    repeat()
def setTime():
    global noOfCars, noOfBikes, noOfBuses, noOfTrucks, noOfRickshaws, noOfLanes
    global carTime, busTime, truckTime, rickshawTime, bikeTime
    os.system("say detecting vehicles, " + directionNumbers[(currentGreen + 1) % noOfSignals])
#    detection_result=detection(currentGreen,tfnet)
#    greenTime = math.ceil(((noOfCars*carTime) + (noOfRickshaws*rickshawTime) + (noOfBuses*busTime) + (noOfBikes*bikeTime))/(noOfLanes+1))
#    if(greenTime<defaultMinimum):
#       greenTime = defaultMinimum
#    elif(greenTime>defaultMaximum):
#       greenTime = defaultMaximum
    # greenTime = len(vehicles[currentGreen][0])+len(vehicles[currentGreen][1])+len(vehicles[currentGreen][2])
    # noOfVehicles = len(vehicles[directionNumbers[nextGreen]][1])+len(vehicles[directionNumbers[nextGreen]][2])-vehicles[directionNumbers[nextGreen]]['crossed']
    # print("no. of vehicles = ",noOfVehicles)
    noOfCars, noOfBuses, noOfTrucks, noOfRickshaws, noOfBikes = 0 ,0, 0, 0, 0
    for j in range(len(vehicles[directionNumbers[nextGreen]][0])):
        vehicle = vehicles[directionNumbers[nextGreen]][0][j]
        if(vehicle.crossed == 0):
            vclass = vehicle.vehicleClass
            # print(vclass)
            noOfBikes += 1
    for i in range(1,3):
        for j in range(len(vehicles[directionNumbers[nextGreen]][i])):
            vehicle = vehicles[directionNumbers[nextGreen]][i][j]
            if(vehicle.crossed == 0):
                vclass = vehicle.vehicleClass
                # print(vclass)
                if(vclass == 'car'):
                    noOfCars += 1
                elif(vclass == 'bus'):
                    noOfBuses += 1
                elif(vclass == 'truck'):
                    noOfTrucks += 1
                elif(vclass == 'rickshaw'):
                    noOfRickshaws += 1
    # print(noOfCars)
    '''greenTime = math.ceil(((noOfCars * carTime) + (noOfRickshaws * rickshawTime) + (noOfBuses * busTime) + (noOfTrucks * truckTime)+ (noOfBikes * bikeTime))/(noOfLanes + 1))
    # greenTime = math.ceil((noOfVehicles)/noOfLanes)
    print('Green Time: ',greenTime)
    if(greenTime < defaultMinimum):
        greenTime = defaultMinimum
    elif(greenTime > defaultMaximum):
        greenTime = defaultMaximum
    # greenTime = random.randint(15,50)
    signals[(currentGreen+1)%(noOfSignals)].green = greenTime'''

    greenTime = defaultGreen
    if green_time_mode == "formula":
        greenTime = math.ceil(((noOfCars * carTime) + (noOfRickshaws * rickshawTime) + (noOfBuses * busTime) + (noOfTrucks * truckTime)+ (noOfBikes * bikeTime))/(noOfLanes + 1))
        print('Green Time (calculé): ', greenTime)
        if(greenTime < defaultMinimum):
            greenTime = defaultMinimum
        elif(greenTime > defaultMaximum):
            greenTime = defaultMaximum
    else:
        print('Green Time (défaut): ', greenTime)
    signals[(currentGreen+1)%(noOfSignals)].green = greenTime


def repeat():
    global currentGreen, currentYellow, nextGreen
    while(signals[currentGreen].green > 0):
        printStatus()
        updateValues()
        if(signals[(currentGreen + 1) % (noOfSignals)].red == detectionTime):
            thread = threading.Thread(name="detection", target=setTime, args=())
            thread.daemon = True
            thread.start()
            # setTime()
        time.sleep(1)
    currentYellow = 1
    vehicleCountTexts[currentGreen] = "0"
    for i in range(0,3):
        stops[directionNumbers[currentGreen]][i] = defaultStop[directionNumbers[currentGreen]]
        for vehicle in vehicles[directionNumbers[currentGreen]][i]:
            vehicle.stop = defaultStop[directionNumbers[currentGreen]]
    while(signals[currentGreen].yellow > 0):
        printStatus()
        updateValues()
        time.sleep(1)
    currentYellow = 0
    signals[currentGreen].green = defaultGreen
    signals[currentGreen].yellow = defaultYellow
    signals[currentGreen].red = defaultRed
    currentGreen = nextGreen
    nextGreen = (currentGreen + 1) % noOfSignals
    signals[nextGreen].red = signals[currentGreen].yellow + signals[currentGreen].green #??
    repeat()
def printStatus():
	for i in range(0, noOfSignals):
		if(i == currentGreen):
			if(currentYellow == 0):
				print(" GREEN TS", i+1, "-> r:", signals[i].red, " y:", signals[i].yellow, " g:", signals[i].green)
			else:
				print("YELLOW TS", i+1, "-> r:", signals[i].red, " y:", signals[i].yellow, " g:",signals[i].green)
		else:
			print("   RED TS", i+1, "-> r:", signals[i].red, " y:", signals[i].yellow, " g:", signals[i].green)
	print()
def updateValues():
    for i in range(0, noOfSignals):
        if(i == currentGreen):
            if(currentYellow == 0):
                signals[i].green -= 1
                signals[i].totalGreenTime += 1
            else:
                signals[i].yellow -= 1
        else:
            signals[i].red -= 1
def generateVehicles():
    while(True):
        vehicle_type = random.randint(0,4)
        if(vehicle_type == 4):
            lane_number = 0
        else:
            lane_number = random.randint(0,1) + 1
        will_turn = 0
        if(lane_number == 2):
            temp = random.randint(0,4)
            if(temp <= 2):
                will_turn = 1
            elif(temp > 2):
                will_turn = 0
        temp = random.randint(0,999)
        direction_number = 0
        a = [400,800,900,1000]
        if(temp < a[0]):
            direction_number = 0
        elif(temp < a[1]):
            direction_number = 1
        elif(temp < a[2]):
            direction_number = 2
        elif(temp < a[3]):
            direction_number = 3
        Vehicle(lane_number, vehicleTypes[vehicle_type], direction_number, directionNumbers[direction_number], will_turn)
        time.sleep(0.75)
def simulationTime():
    global timeElapsed, simTime
    while(True):
        timeElapsed += 1
        time.sleep(1)
        if(timeElapsed == simTime):
            totalVehicles = 0
            print('Lane-wise Vehicle Counts')
            for i in range(noOfSignals):
                print('Lane', i+1, ':', vehicles[directionNumbers[i]]['crossed'])
                totalVehicles += vehicles[directionNumbers[i]]['crossed']
            print('Total vehicles passed: ',totalVehicles)
            print('Total time passed: ',timeElapsed)
            print('No. of vehicles passed per unit time: ',(float(totalVehicles)/float(timeElapsed)))
            os._exit(1)

def enregistrer_resultats(code_formule, temp_simulation, nombre_vehicule, nom_fichier='resultats.csv'):
    # Vérifie si le fichier existe déjà pour l'en-tête
    try:
        with open(nom_fichier, 'r', encoding='utf-8') as f:
            existe = True
    except FileNotFoundError:
        existe = False

    with open(nom_fichier, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['code de formule', 'temp de simulation', 'nombre de véhicule'])
        if not existe:
            writer.writeheader()
        writer.writerow({
            'code de formule': code_formule,
            'temp de simulation': temp_simulation,
            'nombre de véhicule': nombre_vehicule
        })

def ask_green_time_mode():
    print("Choisissez le mode de calcul du temps vert :")
    print("1 - Utiliser la valeur par défaut (", defaultGreen, "secondes)")
    print("2 - Calculer selon la formule (en fonction du nombre de véhicules)")
    choix = input("Entrez 1 ou 2 : ")
    if choix == "2":
        return "formula"
    else:
        return "default"
# Demander à l'utilisateur le mode de calcul
green_time_mode = ask_green_time_mode()

class Main:
    thread4 = threading.Thread(name="simulationTime", target=simulationTime, args=()) 
    thread4.daemon = True
    thread4.start()
    thread2 = threading.Thread(name="initialization", target=initialize, args=())
    thread2.daemon = True
    thread2.start()
    black = (0, 0, 0)
    white = (255, 255, 255)
    screenWidth = 1400
    screenHeight = 800
    screenSize = (screenWidth, screenHeight)
    background = pygame.image.load('images/mod_int.png')
    screen = pygame.display.set_mode(screenSize)
    pygame.display.set_caption("SIMULATION")
    redSignal = pygame.image.load('images/signals/red.png')
    yellowSignal = pygame.image.load('images/signals/yellow.png')
    greenSignal = pygame.image.load('images/signals/green.png')
    font = pygame.font.Font(None, 30)
    thread3 = threading.Thread(name="generateVehicles", target=generateVehicles, args=())
    thread3.daemon = True
    thread3.start()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        screen.blit(background,(0,0))
        for i in range(0,noOfSignals):
            if(i == currentGreen):
                if(currentYellow == 1):
                    if(signals[i].yellow == 0):
                        signals[i].signalText = "STOP"
                    else:
                        signals[i].signalText = signals[i].yellow
                    screen.blit(yellowSignal, signalCoods[i])
                else:
                    if(signals[i].green == 0):
                        signals[i].signalText = "SLOW"
                    else:
                        signals[i].signalText = signals[i].green
                    screen.blit(greenSignal, signalCoods[i])
            else:
                if(signals[i].red <= 10):
                    if(signals[i].red == 0):
                        signals[i].signalText = "GO"
                    else:
                        signals[i].signalText = signals[i].red
                else:
                    signals[i].signalText = "---"
                screen.blit(redSignal, signalCoods[i])
        signalTexts = ["","","",""]
        for i in range(0,noOfSignals):
            signalTexts[i] = font.render(str(signals[i].signalText), True, white, black)
            screen.blit(signalTexts[i],signalTimerCoods[i]) 
            displayText = vehicles[directionNumbers[i]]['crossed']
            vehicleCountTexts[i] = font.render(str(displayText), True, black, white)
            screen.blit(vehicleCountTexts[i],vehicleCountCoods[i])
        timeElapsedText = font.render(("Time Elapsed: "+ str(timeElapsed)), True, black, white)
        screen.blit(timeElapsedText,(1100,50))
        for vehicle in simulation:
            screen.blit(vehicle.currentImage, [vehicle.x, vehicle.y])
            # vehicle.render(screen)
            vehicle.move()
        pygame.display.update()

Main()