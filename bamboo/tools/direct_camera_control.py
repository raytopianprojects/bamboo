from bamboo.showbase.DirectObject import DirectObject
from .direct_util import *
from .direct_geometry import *
from .direct_globals import *
from .direct_selection import SelectionRay
from bamboo.interval.IntervalGlobal import Sequence, Func
from bamboo.directnotify import DirectNotifyGlobal
from bamboo.task import Task

CAM_MOVE_DURATION = 1.2
COA_MARKER_SF = 0.0075
Y_AXIS = Vec3(0, 1, 0)


class DirectCameraControl(DirectObject):

    notify = DirectNotifyGlobal.directNotify.newCategory('DirectCameraControl')

    def __init__(self):
        # Create the grid
        self.startT = 0.0
        self.startF = 0
        self.orthoViewRoll = 0.0
        self.lastView = 0
        self.coa = Point3(0, 100, 0)
        self.coaMarker = loader.loadModel('models/misc/sphere')
        self.coaMarker.setName('DirectCameraCOAMarker')
        self.coaMarker.setTransparency(1)
        self.coaMarker.setColor(1, 0, 0, 0)
        self.coaMarker.setPos(0, 100, 0)
        useDirectRenderStyle(self.coaMarker)
        self.coaMarkerPos = Point3(0)
        self.coaMarkerColorIval = None
        self.fLockCOA = 0
        self.nullHitPointCount = 0
        self.cqEntries = []
        self.coaMarkerRef = base.bamboo.group.attachNewNode('coaMarkerRef')
        self.camManipRef = base.bamboo.group.attachNewNode('camManipRef')
        self.switchDirBelowZero = True
        self.manipulateCameraTask = None
        self.manipulateCameraInterval = None

        t = CAM_MOVE_DURATION
        self.actionEvents = [
            ['DIRECT-mouse1', self.mouseRotateStart],
            ['DIRECT-mouse1Up', self.mouseDollyStop],
            ['DIRECT-mouse2', self.mouseFlyStart],
            ['DIRECT-mouse2Up', self.mouseFlyStop],
            ['DIRECT-mouse3', self.mouseDollyStart],
            ['DIRECT-mouse3Up', self.mouseDollyStop],
        ]

        # [gjeon] moved all of the hotkeys to single place for easy remapping
# self.keyEvents = [
# ['c', self.centerCamIn, 0.5],
# ['f', self.fitOnWidget],                  # Note: This function doesn't work as intended
# ['h', self.homeCam],
# ['shift-v', self.toggleMarkerVis],
# ['m', self.moveToFit],                      # Note: This function doesn't work as intended; the object dissappears and screen flashes
# ['n', self.pickNextCOA],
# ['u', self.orbitUprightCam],
# ['shift-u', self.uprightCam],
# [repr(1), self.spawnMoveToView, 1],
# [repr(2), self.spawnMoveToView, 2],
# [repr(3), self.spawnMoveToView, 3],
# [repr(4), self.spawnMoveToView, 4],
# [repr(5), self.spawnMoveToView, 5],
# [repr(6), self.spawnMoveToView, 6],
# [repr(7), self.spawnMoveToView, 7],
# [repr(8), self.spawnMoveToView, 8],
# ['9', self.swingCamAboutWidget, -90.0, t],
# ['0', self.swingCamAboutWidget,  90.0, t],
# ['`', self.removeManipulateCameraTask],
# ['=', self.zoomCam, 0.5, t],
# ['+', self.zoomCam, 0.5, t],
# ['-', self.zoomCam, -2.0, t],
# ['_', self.zoomCam, -2.0, t],
# ]

        self.keyEvents = [
            ['DIRECT-centerCamIn', self.centerCamIn, 0.5],
            # Note: This function doesn't work as intended
            ['DIRECT-fitOnWidget', self.fitOnWidget],
            ['DIRECT-homeCam', self.homeCam],
            ['DIRECT-toggleMarkerVis', self.toggleMarkerVis],
            # Note: This function doesn't work as intended; the object dissappears and screen flashes
            ['DIRECT-moveToFit', self.moveToFit],
            ['DIRECT-pickNextCOA', self.pickNextCOA],
            ['DIRECT-orbitUprightCam', self.orbitUprightCam],
            ['DIRECT-uprightCam', self.uprightCam],
            ['DIRECT-spwanMoveToView-1', self.spawnMoveToView, 1],
            ['DIRECT-spwanMoveToView-2', self.spawnMoveToView, 2],
            ['DIRECT-spwanMoveToView-3', self.spawnMoveToView, 3],
            ['DIRECT-spwanMoveToView-4', self.spawnMoveToView, 4],
            ['DIRECT-spwanMoveToView-5', self.spawnMoveToView, 5],
            ['DIRECT-spwanMoveToView-6', self.spawnMoveToView, 6],
            ['DIRECT-spwanMoveToView-7', self.spawnMoveToView, 7],
            ['DIRECT-spwanMoveToView-8', self.spawnMoveToView, 8],
            ['DIRECT-swingCamAboutWidget-0', self.swingCamAboutWidget, -90.0, t],
            ['DIRECT-swingCamAboutWidget-1', self.swingCamAboutWidget,  90.0, t],
            ['DIRECT-removeManipulateCameraTask', self.removeManipulateCameraTask],
            ['DIRECT-zoomInCam', self.zoomCam, 0.5, t],
            ['DIRECT-zoomOutCam', self.zoomCam, -2.0, t],
        ]
        # set this to true to prevent the camera from rolling
        self.lockRoll = False
        # NIK - flag to determine whether to use maya camera controls
        self.useMayaCamControls = 0
        self.altDown = 0
        self.perspCollPlane = None  # [gjeon] used for new LE
        self.perspCollPlane2 = None  # [gjeon] used for new LE

    def toggleMarkerVis(self):
        # if base.bamboo.cameraControl.coaMarker.isHidden():
        # base.bamboo.cameraControl.coaMarker.show()
        # else:
        # base.bamboo.cameraControl.coaMarker.hide()

        if self.coaMarker.isHidden():
            self.coaMarker.show()
        else:
            self.coaMarker.hide()

    def mouseRotateStart(self, modifiers):
        if self.useMayaCamControls and modifiers == 4:          # alt is pressed - use maya controls
            # base.bamboo.pushUndo([base.bamboo.camera])        # Wasteful use of undo
            self.spawnMouseRotateTask()

    def mouseDollyStart(self, modifiers):
        if self.useMayaCamControls and modifiers == 4:  # alt is pressed - use maya controls
            # Hide the marker for this kind of motion
            self.coaMarker.hide()
            # Record time of start of mouse interaction
            self.startT = globalClock.getFrameTime()
            self.startF = globalClock.getFrameCount()
            # If the cam is orthogonal, spawn differentTask
            if hasattr(base.direct, "manipulationControl") and base.bamboo.manipulationControl.fMultiView and\
               base.bamboo.camera.getName() != 'persp':
                self.spawnOrthoZoom()
            else:
                # Start manipulation
                self.spawnHPanYZoom()

    def __stopManipulateCamera(self):
        if self.manipulateCameraTask:
            taskMgr.remove(self.manipulateCameraTask)
            self.manipulateCameraTask = None

        if self.manipulateCameraInterval:
            self.manipulateCameraInterval.finish()
            self.manipulateCameraInterval = None

    def __startManipulateCamera(self, func=None, task=None, ival=None):
        self.__stopManipulateCamera()
        if func:
            assert (task is None)
            task = Task.Task(func)
        if task:
            self.manipulateCameraTask = taskMgr.add(task, 'manipulateCamera')
        if ival:
            ival.start()
            self.manipulateCameraInterval = ival

    def mouseDollyStop(self):
        self.__stopManipulateCamera()

    def mouseFlyStart(self, modifiers):
        # Record undo point
        # base.bamboo.pushUndo([base.bamboo.camera])            # Wasteful use of undo
        if self.useMayaCamControls and modifiers == 4:          # alt is down, use maya controls
            # Hide the marker for this kind of motion
            self.coaMarker.hide()
            # Record time of start of mouse interaction
            self.startT = globalClock.getFrameTime()
            self.startF = globalClock.getFrameCount()
            # Start manipulation
            # If the cam is orthogonal, spawn differentTask
            if hasattr(base.direct, "manipulationControl") and base.bamboo.manipulationControl.fMultiView and\
               base.bamboo.camera.getName() != 'persp':
                self.spawnOrthoTranslate()
            else:
                self.spawnXZTranslate()
            self.altDown = 1
        elif not self.useMayaCamControls:
            # Where are we in the display region?
            if ((abs(base.bamboo.dr.mouseX) < 0.9) and (abs(base.bamboo.dr.mouseY) < 0.9)):
                # MOUSE IS IN CENTRAL REGION
                # Hide the marker for this kind of motion
                self.coaMarker.hide()
                # Record time of start of mouse interaction
                self.startT = globalClock.getFrameTime()
                self.startF = globalClock.getFrameCount()
                # Start manipulation
                self.spawnXZTranslateOrHPanYZoom()
                # END MOUSE IN CENTRAL REGION
            else:
                if ((abs(base.bamboo.dr.mouseX) > 0.9) and
                        (abs(base.bamboo.dr.mouseY) > 0.9)):
                    # Mouse is in corners, spawn roll task
                    self.spawnMouseRollTask()
                else:
                    # Mouse is in outer frame, spawn mouseRotateTask
                    self.spawnMouseRotateTask()
        if not modifiers == 4:
            self.altDown = 0

    def mouseFlyStop(self):
        self.__stopManipulateCamera()
        stopT = globalClock.getFrameTime()
        deltaT = stopT - self.startT
        stopF = globalClock.getFrameCount()
        deltaF = stopF - self.startF
        # No reason this shouldn't work with Maya cam on
        # if not self.useMayaCamControls and (deltaT <= 0.25) or (deltaF <= 1):

        # Do this when not trying to manipulate camera
        if not self.altDown and len(base.bamboo.selected.getSelectedAsList()) == 0:
            # Check for a hit point based on
            # current mouse position
            # Allow intersection with unpickable objects
            # And then spawn task to determine mouse mode
            # Don't intersect with hidden or backfacing objects
            skipFlags = SKIP_HIDDEN | SKIP_BACKFACE
            # Skip camera (and its children), unless control key is pressed
            skipFlags |= SKIP_CAMERA * (1 - base.getControl())
            self.computeCOA(base.bamboo.iRay.pickGeom(skipFlags=skipFlags))
            # Record reference point
            self.coaMarkerRef.setPosHprScale(
                base.cam, 0, 0, 0, 0, 0, 0, 1, 1, 1)
            # Record entries
            self.cqEntries = []
            for i in range(base.bamboo.iRay.getNumEntries()):
                self.cqEntries.append(base.bamboo.iRay.getEntry(i))
        # Show the marker
        self.coaMarker.show()
        # Resize it
        self.updateCoaMarkerSize()

    def mouseFlyStartTopWin(self):
        print("Moving mouse 2 in new window")
        # altIsDown = base.getAlt()
        # if altIsDown:
        #    print "Alt is down"

    def mouseFlyStopTopWin(self):
        print("Stopping mouse 2 in new window")

    def spawnXZTranslateOrHPanYZoom(self):
        # Kill any existing tasks
        self.__stopManipulateCamera()
        # Spawn the new task
        t = Task.Task(self.XZTranslateOrHPanYZoomTask)
        # For HPanYZoom
        t.zoomSF = Vec3(self.coaMarker.getPos(base.bamboo.camera)).length()
        self.__startManipulateCamera(task=t)

    def spawnXZTranslateOrHPPan(self):
        # Kill any existing tasks
        self.__stopManipulateCamera()
        # Spawn new task
        self.__startManipulateCamera(func=self.XZTranslateOrHPPanTask)

    def spawnXZTranslate(self):
        # Kill any existing tasks
        self.__stopManipulateCamera()
        # Spawn new task
        self.__startManipulateCamera(func=self.XZTranslateTask)

    def spawnOrthoTranslate(self):
        # Kill any existing tasks
        self.__stopManipulateCamera()
        # Spawn new task
        self.__startManipulateCamera(func=self.OrthoTranslateTask)

    def spawnHPanYZoom(self):
        # Kill any existing tasks
        self.__stopManipulateCamera()
        # Spawn new task
        t = Task.Task(self.HPanYZoomTask)
        t.zoomSF = Vec3(self.coaMarker.getPos(base.bamboo.camera)).length()
        self.__startManipulateCamera(task=t)

    def spawnOrthoZoom(self):
        # Kill any existing tasks
        self.__stopManipulateCamera()
        # Spawn new task
        t = Task.Task(self.OrthoZoomTask)
        self.__startManipulateCamera(task=t)

    def spawnHPPan(self):
        # Kill any existing tasks
        self.__stopManipulateCamera()
        # Spawn new task
        self.__startManipulateCamera(func=self.HPPanTask)

    def XZTranslateOrHPanYZoomTask(self, state):
        if base.bamboo.fShift:
            return self.XZTranslateTask(state)
        else:
            return self.HPanYZoomTask(state)

    def XZTranslateOrHPPanTask(self, state):
        if base.bamboo.fShift:
            # Panning action
            return self.HPPanTask(state)
        else:
            # Translation action
            return self.XZTranslateTask(state)

    def XZTranslateTask(self, state):
        coaDist = Vec3(self.coaMarker.getPos(base.bamboo.camera)).length()
        xlateSF = (coaDist / base.bamboo.dr.near)
        base.bamboo.camera.setPos(base.bamboo.camera,
                                  (-0.5 * base.bamboo.dr.mouseDeltaX *
                                   base.bamboo.dr.nearWidth *
                                   xlateSF),
                                  0.0,
                                  (-0.5 * base.bamboo.dr.mouseDeltaY *
                                      base.bamboo.dr.nearHeight *
                                      xlateSF))
        return Task.cont

    def OrthoTranslateTask(self, state):
        # create ray from the camera to detect 3d position
        iRay = SelectionRay(base.bamboo.camera)
        iRay.collider.setFromLens(
            base.bamboo.cam_node, base.bamboo.dr.mouseX, base.bamboo.dr.mouseY)
        # iRay.collideWithBitMask(1)
        iRay.collideWithBitMask(BitMask32.bit(21))
        iRay.ct.traverse(base.bamboo.grid)

        entry = iRay.getEntry(0)
        hitPt = entry.getSurfacePoint(entry.getFromNodePath())
        iRay.collisionNodePath.removeNode()
        del iRay
        if hasattr(state, 'prevPt'):
            base.bamboo.camera.setPos(
                base.bamboo.camera, (state.prevPt - hitPt))
        state.prevPt = hitPt
        return Task.cont

    def HPanYZoomTask(self, state):
        # If the cam is orthogonal, don't rotate or zoom.
        if (hasattr(base.bamboo.cam.node(), "getLens") and
                base.bamboo.cam.node().getLens().__class__.__name__ == "OrthographicLens"):
            return

        if base.bamboo.fControl:
            moveDir = Vec3(self.coaMarker.getPos(base.bamboo.camera))
            # If marker is behind camera invert vector
            if moveDir[1] < 0.0:
                moveDir.assign(moveDir * -1)
            moveDir.normalize()
        else:
            moveDir = Vec3(Y_AXIS)

        if self.useMayaCamControls:  # use maya controls
            moveDir.assign(moveDir * ((base.bamboo.dr.mouseDeltaX - 1.0 * base.bamboo.dr.mouseDeltaY)
                                      * state.zoomSF))
            hVal = 0.0
        else:
            moveDir.assign(moveDir * (-1.0 * base.bamboo.dr.mouseDeltaY *
                                      state.zoomSF))
            if base.bamboo.dr.mouseDeltaY > 0.0:
                moveDir.setY(moveDir[1] * 1.0)

            hVal = 0.5 * base.bamboo.dr.mouseDeltaX * base.bamboo.dr.fovH

        base.bamboo.camera.setPosHpr(base.bamboo.camera,
                                     moveDir[0],
                                     moveDir[1],
                                     moveDir[2],
                                     hVal,
                                     0.0, 0.0)
        if (self.lockRoll == True):
            # flatten roll
            base.bamboo.camera.setR(0)

        return Task.cont

    def OrthoZoomTask(self, state):
        filmSize = base.bamboo.cam_node.getLens().getFilmSize()
        factor = (base.bamboo.dr.mouseDeltaX - 1.0 *
                  base.bamboo.dr.mouseDeltaY) * 0.1
        x = base.bamboo.dr.getWidth()
        y = base.bamboo.dr.getHeight()
        base.bamboo.dr.orthoFactor -= factor
        if base.bamboo.dr.orthoFactor < 0:
            base.bamboo.dr.orthoFactor = 0.0001
        base.bamboo.dr.updateFilmSize(x, y)
        return Task.cont

    def HPPanTask(self, state):
        base.bamboo.camera.setHpr(base.bamboo.camera,
                                  (0.5 * base.bamboo.dr.mouseDeltaX *
                                   base.bamboo.dr.fovH),
                                  (-0.5 * base.bamboo.dr.mouseDeltaY *
                                      base.bamboo.dr.fovV),
                                  0.0)
        return Task.cont

    def spawnMouseRotateTask(self):
        # Kill any existing tasks
        self.__stopManipulateCamera()
        if self.perspCollPlane:
            iRay = SelectionRay(base.bamboo.camera)
            iRay.collider.setFromLens(base.bamboo.cam_node, 0.0, 0.0)
            iRay.collideWithBitMask(1)

            if base.bamboo.camera.getPos().getZ() >= 0:
                iRay.ct.traverse(self.perspCollPlane)
            else:
                iRay.ct.traverse(self.perspCollPlane2)

            if iRay.getNumEntries() > 0:
                entry = iRay.getEntry(0)
                hitPt = entry.getSurfacePoint(entry.getFromNodePath())

                # create a temp nodePath to get the position
                np = NodePath('temp')
                np.setPos(base.bamboo.camera, hitPt)
                self.coaMarkerPos = np.getPos()
                np.removeNode()
                self.coaMarker.setPos(self.coaMarkerPos)

            iRay.collisionNodePath.removeNode()
            del iRay

        # Set at markers position in render coordinates
        self.camManipRef.setPos(self.coaMarkerPos)
        self.camManipRef.setHpr(base.bamboo.camera, ZERO_POINT)
        t = Task.Task(self.mouseRotateTask)
        if abs(base.bamboo.dr.mouseX) > 0.9:
            t.constrainedDir = 'y'
        else:
            t.constrainedDir = 'x'
        self.__startManipulateCamera(task=t)

    def mouseRotateTask(self, state):
        # If the cam is orthogonal, don't rotate.
        if (hasattr(base.bamboo.cam.node(), "getLens") and
                base.bamboo.cam.node().getLens().__class__.__name__ == "OrthographicLens"):
            return
        # If moving outside of center, ignore motion perpendicular to edge
        if ((state.constrainedDir == 'y') and (abs(base.bamboo.dr.mouseX) > 0.9)):
            deltaX = 0
            deltaY = base.bamboo.dr.mouseDeltaY
        elif ((state.constrainedDir == 'x') and (abs(base.bamboo.dr.mouseY) > 0.9)):
            deltaX = base.bamboo.dr.mouseDeltaX
            deltaY = 0
        else:
            deltaX = base.bamboo.dr.mouseDeltaX
            deltaY = base.bamboo.dr.mouseDeltaY
        if base.bamboo.fShift:
            base.bamboo.camera.setHpr(base.bamboo.camera,
                                      (deltaX * base.bamboo.dr.fovH),
                                      (-deltaY * base.bamboo.dr.fovV),
                                      0.0)
            if (self.lockRoll == True):
                # flatten roll
                base.bamboo.camera.setR(0)
            self.camManipRef.setPos(self.coaMarkerPos)
            self.camManipRef.setHpr(base.bamboo.camera, ZERO_POINT)
        else:
            if base.bamboo.camera.getPos().getZ() >= 0 or not self.switchDirBelowZero:
                dirX = -1
            else:
                dirX = 1

            wrt = base.bamboo.camera.getTransform(self.camManipRef)
            self.camManipRef.setHpr(self.camManipRef,
                                    (dirX * deltaX * 180.0),
                                    (deltaY * 180.0),
                                    0.0)

            if (self.lockRoll == True):
                # flatten roll
                self.camManipRef.setR(0)
            base.bamboo.camera.setTransform(self.camManipRef, wrt)
        return Task.cont

    def spawnMouseRollTask(self):
        # Kill any existing tasks
        self.__stopManipulateCamera()
        # Set at markers position in render coordinates
        self.camManipRef.setPos(self.coaMarkerPos)
        self.camManipRef.setHpr(base.bamboo.camera, ZERO_POINT)
        t = Task.Task(self.mouseRollTask)
        t.coaCenter = getScreenXY(self.coaMarker)
        t.lastAngle = getCrankAngle(t.coaCenter)
        # Store the camera/manipRef offset transform
        t.wrt = base.bamboo.camera.getTransform(self.camManipRef)
        self.__startManipulateCamera(task=t)

    def mouseRollTask(self, state):
        wrt = state.wrt
        angle = getCrankAngle(state.coaCenter)
        deltaAngle = angle - state.lastAngle
        state.lastAngle = angle
        self.camManipRef.setHpr(self.camManipRef, 0, 0, deltaAngle)
        if (self.lockRoll == True):
            # flatten roll
            self.camManipRef.setR(0)
        base.bamboo.camera.setTransform(self.camManipRef, wrt)
        return Task.cont

    def lockCOA(self):
        self.fLockCOA = 1
        base.bamboo.message('COA Lock On')

    def unlockCOA(self):
        self.fLockCOA = 0
        base.bamboo.message('COA Lock Off')

    def toggleCOALock(self):
        self.fLockCOA = 1 - self.fLockCOA
        if self.fLockCOA:
            base.bamboo.message('COA Lock On')
        else:
            base.bamboo.message('COA Lock Off')

    def pickNextCOA(self):
        """ Cycle through collision handler entries """
        if self.cqEntries:
            # Get next entry and rotate entries
            entry = self.cqEntries[0]
            self.cqEntries = self.cqEntries[1:] + self.cqEntries[:1]
            # Filter out object's under camera
            nodePath = entry.getIntoNodePath()
            if base.bamboo.camera not in nodePath.getAncestors():
                # Compute new hit point
                hitPt = entry.getSurfacePoint(entry.getFromNodePath())
                # Move coa marker to new point
                self.updateCoa(hitPt, ref=self.coaMarkerRef)
            else:
                # Remove offending entry
                self.cqEntries = self.cqEntries[:-1]
                self.pickNextCOA()

    def computeCOA(self, entry):
        coa = Point3(0)
        dr = base.bamboo.drList.getCurrentDr()
        if self.fLockCOA:
            # COA is locked, use existing point
            # Use existing point
            coa.assign(self.coaMarker.getPos(base.bamboo.camera))
            # Reset hit point count
            self.nullHitPointCount = 0
        elif entry:
            # Got a hit point (hit point is in camera coordinates)
            # Set center of action
            hitPt = entry.getSurfacePoint(entry.getFromNodePath())
            hitPtDist = Vec3(hitPt).length()
            coa.assign(hitPt)
            # Handle case of bad coa point (too close or too far)
            if ((hitPtDist < (1.1 * dr.near)) or
                    (hitPtDist > dr.far)):
                # Just use existing point
                coa.assign(self.coaMarker.getPos(base.bamboo.camera))
            # Reset hit point count
            self.nullHitPointCount = 0
        else:
            # Increment null hit point count
            self.nullHitPointCount = (self.nullHitPointCount + 1) % 7
            # No COA lock and no intersection point
            # Use a point out in front of camera
            # Distance to point increases on multiple null hit points
            # MRM: Would be nice to be able to control this
            # At least display it
            dist = pow(10.0, self.nullHitPointCount)
            base.bamboo.message('COA Distance: ' + repr(dist))
            coa.set(0, dist, 0)
        # Compute COA Dist
        coaDist = Vec3(coa - ZERO_POINT).length()
        if coaDist < (1.1 * dr.near):
            coa.set(0, 100, 0)
            coaDist = 100
        # Update coa and marker
        self.updateCoa(coa, coaDist=coaDist)

    def updateCoa(self, ref2point, coaDist=None, ref=None):
        self.coa.set(ref2point[0], ref2point[1], ref2point[2])
        if not coaDist:
            coaDist = Vec3(self.coa - ZERO_POINT).length()
        # Place the marker in render space
        if ref == None:
            # KEH: use the current display region
            # ref = base.cam
            ref = base.bamboo.drList.getCurrentDr().cam
        self.coaMarker.setPos(ref, self.coa)
        pos = self.coaMarker.getPos()
        self.coaMarker.setPosHprScale(pos, Vec3(0), Vec3(1))
        # Resize it
        self.updateCoaMarkerSize(coaDist)
        # Record marker pos in render space
        self.coaMarkerPos.assign(self.coaMarker.getPos())

    def updateCoaMarkerSizeOnDeath(self):
        # Needed because tasks pass in state as first arg
        self.updateCoaMarkerSize()

    def updateCoaMarkerSize(self, coaDist=None):
        if not coaDist:
            coaDist = Vec3(self.coaMarker.getPos(base.bamboo.camera)).length()
        # Nominal size based on default 30 degree vertical FOV
        # Need to adjust size based on distance and current FOV
        sf = COA_MARKER_SF * coaDist * \
            (base.bamboo.drList.getCurrentDr().fovV/30.0)
        if sf == 0.0:
            sf = 0.1
        self.coaMarker.setScale(sf)
        # Lerp color to fade out
        if self.coaMarkerColorIval:
            self.coaMarkerColorIval.finish()
        self.coaMarkerColorIval = Sequence(
            Func(self.coaMarker.unstash),
            self.coaMarker.colorInterval(1.5, Vec4(1, 0, 0, 0),
                                         startColor=Vec4(1, 0, 0, 1),
                                         blendType='easeInOut'),
            Func(self.coaMarker.stash)
        )
        self.coaMarkerColorIval.start()

    def homeCam(self):
        # Record undo point
        base.bamboo.pushUndo([base.bamboo.camera])
        base.bamboo.camera.reparentTo(render)
        base.bamboo.camera.clearMat()
        # Resize coa marker
        self.updateCoaMarkerSize()

    def uprightCam(self):
        self.__stopManipulateCamera()
        # Record undo point
        base.bamboo.pushUndo([base.bamboo.camera])
        # Pitch camera till upright
        currH = base.bamboo.camera.getH()
        ival = base.bamboo.camera.hprInterval(CAM_MOVE_DURATION,
                                              (currH, 0, 0),
                                              other=render,
                                              blendType='easeInOut',
                                              name='manipulateCamera')
        self.__startManipulateCamera(ival=ival)

    def orbitUprightCam(self):
        self.__stopManipulateCamera()
        # Record undo point
        base.bamboo.pushUndo([base.bamboo.camera])
        # Transform camera z axis to render space
        # [gjeon] fixed to give required argument
        mCam2Render = Mat4(Mat4.identMat())
        mCam2Render.assign(base.bamboo.camera.getMat(render))
        zAxis = Vec3(mCam2Render.xformVec(Z_AXIS))
        zAxis.normalize()
        # Compute rotation angle needed to upright cam
        orbitAngle = rad2Deg(math.acos(CLAMP(zAxis.dot(Z_AXIS), -1, 1)))
        # Check angle
        if orbitAngle < 0.1:
            # Already upright
            return
        # Compute orthogonal axis of rotation
        rotAxis = Vec3(zAxis.cross(Z_AXIS))
        rotAxis.normalize()
        # Find angle between rot Axis and render X_AXIS
        rotAngle = rad2Deg(math.acos(CLAMP(rotAxis.dot(X_AXIS), -1, 1)))
        # Determine sign or rotation angle
        if rotAxis[1] < 0:
            rotAngle *= -1
        # Position ref CS at coa marker with xaxis aligned with rot axis
        self.camManipRef.setPos(self.coaMarker, Vec3(0))
        self.camManipRef.setHpr(render, rotAngle, 0, 0)
        # Reparent Cam to ref Coordinate system
        parent = base.bamboo.camera.getParent()
        base.bamboo.camera.wrtReparentTo(self.camManipRef)
        # Rotate ref CS to final orientation
        ival = self.camManipRef.hprInterval(CAM_MOVE_DURATION,
                                            (rotAngle, orbitAngle, 0),
                                            other=render,
                                            blendType='easeInOut')
        ival = Sequence(ival, Func(self.reparentCam, parent),
                        name='manipulateCamera')
        self.__startManipulateCamera(ival=ival)

    def centerCam(self):
        self.centerCamIn(1.0)

    def centerCamNow(self):
        self.centerCamIn(0.)

    def centerCamIn(self, t):
        self.__stopManipulateCamera()
        # Record undo point
        base.bamboo.pushUndo([base.bamboo.camera])
        # Determine marker location
        markerToCam = self.coaMarker.getPos(base.bamboo.camera)
        dist = Vec3(markerToCam - ZERO_POINT).length()
        scaledCenterVec = Y_AXIS * dist
        delta = markerToCam - scaledCenterVec
        self.camManipRef.setPosHpr(base.bamboo.camera, Point3(0), Point3(0))
        ival = base.bamboo.camera.posInterval(CAM_MOVE_DURATION,
                                              Point3(delta),
                                              other=self.camManipRef,
                                              blendType='easeInOut')
        ival = Sequence(ival, Func(self.updateCoaMarkerSizeOnDeath),
                        name='manipulateCamera')
        self.__startManipulateCamera(ival=ival)

    def zoomCam(self, zoomFactor, t):
        self.__stopManipulateCamera()
        # Record undo point
        base.bamboo.pushUndo([base.bamboo.camera])
        # Find a point zoom factor times the current separation
        # of the widget and cam
        zoomPtToCam = self.coaMarker.getPos(base.bamboo.camera) * zoomFactor
        # Put a target nodePath there
        self.camManipRef.setPos(base.bamboo.camera, zoomPtToCam)
        # Move to that point
        ival = base.bamboo.camera.posInterval(CAM_MOVE_DURATION,
                                              ZERO_POINT,
                                              other=self.camManipRef,
                                              blendType='easeInOut')
        ival = Sequence(ival, Func(self.updateCoaMarkerSizeOnDeath),
                        name='manipulateCamera')
        self.__startManipulateCamera(ival=ival)

    def spawnMoveToView(self, view):
        # Kill any existing tasks
        self.__stopManipulateCamera()
        # Record undo point
        base.bamboo.pushUndo([base.bamboo.camera])
        # Calc hprOffset
        hprOffset = VBase3()
        if view == 8:
            # Try the next roll angle
            self.orthoViewRoll = (self.orthoViewRoll + 90.0) % 360.0
            # but use the last view
            view = self.lastView
        else:
            self.orthoViewRoll = 0.0
        # Adjust offset based on specified view
        if view == 1:
            hprOffset.set(180., 0., 0.)
        elif view == 2:
            hprOffset.set(0., 0., 0.)
        elif view == 3:
            hprOffset.set(90., 0., 0.)
        elif view == 4:
            hprOffset.set(-90., 0., 0.)
        elif view == 5:
            hprOffset.set(0., -90., 0.)
        elif view == 6:
            hprOffset.set(0., 90., 0.)
        elif view == 7:
            hprOffset.set(135., -35.264, 0.)
        # Position target
        self.camManipRef.setPosHpr(self.coaMarker, ZERO_VEC,
                                   hprOffset)
        # Scale center vec by current distance to target
        offsetDistance = Vec3(base.bamboo.camera.getPos(self.camManipRef) -
                              ZERO_POINT).length()
        scaledCenterVec = Y_AXIS * (-1.0 * offsetDistance)
        # Now put the camManipRef at that point
        self.camManipRef.setPosHpr(self.camManipRef,
                                   scaledCenterVec,
                                   ZERO_VEC)
        # Record view for next time around
        self.lastView = view
        ival = base.bamboo.camera.posHprInterval(CAM_MOVE_DURATION,
                                                 pos=ZERO_POINT,
                                                 hpr=VBase3(
                                                     0, 0, self.orthoViewRoll),
                                                 other=self.camManipRef,
                                                 blendType='easeInOut')
        ival = Sequence(ival, Func(self.updateCoaMarkerSizeOnDeath),
                        name='manipulateCamera')
        self.__startManipulateCamera(ival=ival)

    def swingCamAboutWidget(self, degrees, t):
        # Remove existing camera manipulation task
        self.__stopManipulateCamera()

        # Record undo point
        base.bamboo.pushUndo([base.bamboo.camera])

        # Coincident with widget
        self.camManipRef.setPos(self.coaMarker, ZERO_POINT)
        # But aligned with render space
        self.camManipRef.setHpr(ZERO_POINT)

        parent = base.bamboo.camera.getParent()
        base.bamboo.camera.wrtReparentTo(self.camManipRef)

        ival = self.camManipRef.hprInterval(CAM_MOVE_DURATION,
                                            VBase3(degrees, 0, 0),
                                            blendType='easeInOut')
        ival = Sequence(ival, Func(self.reparentCam, parent),
                        name='manipulateCamera')
        self.__startManipulateCamera(ival=ival)

    def reparentCam(self, parent):
        base.bamboo.camera.wrtReparentTo(parent)
        self.updateCoaMarkerSize()

    def fitOnWidget(self, nodePath='None Given'):
        # Fit the node on the screen
        # stop any ongoing tasks
        self.__stopManipulateCamera()
        # How big is the node?
        nodeScale = base.bamboo.widget.scalingNode.getScale(render)
        maxScale = max(nodeScale[0], nodeScale[1], nodeScale[2])
        maxDim = min(base.bamboo.dr.nearWidth, base.bamboo.dr.nearHeight)

        # At what distance does the object fill 30% of the screen?
        # Assuming radius of 1 on widget
        camY = base.bamboo.dr.near * (2.0 * maxScale)/(0.3 * maxDim)

        # What is the vector through the center of the screen?
        centerVec = Y_AXIS * camY

        # Where is the node relative to the viewpoint
        vWidget2Camera = base.bamboo.widget.getPos(base.bamboo.camera)

        # How far do you move the camera to be this distance from the node?
        deltaMove = vWidget2Camera - centerVec

        # Move a target there
        try:
            self.camManipRef.setPos(base.bamboo.camera, deltaMove)
        except Exception:
            self.notify.debug

        parent = base.bamboo.camera.getParent()
        base.bamboo.camera.wrtReparentTo(self.camManipRef)
        ival = base.bamboo.camera.posInterval(CAM_MOVE_DURATION,
                                              Point3(0, 0, 0),
                                              blendType='easeInOut')
        ival = Sequence(ival, Func(self.reparentCam, parent),
                        name='manipulateCamera')
        self.__startManipulateCamera(ival=ival)

    def moveToFit(self):
        # How big is the active widget?
        widgetScale = base.bamboo.widget.scalingNode.getScale(render)
        maxScale = max(widgetScale[0], widgetScale[1], widgetScale[2])
        # At what distance does the widget fill 50% of the screen?
        camY = ((2 * base.bamboo.dr.near * (1.5 * maxScale)) /
                min(base.bamboo.dr.nearWidth, base.bamboo.dr.nearHeight))
        # Find a point this distance along the Y axis
        # MRM: This needs to be generalized to support non uniform frusta
        centerVec = Y_AXIS * camY
        # Before moving, record the relationship between the selected nodes
        # and the widget, so that this can be maintained
        base.bamboo.selected.getWrtAll()
        # Push state onto undo stack
        base.bamboo.pushUndo(base.bamboo.selected)
        # Remove the task to keep the widget attached to the object
        taskMgr.remove('followSelectedNodePath')
        # Spawn a task to keep the selected objects with the widget
        taskMgr.add(self.stickToWidgetTask, 'stickToWidget')
        # Spawn a task to move the widget
        ival = base.bamboo.widget.posInterval(CAM_MOVE_DURATION,
                                              Point3(centerVec),
                                              other=base.bamboo.camera,
                                              blendType='easeInOut')
        ival = Sequence(ival, Func(lambda: taskMgr.remove('stickToWidget')),
                        name='moveToFit')
        ival.start()

    def stickToWidgetTask(self, state):
        # Move the objects with the widget
        base.bamboo.selected.moveWrtWidgetAll()
        # Continue
        return Task.cont

    def enableMouseFly(self, fKeyEvents=1):
        # disable C++ fly interface
        base.disable_mouse()
        # Enable events
        for event in self.actionEvents:
            self.accept(event[0], event[1], extraArgs=event[2:])
        if fKeyEvents:
            for event in self.keyEvents:
                self.accept(event[0], event[1], extraArgs=event[2:])
        # Show marker
        self.coaMarker.reparentTo(base.bamboo.group)

    def disableMouseFly(self):
        # Hide the marker
        self.coaMarker.reparentTo(hidden)
        # Ignore events
        for event in self.actionEvents:
            self.ignore(event[0])
        for event in self.keyEvents:
            self.ignore(event[0])
        # Kill tasks
        self.removeManipulateCameraTask()
        taskMgr.remove('stickToWidget')
        base.enable_mouse()

    def removeManipulateCameraTask(self):
        self.__stopManipulateCamera()
