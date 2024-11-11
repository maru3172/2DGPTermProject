# 2DGPTermProject
2D Game Programming Term Project 2021180023

Project 2021180023

게임의 간단한 소개

"1942"와 유사한 생존 게임으로, 플레이어가 전투기를 조종하여 몰려오는 적의 공격을 피하는 게임,

주요 기능은 플레이어 조작과 충돌 판정, 가까운 적에게 유도되는 탄이다.

플레이 예시 스크린샷

<p align="left">
<img width="70%" alt="스크린샷 2-24-10-21" src="https://github.com/user-attachments/assets/78cc9f41-f91b-4633-91ff-480085041206">
</p>

-------------------------------------------------------------------------------------

예상 게임 실행 흐름

1. 타이틀 화면

2. 게임 플레이
 
3. 플레이어 사망
 
4. 게임 종료 화면
 
5. 게임 종료

<p align="left">
<img width="70%" alt="스크린샷 2-24-10-21" src="https://github.com/user-attachments/assets/33c19682-d72d-481b-82d8-5fe675d272aa">
</p>

-------------------------------------------------------------------------------------

개발 내용

씬 종류: 타이틀 화면, 게임 화면, 게임 종료 화면

전환 방법

타이틀 → 게임: Enter 키를 눌러 전환.

게임 조작: 좌/우 키로 캐릭터 이동.

게임 → 게임 종료: 플레이어 사망 시 전환.

===================================================================

- 각 Scene 에 등장하는 GameObject 의 종류 및 구성, 상호작용

 Enemy 클래스: 적 캐릭터로, 화면에서 이동하며 체력 바를 표시하고, 체력이 0이 되면 제거됨

 EnemyGen 클래스: 일정 시간 간격으로 적을 생성하고, 점차 강해지는 적들을 등장시킴

 Fighter: 플레이어의 전투기로, 좌우 이동과 총알 발사 및 회전 애니메이션을 처리, 비행기의 애니메이션 프레임과 총알 발사 효과로 구성

 Bullet: 전투기에서 발사된 총알로, 위로 날아가면서 적을 추적, 화면을 벗어나면 사라짐, laser_1.png 총알 이미지

 MainScenUI 클래스: 게임의 UI에서 플레이어의 목숨을 화면에 표시하는 역할, 큰 글씨로 목숨을 오른쪽 아래에 표시

 CollisionChecker 클래스: 화면에 표시되는 요소는 없으며, 적과 총알, 전투기와 적 간의 충돌 처리를 담당

- 함수 단위 설명

현재 개발 중, 추후 수정 예정

===================================================================

- 사용한/할 개발 기법들에 대한 간단한 소개



- 게임 프레임워크



-------------------------------------------------------------------------------------

10/28 이전

개발 계획 수립 및 게임 컨셉 확립

피요한기능 구현 방법 조사 및 강의 내용 참고

개발에 필요한 리소스 고안 및 조사

===================================================================

각 주차별 계획

1주차 - 계획 적용 및 건의 사항을 바탕으로 내용 보완

2주차 - 추가 내용 보완 및 게임 프레임워크, 게임 루프 수립, 피드백 반영(진행중)

3주차 - 플레이어 이동 및 공격 구현.

4주차 - 적의 공격 및 이동 구현.

5주차 - 충돌 판정으로 플레이어 피격 시 목숨 감소 적용.

6주차 - 배경 화면 이동 구현, 기능 테스트 및 최종 유지보수

-------------------------------------------------------------------------------------
출처

https://www.taptap.io/kr/app/33601228 - TapTap, 1942 Air Force Classic Fighter Game Play ScreenShot
