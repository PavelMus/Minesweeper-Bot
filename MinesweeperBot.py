import numpy as np
import pygame

def printList(list):
    for i in range(0, 9):
        print("{}".format(list[i]))

class MineSweeperBot:
    def __init__(self, x, y, numBombs):
        '''
        Initialize the bots parameters with some sort of data
        1. Dimnensions of Board
        2. Number of Bombs
        '''
        self.x = x
        self.y = y
        self.numBombs = numBombs
        self.checkedBoxes = np.zeros((x, y)) #a list of already checked boxes, so that we don't check the same box multiple times
        self.checkedNumbers = [] # keep a list of coordinates that are checked in thinking period
        self.validNumberedBoxes = [] #we need a list of the numbers that we will be working off of
        for i in range(1, 10): # keep a list of valid numbers that  from 1 - 10
            self.validNumberedBoxes.append('[{}]'.format(i))
        self.blackList = [] # keep a list of blacklisted coordinates
        self.whiteList = [] # keep a list of coordinates that a guaranteed safe
        self.lowest = [] # keep the coordinates of lowest probability

    def performmove(self, revealedBoxes, mineField):
        '''
        Method to have bot perform a move, will need x and y coordinates
        '''
        pygame.display.update()
        performMove = True
        x, y = self.thinkofmove(revealedBoxes, mineField)
        # first move is always a fail
        if x == -1 and y == -1:
            x = np.random.randint(low=0, high=self.x)
            y = np.random.randint(low=0, high=self.y)
            self.checkedBoxes = np.zeros((self.x, self.y))
        # if we did not find an appropriate tile to choose, we don't perform the move
        elif (x is False) and (y is False):
            # special case where we have run out of boxes to check
            if (self.number_of_unchecked_boxes(revealedBoxes, mineField) == 0):
                self.checkedBoxes = np.zeros((self.x, self.y))
            performMove = False
        
        # clear temporary lists of coordinates, since we are done with calculations of coordinates
        self.lowest.clear()
        self.whiteList.clear()
        self.checkedNumbers.clear()
        return x, y, performMove

    def thinkofmove(self, revealedBoxes, mineField):
        '''
        Bot will analyze board and decide what is the best move
        (aka what move doesn't hit a mine)
        '''
        # check all boxes for a box that is not checked yet
        for x in range(0, self.x):
            for y in range(0, self.y):
                # if we have a box that is revealed and not checked, enter if statement
                if(revealedBoxes[x][y] == True) and (self.checkedBoxes[x][y] == 0) and (mineField[x][y] in self.validNumberedBoxes):
                    # mark box as checked
                    self.checkedBoxes[x][y] = 1
                    print("Origin Coordinates :[{}, {}]".format(x,y))

                    #check entire board for tiles that are safe or unsafe
                    self.clean_blacklist(revealedBoxes)
                    self.check_for_blacklist(revealedBoxes, mineField)
                    self.check_for_whitelist(revealedBoxes, mineField)

                    #print("Checked numbers: {}".format(self.checkedNumbers))
                    print("Blacklisted Tiles: {}".format(self.blackList))
                    print("WhiteListed Tiles: {}".format(self.whiteList))

                    #if there are whitelisted tiles, return first whitelist element
                    if(len(self.whiteList) > 0):
                        return self.whiteList[0][0], self.whiteList[0][1]

                    # create a list of probabilities of nearby boxes
                    probabilityBoard = self.boxProbability(x, y, 0, np.zeros((self.x, self.y)), revealedBoxes, mineField)
                    self.checkedNumbers.clear()
                    # recursively look for coordinates that have low probability
                    lowestX, lowestY = self.look_at_probabilities(probabilityBoard, x, y, revealedBoxes, mineField)

                    # return coordinates of block with lowest probability to have bomb
                    return lowestX, lowestY
        return -1, -1 # return statement for first move/invalid move

    def look_at_probabilities(self, probabilityBoard, x, y, revealedBoxes, mineField, iteration = 0):
        '''
        Method to look through probability board 
        to find next tile to select
        '''
        # special case that there are exactly the same number of unrevealed boxes as the number in the tile
        unrevealedBoxes = self.count_unrevealed_boxes(x,y,revealedBoxes)
        numberinTile = self.get_tile_number(x,y,mineField)
        #numberofBlacklisted = self.number_of_blacklisted_boxes(x, y, revealedBoxes)
        self.checkedNumbers.append([x,y])
        
        '''
        Special Cases
        1. if we have the case where the number of unrevealed tiles is equal to number in tiles
        2. if we already know that the tiles near the test block are already bombs
        '''
        while True:
            if(int(numberinTile) == int(unrevealedBoxes)):
                return bool(False), bool(False)
            lowestX = False
            lowestY = False
            lowestProbability = 9999999999
            for xi in range(-1, 2, 1):
                for yi in range(-1, 2, 1):
                    if (x + xi >= 0 and x+xi < self.x) and (y + yi >= 0 and y+yi < self.y) and not([x+xi, y+yi] in self.blackList):
                        if(probabilityBoard[x+xi][y+yi] <= lowestProbability) and (revealedBoxes[x+xi][y+yi] == False):
                            lowestX = x+xi
                            lowestY = y+yi
                            lowestProbability = probabilityBoard[x+xi][y+yi]
                            if not ([lowestX, lowestY] in self.lowest):
                                self.lowest.append([lowestX,lowestY])
            nextX, nextY = self.findNextNumberedBox(x, y, revealedBoxes, mineField)
            if (nextX == -1) and (nextY == -1):
                break
            else:
                lowestX, lowestY = self.look_at_probabilities(probabilityBoard, nextX, nextY, revealedBoxes, mineField, iteration + 1)
            
        if iteration == 0:
            #print("Tile Number: {}\n# unrevealed tiles: {}\n# blacklisted tiles: {}".format(numberinTile, unrevealedBoxes, numberofBlacklisted))
            #print("Lowest Points: {}".format(self.lowest))
            #find the lowest probability in range of low probability points from before
            lowestX = False
            lowestY = False
            lowestProbability = 9999999999
            for i in range(0, len(self.lowest)):
                if(probabilityBoard[self.lowest[i][0]][self.lowest[i][1]] <= lowestProbability):
                    lowestX = self.lowest[i][0]
                    lowestY = self.lowest[i][1]
                    lowestProbability = probabilityBoard[self.lowest[i][0]][self.lowest[i][1]] 
                    
            # now we find all points with that low probability
            lowestX = False
            lowestY = False
            tempList = []
            for i in range(0, len(self.lowest)):
                if(probabilityBoard[self.lowest[i][0]][self.lowest[i][1]] == lowestProbability):
                    tempList.append([self.lowest[i][0], self.lowest[i][1]])
            print("Lowest List: {}".format(tempList))
            print("Size of list of smallest probabilities: {}".format(len(tempList)))
            # pick a random point from that list, and return those coordinates
            if(len(tempList) <= 0):
                return bool(False), bool(False)
            randomIndex = np.random.randint(0, len(tempList))
            lowestX = tempList[randomIndex][0]
            lowestY = tempList[randomIndex][1]
        return lowestX, lowestY

    def boxProbability(self, x, y, iteration, probabilityBoard, revealedBoxes, mineField):
        '''
        if iteration is equal to 3 return immediately
        else
            calculate probabiity of bomb being at block, and add proportion to each unrevealed block
            increment iteration
            call function again with new proportionBoard and iteration
        return proportionBoard
        '''
        #print("Iteration: {}".format(iteration))
        if not (x == -1):
            self.checkedNumbers.append([x,y])
        else:
            return probabilityBoard
        nextX, nextY = self.findNextNumberedBox(x, y, revealedBoxes, mineField)
        while True:
            # get tile number so that probability can be scaled
            numberOfTile = self.get_tile_number(x, y, mineField)
            # get probability of a bomb being in nearby unreaveled boxes and scale it by the number in the tile
            probabilityOfNearbyBoxes = self.calculateProbability(x, y, revealedBoxes) ** float(numberOfTile)
            for i in range(-1, 2, 1):
                for j in range(-1, 2, 1):
                    # if box is unrevealed then increment value of probabilityBoard at indices by calculated probability
                        try:
                            if (revealedBoxes[x+i][y+j] == False) and not([x+i, y+j] in self.blackList):
                                probabilityBoard[x+i][y+j] = (probabilityBoard[x+i][y+j] + probabilityOfNearbyBoxes) / 2.0
                        except:
                            pass

            # call function again, with next numbered box
            nextX, nextY = self.findNextNumberedBox(x, y, revealedBoxes, mineField)

            # if the next found numbered box is invalid/doesn't exist don't recursively call
            if not((nextX == -1) and (nextY == -1)):
                probabilityBoard = self.boxProbability(nextX, nextY, iteration + 1, probabilityBoard, revealedBoxes, mineField)
            else:
                break

        # print out board of probabilities just for debugging
        #np.set_printoptions(precision=1)
        #if iteration == 0:
            #print(np.transpose(probabilityBoard))
        #nextX, nextY = self.findNextNumberedBox(x, y, revealedBoxes, mineField)
        return probabilityBoard

    def check_for_blacklist(self, revealedBoxes, mineField):
        '''
        check entire list for missed blacklist coordinates
        '''
        for x in range(0, self.x):
            for y in range(0, self.y):
                if(mineField[x][y] in self.validNumberedBoxes) and (revealedBoxes[x][y] == True):
                    num1 = self.count_unrevealed_boxes(x, y, revealedBoxes)
                    num2 = self.number_of_blacklisted_boxes(x, y,revealedBoxes)
                    num3 = self.get_tile_number(x, y, mineField)
                    #print("Coordinates: {}\nUnRevealed Check: {}\nBlackListed Check: {}".format([x,y], num1, num2))
                    for i in range(-1, 2, 1):
                        for j in range(-1, 2, 1):
                        # if box is unrevealed then increment value of probabilityBoard at indices by calculated probability
                            try:
                                if (revealedBoxes[x+i][y+j] == False) and (num1 == num3) and (num1 == (num2 + 1))and not([x+i, y+j] in self.blackList) and (x+i < self.x and x+i >= 0) and (y+j < self.y and y+j >= 0):
                                    print("ADDED BLACKLIST: [{}, {}]".format(x+i, y+j))
                                    self.blackList.append([x+i, y+j])
                            except:
                                pass

    def clean_blacklist(self, revealedBoxes):
        for i in range(0, len(self.blackList)):
            try:
                if revealedBoxes[self.blackList[i][0]][self.blackList[i][1]] == True:
                    self.blackList.remove([self.blackList[i][0], self.blackList[i][1]])
            except:
                pass

    def check_for_whitelist(self, revealedBoxes, mineField):
        '''
        check entire list for possible whitelist coordinates
        '''
        for x in range(0, self.x):
            for y in range(0, self.y):
                if(mineField[x][y] in self.validNumberedBoxes) and (revealedBoxes[x][y] == True):
                    # find the number of unrevealed tiles, number of blacklisted tiles, and the number from the tile
                    num1 = self.count_unrevealed_boxes(x, y, revealedBoxes)
                    num2 = self.number_of_blacklisted_boxes(x, y,revealedBoxes) + 1
                    num3 = self.get_tile_number(x, y, mineField)
                    #print("Coordinates: {}\nUnRevealed Check: {}\nBlackListed Check: {}".format([x,y], num1, num2))
                    # if we have it where there are definitely safe tiles, we try to find them
                    if (num1 == num2) and (num3 < num1):
                        for xi in range(-1, 2, 1):
                            for yj in range(-1, 2, 1):
                                if ((x+xi >= 0) and (x+xi < self.x) and (y+yj >= 0) and (y+yj < self.y)):
                                    if not([x+xi, y+yj] in self.blackList) and (revealedBoxes[x+xi][y+yj] == False) and not([x+xi, y+yj] in self.whiteList):
                                            self.whiteList.append([x+xi, y+yj])

    def calculateProbability(self, x, y, revealedBoxes):
        '''
        Take coordinate and then check immediate area, and return probability
        0 0 0
        0 X 0
        0 0 0
        '''
        # check the number of unrevealed boxes
        unrevealedBoxes = self.count_unrevealed_boxes(x, y, revealedBoxes)
        # we have found no boxes that are unrevealed around box, reset checked boxes
        if unrevealedBoxes == 0:
            #self.checkedBoxes = np.zeros((self.x, self.y))
            return 999
        return float(100.0 / unrevealedBoxes)

    def findNextNumberedBox(self, x, y, revealedBoxes, mineField):
        '''
        Find the next block around the current block
        '''
        nextBlockX = -1
        nextBlockY = -1
        # search around box
        for j in range(-1, 2, 1):
            for i in range(-1, 2, 1):
                #if the box is revealed, and box is a numbered tile, and we are not looking at the current block
                if ((x + i < 0) or (x + i >= self.x)) or ((y + j < 0) or (y + j >= self.y)) or ((x + i == x) and (y + j == y)):
                    pass
                elif (revealedBoxes[x+i][y+j] == True) and (mineField[x+i][y+j] in self.validNumberedBoxes) and not ([x+i,y+j] in self.checkedNumbers):
                    nextBlockX = x+i
                    nextBlockY = y+j
        return nextBlockX, nextBlockY

    def count_unrevealed_boxes(self, x, y, revealedBoxes):
        '''
        Method to count the number of unrevealed tiles
        '''
        unrevealedBoxes = 0
        # search surrounding boxes
        for i in range(-1, 2, 1):
            for j in range(-1, 2, 1):
                # if box is unrevealed then increment unrevealedBoxes
                try:
                    if (revealedBoxes[x+i][y+j] == False) and ((x+i < self.x) and (x+i >= 0) and (y+j < self.y) and (y+j >= 0)):
                        unrevealedBoxes+=1
                except:
                    pass
        return unrevealedBoxes

    def get_tile_number(self, x, y, mineField):
        '''
        Method to remove unecessary markings from tile element
        '''
        numberOfTile = mineField[x][y]
        numberOfTile = numberOfTile.replace('[','')
        numberOfTile = numberOfTile.replace(']','')
        return int(numberOfTile)
    
    def number_of_unchecked_boxes(self, revealedBoxes, mineField):
        '''
        Method to check the number of unchecked boxes in the grid
        '''
        numberOfUnChecked = 0
        for x in range(0, self.x):
            for y in range(0, self.y):
                if (mineField[x][y] in self.validNumberedBoxes) and (revealedBoxes[x][y] == True) and (self.checkedBoxes[x][y] == False):
                    numberOfUnChecked += 1
        return numberOfUnChecked
    
    def number_of_blacklisted_boxes(self, x, y, revealedBoxes):
        numberofBlacklisted = 0
        # search surrounding boxes
        for i in range(-1, 2, 1):
            for j in range(-1, 2, 1):
                # if box is unrevealed then increment unrevealedBoxes
                try:
                    if (x+i < self.x and x+i >= 0) and (y+j < self.y and y+j >= 0):
                        if (revealedBoxes[x+i][y+j] == False) and ([x+i,y+j] in self.blackList):
                            numberofBlacklisted += 1
                except:
                    pass
        return numberofBlacklisted

    def clear_Lists_total(self):
        self.checkedBoxes = np.empty((1,0))
        self.checkedNumbers.clear()
        self.blackList.clear()