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

class GameState:
    TITLE = 0
    PLAYING = 1
    GAME_OVER = 2

class TitleScene:
    def __init__(self):
        self.image = load_image('res/Title.png')
        self.start_time = get_time()
        
    def enter(self):
        pass
        
    def update(self):
        pass
        
    def draw(self):
        self.image.draw(get_canvas_width()//2, get_canvas_height()//2)
        # 특정 시간이 지난 후 시작 안내 메시지 표시
        if get_time() - self.start_time > 1.0:
            font = load_font('res/ENCR10B.TTF', 20)
            msg = "Press SPACE to Start"
            w = font.width(msg)
            font.draw(get_canvas_width()//2 - w//2, 200, msg, (255, 255, 255))
            
    def handle_event(self, e):
        if e.type == SDL_KEYDOWN and e.key == SDLK_SPACE:
            gfw.change(MainScene())
            return True
        return False

class GameOverScene:
    def __init__(self, score=0):
        # world 속성 추가
        self.world = gfw.World(['bg', 'ui'])
        
        self.image = load_image('res/Game_Over.png')
        self.score = score
        self.opacity = 0
        self.start_time = get_time()
        
    def enter(self):
        # 배경 추가 (옵션)
        self.world.append(gfw.VertFillBackground('res/clouds.png', -60), self.world.layer.bg)
        
    def update(self):
        self.world.update()  # world 업데이트 추가
        
        elapsed = get_time() - self.start_time
        self.opacity = min(255, int(elapsed * 255))
        
    def draw(self):
        # world 그리기 추가
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
            return True
        return False


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
    
    collision_checker = CollisionChecker()
    collision_checker.set_game_objects(fighter, lives, lives_sprite)
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
    def __init__(self):
        self.fighter = None
        self.lives = 3
        self.lives_sprite = None
        
    def set_game_objects(self, fighter, lives, lives_sprite):
        self.fighter = fighter
        self.lives = lives
        self.lives_sprite = lives_sprite
        
    def update(self):
        # 플레이어 탄환과 적 충돌 체크
        for enemy in list(gfw.top().world.objects_at(gfw.top().world.layer.enemy))[:]:
            for bullet in Bullet.bullets[:]:
                if self.check_collision(bullet, enemy):
                    # 총알 제거
                    if bullet in Bullet.bullets:
                        Bullet.bullets.remove(bullet)
            
            # 적 체력 감소
                    if enemy.decrease_life(bullet.power):
                        # 적 제거 (안전한 방법)
                        try:
                            gfw.top().world.remove(enemy)
                        except ValueError:
                            print(f"Enemy {enemy} already removed")
            
        # 적 탄환과 플레이어 충돌 체크
        if self.fighter:
            for bullet in EnemyBullet.bullets[:]:
                if self.check_collision(bullet, self.fighter):
                    # 총알 제거
                    if bullet in EnemyBullet.bullets:
                        EnemyBullet.bullets.remove(bullet)
                    
                    # 목숨 감소
                    if self.lives_sprite:
                        self.lives_sprite.decrease()
                        self.lives = self.lives_sprite.lives
                        print(f"Player hit! Lives: {self.lives}")
                    
                    # 게임 오버 체크
                    if self.lives <= 0:
                        self.game_over()
                
    def check_collision(self, a, b):
        ax1, ay1, ax2, ay2 = a.get_bb()
        bx1, by1, bx2, by2 = b.get_bb()
        
        if ax2 < bx1: return False
        if ax1 > bx2: return False
        if ay2 < by1: return False
        if ay1 > by2: return False
        
        return True
        
    def game_over(self):
        gfw.change(GameOverScene(score=0))
        
    def draw(self):
        pass
                
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
        self.world = gfw.World(['bg', 'fighter', 'bullet', 'enemy', 'ui'])
        self.collision_checker = CollisionChecker()
        
    def enter(self):
        # 배경 초기화
        self.world.append(gfw.VertFillBackground('res/clouds.png', -60), self.world.layer.bg)
        self.world.append(gfw.VertFillBackground('res/bg_city.png', -30), self.world.layer.bg)
        
        # 플레이어 초기화
        self.fighter = Fighter()
        self.world.append(self.fighter, self.world.layer.fighter)
        self.collision_checker.set_fighter(self.fighter)
        
        # 적 생성기 초기화
        self.world.append(EnemyGen(), self.world.layer.enemy)
    def update(self):
        self.world.update()
    
        # 플레이어 및 적 총알 업데이트
        PlayerBullet.update_all(gfw.frame_time)
        EnemyBullet.update_all(gfw.frame_time)
    
        # CollisionChecker 업데이트
        self.collision_checker.update()

# MainScene draw 메서드  
    def draw(self):
        self.world.draw()
    
        # 플레이어 및 적 총알 그리기
        PlayerBullet.draw_all()
        EnemyBullet.draw_all()
        
    def handle_event(self, e):
        self.fighter.handle_event(e)


if __name__ == '__main__':
    gfw.start_main_module()