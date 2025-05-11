import neat.population
import pygame
import random
import os
import time
import neat

pygame.font.init()


WINDOW_WIDTH= 500
WINDOW_HEIGHT= 700
 
 #Load images from the folder
BIRD_IMAGES= [pygame.transform.scale2x(pygame.image.load(os.path.join('imgs_flappy','imgs','bird1.png'))),pygame.transform.scale2x(pygame.image.load(os.path.join('imgs_flappy','imgs','bird2.png'))),pygame.transform.scale2x(pygame.image.load(os.path.join('imgs_flappy','imgs','bird3.png')))]
BASE_IMAGE= pygame.transform.scale2x(pygame.image.load(os.path.join('imgs_flappy','imgs','base.png')))
BACKGROUND_IMAGE= pygame.transform.scale2x(pygame.image.load(os.path.join('imgs_flappy','imgs','bg.png')))
PIPE_IMAGE= pygame.transform.scale2x(pygame.image.load(os.path.join('imgs_flappy','imgs','pipe.png')))
GEN=0
STAT_FONT= pygame.font.SysFont("comicsans",20)

#Class bird handles the animation, falling, jumping and mask of bird
class Bird:
    IMGS= BIRD_IMAGES
    MAX_ROTATION= 25
    ROT_VEL= 20
    ANIMATION_TIME= 5

    def __init__(self,x,y):
        self.x=x
        self.y=y
        self.tilt=0
        self.tick_count= 0 #represents the time the bird has been falling 
        self.velocity= 0 
        self.height= self.y
        self.image_count=0
        self.img= self.IMGS[0]

    def jump(self):

        self.velocity= -10.5
        self.tick_count=0 #every time the bird jumps the falling time resets to 0
        self.height= self.y              

    def move(self): #falling and rotation of the bird
        self.tick_count +=1
        
        displacement = self.velocity*self.tick_count + (3/2)*self.tick_count**2 # d= v0t +1/2at^2 in this case a=3

        if displacement >= 16:
            displacement = 16
        if displacement <0:
            displacement -= 2

        self.y += displacement

        if displacement <0 or self.y < self.height +50 :
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else: 
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self,win): #animation of the wings flapping
        self.image_count +=1

        if self.image_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.image_count < self.ANIMATION_TIME *2 :
            self.img = self.IMGS[1]
        elif self.image_count < self.ANIMATION_TIME *3 :
            self.img = self.IMGS[2]
        elif self.image_count < self.ANIMATION_TIME *4 :
            self.img = self.IMGS[1]
        elif self.image_count == self.ANIMATION_TIME *4+1 :
            self.img = self.IMGS[0]
            self.image_count = 0

        if self.tilt <= -80:
            self.img= self.IMGS[1]
            self.img_count =self.ANIMATION_TIME*2

        rotated_image= pygame.transform.rotate(self.img,self.tilt)
        new_rect= rotated_image.get_rect(center= self.img.get_rect(topleft= (self.x , self.y)).center )
        win.blit(rotated_image, new_rect.topleft)

    def get_mask(self,):
        return pygame.mask.from_surface(self.img)
    
class Pipe:
    GAP=200
    VEL= 5

    def __init__(self,x):
        self.x=x
        self.heigth=0

        
        self.top=0
        self.bottom=0
        self.TOP_PIPE= pygame.transform.flip(PIPE_IMAGE, False, True)
        self.BOTTOM_PIPE= PIPE_IMAGE

        self.passed= False
        self.set_heigth()

    def set_heigth(self):
        self.heigth= random.randrange(50,450)
        self.top= self.heigth - self.TOP_PIPE.get_height()
        self.bottom= self.heigth + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self,win):
        win.blit(self.TOP_PIPE, (self.x, self.top))
        win.blit(self.BOTTOM_PIPE,(self.x,self.bottom))

    def collide(self, bird): #handles collisions with precision

        bird_mask= bird.get_mask()

        top_mask= pygame.mask.from_surface(self.TOP_PIPE)
        bottom_mask= pygame.mask.from_surface(self.BOTTOM_PIPE)

        top_offset= (self.x-bird.x, self.top- round(bird.y))
        bottom_offset=(self.x-bird.x, self.bottom- round(bird.y))

        b_point= bird_mask.overlap(bottom_mask,bottom_offset)
        t_point= bird_mask.overlap(top_mask,top_offset)

        if t_point or b_point:
            return True
        


        return False 
    

class Base:
    VEL= 5
    WIDTH= BASE_IMAGE.get_width()
    IMAGE= BASE_IMAGE

    def __init__(self,y):
        self.y =y
        self.x1=0
        self.x2= self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 +self.WIDTH<0 :
            self.x1 = self.x2 + self.WIDTH

        if self.x2 +self.WIDTH <0:
            self.x2= self.x1+ self.WIDTH
    #We have two bases moving one after the other, 
    # as soon as one leaves the screen completely it cycles back to the start

    def draw(self,win):
        win.blit(self.IMAGE, (self.x1, self.y))
        win.blit(self.IMAGE, (self.x2, self.y))




def draw_window(win,birds,pipes, base, score, gen, NUM_BIRDS):

    
    win.blit(BACKGROUND_IMAGE,(0,0))
    text= STAT_FONT.render("SCORE: " + str(score), 1, (255,255,255))
    win.blit(text, (WINDOW_WIDTH - 10 - text.get_width(), 10 ))

    text= STAT_FONT.render("GEN: " + str(gen), 1, (255,255,255))
    win.blit(text, (10, 10 ))

    text= STAT_FONT.render("BIRDS: " + str(NUM_BIRDS), 1, (255,255,255))
    win.blit(text, (10, 30 ))

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)

    for bird in birds:
        bird.draw(win)

    pygame.display.update() 

def main( genomes, config ): #we pass genomes (population) and the configuration for each one 
    
    global GEN
    GEN +=1
    #In the main we initialize objects of all the clases including the bases, bird, and pipes also the game loop runs here
    clock=pygame.time.Clock()
    birds= [] #bird objects list
    nets= [] #networks list
    ge=[] #genomes list



    for _,genome in genomes: #genomes is a tuple
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        genome.fitness = 0
        ge.append(genome)

    

    base= Base(730)
    pipes=[Pipe(600)]
    win= pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT))
    run= True

    score=0

    while run:
        clock.tick(30) #30 frames per second
        for event in pygame.event.get():
            if event.type== pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        pipe_index =0 
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].TOP_PIPE.get_width():
                pipe_index=1 
        else: 
            run= False
            break 
        #if there is a bird and more than one pipe on screen and we have already passed a pipe,
        # we are looking at the second pipe (pipe_index = 1 ) 

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1 #reward for surviving, one fitness point per second survived

            output= nets[x].activate( 
                (bird.y, abs(bird.y - pipes[pipe_index].heigth ), abs(bird.y - pipes[pipe_index].bottom ) ))
            #send bird and pipes position and get an output
            if output[0] > 0.5: #decide wheter to jump or not from that output gathered from the neura network
                bird.jump()



        #bird.move()
        removed_pipes= []
        add_pipe= False

        for pipe in pipes:
            for x, bird in enumerate(birds): 
                if pipe.collide(bird):
                    ge[x].fitness -= 1  #if a bird collides with a pipe we punish it by removing a fitness point
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)



                if not pipe.passed and pipe.x <  bird.x:
                    pipe.passed= True
                    add_pipe= True 

            if pipe.x + pipe.TOP_PIPE.get_width() <0 :
                removed_pipes.append(pipe)

            
            pipe.move()

        if add_pipe:

            score+=1
            for g in ge:
                g.fitness += 5 #if the bird passses a pipe we reward it by adding 5 points to its fitness score 
                                #genomes that passed a pipe didnt collide so the bird and genome is still alive

            pipes.append(Pipe(600))

        for r in removed_pipes:
            pipes.remove(r)

        for x, bird in enumerate(birds): 

            if bird.y + bird.img.get_height() >= 730 or bird.y < 0 :
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

            
        base.move()
        NUM_BIRDS = len(birds)
        draw_window(win,birds,pipes,base, score, GEN, NUM_BIRDS )

   


        
        
def run(config_path):
    config= neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, 
                               neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path
                               ) #configuration headings from configuration file 
    
    population= neat.Population(config) #population

    population.add_reporter(neat.StdOutReporter(True)) #gives information of population
    stats= neat.StatisticsReporter()
    population.add_reporter(stats)

    winner= population.run(main,50) #fitness function, number of generations

    

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__) #path to local directory
    config_path= os.path.join(local_dir, "config-feedforward.txt") #path to configuration file
    run(config_path)



