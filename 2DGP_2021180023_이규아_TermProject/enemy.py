from pico2d import *
import random
import gfw

def clamp(min_value, value, max_value):
    return max(min_value, min(value, max_value))

class Enemy(gfw.AnimSprite):
    WIDTH = 100
    MAX_LEVEL = 20
    gauge = None

    def __init__(self, x, y, level):
        self.x = x
        self.y = y
        self.level = level
        super().__init__(f'res/enemy_{level:02d}.png', x, y, 10)
        self.speed = -100  # 100 pixels per second
        self.max_life = level * 100
        self.life = self.max_life
        self.score = self.max_life
        if Enemy.gauge is None:
            Enemy.gauge = gfw.Gauge('res/gauge_fg.png', 'res/gauge_bg.png')
        self.layer_index = gfw.top().world.layer.enemy
        self.shoot_time = 0  # 발사 시간을 추적하기 위한 변수
        self.shoot_interval = 1.0  # 탄 발사 간격 (초)

        self.move_amplitude = 20  # 좌우 진동 범위 (작게 설정)
        self.move_frequency = 0.2  # 좌우 진동 속도 (느리게 설정)
        self.move_time = 0  # 진동 시간을 추적하기 위한 변수

        # 초기 상태 변수들
        self.is_moving_sideways = False  # 처음에는 좌우로 이동하지 않음
        self.sideway_duration = 2.0  # 좌우로 이동하는 시간 (초)
        self.sideway_timer = 0  # 좌우 이동 타이머
        self.idle_time = 3.0  # 아래로만 내려오는 시간 (초)
        self.idle_timer = 0  # 아래로만 내려오는 타이머
        self.move_direction = random.choice(['left', 'right'])  # 좌우 이동 방향 (초기 랜덤)

    def update(self):
        # 화면 크기 가져오기
        screen_width = gfw.top().screen_width  # 게임 화면의 가로 길이
        screen_height = gfw.top().screen_height  # 게임 화면의 세로 길이

        # 적의 이동 (y축) -> 기본적으로 아래로만 내려옴
        self.y += self.speed * gfw.frame_time

        if self.is_moving_sideways:
            # 좌우로 이동하는 상태
            self.sideway_timer += gfw.frame_time
            if self.move_direction == 'left':
                self.x -= self.move_amplitude * math.sin(self.move_frequency * self.move_time)
            elif self.move_direction == 'right':
                self.x += self.move_amplitude * math.sin(self.move_frequency * self.move_time)

            # 일정 시간 뒤, 다시 아래로만 내려옴
            if self.sideway_timer >= self.sideway_duration:
                self.is_moving_sideways = False
                self.sideway_timer = 0
                self.move_time = 0  # 진동 초기화
        else:
            # 아래로만 내려오는 상태
            self.idle_timer += gfw.frame_time
            if self.idle_timer >= self.idle_time:
                # 일정 시간 후에 좌우 이동을 시작
                self.is_moving_sideways = True
                self.move_direction = random.choice(['left', 'right'])  # 좌우 방향 랜덤 설정
                self.idle_timer = 0  # 타이머 초기화

        # 화면 밖으로 나가지 않도록 제한
        left_bound = 0  # 화면 왼쪽 경계
        right_bound = screen_width - self.WIDTH  # 화면 오른쪽 경계

        # 적의 x좌표가 화면 바깥으로 나가지 않도록 제한
        if self.x < left_bound:
            self.x = left_bound
        elif self.x > right_bound:
            self.x = right_bound

        # 화면 위로 나가면 제거
        if self.y < -self.WIDTH:
            gfw.top().world.remove(self)

        # 탄 발사 로직
        self.shoot_time += gfw.frame_time
        if self.shoot_time >= self.shoot_interval:
            self.fire()
            self.shoot_time = 0  # 발사 간격을 초기화

    def draw(self):
        super().draw()
        gy = self.y - self.WIDTH // 2
        rate = self.life / self.max_life
        self.gauge.draw(self.x, gy, self.WIDTH - 10, rate)

    def fire(self):
        # WIDTH//2를 제거하여 적의 중심점에서 발사하도록 수정
        bullet = EnemyBullet(self.x, self.y, power=self.level)
        print(f"Enemy firing bullet at ({self.x}, {self.y})")
        if bullet.image:
            gfw.top().world.append(bullet, bullet.layer_index)
        else:
            print("Error: Bullet creation failed - no image!")

    def decrease_life(self, power):
        self.life -= power
        return self.life <= 0

    def get_bb(self):
        r = 42
        return self.x - r, self.y - r, self.x + r, self.y + r

    def __repr__(self):
        return f'Enemy({self.level}/{self.life})'
        
class EnemyGen:
    GEN_INTERVAL = 5.0
    GEN_INIT = 1.0
    GEN_X = [50, 150, 250, 350, 450]  # 고정된 X 좌표 리스트
    GEN_Y_TOP = 800  # 화면 상단의 Y 좌표

    def __init__(self):
        self.time = self.GEN_INTERVAL - self.GEN_INIT
        self.wave_index = 0

    def draw(self):
        pass

    def update(self):
        self.time += gfw.frame_time
        if self.time < self.GEN_INTERVAL:
            return

        # 한 번에 생성될 적의 수를 1에서 5까지 랜덤으로 결정
        num_enemies = random.randint(1, 5)

        for i in range(num_enemies):
            # 랜덤으로 X 좌표를 선택
            x = random.choice(self.GEN_X)

            # 적의 레벨을 계산
            level = clamp(1, (self.wave_index + 18) // 10 - random.randrange(3), Enemy.MAX_LEVEL)

            # 랜덤 Y 좌표로 적 생성
            y = random.randint(self.GEN_Y_TOP - 100, self.GEN_Y_TOP)  # 화면 상단에서 랜덤 위치

            # Enemy 객체 생성
            enemy = Enemy(x, y, level)  # x, y, level을 전달
            gfw.top().world.append(enemy, gfw.top().world.layer.enemy)

        # 생성 주기 리셋
        self.time -= self.GEN_INTERVAL
        self.wave_index += 1

class EnemyBullet(gfw.Sprite):
    bullet_image = None
    
    def __init__(self, x, y, power=10):
        if EnemyBullet.bullet_image is None:
            EnemyBullet.bullet_image = load_image('res/enemy_bullet.png')
            print("Loading enemy bullet image")
        
        self.x, self.y = x, y
        self.image = EnemyBullet.bullet_image
        self.speed = 200  # 음수에서 양수로 변경 (아래로 이동)
        self.min_y = -50
        self.power = power
        self.layer_index = gfw.top().world.layer.bullet
        self.is_removed = False
        print(f"Bullet created at ({self.x}, {self.y})")
        
    def update(self):
        if self.is_removed:
            return
    
        old_y = self.y
        self.y -= self.speed * gfw.frame_time
        print(f"Bullet moved from y={old_y} to y={self.y}")

    def draw(self):
        if self.is_removed:
            return
            
        if self.image:
            self.image.draw(self.x, self.y)
        else:
            print("Error: No bullet image loaded!")
            
    def get_bb(self):
        r = 15
        return self.x - r, self.y - r, self.x + r, self.y + r