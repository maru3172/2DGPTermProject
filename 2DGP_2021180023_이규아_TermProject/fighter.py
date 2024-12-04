from pico2d import *
import math
from enemy import Enemy
import gfw

class Fighter(gfw.Sprite):
    KEY_MAP = {
        (SDL_KEYDOWN, SDLK_LEFT): -1,
        (SDL_KEYDOWN, SDLK_RIGHT): 1,
        (SDL_KEYUP, SDLK_LEFT): 1,
        (SDL_KEYUP, SDLK_RIGHT): -1,
    }
    LASER_INTERVAL = 0.25
    SPARK_INTERVAL = 0.05
    SPARK_OFFSET = 28
    MAX_ROLL = 0.4
    IMAGE_RECTS = [
        (8, 0, 42, 80),
        (76, 0, 42, 80),
        (140, 0, 50, 80),
        (205, 0, 56, 80),
        (270, 0, 62, 80),
        (334, 0, 70, 80),
        (406, 0, 62, 80),
        (477, 0, 56, 80),
        (549, 0, 48, 80),
        (621, 0, 42, 80),
        (689, 0, 42, 80),
    ]

    def __init__(self):
        super().__init__('res/fighters.png', get_canvas_width() // 2, 80)
        self.dx = 0
        self.speed = 320  # 320 pixels per second
        self.width = 72
        half_width = self.width // 2
        self.min_x = half_width
        self.max_x = get_canvas_width() - half_width
        self.laser_time = 0
        self.spark_image = gfw.image.load('res/laser_0.png')
        self.roll_time = 0
        self.src_rect = Fighter.IMAGE_RECTS[5]  # 0~10 의 11 개 중 5번이 가운데이다.
        self.dead = False  # 죽은 상태
        self.respawn_time = 0  # 부활 시간
        self.life = 100  # 생명

    def handle_event(self, e):
        if self.dead:
            return  # 사망 상태에서는 이동하지 않음
        
        pair = (e.type, e.key)
        if pair in Fighter.KEY_MAP:
            self.dx += Fighter.KEY_MAP[pair]

    def update(self):
        if self.dead:
            # 사망 상태이면 부활 대기
            if time.time() - self.respawn_time > 3:  # 3초 대기 후 부활
                self.respawn()
            return

        self.x += self.dx * self.speed * gfw.frame_time
        self.x = clamp(self.min_x, self.x, self.max_x)
        self.laser_time += gfw.frame_time
        if self.laser_time >= Fighter.LASER_INTERVAL:
            self.fire()
        self.update_roll()

    def update_roll(self):
        roll_dir = self.dx
        if roll_dir == 0:  # 현재 비행기가 움직이고 있지 않은데
            if self.roll_time > 0:  # roll 이 + 라면
                roll_dir = -1  # 감소시킨다
            elif self.roll_time < 0:  # roll 이 - 라면
                roll_dir = 1  # 증가시킨다

        self.roll_time += roll_dir * gfw.frame_time
        self.roll_time = clamp(-Fighter.MAX_ROLL, self.roll_time, Fighter.MAX_ROLL)

        if self.dx == 0:  # 현재 비행기가 움직이고 있지 않은데
            if roll_dir < 0 and self.roll_time < 0:  # roll 이 감소중이었고 0 을 지나쳤으면
                self.roll_time = 0  # 0 이 되게 한다
            if roll_dir > 0 and self.roll_time > 0:  # roll 이 증가중이었고 0 을 지나쳤으면
                self.roll_time = 0  # 0 이 되게 한다

        roll = int(self.roll_time * 5 / Fighter.MAX_ROLL)
        self.src_rect = Fighter.IMAGE_RECTS[roll + 5]  # [-5 ~ +5] 를 [0 ~ 10] 으로 변환한다.

    def draw(self):
        if self.dead:
            # 사망 중일 때 그리기 처리 (예: 반투명 상태로)
            pass
        else:
            self.image.clip_draw(*self.src_rect, self.x, self.y)
            if self.laser_time < Fighter.SPARK_INTERVAL:
                self.spark_image.draw(self.x, self.y + Fighter.SPARK_OFFSET)

    def fire(self):
        self.laser_time = 0
        world = gfw.top().world
        world.append(Bullet(self.x, self.y), world.layer.bullet)

    def get_bb(self):
        return self.x - 30, self.y - 32, self.x + 30, self.y + 28

    def decrease_life(self, power):
        print(f"Decrease life called. Current life: {self.life}, Power: {power}")
        # 무적 상태가 아니라면 생명 감소
        if not getattr(self, 'invincible', False):
            self.life -= power
            print(f"Life after decrease: {self.life}")
            if self.life <= 0:
                print("Life reached 0, calling game over")
                # 현재 씬의 게임 오버 메서드 호출
                current_scene = gfw.top()
                if hasattr(current_scene, 'game_over'):
                    current_scene.game_over()
                else:
                    # 대체 방법으로 world의 controller에서 game_over 함수 찾기
                    for obj in gfw.top().world.objects_at(gfw.top().world.layer.controller):
                        if hasattr(obj, 'game_over'):
                            obj.game_over()
                            break
    
    def respawn(self):
        """플레이어 부활 처리"""
        self.dead = False  # 부활
        self.life = 100  # 체력 회복
        self.x = get_canvas_width() // 2  # 초기 위치로 리셋
        self.y = 80

class Bullet(gfw.Sprite):
    bullets = []  # Class-level list to track all bullets

    @classmethod
    def update_all(cls, frame_time):
        cls.bullets = [bullet for bullet in cls.bullets if bullet.update()]

    @classmethod
    def draw_all(cls):
        for bullet in cls.bullets:
            bullet.draw()

    def __init__(self, x, y):  # 생성자
        super().__init__('res/laser_1.png', x, y)
        self.speed = 400  # 400 pixels per second
        self.max_y = get_canvas_height() + 50
        self.power = 40
        self.target = None
        self.is_removed = False
        self.layer_index = 2  # 레이어 인덱스 추가
        
        # Add to class-level bullet list
        Bullet.bullets.append(self)

    def get_nearest_enemy(self):
        try:
            enemies = [
                enemy for enemy in gfw.top().world.objects_of(gfw.top().world.layer.enemy)
                if hasattr(enemy, 'x') and hasattr(enemy, 'y')
            ]
            
            if not enemies:
                return None

            return min(
                enemies, 
                key=lambda enemy: math.sqrt((enemy.x - self.x) ** 2 + (enemy.y - self.y) ** 2)
            )
        except Exception as e:
            print(f"Error in get_nearest_enemy: {e}")
            return None

    def update(self):
        # Return False if bullet should be removed (like PlayerBullet)
        if self.is_removed:
            return False

        if self.target is None:
            self.target = self.get_nearest_enemy()

        if self.target is not None:
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            distance = math.sqrt(dx ** 2 + dy ** 2)
        
            if distance != 0:
                direction_x = dx / distance
                direction_y = dy / distance
                self.x += direction_x * self.speed * gfw.frame_time
                self.y += direction_y * self.speed * gfw.frame_time

                # 적과 충돌했을 때 총알 제거
                if self.target and self.collide_with_target():
                    self.remove()
                    return False
        else:
            self.y += self.speed * gfw.frame_time

        # Check if bullet is out of bounds
        if self.y > self.max_y:
            self.remove()
            return False
    
        return True

    def collide_with_target(self):
        if not self.target:
            return False

        b_left, b_bottom, b_right, b_top = self.get_bb()
        e_left, e_bottom, e_right, e_top = self.target.get_bb()

        if b_right < e_left or b_left > e_right:
            return False
        if b_top < e_bottom or b_bottom > e_top:
            return False

        # 적의 생명 감소
        is_killed = self.target.decrease_life(self.power)

        # 적이 죽으면 적 제거
        if is_killed:
            try:
                gfw.top().world.remove(self.target)
            except ValueError:
                # 이미 제거된 경우 무시
                pass

        return True
    def remove(self):
        self.is_removed = True
        if self in Bullet.bullets:
            Bullet.bullets.remove(self)
        gfw.top().world.remove(self)

    def draw(self):
        if not self.is_removed:
            super().draw()

    def get_bb(self):
        # Bounding box method from PlayerBullet
        return self.x - 4, self.y - 4, self.x + 4, self.y + 4