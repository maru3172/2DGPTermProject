from pico2d import * 
import gfw

from fighter import Fighter
from enemy import EnemyGen

world = gfw.World(['bg', 'fighter', 'bullet', 'enemy', 'ui', 'controller'])

canvas_width = 500
canvas_height = 800
shows_bounding_box = True
shows_object_count = True

class GameOverScene:
    def __init__(self):
        self.world = gfw.World(['ui'])
        self.image = load_image('res/Game_Over.png')
        self.pos = (canvas_width // 2, canvas_height // 2)
        self.opacity = 0
        self.start_time = get_time()

    def enter(self):
        print("GameOverScene에 들어왔습니다.")
        self.world.append(self, self.world.layer.ui)

    def exit(self):
        print("GameOverScene을 나갑니다.")
        self.world.clear()

    def pause(self): pass
    def resume(self): pass

    def update(self):
        elapsed_time = get_time() - self.start_time
        self.opacity = min(255, int(elapsed_time * 255))

    def draw(self):
        self.image.opacify(self.opacity / 255.0)
        self.image.draw(self.pos[0], self.pos[1])
        
        if self.opacity >= 255:
            font = load_font('res/ENCR10B.TTF', 20)
            font.draw(self.pos[0] - 100, self.pos[1] - 50, "Press Enter to Restart", (255, 255, 255))

    def handle_event(self, e):
        if e.type == SDL_KEYDOWN and e.key == SDLK_RETURN:
            print("게임을 재시작합니다.")
            gfw.change(MainScene())
            return True
        return False

def check_game_over():
    if lives <= 0:
        print("Game Over: Lives are 0")
        lives_sprite.set_game_over(True)
        main_scene_ui.set_game_over(True)
        gfw.change(GameOverScene())  # push 대신 change를 사용


class LivesSprite:
    def __init__(self, image_path, x, y, max_lives=3):
        self.image = load_image(image_path)
        self.x = x
        self.y = y
        self.max_lives = max_lives
        self.lives = max_lives
        self.digit_width = 24
        self.digit_height = 32

    def update(self): pass

    def draw(self):
        sx = self.lives * self.digit_width
        self.image.clip_draw(sx, 0, self.digit_width, self.digit_height, self.x, self.y)

    def decrease(self):
        if self.lives > 0:
            self.lives -= 1

    def increase(self):
        if self.lives < self.max_lives:
            self.lives += 1

    def set_game_over(self, value):
        self.game_over = value
        if value:
            print("Game Over!")

def enter():
    world.append(gfw.VertFillBackground('res/clouds.png', -60), world.layer.bg)
    world.append(gfw.VertFillBackground('res/bg_city.png', -30), world.layer.bg)
    global fighter
    fighter = Fighter()
    world.append(fighter, world.layer.fighter)

    global lives_sprite
    lives_sprite = LivesSprite('res/number_24x32.png', canvas_width - 50, canvas_height - 50)
    world.append(lives_sprite, world.layer.ui)  # UI 레이어에 lives_sprite 추가

    global main_scene_ui
    main_scene_ui = MainScenUI()  # Initialize MainScenUI
    world.append(main_scene_ui, world.layer.ui)  # Add to UI layer

    world.append(EnemyGen(), world.layer.controller)
    world.append(CollisionChecker(), world.layer.controller)

    global lives
    lives = 3  # Initial lives

def exit():
    world.clear()
    print('[main.exit()]')

def pause():
    print('[main.pause()]')

def resume():
    print('[main.resume()]')

def handle_event(e):
    if e.type == SDL_KEYDOWN and e.key == SDLK_1:
        print(world.objects)
    fighter.handle_event(e)
    if e.type == SDL_KEYDOWN:
        if e.key == SDLK_SPACE:
            if lives_sprite:  # lives_sprite가 유효한지 확인
                lives_sprite.decrease()  # 목숨 감소
                print(f"Lives: {lives_sprite.lives}")  # 현재 목숨 출력
            else:
                print("lives_sprite가 초기화되지 않았습니다.")

class CollisionChecker:
    def __init__(self, scene):
        self.scene = scene
    
    def draw(self): 
        pass
    
    def update(self):
        bullets = self.scene.world.objects_at(self.scene.world.layer.bullet)
        for b in bullets:
            if hasattr(b, 'y'):
                if b.y > canvas_height or b.y < 0:
                    self.scene.world.remove(b)
                    continue
        
        enemies = self.scene.world.objects_at(self.scene.world.layer.enemy)
        for e in enemies:
            collided = False
            bullets = self.scene.world.objects_at(self.scene.world.layer.bullet)
            for b in bullets:
                if gfw.collides_box(b, e):
                    collided = True
                    self.scene.world.remove(b)
                    dead = e.decrease_life(b.power)
                    if dead:
                        self.scene.world.remove(e)
                    break
            if collided: continue
            
            if gfw.collides_box(self.scene.fighter, e):
                self.scene.world.remove(e)
                self.scene.lives -= 1
                self.scene.lives_sprite.decrease()
                if self.scene.lives <= 0:
                    self.scene.check_game_over()
                break
                
class MainScenUI:
    def __init__(self):
        self.image = load_image('res/Game_Over.png')
        self.pos = (canvas_width // 2, canvas_height // 2)
        self.game_over = False

    def update(self): pass
    
    def draw(self):
        if self.game_over:
            self.image.draw(self.pos[0], self.pos[1])

    def set_game_over(self, value):
        self.game_over = value

class MainScene:
    def __init__(self):
        self.world = gfw.World(['bg', 'fighter', 'bullet', 'enemy', 'ui', 'controller'])
        self.lives = 3
        
    def enter(self):
        self.world.append(gfw.VertFillBackground('res/clouds.png', -60), self.world.layer.bg)
        self.world.append(gfw.VertFillBackground('res/bg_city.png', -30), self.world.layer.bg)
        
        self.fighter = Fighter()
        self.world.append(self.fighter, self.world.layer.fighter)

        self.lives_sprite = LivesSprite('res/number_24x32.png', canvas_width - 50, canvas_height - 50)
        self.world.append(self.lives_sprite, self.world.layer.ui)

        self.main_scene_ui = MainScenUI()
        self.world.append(self.main_scene_ui, self.world.layer.ui)

        self.world.append(EnemyGen(), self.world.layer.controller)
        # 여기서 CollisionChecker 생성 시 self(현재 scene)를 전달
        self.world.append(CollisionChecker(self), self.world.layer.controller)


if __name__ == '__main__':
    gfw.start_main_module()