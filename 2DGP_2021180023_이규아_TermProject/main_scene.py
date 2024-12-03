from pico2d import * 
import gfw

from fighter import Fighter
from fighter import Bullet
from enemy import EnemyGen
from enemy import EnemyBullet

world = gfw.World(['bg', 'fighter', 'bullet', 'enemy', 'ui', 'controller'])

canvas_width = 500
canvas_height = 800
shows_bounding_box = True
shows_object_count = True
global current_state
global t
t = False

class GameState:
    TITLE = 0
    PLAYING = 1
    GAME_OVER = 2

current_state = GameState.TITLE

class TitleScene:
    def __init__(self):
        # world를 씬 내부에서 관리
        self.world = gfw.World(['bg'])
        self.image = load_image('res/Title.png')
        self.start_time = get_time()
        
    def enter(self):
        # 기존 배경 제거 후 새로 추가
        self.world.clear()
        self.world.append(gfw.VertFillBackground('res/Title.png', -30), self.world.layer.bg)
        
    def draw(self):
        # 배경 그리기
        self.world.draw()
        
        # 타이틀 이미지 그리기
        self.image.draw(get_canvas_width()//2, get_canvas_height()//2)
        
        # 시작 메시지
        if get_time() - self.start_time > 1.0:
            font = load_font('res/ENCR10B.TTF', 20)
            msg = "Press SPACE to Start"
            w = font.width(msg)
            font.draw(get_canvas_width()//2 - w//2, 200, msg, (255, 255, 255))

    def handle_event(self, e):
        if e.type == SDL_KEYDOWN and e.key == SDLK_SPACE:
            gfw.change(MainScene())
            current_state = GameState.PLAYING
            t = True
            return True
        return False
    def exit(self):
        pass

class GameOverScene:
    def __init__(self, score):
        self.world = gfw.World(['bg'])
        self.image = load_image('res/Game_Over.png')
        self.score = score
        self.opacity = 0
        self.start_time = get_time()
        
    def enter(self):
        # 기존 배경 제거 후 새로 추가
        self.world.clear()
        self.world.append(gfw.VertFillBackground('res/Game_Over.png', -30), self.world.layer.bg)
        
    def update(self):
        self.world.update()
        
        elapsed = get_time() - self.start_time
        self.opacity = min(255, int(elapsed * 255))
        
    def draw(self):
        self.world.draw()
        
        self.image.opacify(self.opacity / 255.0)
        self.image.draw(get_canvas_width()//2, get_canvas_height()//2)
        
        if self.opacity >= 255:
            font = load_font('res/ENCR10B.TTF', 20)
            msg = f"Final Score: {self.score}"
            w = font.width(msg)
            font.draw(get_canvas_width()//2 - w//2, 200, msg, (255, 255, 255))
            
            msg2 = "Press SPACE to Restart"
            w = font.width(msg2)
            font.draw(get_canvas_width()//2 - w//2, 150, msg2, (255, 255, 255))
            
    def handle_event(self, e):
        if e.type == SDL_KEYDOWN and e.key == SDLK_SPACE:
            gfw.change(MainScene())
            current_state = GameState.PLAYING
            return True
        return False
    def exit(self):
        pass

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

def Title():
    if t == False:
        current_state = GameState.TITLE
        gfw.change(TitleScene())

def enter():
    Title()
    world.append(gfw.VertFillBackground('res/clouds.png', -60), world.layer.bg)
    world.append(gfw.VertFillBackground('res/bg_city.png', -30), world.layer.bg)
    
    global fighter, lives, lives_sprite
    fighter = Fighter()
    world.append(fighter, world.layer.fighter)

    lives = 3
    lives_sprite = LivesSprite('res/number_24x32.png', canvas_width - 50, canvas_height - 50)
    world.append(lives_sprite, world.layer.ui)

    global main_scene_ui
    main_scene_ui = MainScenUI()
    world.append(main_scene_ui, world.layer.ui)

    world.append(EnemyGen(), world.layer.controller)
    
    collision_checker = CollisionChecker(fighter, lives_sprite)
    world.append(collision_checker, world.layer.controller)

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
    def __init__(self, fighter=None, lives_sprite=None):
        self.fighter = fighter
        self.lives_sprite = lives_sprite
        
    def update(self):
        # 플레이어 탄환과 적 충돌 체크
        for enemy in list(world.objects_at(world.layer.enemy))[:]:
            for bullet in list(Bullet.bullets)[:]:
                if self.check_collision(bullet, enemy):
                    # 총알 제거
                    if bullet in Bullet.bullets:
                        Bullet.bullets.remove(bullet)
                    
                    # 적 생명력 감소
                    if enemy.decrease_life(bullet.power):
                        try:
                            world.remove(enemy)
                        except ValueError:
                            print("Enemy already removed")
                        break
        
        # 적 탄환과 플레이어 충돌 체크
        for bullet in list(EnemyBullet.bullets)[:]:
            if self.check_collision(bullet, self.fighter):
                # 목숨 감소
                if self.lives_sprite:
                    self.lives_sprite.decrease()  # 충돌 시 목숨 감소
                    print(f"목숨 감소: {self.lives_sprite.lives}")
                
                # 적 탄 제거
                if bullet in EnemyBullet.bullets:
                    EnemyBullet.bullets.remove(bullet)
                
                # 게임 오버 체크
                if self.lives_sprite.lives <= 0:
                    game_over(score=0)

    def draw(self):
        pass
    
    def check_collision(self, a, b):
        ax1, ay1, ax2, ay2 = a.get_bb()
        bx1, by1, bx2, by2 = b.get_bb()
        
        if ax2 < bx1: return False
        if ax1 > bx2: return False
        if ay2 < by1: return False
        if ay1 > by2: return False
        
        return True

def game_over(score):
    global current_state
    current_state = GameState.GAME_OVER
    gfw.change(GameOverScene(score))
                
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
        # 초기화 시 world 새로 생성
        self.screen_width = get_canvas_width()  # 게임 화면의 가로 길이
        self.screen_height = get_canvas_height()  # 게임 화면의 세로 길이
        self.world = gfw.World(['bg', 'fighter', 'bullet', 'enemy', 'ui', 'controller'])
        self.world.layer.fighter = 1
        self.world.layer.bullet = 2
        
    def enter(self):
        # 기존 world 내용 완전 초기화
        self.world.clear()
        # 배경 초기화
        self.world.append(gfw.VertFillBackground('res/clouds.png', -60), self.world.layer.bg)
        self.world.append(gfw.VertFillBackground('res/bg_city.png', -30), self.world.layer.bg)
        
        # 플레이어 초기화
        self.fighter = Fighter()
        self.world.append(self.fighter, self.world.layer.fighter)
        
        # 목숨 표시
        self.lives_sprite = LivesSprite('res/number_24x32.png', canvas_width - 50, canvas_height - 50)
        self.world.append(self.lives_sprite, self.world.layer.ui)
        
        # 충돌 체커 초기화
        self.collision_checker = CollisionChecker(self.fighter, self.lives_sprite)
        self.world.append(self.collision_checker, self.world.layer.controller)
        
        # 적 생성기 초기화
        self.world.append(EnemyGen(), self.world.layer.enemy)
    
    def update(self):
        self.world.update()
    
    def draw(self):
        self.world.draw()
    
    def handle_event(self, e):
        if e.type == SDL_KEYDOWN and e.key == SDLK_ESCAPE:
            gfw.pop()
            return True
        self.fighter.handle_event(e)
        return False

    def exit(self):
        self.world.clear()

if __name__ == '__main__':
    gfw.start_main_module()