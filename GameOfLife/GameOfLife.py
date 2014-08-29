
import pygame, sys, time, os, itertools
from pygame.locals import*
from textbox import TextBox
from parser import parser

WINDOWHEIGHT = 600
WINDOWWIDTH = 800
LARGECELLSIZE = 20
NORMALCELLSIZE = 10
SMALLCELLSIZE = 5


FPS = 30

GREY = (133, 133, 133)
BLACK = (0, 0, 0)
DARKGREY = (50, 50, 50)
GREEN = (0, 255, 255)
WHITE = (255, 255, 255)
BLUE = (0, 0, 200)
BORDO = (141, 12, 12)
ORANGE = (255, 111, 0)
DARKBLUE = (0, 2, 70)
LIGHTGREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PINK = (255, 117, 255)
DARKPINK = (255, 0, 255)
BROWN = (118, 60, 35)

MENUCOLOR = BLUE 
TEXTCOLOR = BLACK


UP = True
DOWN = False


def main ():
    global DISPLAYSURF, BASICFONT, LARGEFONT, SMALLFONT, CLICKSOUND
    pygame.init ()
    pygame.display.set_caption ('Game Of Life')
    DISPLAYSURF = pygame.display.set_mode ((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font ('freesansbold.ttf', 32)
    SMALLFONT = pygame.font.Font ('freesansbold.ttf', 20)
    LARGEFONT = pygame.font.Font ('freesansbold.ttf', 64)
    while True: # main game loop
        game = EventLoop ()
        game.runGame ()


class EventLoop (object):

    def __init__ (self):
        self.string = ''
        self.board = set ()
        self.msg = ''
        self.cellSize = LARGECELLSIZE
        self.saveMode = False
        self.loadMode = False

    def runGame (self):
        FPSCLOCK = pygame.time.Clock()
        mouseButton = 0
        mouseDown = False
        pause = True
        activeFPS = 10
        generation = 1
        buttons = []
        mousey2 = 200
        mousex2 = 200 #arbitrary number
        history = []
        lastUpdate = 0
        menuHidden = False
        hideTime = 0
        optionsMode = False
        modeSwitch = False
        inputDelayStart = 0
        cellColor = DARKGREY
        bgColor = WHITE
        drawBox = False
    
        inPut = TextBox ((116, 483, 492, 41), command=self.getString, clear_on_enter=True)
        while True: # event loop
            DISPLAYSURF.fill (bgColor)
            mousex = None
            mousey = None
            hilight = None
            currentTime = time.time () # needed for time based events with menu hiding
                                       # and generations per second
            if currentTime - inputDelayStart < 0.5: # input delay
                modeSwitch = False
                pygame.event.clear ()
            for event in pygame.event.get ():
                if event.type == QUIT:
                    terminate ()
                elif event.type == KEYUP and not optionsMode:
                    if event.key == K_ESCAPE:
                        terminate ()
                    if event.key == K_SPACE:
                        if pause:
                            pause = False
                        else:    
                            pause = True
                    if event.key == K_EQUALS:
                        activeFPS = framesPerSecond (activeFPS, UP)
                    elif event.key == K_MINUS:
                        activeFPS = framesPerSecond (activeFPS, DOWN)
                    if event.key == K_r:
                        self.board = set ()
                        generation = 1
                        history = []
                    # buttons for regulating generations
                    if event.key == K_i and pause:
                        if history != []:
                            poppedBoard = history.pop ()
                            if self.board == poppedBoard and history != []:
                                self.board = history.pop ()
                            else:
                                self.board = poppedBoard
                            # we dont want negative numbers in gen count
                            generation -= 1
                            generation = max (1, generation)
                    elif event.key == K_o and pause:
                        self.board = advance (self.board)
                        history.append (self.board)
                        generation += 1
                    if event.key == K_h:
                        if menuHidden:
                            menuHidden = False
                            hideTime = 0
                        else:    
                            menuHidden = True
                            hideTime = time.time()
                elif event.type ==KEYUP:
                    if event.key == K_RETURN:
                        drawBox = False
                        self.saveMode = False
                        self.loadMode = False
                # mouse events
                elif event.type == MOUSEBUTTONDOWN:
                    mouseDown = True
                    mouseButton = event.button
                    mousex, mousey = event.pos
                elif event.type == MOUSEBUTTONUP:
                    mousex, mousey = event.pos 
                    mouseButton = event.button
                    mouseDown = False
                if event.type == MOUSEMOTION:
                    if mouseDown == True:
                        mousex, mousey = event.pos # for filling/emptying cells
                    mousex2, mousey2 = event.pos # for menu
                inPut.get_event (event)
            if pause  and not optionsMode:
                if mousex != None:
                    x, y = convertCellCoords (mousex, mousey, self.cellSize)
                    if mouseButton == 1 and not inMenuZone (mousex, mousey, menuHidden): 
                        self.board.add ((x, y)) 
                    elif mouseButton == 3:
                        self.board.discard ((x, y))
                    history.insert (generation - 1, self.board)
            elif not optionsMode:
                if history == []:
                     history.append (self.board)
                if currentTime - lastUpdate > 1.000/activeFPS:
                    self.board = advance (self.board) 
                    lastUpdate = time.time ()
                    generation += 1
                    history.append (self.board)
            
            # draw everything
            drawCells (self.board, self.cellSize, cellColor)
            drawGrid (self.cellSize)
    
            
            if not menuHidden and not optionsMode:
                 if buttons != []:
                     for butt in range (len (buttons)):
                         if buttons[butt][1].collidepoint (mousex2, mousey2):
                             hilight = butt
                 # handles button presses
                 if buttons != []:
                     if buttons[0][1].collidepoint (mousex2, mousey2) and mouseDown:
                         self.board = set ()
                         history = []
                         generation = 1
                     elif buttons[2][1].collidepoint (mousex2, mousey2) and mouseDown:
                         pause = False
                     elif buttons[3][1].collidepoint (mousex2, mousey2) and mouseDown:
                         pause = True
                     elif buttons[4][1].collidepoint (mousex2, mousey2) and mouseDown:
                         activeFPS = framesPerSecond (activeFPS, DOWN)
                     elif buttons[5][1].collidepoint (mousex2, mousey2) and mouseDown:
                         activeFPS = framesPerSecond (activeFPS, UP)
                     elif buttons[7][1].collidepoint (mousex2, mousey2) and mouseDown:
                         pygame.event.post(pygame.event.Event (KEYUP, {'key':105, 'mod':0}))
                     elif buttons[9][1].collidepoint (mousex2, mousey2) and mouseDown:
                         pygame.event.post(pygame.event.Event (KEYUP, {'key':111, 'mod':0}))
                         
                     elif buttons[11][1].collidepoint (mousex2, mousey2): 
                         drawImage ('images/kb.png')
    
                     elif buttons[1][1].collidepoint (mousex2, mousey2) and mouseDown:
                         optionsMode = True
    
                 
                 buttons = menuCraft (activeFPS, generation, bgColor, hilight)
            
                 drawMenu (buttons)
            else:
                if currentTime - hideTime < 3 and menuHidden: # hint time
                    drawHint ()
            #options 
            if optionsMode:
                control = OptControls (mousex2, mousey2, mouseDown) # options class
                drawImage ('images/sas.png') 
                printText (self.msg)
                if control.exitOptions ():
                    modeSwitch = True
                    inputDelayStart = time.time ()
                    optionsMode = False
                    drawBox = False
                    self.saveMode = False
                    self.loadMode = False
                    mouseDown = False
                if control.getColors () != None:
                    bgColor, cellColor = control.getColors ()
                if control.getCellSize () != None:
                    self.cellSize = control.getCellSize ()
                if control.loadPat ():
                    drawBox = True
                    self.loadMode = True
                if control.savePat ():
                    drawBox = True
                    self.saveMode = True
                if drawBox:
                    inPut.update ()
                    inPut.draw (DISPLAYSURF)
                pygame.display.flip ()

            pygame.display.update ()
            pygame.display.flip ()
            FPSCLOCK.tick (FPS)

    def getString (self, id, string):
        self.string = string
        if self.saveMode:
            self.stringSave (self.string)
        elif self.loadMode:
            self.stringLoad (self.string)

    def stringSave (self, string):
        filename = 'Patterns/' + string + '.cells'
        if os.path.exists (filename):
            self.msg ='%s already exists, pattern not saved' % filename
        else:
            self.msg = 'pattern saved as %s' % filename
            parser.writer (self.board, filename)

    def stringLoad (self, string):
        middle = self.findMiddleOfBoard ()
        filename = 'Patterns/' + string + '.cells'
        if os.path.exists (filename):
            self.board = parser.parser (filename, middle)
            self.msg ='%s Loaded' % filename
        else:
            self.msg = "File Doesn't Exist"

    def findMiddleOfBoard (self):
        boardHeight = WINDOWHEIGHT/self.cellSize
        boardWidth = WINDOWWIDTH/self.cellSize 
        boardMiddle = (boardWidth/2, boardHeight/2)
        return boardMiddle


def drawGrid (cellsize):
    for linex in range (cellsize, WINDOWWIDTH, cellsize):
        pygame.draw.line (DISPLAYSURF, GREY, (linex, 0), (linex, WINDOWHEIGHT))

    for liney in range (cellsize, WINDOWHEIGHT, cellsize):
        pygame.draw.line(DISPLAYSURF, GREY, (0,liney), (WINDOWWIDTH, liney))

def drawCells (board, cellsize, cellColor):
    if len(board) == 0:
        return
    for cell in board:
        cellx, celly = cell
        cellx *= cellsize
        celly *= cellsize
        pygame.draw.rect (DISPLAYSURF, cellColor, (cellx, celly, cellsize, cellsize))

def convertCellCoords (mousex, mousey, cellsize):
    x = mousex/cellsize
    y = mousey/cellsize
    
    return x, y

def neighbours (point):
    x, y = point
    yield x + 1, y
    yield x - 1, y
    yield x, y + 1
    yield x, y - 1
    yield x + 1, y + 1
    yield x + 1, y - 1
    yield x - 1, y + 1
    yield x - 1, y - 1

def advance (board):

    newstate = set ()
    recalc = board | set (itertools.chain(*map(neighbours, board)))
    for point in recalc:
	count = sum ((neigh in board)
		for neigh in neighbours (point))
	if count == 3 or (count == 2 and point in board):
		newstate.add(point)
    return newstate


def terminate ():
    pygame.quit ()
    sys.exit ()



def framesPerSecond (activeFPS, decision):
    modes = [1, 5, 10, 20, 40, 60]
    m = modes.index (activeFPS)
    if decision == UP and m != 5:
        activeFPS = modes[m + 1]
    elif decision == DOWN and m != 0:
        activeFPS = modes[m - 1]
    return activeFPS

def drawMenu (buttons):
    for butt in buttons:
        DISPLAYSURF.blit (butt[0], butt[1])


def getTextColor (buttonNum, bgColor, hilight):
    if buttonNum == hilight:
        textColor = BLUE
    elif bgColor == WHITE:
        textColor = BLACK
    elif bgColor == BLACK:
        textColor = WHITE

    return textColor

def menuCraft (activeFPS, generation,bgColor, hilight  = 0):
    buttons = []

    # gen and speed text shouldn't highligh
    # thats why they are gettin number 11,
    # which doesn't match with thei index number
    # therefore never highlighting.

    textColor = getTextColor (0, bgColor, hilight)
    ctrlSurf = BASICFONT.render ('Reset', True, textColor)
    ctrlRect = ctrlSurf.get_rect()
    ctrlRect.topleft = (0, WINDOWHEIGHT - 32) #32 is a fontsize
    buttons.append ((ctrlSurf, ctrlRect))

    textColor = getTextColor (1, bgColor, hilight)
    optSurf = BASICFONT.render ('Options', True, textColor)
    optRect = optSurf.get_rect()
    optRect.topright = (WINDOWWIDTH, WINDOWHEIGHT - 32)
    buttons.append ((optSurf, optRect))

    textColor = getTextColor (2, bgColor, hilight)
    playSurf = BASICFONT.render ('Play', True, textColor)
    playRect = playSurf.get_rect()
    playRect.topleft = (ctrlRect.right + 60, ctrlRect.top) 
    buttons.append ((playSurf, playRect))

    textColor = getTextColor (3, bgColor, hilight)
    stopSurf = BASICFONT.render ('Stop', True, textColor)
    stopRect = playSurf.get_rect()
    stopRect.topleft = (playRect.right + 60, playRect.top) 
    buttons.append ((stopSurf, stopRect))

    textColor = getTextColor (4, bgColor,  hilight)
    slowSurf = LARGEFONT.render ('-', True, textColor)
    slowRect = slowSurf.get_rect()
    slowRect.topleft = (stopRect.right + 60, WINDOWHEIGHT - 60)
    buttons.append ((slowSurf, slowRect))

    textColor = getTextColor (5, bgColor, hilight)
    fastSurf = LARGEFONT.render ('+', True, textColor)
    fastRect = fastSurf.get_rect()
    fastRect.topright = (optRect.left - 60, WINDOWHEIGHT - 60) # gap and fontsize
    buttons.append ((fastSurf, fastRect))

    textColor = getTextColor (12, bgColor, hilight)
    speedSurf = BASICFONT.render ('GPS : %d' % activeFPS, True, textColor) 
    speedRect = speedSurf.get_rect()
    speedRect.topleft = (slowRect.right + 12, WINDOWHEIGHT - 32) 
    buttons.append ((speedSurf, speedRect))

    textColor = getTextColor (7, bgColor, hilight)
    lessSurf = LARGEFONT.render ('-', True, textColor)
    lessRect = lessSurf.get_rect()
    lessRect.topleft = (0,-24) # gap and fontsize
    buttons.append ((lessSurf, lessRect))

    textColor = getTextColor (12, bgColor, hilight)
    genSurf = SMALLFONT.render ('Gen : %d' % generation, True, textColor) 
    genRect = genSurf.get_rect()
    genRect.topleft = (lessRect.right + 20, 10) 
    buttons.append ((genSurf, genRect))

    textColor = getTextColor (9, bgColor, hilight)
    moreSurf = LARGEFONT.render ('+', True, textColor)
    moreRect = moreSurf.get_rect()
    moreRect.topleft = (180, -24) # gap and fontsize
    buttons.append ((moreSurf, moreRect))

    textColor = getTextColor (10, bgColor, hilight)
    hideSurf = BASICFONT.render ('Hide Menu', True, textColor) 
    hideRect = hideSurf.get_rect()
    hideRect.topright = (WINDOWWIDTH, 0) 
    buttons.append ((hideSurf, hideRect))

    textColor = getTextColor (11, bgColor, hilight)
    keyBSurf = BASICFONT.render ('Key Binds', True, textColor)
    keyBRect = keyBSurf.get_rect()
    keyBRect.center = (WINDOWWIDTH/2, 16)
    buttons.append ((keyBSurf, keyBRect))

    return buttons
# Returns true, if coords is on the menu

def inMenuZone (x, y, menuHidden):
    if menuHidden:
        return False
    if x in range (0, WINDOWWIDTH) and y in range (0, 40):
        return True
    if x in range (0, WINDOWWIDTH) and y in range (WINDOWHEIGHT, WINDOWHEIGHT - 50, -1):
        return True
    else:
        return False

def drawHint ():
    hintSurf = BASICFONT.render ('Menu hidden, press "h" to reveal it.', True, BLACK) 
    hintRect = hintSurf.get_rect()
    hintRect.center = (WINDOWWIDTH/2, WINDOWHEIGHT/2) 

    DISPLAYSURF.blit ( hintSurf, hintRect)
    

def drawImage (image):
    imSurf = pygame.image.load (image)
    imRect = pygame.Rect (0, 0, WINDOWWIDTH, WINDOWHEIGHT)

    DISPLAYSURF.blit (imSurf, imRect)
    pygame.display.update ()


# made only for sas.png
class OptControls (object):

    def __init__(self, mousex, mousey, mouseDown):
        self.mousex = mousex
        self.mousey = mousey
        self.mouseDown = mouseDown
        self.exitRect = pygame.Rect ((626, 501, 89, 41))
        self.cellRect = [(25, 387, 74, 38), (333, 387, 76, 42), (620, 387, 77, 42)]
        self.themeRect = [(38, 145, 110, 45), (249, 145, 110, 45), 
                        (445, 145, 110, 45), (624, 145, 110, 45),
                        (38, 203, 110, 45), (249, 203, 110, 45),
                        (445, 205, 110, 45), (624, 203, 110, 45),
                        (38, 261, 110, 45), (249, 263, 110, 45),
                        (445, 261, 110, 45), (624, 263, 110, 45)]
        self.saveRect = (17, 449, 95, 37)
        self.loadRect = (16, 523, 93, 37)
        self.themes = ((WHITE, DARKGREY), (WHITE, BORDO), (WHITE, ORANGE), (WHITE, DARKBLUE), (BLACK, LIGHTGREEN), (BLACK, BORDO), (BLACK, WHITE), (BLACK, YELLOW), (WHITE, PINK), (WHITE, BROWN), (WHITE, YELLOW), (BLACK, DARKPINK)) 
        self.string = ''


    def exitOptions (self):
        if self.exitRect.collidepoint (self.mousex, self.mousey):
            pygame.draw.rect (DISPLAYSURF, BLUE, self.exitRect, 5)
        if self.exitRect.collidepoint (self.mousex, self.mousey) and self.mouseDown:
            return True
        else:
            return False 

    def getColors (self):
        for themeNum in range (len (self.themes)):
            themeRect = self.themeRect[themeNum]
            themeRect = pygame.Rect (themeRect)
            if themeRect.collidepoint (self.mousex, self.mousey):
                pygame.draw.rect (DISPLAYSURF, BLUE, themeRect, 5)

            if themeRect.collidepoint (self.mousex, self.mousey) and self.mouseDown:
                return self.themes[themeNum]

    def getCellSize (self):
        rectList = []
        for rect in self.cellRect:
            rect = pygame.Rect (rect)
            rectList.append (rect)

        for cellRect in rectList:
            if cellRect.collidepoint (self.mousex, self.mousey):
                pygame.draw.rect (DISPLAYSURF, BLUE, cellRect, 5) 
        if rectList[2].collidepoint (self.mousex, self.mousey) and self.mouseDown:
            cellsize = LARGECELLSIZE 
        elif rectList[1].collidepoint (self.mousex, self.mousey) and self.mouseDown:
            cellsize = NORMALCELLSIZE 
        elif rectList[0].collidepoint (self.mousex, self.mousey) and self.mouseDown:
            cellsize = SMALLCELLSIZE 
        else:
            return None

        return cellsize

    def loadPat (self):
        loadR = pygame.Rect (self.loadRect)
        if loadR.collidepoint (self.mousex, self.mousey):
            pygame.draw.rect (DISPLAYSURF, BLUE, loadR, 5)
        if loadR.collidepoint (self.mousex, self.mousey) and self.mouseDown:
            return True
        else:
            return False

    def savePat (self):
        saveR = pygame.Rect (self.saveRect)
        if saveR.collidepoint (self.mousex, self.mousey):
            pygame.draw.rect (DISPLAYSURF, BLUE, saveR, 5)
        if saveR.collidepoint (self.mousex, self.mousey) and self.mouseDown:
            return True
        else:
            return False
        
def printText (string):
    stringSurf = SMALLFONT.render (string, True, WHITE)
    stringRect = stringSurf.get_rect()
    stringRect.center = (371, 545) 

    DISPLAYSURF.blit (stringSurf, stringRect)
       
    
main () 
