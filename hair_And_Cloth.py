import bpy

from bpy.props import (
        StringProperty,
        IntProperty,
        PointerProperty,
        )

import math
from bpy.types import Operator
from mathutils import Vector

# DAMPING = 0.2  # how much to damp the cloth simulation each frame
CONSTRAINT_ITERATIONS = 15 # how many iterations of constraint satisfaction each frame (more is rigid, less is soft)

class ParticleCreaterUtils():
    # Just below are three global variables holding the actual animated stuff; Cloth and Ball 
    cloth1 = None 

    ball = None
    ball_pos = Vector((7, -5, 0)) # the center of our one ball
    ball_radius = 2 # the radius of our one ball
    ball_time = 0

    cloth = None

    # mesh arrays
    verts = []
    faces = []

    mesh = None
    
    
def updateMesh():
    #fill faces array
    count = 0
    pref = bpy.context.preferences.addons[__package__].preferences
    for i in range (0, pref.numY *(pref.numX-1)):
        if count < pref.numY-1:
            A = i
            B = i+1
            C = (i+ pref.numY)+1
            D = (i+ pref.numY)
            face = (A,B,C,D)
            ParticleCreaterUtils.faces.append(face)
            count = count + 1
        else:
            count = 0

class Particle():
    movable = True  # can the particle move or not ? used to pin parts of the cloth
    pos = Vector((0, 0, 0))  # the current position of the particle in 3D space
    old_pos = Vector((0, 0, 0))  # the position of the particle in the previous time step, used as part of the verlet numerical integration scheme
    velocity = Vector((0, 0, 0))
    acceleration = Vector((0, 0, 0))  # a vector representing the current acceleration of the particle
    accumulated_normal = Vector((0, 0, 0)) # an accumulated normal (i.e. non normalized), used for OpenGL soft shading
    
    simVelocity = Vector((0, 0, 0))
    simAcce = Vector((0, 0, 0))
    
    oriPos = Vector((0, 0, 0))
    
    def __init__(self, pos):
        self.pos = pos
        self.old_pos = pos
        self.oriPos = pos
        
    def addForce(self, f):
        pref = bpy.context.preferences.addons[__package__].preferences
        self.acceleration += f / pref.mass

    '''This is one of the important methods, where the time is progressed a single step size (TIME_STEPSIZE)
       The method is called by Cloth.time_step()
       Given the equation "force = mass * acceleration" the next position is found through verlet integration'''

    def timeStep(self, time = 0.02, mode = "Eular"):
        if self.movable:
            if mode == "Eular":
                # print("Eular")
                self.simVelocity = self.velocity
                self.simAcce = self.acceleration
            elif mode == "RungeKutta2":
                # print("RungeKutta2")
                self.simVelocity = self.velocity + self.acceleration / 2 * time
                self.simAcce = self.acceleration
            elif mode == "Verlet":
                # print("Verlet")
                pref = bpy.context.preferences.addons[__package__].preferences
                self.simAcce = self.acceleration
                self.simVelocity = self.velocity + self.acceleration * time
                self.simVelocity = self.velocity + (self.simVelocity + self.velocity) / (2 * pref.mass) * time
            elif mode == "Leapfrog":
                # print("Leapfrog")
                # tmp : need to use the acceleration of next frame
                self.simAcce = self.acceleration
                self.simVelocity = self.velocity + (self.acceleration + self.acceleration) / 2 * time
            elif mode == "Symplectic":
                # print("Symplectic")
                self.simVelocity = self.velocity + self.acceleration * time
                self.simAcce = self.acceleration
            # print(self.simAcce)
            # print(self.simVelocity)
    def updatePos(self, time = 0.02, mode = "Eular"):
        if self.movable:
            pref = bpy.context.preferences.addons[__package__].preferences
            damping = pref.damping
            temp = self.pos

            if mode == "Leapfrog":
                self.pos = self.pos + self.simVelocity * time + self.simAcce / 2 * time * time
            else:
                self.pos = self.pos + self.simVelocity * time
                self.simVelocity = self.velocity + self.simAcce * time
            self.velocity = self.simVelocity
            # self.acceleration = self.simAcce
            self.old_pos = temp
            self.acceleration = Vector((0, 0, 0))# acceleration is reset since it HAS been translated into a change in position(and implicitely into velocity)
    # Vec3 & getPos() {return pos;}

    def resetAcceleration(self):
        self.acceleration = Vector((0, 0, 0))

    def offsetPos(self, v):
        if self.movable:
            self.pos += v

    def makeUnmovable(self):
        self.movable = False

    def addToNormal(self, normal):
        self.accumulated_normal += normal.normalized()

    #Vec3 & getNormal() {return accumulated_normal;} // notice, the normal is not unit length
    def resetNormal(self):
        self.accumulated_normal = Vector((0, 0, 0))

class Constraint():

    rest_distance = 0 # the length between particle p1 and p2 in rest configuration

    # the two particles that are connected through this constraint
    p1 = Particle(Vector((0,0,0)))
    p2 = Particle(Vector((0,0,0)))

    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        #vec = p1 -> getPos() - p2 -> getPos();
        #rest_distance = vec.length();     }
        vec = self.p1.pos - self.p2.pos
        self.rest_distance = vec.length
        # print(self.rest_distance)
    '''This is one of the important methods, where a single constraint between two particles p1 and p2 is solved
    the method is called by Cloth.time_step() many times per frame'''
    def satisfyConstraint(self):
        #  + (self.pos - self.old_pos) * (1.0 - damping)
        pref = bpy.context.preferences.addons[__package__].preferences
        p1_to_p2 = self.p2.pos - self.p1.pos # vector from p1 to p2
        v1_to_v2 = self.p2.velocity - self.p1.velocity
        # print(self.p2.velocity, self.p1.velocity)
        ppNormalize = p1_to_p2.normalized()
        # print(p1_to_p2, self.p2.pos, self.p1.pos)
        current_distance = p1_to_p2.length # current distance between p1 and p2
        # correctionVector = p1_to_p2 * (1 - self.rest_distance / current_distance)
        springForce = (current_distance - self.rest_distance) * pref.spring
        dampingForce = (p1_to_p2.dot(v1_to_v2) / current_distance) * pref.damping
        finalForce = ppNormalize * (springForce + dampingForce) * 0.5
        # self.p1.offsetPos(correctionVectorHalf)
        # self.p2.offsetPos(-correctionVectorHalf)
        self.p1.addForce(finalForce)
        self.p2.addForce(-finalForce)

class Cloth():
    resetFlag = False
    width = 5
    height = 5
    num_particles_width = 10 # number of particles in "width" direction
    num_particles_height = 10 # number of particles in "height" direction
    # total number of particles is num_particles_width*num_particles_height

    particles = [] # all particles that are part of this 　cloth　****vector < Particle > 
    constraints = [] # alle constraints between particles as part of this cloth　****vector < Constraint >
    
    def getParticle(self, x, y) :
        return self.particles[y* self.num_particles_width + x]
    #------------------------------------construct??
    def makeConstraint(self, p1, p2):
        self.constraints.append(Constraint(p1, p2))

    ''' A private method used by drawShaded() and addWindForcesForTriangle() to retrieve the
    normal vector of the triangle defined by the position of the particles p1, p2, and p3.
    The magnitude of the normal vector is equal to the area of the parallelogram defined by p1, p2 and p3
    '''
    def calcTriangleNormal(self, p1, p2, p3):
        pos1 = p1.pos
        pos2 = p2.pos
        pos3 = p3.pos

        v1 = pos2 - pos1
        v2 = pos3 - pos1

        return v1.cross(v2)

    ''' A private method used by windForce() to calcualte the wind force for a single triangle
    defined by p1, p2, p3'''
    def addWindForcesForTriangle(self, p1, p2, p3, direction):
        normal = self.calcTriangleNormal(p1, p2, p3)
        d = normal.normalized()
        force = normal * (d.dot(direction))
        p1.addForce(force)
        p2.addForce(force)
        p3.addForce(force)

    ''' A private method used by drawShaded(), that draws a single triangle p1, p2, p3 with a color'''
    #-------------------------------------------------------------

    '''This is a important constructor for the entire system of particles and constraints'''
    def __init__(self, width = 5, height = 5, num_particles_width = 10, num_particles_height = 10): 
        self.width = width
        self.height = height
        self.num_particles_width = num_particles_width
        self.num_particles_height = num_particles_height
        #----------------------------------------------
        #self.particles.resize(num_particles_width*num_particles_height); // I am essentially using this vector as an array with room for num_particles_width*num_particles_height particles

        # creating particles in a grid of particles from (0, 0, 0) to(width, -height, 0)
        for y in range(0, self.num_particles_height):
            for x in range(0, self.num_particles_width):
                pos = Vector((width * (x / self.num_particles_width),
                    -height * (y / self.num_particles_height), 0))
                self.particles.append(Particle(pos)) # insert particle in column x at y'th row
                ParticleCreaterUtils.verts.append(pos)
        #update mesh
        updateMesh()
        ParticleCreaterUtils.mesh.from_pydata(ParticleCreaterUtils.verts, [], ParticleCreaterUtils.faces)
        ParticleCreaterUtils.mesh.update(calc_edges=True)
        # Connecting immediate neighbor particles with constraints(distance 1 and sqrt(2) in the grid)
        for x in range (0, self.num_particles_width):
            for y in range (0,self.num_particles_height):
                if x < self.num_particles_width - 1:
                    self.makeConstraint(self.getParticle(x, y), self.getParticle(x + 1, y))
                if y < self.num_particles_height - 1:
                    self.makeConstraint(self.getParticle(x, y), self.getParticle(x, y + 1))
                if x < self.num_particles_width - 1 and y < self.num_particles_height - 1:
                    self.makeConstraint(self.getParticle(x, y), self.getParticle(x + 1, y + 1))
                if x < self.num_particles_width - 1 and y < self.num_particles_height - 1:
                    self.makeConstraint(self.getParticle(x + 1, y), self.getParticle(x, y + 1))

        # Connecting secondary neighbors with constraints(distance 2 and sqrt(4) in the grid)
        for x in range (0, self.num_particles_width):
            for y in range (0, self.num_particles_height):
                if x < self.num_particles_width - 2: 
                    self.makeConstraint(self.getParticle(x, y), self.getParticle(x + 2, y))
                if y < self.num_particles_height - 2: 
                    self.makeConstraint(self.getParticle(x, y), self.getParticle(x, y + 2))
                if x < self.num_particles_width - 2 and y < self.num_particles_height - 2:
                    self.makeConstraint(self.getParticle(x, y), self.getParticle(x + 2, y + 2))
                if x < self.num_particles_width - 2 and y < self.num_particles_height - 2:
                    self.makeConstraint(self.getParticle(x + 2, y), self.getParticle(x, y + 2))

        # making the upper left most three and right most three particles unmovable
        for i in range (0,4):
            self.getParticle(0 + i, 0).offsetPos(Vector((0.5, 0.0, 0.0))) # moving the particle a bit towards the center, to make it hang more natural - because I like it;)
            self.getParticle(0 + i, 0).makeUnmovable()

            self.getParticle(0 + i, 0).offsetPos(Vector((-0.5, 0.0, 0.0))) # moving the particle a bit towards the center, to make it hang more natural - because I like it;)
            self.getParticle(num_particles_width - 1 - i, 0).makeUnmovable()
    ''' drawing the cloth as a smooth shaded (and colored according to column) OpenGL triangular mesh
    Called from the display() method
    The cloth is seen as consisting of triangles for four particles in the grid as follows:

    (x,y)   *--* (x+1,y)
            | /|
            |/ |
    (x,y+1) *--* (x+1,y+1)
    '''
    def drawShaded(self):
        # reset normals (which where written to last frame)
        for particle in self.particles :
            particle.resetNormal()

        #create smooth per particle normals by adding up all the (hard) triangle normals that each particle is part of
        for x in range(0, self.num_particles_width - 1) :
            for y in range(0, self.num_particles_height - 1) :
                normal = self.calcTriangleNormal(self.getParticle(x + 1, y), self.getParticle(x, y), self.getParticle(x, y + 1))
                self.getParticle(x + 1, y).addToNormal(normal)
                self.getParticle(x, y).addToNormal(normal)
                self.getParticle(x, y + 1).addToNormal(normal)

                normal = self.calcTriangleNormal(self.getParticle(x + 1, y + 1), self.getParticle(x + 1, y), self.getParticle(x, y + 1))
                self.getParticle(x + 1, y + 1).addToNormal(normal)
                self.getParticle(x + 1, y).addToNormal(normal)
                self.getParticle(x, y + 1).addToNormal(normal)

        ParticleCreaterUtils.verts.clear()
        for x in range(0, self.num_particles_width):
            for y in range(0, self.num_particles_height):
                ParticleCreaterUtils.cloth.data.vertices[y* self.num_particles_width + x].co = self.getParticle(x, y).pos

    ''' this is an important methods where the time is progressed one time step for the entire cloth.
    This includes calling satisfyConstraint() for every constraint, and calling timeStep() for all particles
    '''
    def timeStep(self, time = 0.02, mode = "Eular"):
        for i in range (0, CONSTRAINT_ITERATIONS):# iterate over all constraints several times
            for constraint in self.constraints:
                constraint.satisfyConstraint() # satisfy constraint.

        for particle in self.particles:
            particle.timeStep(time, mode) # calculate the position of each particle at the next time step.
            particle.updatePos(time, mode)
    # used to add gravity (or any other arbitrary vector) to all particles*/
    def addForce(self, direction):
        for particle in self.particles:
            particle.addForce(direction) # add the forces to each particle

    # used to add wind forces to all particles, is added for each triangle since the final force is proportional 
    # to the triangle area as seen from the wind direction
    def windForce(self, direction):
        # print(direction)
        for x in range(0, self.num_particles_width - 1):
            for y in range(0, self.num_particles_height - 1):
                self.addWindForcesForTriangle(self.getParticle(x + 1, y), self.getParticle(x, y), self.getParticle(x, y + 1), direction)
                self.addWindForcesForTriangle(self.getParticle(x + 1, y + 1), self.getParticle(x + 1, y), self.getParticle(x, y + 1), direction)

    ''' used to detect and resolve the collision of the cloth with the ball.
    This is based on a very simples scheme where the position of each particle is simply compared to the sphere and corrected.
    This also means that the sphere can "slip through" if the ball is small enough compared to the distance in the grid bewteen particles
    '''
    def ballCollision(self, center, radius):
        for particle in self.particles:
            v = particle.pos - center
            if v.length < radius: # if the particle is inside the ball
                particle.offsetPos(v.normalized()*(radius - v.length)) # project the particle to the surface of the ball

    def floorCollision(self, y):
        for particle in self.particles:
            if particle.pos.y < y: # if the particle is inside the ball
                p = particle.pos
                particle.offsetPos(Vector((0, (y - p[1])/10, 0))) # project the particle to the surface of the ball
    
    def Reset(self):
        for particle in self.particles:
            particle.pos = particle.oriPos
            particle.old_pos = particle.oriPos
            particle.velocity = Vector((0, 0, 0))
            particle.acceleration = Vector((0, 0, 0))
            particle.accumulated_normal = Vector((0, 0, 0))
            particle.simVelocity = Vector((0, 0, 0))
            particle.simAcce = Vector((0, 0, 0))
            
def resetCloth():
    if ParticleCreaterUtils.cloth1:
        ParticleCreaterUtils.cloth1.resetFlag = True
        # ParticleCreaterUtils.ball_time = 0
        # ParticleCreaterUtils.cloth1.Reset()
        # ParticleCreaterUtils.cloth1.drawShaded()
    
#update ------------------------------------------------------
def in_1_seconds():
    pref = bpy.context.preferences.addons[__package__].preferences
    timeStep = pref.timeStep
    frameRate = 1 / pref.frameRate
    
    if not ParticleCreaterUtils.cloth1:
        return frameRate
    if ParticleCreaterUtils.cloth1.resetFlag == True:
        ParticleCreaterUtils.ball_time = 0
        ParticleCreaterUtils.cloth1.Reset()
        ParticleCreaterUtils.cloth1.drawShaded()
        ParticleCreaterUtils.cloth1.resetFlag = False
        return frameRate
    # calculating positions
    ParticleCreaterUtils.ball_time += 1
    
    ParticleCreaterUtils.ball_pos[2] = math.cos(ParticleCreaterUtils.ball_time / 50.0) * 7
    ParticleCreaterUtils.ball.location = ParticleCreaterUtils.ball_pos
    ParticleCreaterUtils.cloth1.addForce(Vector(pref.gravity)) # add gravity each frame, pointing down
    ParticleCreaterUtils.cloth1.windForce(Vector(pref.windForce)); # generate some wind each frame
    #integrator method
    # getVelocityTime(timeStep, ParticleCreaterUtils.cloth1)
    #-----------------
    ParticleCreaterUtils.cloth1.timeStep(timeStep, mode = pref.integrateMode) # calculate the particle positions of the next frame
    # ParticleCreaterUtils.cloth1.ballCollision(ParticleCreaterUtils.ball_pos, ParticleCreaterUtils.ball_radius) # resolve collision with the ball
    # ParticleCreaterUtils.cloth1.floorCollision(-5) # resolve collision with the ball
    
    # drawing
    ParticleCreaterUtils.cloth1.drawShaded() # finally draw the cloth with smooth shading
    return frameRate
    
def register():
    bpy.app.timers.register(in_1_seconds)