# runAppWithScreensDemo2.py
# This version works in both the sandbox and on the desktop.
# It does so by including the definition of runAppWithScreens, which
# is not yet in the desktop's cmu_graphics file.  It also has a modified
# import that works both in the sandbox and on the desktop.

try: from cmu_cs3_graphics import *
except: from cmu_graphics import *

import inspect

##################################################################
# runAppWithScreens() and setActiveScreen(screen)
##################################################################

def runAppWithScreens(initialScreen, *args, **kwargs):
    global _callerGlobals
    _callerGlobals = inspect.stack()[1][0].f_globals

    appFnNames = ['onAppStart',
                  'onKeyPress', 'onKeyHold', 'onKeyRelease',
                  'onMousePress', 'onMouseDrag', 'onMouseRelease',
                  'onMouseMove', 'onStep', 'redrawAll']
             
    def checkForAppFns():
        globalVars = _callerGlobals # globals()
        for appFnName in appFnNames:
            if appFnName in globalVars:
                raise Exception(f'Do not define {appFnName} when using screens')
   
    def getScreenFnNames(appFnName):
        globalVars = _callerGlobals # globals()
        screenFnNames = [ ]
        for globalVarName in globalVars:
            screenAppSuffix = f'_{appFnName}'
            if globalVarName.endswith(screenAppSuffix):
                screenFnNames.append(globalVarName)
        return screenFnNames
   
    def wrapScreenFns():
        globalVars = _callerGlobals # globals()
        for appFnName in appFnNames:
            screenFnNames = getScreenFnNames(appFnName)
            if (screenFnNames != [ ]) or (appFnName == 'onAppStart'):
                globalVars[appFnName] = makeAppFnWrapper(appFnName)
   
    def makeAppFnWrapper(appFnName):
        if appFnName == 'onAppStart':
            def onAppStartWrapper(app):
                globalVars = _callerGlobals # globals()
                for screenFnName in getScreenFnNames('onScreenStart'):
                    screenFn = globalVars[screenFnName]
                    screenFn(app)
            return onAppStartWrapper
        else:
            def appFnWrapper(*args):
                globalVars = _callerGlobals # globals()
                screen = globalVars['_activeScreen']
                wrappedFnName = ('onScreenStart'
                                 if appFnName == 'onAppStart' else appFnName)
                screenFnName = f'{screen}_{wrappedFnName}'
                if screenFnName in globalVars:
                    screenFn = globalVars[screenFnName]
                    return screenFn(*args)
            return appFnWrapper

    def go():
        checkForAppFns()
        wrapScreenFns()
        setActiveScreen(initialScreen)
        runApp(*args, **kwargs)
   
    go()

def setActiveScreen(screen):
    globalVars = _callerGlobals # globals()
    if (screen in [None, '']) or (not isinstance(screen, str)):
        raise Exception(f'{repr(screen)} is not a valid screen')
    redrawAllFnName = f'{screen}_redrawAll'
    if redrawAllFnName not in globalVars:
        raise Exception(f'Screen {screen} requires {redrawAllFnName}()')
    globalVars['_activeScreen'] = screen

##################################################################
# end of runAppWithScreens() and setActiveScreen(screen)
##################################################################

##################################
# Screen1
##################################

# def screen1_onScreenStart(app):
#     app.color = 'gold'

# def screen1_onKeyPress(app, key):
#     if key == 's': setActiveScreen('screen2')
#     elif key == 'c': app.color = 'navy' if (app.color == 'gold') else 'gold'

# def screen1_redrawAll(app):
#     drawLabel('Screen 1', app.width/2, 30, size=16)
#     drawLabel('Press c to change square color', app.width/2, 50, size=16)
#     drawLabel('Press s to change screen to screen2', app.width/2, 70, size=16)
#     drawRect(100, 100, app.width-200, app.height-200, fill=app.color)

# ##################################
# # Screen2
# ##################################

# def screen2_onScreenStart(app):
#     app.cx = app.width/2
#     app.dx = 10

# def screen2_onKeyPress(app, key):
#     if key == 's': setActiveScreen('screen1')
#     elif key == 'd': app.dx = -app.dx

# def screen2_onStep(app):
#     app.cx = (app.cx + app.dx) % app.width

# def screen2_redrawAll(app):
#     drawLabel('Screen 2', app.width/2, 30, size=16)
#     drawLabel('Press d to change direction of dot', app.width/2, 50, size=16)
#     drawLabel('Press s to change the screen to screen1', app.width/2, 70, size=16)
#     drawCircle(app.cx, app.height/2, 50, fill='lightGreen')

# ##################################
# # main
# ##################################

# def main():
#     runAppWithScreens(initialScreen='screen1', width=800)

# main()