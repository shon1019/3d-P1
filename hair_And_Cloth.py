import bpy


from bpy.props import (
        StringProperty,
        IntProperty,
        PointerProperty,
        )

from bpy.types import Operator
from mathutils import Vector

DAMPING = 0.01  # how much to damp the cloth simulation each frame
TIME_STEPSIZE2 = 0.5 * 0.5  # how large time step each particle takes each frame
CONSTRAINT_ITERATIONS = 15 # how many iterations of constraint satisfaction each frame (more is rigid, less is soft)

'''
// Just below are three global variables holding the actual animated stuff; Cloth and Ball 
Cloth cloth1(14, 10, 55, 45); // one Cloth object of the Cloth class
Vec3 ball_pos(7, -5, 0); // the center of our one ball
float ball_radius = 2; // the radius of our one ball
'''


class ParticleCreaterUtils():
    # 布的大小 100 * 100
    particleSizw = 100
    # particle 的距離 1
    particledis = 1
    # 重力
    gravity = 9.8


class Particle():
    movable = True  # can the particle move or not ? used to pin parts of the cloth
    mass = 1  # the mass of the particle (is always 1 in this example)
    pos = Vector()  # the current position of the particle in 3D space
    old_pos = Vector()  # the position of the particle in the previous time step, used as part of the verlet numerical integration scheme
    acceleration = Vector()  # a vector representing the current acceleration of the particle
    accumulated_normal = Vector() # an accumulated normal (i.e. non normalized), used for OpenGL soft shading

    def __init__(self, pos, old_pos, acceleration, mass, movable, accumulated_normal):
        self.pos = pos
        self.old_pos = old_pos
        self.acceleration = acceleration
        self.mass = mass
        self.movable = movable
        self.accumulated_normal = accumulated_normal

    def addForce(self, f):
        self.acceleration += f / self.mass

    '''This is one of the important methods, where the time is progressed a single step size (TIME_STEPSIZE)
       The method is called by Cloth.time_step()
       Given the equation "force = mass * acceleration" the next position is found through verlet integration'''

    def timeStep(self):
        if movable:
            temp = self.pos
            self.pos = self.pos + (self.pos - self.old_pos) * (1.0 - DAMPING) + self.acceleration * TIME_STEPSIZE2
            self.old_pos = temp
            self.acceleration = Vector((0, 0, 0))# acceleration is reset since it HAS been translated into a change in position(and implicitely into velocity)

    # Vec3 & getPos() {return pos;}

    def resetAcceleration(self):
        self.acceleration = Vector((0, 0, 0))

    def offsetPos(self, v):
        if self.movable:
            pos += v

    def makeUnmovable(self):
        self.movable = False

    def addToNormal(self, normal):
        accumulated_normal += normal.normalized()

    #Vec3 & getNormal() {return accumulated_normal;} // notice, the normal is not unit length

    #void resetNormal() {accumulated_normal = Vec3(0, 0, 0); }

class Constraint():

    rest_distance = 0 # the length between particle p1 and p2 in rest configuration

    # the two particles that are connected through this constraint
    p1 = Particle()
    p2 = Particle()

    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        #vec = p1 -> getPos() - p2 -> getPos();
        #rest_distance = vec.length();     }
        vec = self.p1.pos - self.p2.pos
        rest_distance = vec.length

    '''This is one of the important methods, where a single constraint between two particles p1 and p2 is solved
    the method is called by Cloth.time_step() many times per frame'''
    def satisfyConstraint(self):
        p1_to_p2 = self.p2.pos - self.p1.pos # vector from p1 to p2
        current_distance = p1_to_p2.length # current distance between p1 and p2
        correctionVector = p1_to_p2 * (1 - rest_distance / current_distance) # The offset vector that could moves p1 into a distance of rest_distance to p2
        correctionVectorHalf = correctionVector * 0.5 # Lets make it half that length, so that we can move BOTH p1 and p2.
        self.p1.offsetPos(correctionVectorHalf) # correctionVectorHalf is pointing from p1 to p2, so the length should move p1 half the length needed to satisfy the constraint.
        self.p2.offsetPos(-correctionVectorHalf) # we must move p2 the negative direction of correctionVectorHalf since it points from p2 to p1, and not p1 to p2.


class Cloth(bpy.types.Operator):
    """ClothCreater"""
    bl_idname = "ldops.Cloth_creater"
    bl_label = "ClothCreater"

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
        normal = calcTriangleNormal(p1, p2, p3)
        d = normal.normalized()
        force = normal * (d.dot(direction))
        p1.addForce(force)
        p2.addForce(force)
        p3.addForce(force)

    ''' A private method used by drawShaded(), that draws a single triangle p1, p2, p3 with a color'''
    #-------------------------------------------------------------
    '''def drawTriangle(p1, p2, p3, color):
        glColor3fv((GLfloat*) & color)

        glNormal3fv((GLfloat *) & (p1 -> getNormal().normalized()))
        glVertex3fv((GLfloat *) & (p1 -> getPos()))

        glNormal3fv((GLfloat *) & (p2 -> getNormal().normalized()))
        glVertex3fv((GLfloat *) & (p2 -> getPos()))

        glNormal3fv((GLfloat *) & (p3 -> getNormal().normalized()))
        glVertex3fv((GLfloat * ) & (p3 -> getPos()))'''


    ''' This is a important constructor for the entire system of particles and constraints'''
    def __init__(self, width, height, num_particles_width, num_particles_height): 
        self.num_particles_width = num_particles_width
        self.num_particles_height = num_particles_height
        #----------------------------------------------
        #self.particles.resize(num_particles_width*num_particles_height); // I am essentially using this vector as an array with room for num_particles_width*num_particles_height particles

        # creating particles in a grid of particles from (0, 0, 0) to(width, -height, 0)
        for x in range(0, self.num_particles_width):
            for y in range(0, self.num_particles_height):
                pos = Vector((width * (x / self.num_particles_width),
                    -height * (y / self.num_particles_height),
                    0));
                self.particles[y*num_particles_width + x] = Particle(pos); # insert particle in column x at y'th row

        # Connecting immediate neighbor particles with constraints(distance 1 and sqrt(2) in the grid)
        for x in range (0, self.num_particles_width):
            for y in range (0,self.num_particles_height):
                if x < self.num_particles_width - 1:
                    makeConstraint(getParticle(x, y), getParticle(x + 1, y))
                if y < self.num_particles_height - 1:
                    makeConstraint(getParticle(x, y), getParticle(x, y + 1))
                if x < self.num_particles_width - 1 and y < self.num_particles_height - 1:
                    makeConstraint(getParticle(x, y), getParticle(x + 1, y + 1))
                if x < self.num_particles_width - 1 and y < self.num_particles_height - 1:
                    makeConstraint(getParticle(x + 1, y), getParticle(x, y + 1))


        # Connecting secondary neighbors with constraints(distance 2 and sqrt(4) in the grid)
        for x in range (0, self.num_particles_width):
            for y in range (0, self.num_particles_height):
                if x < self.num_particles_width - 2: 
                    makeConstraint(getParticle(x, y), getParticle(x + 2, y))
                if y < self.num_particles_height - 2: 
                    makeConstraint(getParticle(x, y), getParticle(x, y + 2))
                if x < self.num_particles_width - 2 and y < self.num_particles_height - 2:
                    makeConstraint(getParticle(x, y), getParticle(x + 2, y + 2))
                if x < self.num_particles_width - 2 and y < self.num_particles_height - 2:
                    makeConstraint(getParticle(x + 2, y), getParticle(x, y + 2))

        # making the upper left most three and right most three particles unmovable
        for i in range (0,4):
            getParticle(0 + i, 0).offsetPos(Vector((0.5, 0.0, 0.0))) # moving the particle a bit towards the center, to make it hang more natural - because I like it;)
            getParticle(0 + i, 0).makeUnmovable();

            getParticle(0 + i, 0).offsetPos(Vector((-0.5, 0.0, 0.0))) # moving the particle a bit towards the center, to make it hang more natural - because I like it;)
            getParticle(num_particles_width - 1 - i, 0).makeUnmovable()


    ''' drawing the cloth as a smooth shaded (and colored according to column) OpenGL triangular mesh
    Called from the display() method
    The cloth is seen as consisting of triangles for four particles in the grid as follows:

    (x,y)   *--* (x+1,y)
            | /|
            |/ |
    (x,y+1) *--* (x+1,y+1)

    '''
    void drawShaded()
    {
        // reset normals (which where written to last frame)
        std::vector<Particle>::iterator particle;
        for (particle = particles.begin(); particle != particles.end(); particle++)
        {
            (*particle).resetNormal();
        }

        //create smooth per particle normals by adding up all the (hard) triangle normals that each particle is part of
        for (int x = 0; x < num_particles_width - 1; x++)
        {
            for (int y = 0; y < num_particles_height - 1; y++)
            {
                Vec3 normal = calcTriangleNormal(getParticle(x + 1, y), getParticle(x, y), getParticle(x, y + 1));
                getParticle(x + 1, y)->addToNormal(normal);
                getParticle(x, y)->addToNormal(normal);
                getParticle(x, y + 1)->addToNormal(normal);

                normal = calcTriangleNormal(getParticle(x + 1, y + 1), getParticle(x + 1, y), getParticle(x, y + 1));
                getParticle(x + 1, y + 1)->addToNormal(normal);
                getParticle(x + 1, y)->addToNormal(normal);
                getParticle(x, y + 1)->addToNormal(normal);
            }
        }

        glBegin(GL_TRIANGLES);
        for (int x = 0; x < num_particles_width - 1; x++)
        {
            for (int y = 0; y < num_particles_height - 1; y++)
            {
                Vec3 color(0, 0, 0);
                if (x % 2) // red and white color is interleaved according to which column number
                    color = Vec3(0.6f, 0.2f, 0.2f);
                else
                    color = Vec3(1.0f, 1.0f, 1.0f);

                drawTriangle(getParticle(x + 1, y), getParticle(x, y), getParticle(x, y + 1), color);
                drawTriangle(getParticle(x + 1, y + 1), getParticle(x + 1, y), getParticle(x, y + 1), color);
            }
        }
        glEnd();
    }

    /* this is an important methods where the time is progressed one time step for the entire cloth.
    This includes calling satisfyConstraint() for every constraint, and calling timeStep() for all particles
    */
    void timeStep()
    {
        std::vector<Constraint>::iterator constraint;
        for (int i = 0; i < CONSTRAINT_ITERATIONS; i++) // iterate over all constraints several times
        {
            for (constraint = constraints.begin(); constraint != constraints.end(); constraint++)
            {
                (*constraint).satisfyConstraint(); // satisfy constraint.
            }
        }

        std::vector<Particle>::iterator particle;
        for (particle = particles.begin(); particle != particles.end(); particle++)
        {
            (*particle).timeStep(); // calculate the position of each particle at the next time step.
        }
    }

    /* used to add gravity (or any other arbitrary vector) to all particles*/
    void addForce(const Vec3 direction)
    {
        std::vector<Particle>::iterator particle;
        for (particle = particles.begin(); particle != particles.end(); particle++)
        {
            (*particle).addForce(direction); // add the forces to each particle
        }

    }

    /* used to add wind forces to all particles, is added for each triangle since the final force is proportional to the triangle area as seen from the wind direction*/
    void windForce(const Vec3 direction)
    {
        for (int x = 0; x < num_particles_width - 1; x++)
        {
            for (int y = 0; y < num_particles_height - 1; y++)
            {
                addWindForcesForTriangle(getParticle(x + 1, y), getParticle(x, y), getParticle(x, y + 1), direction);
                addWindForcesForTriangle(getParticle(x + 1, y + 1), getParticle(x + 1, y), getParticle(x, y + 1), direction);
            }
        }
    }

    /* used to detect and resolve the collision of the cloth with the ball.
    This is based on a very simples scheme where the position of each particle is simply compared to the sphere and corrected.
    This also means that the sphere can "slip through" if the ball is small enough compared to the distance in the grid bewteen particles
    */
    void ballCollision(const Vec3 center, const float radius)
    {
        std::vector<Particle>::iterator particle;
        for (particle = particles.begin(); particle != particles.end(); particle++)
        {
            Vec3 v = (*particle).getPos() - center;
            float l = v.length();
            if (v.length() < radius) // if the particle is inside the ball
            {
                (*particle).offsetPos(v.normalized()*(radius - l)); // project the particle to the surface of the ball
            }
        }
    }

};



classes = (

)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

