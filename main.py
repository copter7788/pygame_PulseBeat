import pygame as pg
import os, time, random

TITLE = "PulseBeat "  # ตั้งค่าชื่อเกม
WIDTH = 640  # ความกว้างของหน้าจอ
HEIGHT = 480  # ความสูงของหน้าจอ
FPS = 60  # เฟรมต่อวินาที
DEFAULT_FONT = "NotoSansCJKkr-Regular.otf"  # ฟอนต์เริ่มต้น

COLOR1 = (238, 238, 238)  # กำหนดค่าสี
COLOR2 = (32, 36, 32)
COLOR3 = (246, 36, 74)
COLOR4 = (32, 105, 246)
ALPHA_MAX = 255  # ค่าสูงสุดของอัลฟา (ความโปร่งใส)


class Game:
    def __init__(self):  # เริ่มต้นเกม
        pg.init()  # เริ่มต้น pygame
        pg.mixer.init()  # เริ่มต้นมิกเซอร์เสียง
        pg.display.set_caption(TITLE)  # ตั้งชื่อหน้าต่างเกม
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))  # ตั้งค่าขนาดหน้าจอ
        self.screen_mode = 0  # โหมดหน้าจอ (0: โลโก้, 1: โลโก้ 2, 2: หน้าหลัก, 3: เลือกเพลง, 4: เล่นเกม, 5: คะแนน)
        self.screen_value = [-ALPHA_MAX, 0, 0, 0]  # ตัวจัดการค่าหน้าจอ
        self.clock = pg.time.Clock()  # ตัวนับเวลา FPS
        self.start_tick = 0  # ตัวจับเวลาของเกม
        self.running = True  # ค่าบูลีนสำหรับสถานะการทำงานของเกม
        self.language_mode = 0  # โหมดภาษา (0: อังกฤษ, 1: เกาหลี, 2~: กำหนดเอง)
        self.song_select = 1  # เลือกเพลง
        self.load_date()  # โหลดข้อมูล
        self.new()
        pg.mixer.music.load(self.bg_main)  # โหลดเพลงพื้นหลัง

    def load_date(self):  # โหลดข้อมูล
        self.dir = os.path.dirname(__file__)  # ไดเรกทอรีของไฟล์ปัจจุบัน

        # ฟอนต์
        self.fnt_dir = os.path.join(self.dir, "font")  # ไดเรกทอรีฟอนต์
        self.gameFont = os.path.join(self.fnt_dir, DEFAULT_FONT)  # ฟอนต์เริ่มต้น

        with open(
            os.path.join(self.fnt_dir, "language.ini"), "r", encoding="UTF-8"
        ) as language_file:
            language_lists = language_file.read().split("\n")  # อ่านไฟล์ภาษา

        self.language_list = [n.split("_") for n in language_lists]  # แยกภาษาเป็นรายการ

        # รูปภาพ
        self.img_dir = os.path.join(self.dir, "image")  # ไดเรกทอรีรูปภาพ
        self.spr_logoback = pg.image.load(
            os.path.join(self.img_dir, "logoback.png")
        )  # โหลดพื้นหลังโลโก้
        self.spr_logo = pg.image.load(
            os.path.join(self.img_dir, "logo.png")
        )  # โหลดโลโก้
        self.spr_circle = pg.image.load(
            os.path.join(self.img_dir, "circle.png")
        )  # โหลดรูปวงกลม
        self.spr_shot = Spritesheet(
            os.path.join(self.img_dir, "shot.png")
        )  # โหลดสไปรต์ของช็อต

        # เสียง
        self.snd_dir = os.path.join(self.dir, "sound")  # ไดเรกทอรีเสียง
        self.bg_main = os.path.join(self.snd_dir, "bg_main.ogg")  # เสียงพื้นหลัง
        self.sound_click = pg.mixer.Sound(
            os.path.join(self.snd_dir, "click.ogg")
        )  # เสียงคลิก
        self.sound_drum1 = pg.mixer.Sound(
            os.path.join(self.snd_dir, "drum1.ogg")
        )  # เสียงกลอง 1
        self.sound_drum2 = pg.mixer.Sound(
            os.path.join(self.snd_dir, "drum2.ogg")
        )  # เสียงกลอง 2
        self.sound_drum3 = pg.mixer.Sound(
            os.path.join(self.snd_dir, "drum3.ogg")
        )  # เสียงกลอง 3
        self.sound_drum4 = pg.mixer.Sound(
            os.path.join(self.snd_dir, "drum4.ogg")
        )  # เสียงกลอง 4

        # เพลง
        self.sng_dir = os.path.join(self.dir, "song")  # ไดเรกทอรีเพลง
        music_type = ["ogg", "mp3", "wav"]  # ประเภทไฟล์เพลงที่รองรับ
        song_lists = [
            i for i in os.listdir(self.sng_dir) if i.split(".")[-1] in music_type
        ]  # รายการเพลง
        self.song_list = list()  # รายชื่อเพลง
        self.song_path = list()  # เส้นทางของเพลง

        for song in song_lists:  # โหลดเพลง
            try:
                pg.mixer.music.load(os.path.join(self.sng_dir, song))
                self.song_list.append(song.split(".")[0])
                self.song_path.append(os.path.join(self.sng_dir, song))
            except:
                print("error: " + str(song) + " เป็นไฟล์เพลงที่ไม่รองรับ")

        self.song_num = len(self.song_list)  # จำนวนเพลงที่มี
        self.song_dataPath = list()  # เส้นทางไฟล์ข้อมูลเพลง
        self.song_highScore = list()  # รายการคะแนนสูงสุดของเพลง
        self.song_perfectScore = list()  # รายการคะแนนสมบูรณ์ของเพลง

        for song in self.song_list:
            song_dataCoord = os.path.join(self.sng_dir, song + ".ini")  # ไฟล์ข้อมูลเพลง

            try:
                with open(song_dataCoord, "r", encoding="UTF-8") as song_file:
                    song_scoreList = song_file.read().split("\n")[0]

                self.song_highScore.append(
                    int(song_scoreList.split(":")[1])
                )  # อ่านคะแนนสูงสุด
                self.song_perfectScore.append(
                    int(song_scoreList.split(":")[2])
                )  # อ่านคะแนนสมบูรณ์
                self.song_dataPath.append(song_dataCoord)
            except:
                print("error: ไฟล์ข้อมูลเพลงของ " + str(song) + " เสียหายหรือไม่มีอยู่")
                self.song_highScore.append(-1)
                self.song_perfectScore.append(-1)
                self.song_dataPath.append(-1)

    def new(self):  # เริ่มต้นค่าเกมใหม่
        self.song_data = list()  # รายการข้อมูลเพลง
        self.song_dataLen = 0  # ความยาวข้อมูลเพลง
        self.song_dataIndex = 0  # ดัชนีข้อมูลเพลง
        self.circle_dir = 1  # ทิศทางวงกลม (1: ล่าง, 2: ขวา, 3: บน, 4: ซ้าย)
        self.circle_rot = 0  # การหมุนวงกลม
        self.score = 0  # คะแนนปัจจุบัน
        self.all_sprites = pg.sprite.Group()  # กลุ่มสไปรต์ทั้งหมด
        self.shots = pg.sprite.Group()  # กลุ่มสไปรต์ช็อต

    def run(self):  # ลูปหลักของเกม
        self.playing = True  # สถานะการเล่น

        while self.playing:
            self.clock.tick(FPS)  # จำกัดอัตราเฟรม
            self.events()  # จัดการเหตุการณ์
            self.update()  # อัปเดตสถานะ
            self.draw()  # วาดหน้าจอ
            pg.display.flip()  # อัปเดตหน้าจอ

        pg.mixer.music.fadeout(600)  # ลดเสียงเพลงพื้นหลัง

    def update(self):  # อัปเดตลูปเกม
        self.all_sprites.update()  # อัปเดตสไปรต์ทั้งหมด
        self.game_tick = pg.time.get_ticks() - self.start_tick  # คำนวณเวลาการเล่นเกม

    def events(self):  # จัดการเหตุการณ์ในลูปเกม
        mouse_coord = pg.mouse.get_pos()  # ตำแหน่งของเมาส์
        mouse_move = False  # สถานะการเคลื่อนที่ของเมาส์
        mouse_click = 0  # สถานะการคลิกเมาส์ (1: คลิกซ้าย, 3: คลิกขวา)
        key_click = 0  # ค่าการกดคีย์ (275: ขวา, 276: ซ้าย, 273: ขึ้น, 274: ลง)

        for event in pg.event.get():  # Event Check
            if event.type == pg.QUIT:  # exit
                if self.playing:
                    self.playing, self.running = False, False
            elif event.type == pg.KEYDOWN:  # keyboard check
                key_click = event.key

                if self.screen_mode < 4:
                    self.sound_click.play()
            elif event.type == pg.MOUSEMOTION:
                if event.rel[0] != 0 or event.rel[1] != 0:  # mousemove
                    mouse_move = True
            elif event.type == pg.MOUSEBUTTONDOWN:  # mouse click
                mouse_click = event.button

                if self.screen_mode < 4:
                    self.sound_click.play()

        if self.screen_mode == 0:  # Logo Screen1
            self.screen_value[0] += ALPHA_MAX / 51

            if self.screen_value[0] == ALPHA_MAX:
                self.screen_value[0] = 0
                self.screen_mode = 1
                pg.mixer.music.play(loops=-1)
        elif self.screen_mode == 1:  # Logo Screen2
            if self.screen_value[3] == 0:
                if self.screen_value[0] < ALPHA_MAX:
                    self.screen_value[0] += ALPHA_MAX / 51
                else:
                    if mouse_click == 1 or key_click != 0:
                        self.screen_value[3] = 1
            else:
                if self.screen_value[0] > 0:
                    self.screen_value[0] -= ALPHA_MAX / 15
                else:
                    self.screen_mode = 2
                    self.screen_value[1] = 2
                    self.screen_value[2] = 0
                    self.screen_value[3] = 0

            if self.screen_value[1] > -10:
                self.screen_value[1] -= 1
            else:
                if self.screen_value[2] == 0:
                    self.screen_value[1] = random.randrange(0, 10)
                    self.screen_value[2] = random.randrange(5, 30)
                else:
                    self.screen_value[2] -= 1
        elif self.screen_mode == 2:  # Main Screen
            if self.screen_value[2] == 0:
                if self.screen_value[0] < ALPHA_MAX:
                    self.screen_value[0] += ALPHA_MAX / 15

                    if self.screen_value[3] > 0:
                        self.screen_value[3] -= ALPHA_MAX / 15
                else:
                    for i in range(4):
                        if (
                            mouse_move
                            and 400 < mouse_coord[0] < 560
                            and 105 + i * 70 < mouse_coord[1] < 155 + i * 70
                        ):  # mouse cursor check
                            self.screen_value[1] = i + 1

                    if (key_click == 273 or mouse_click == 4) and self.screen_value[
                        1
                    ] > 1:  # key up check
                        self.screen_value[1] -= 1
                    elif (key_click == 274 or mouse_click == 5) and self.screen_value[
                        1
                    ] < 4:  # key down check
                        self.screen_value[1] += 1

                    if (
                        mouse_click == 1 or key_click == 13 or key_click == 275
                    ):  # click or key enter, key right check
                        if self.screen_value[1] == 1:  # START
                            self.screen_value[2] = 1
                        elif self.screen_value[1] == 2:  # HELP
                            self.screen_value[0] = ALPHA_MAX / 3
                            self.screen_value[2] = 2
                        elif self.screen_value[1] == 3:  # EXIT
                            self.screen_value[2] = 3
                        else:  # Languague
                            self.language_mode = (
                                self.language_mode + 1
                                if self.language_mode < len(self.language_list) - 1
                                else 0
                            )
                            self.gameFont = os.path.join(
                                self.fnt_dir, self.load_language(1)
                            )
            elif self.screen_value[2] == 1:
                if self.screen_value[0] > 0:
                    self.screen_value[0] -= ALPHA_MAX / 15
                else:
                    self.screen_mode = 3
                    self.screen_value[1] = 0
                    self.screen_value[2] = 0

                    if self.song_highScore[self.song_select - 1] == -1:
                        pg.mixer.music.fadeout(600)
                    else:
                        pg.mixer.music.load(self.song_path[self.song_select - 1])
                        pg.mixer.music.play(loops=-1)
            elif self.screen_value[2] == 2:
                if mouse_click == 1 or key_click != 0:
                    self.screen_value[2] = 0
            elif self.screen_value[2] == 3:
                if self.screen_value[0] > 0:
                    self.screen_value[0] -= ALPHA_MAX / 15
                else:
                    self.playing, self.running = False, False
        elif self.screen_mode == 3:  # Song Select Screen
            if self.screen_value[2] == 0:
                if self.screen_value[0] < ALPHA_MAX:
                    self.screen_value[0] += ALPHA_MAX / 15

                self.screen_value[1] = 0
                songChange = False

                if (
                    round(0.31 * WIDTH - 75) < mouse_coord[0] < round(0.31 * WIDTH + 75)
                ):  # mouse coord check
                    if round(0.125 * HEIGHT + 30) > mouse_coord[1]:
                        self.screen_value[1] = 1
                    elif round(0.875 * HEIGHT - 30) < mouse_coord[1]:
                        self.screen_value[1] = 2
                elif round(0.69 * WIDTH - 75) < mouse_coord[0] < round(
                    0.69 * WIDTH + 75
                ) and round(HEIGHT / 2 + 25) < mouse_coord[1] < round(HEIGHT / 2 + 65):
                    self.screen_value[1] = 3
                elif round(0.73 * WIDTH - 75) < mouse_coord[0] < round(
                    0.73 * WIDTH + 75
                ) and round(HEIGHT / 2 + 85) < mouse_coord[1] < round(HEIGHT / 2 + 125):
                    self.screen_value[1] = 4

                if mouse_click == 1:  # mouse clickcheck
                    if self.screen_value[1] == 1:
                        if self.song_select > 1:
                            self.song_select -= 1
                            songChange = True
                    elif self.screen_value[1] == 2:
                        if self.song_select < self.song_num:
                            self.song_select += 1
                            songChange = True
                    elif self.screen_value[1] == 3:
                        if self.song_highScore[self.song_select - 1] != -1:
                            self.screen_value[2] = 1
                    elif self.screen_value[1] == 4:
                        self.screen_value[2] = 2
                elif key_click == 273 or mouse_click == 4:  # key check
                    if self.song_select > 1:
                        self.song_select -= 1
                        songChange = True
                elif key_click == 274 or mouse_click == 5:
                    if self.song_select < self.song_num:
                        self.song_select += 1
                        songChange = True
                elif key_click == 275 or key_click == 13:
                    if self.song_highScore[self.song_select - 1] != -1:
                        self.screen_value[2] = 1
                elif key_click == 276:
                    self.screen_value[2] = 2

                if songChange:
                    if self.song_highScore[self.song_select - 1] == -1:
                        pg.mixer.music.fadeout(600)
                    else:
                        pg.mixer.music.load(self.song_path[self.song_select - 1])
                        pg.mixer.music.play(loops=-1)
            else:
                if self.screen_value[0] > 0:
                    self.screen_value[0] -= ALPHA_MAX / 15
                else:
                    if self.screen_value[2] == 1:
                        self.screen_mode = 4
                        self.screen_value[1] = 0
                        self.screen_value[2] = 0
                        self.start_tick = pg.time.get_ticks()
                        self.load_songData()
                    else:
                        self.screen_mode = 2
                        self.screen_value[1] = 0
                        self.screen_value[2] = 0
                        self.screen_value[3] = ALPHA_MAX
                        pg.mixer.music.load(self.bg_main)
                        pg.mixer.music.play(loops=-1)
        elif self.screen_mode == 4:  # Play Screen
            if self.screen_value[1] == 0:
                if self.screen_value[0] < ALPHA_MAX:
                    self.screen_value[0] += ALPHA_MAX / 15

                if mouse_click == 1:  # mouse clickcheck
                    if mouse_coord[0] < WIDTH / 2:
                        self.circle_dir += 1
                    else:
                        self.circle_dir -= 1
                elif key_click == 276:  # key check
                    self.circle_dir += 1
                elif key_click == 275:
                    self.circle_dir -= 1

                if self.circle_dir > 4:  # circle direction management
                    self.circle_dir = 1
                elif self.circle_dir < 1:
                    self.circle_dir = 4

                rotToDir = (self.circle_dir - 1) * 90  # circle rotation management

                if self.circle_rot != rotToDir:
                    if self.circle_rot >= rotToDir:
                        if self.circle_rot >= 270 and rotToDir == 0:
                            self.circle_rot += 15
                        else:
                            self.circle_rot -= 15
                    else:
                        if self.circle_rot == 0 and rotToDir == 270:
                            self.circle_rot = 345
                        else:
                            self.circle_rot += 15

                if self.circle_rot < 0:
                    self.circle_rot = 345
                elif self.circle_rot > 345:
                    self.circle_rot = 0

                self.create_shot()  # create shot
            else:
                if self.screen_value[0] > 0:
                    self.screen_value[0] -= ALPHA_MAX / 85
                else:
                    self.screen_mode = 5
                    self.screen_value[1] = 0
        else:  # Score Screen
            if self.screen_value[1] == 0:
                if self.screen_value[0] < ALPHA_MAX:
                    self.screen_value[0] += ALPHA_MAX / 15

                if mouse_move:
                    if round(WIDTH / 2 - 160) < mouse_coord[0] < round(
                        WIDTH / 2 - 40
                    ) and round(HEIGHT / 2 + 110) < mouse_coord[1] < round(
                        HEIGHT / 2 + 170
                    ):
                        self.screen_value[2] = 1
                    elif round(WIDTH / 2 + 40) < mouse_coord[0] < round(
                        WIDTH / 2 + 160
                    ) and round(HEIGHT / 2 + 110) < mouse_coord[1] < round(
                        HEIGHT / 2 + 170
                    ):
                        self.screen_value[2] = 2

                if mouse_click == 1:  # mouse clickcheck
                    self.screen_value[1] = self.screen_value[2]
                elif key_click == 276 or mouse_click == 4:  # key check
                    self.screen_value[2] = 1
                elif key_click == 275 or mouse_click == 5:
                    self.screen_value[2] = 2
                elif key_click == 13:
                    self.screen_value[1] = self.screen_value[2]
            else:
                if self.screen_value[0] > 0:
                    self.screen_value[0] -= ALPHA_MAX / 15
                else:
                    self.new()

                    if self.screen_value[1] == 1:
                        self.screen_mode = 3
                    else:
                        self.screen_mode = 4
                        self.start_tick = pg.time.get_ticks()
                        self.load_songData()

                    self.screen_value[1] = 0
                    self.screen_value[2] = 0

    def draw(self):  # Game Loop - Draw
        self.background = pg.Surface((WIDTH, HEIGHT))  # COLOR1 background
        self.background = self.background.convert()
        self.background.fill(COLOR1)
        self.screen.blit(self.background, (0, 0))
        self.draw_screen()  # draw screen
        self.all_sprites.draw(self.screen)
        pg.display.update()

    def draw_screen(self):  # Draw Screen
        screen_alpha = self.screen_value[0]

        if self.screen_mode == 0:  # logo screen1
            screen_alpha = ALPHA_MAX - min(max(self.screen_value[0], 0), ALPHA_MAX)
        elif self.screen_mode == 1:  # logo screen2
            (
                self.spr_logoback.set_alpha(screen_alpha)
                if self.screen_value[3] == 0
                else self.spr_logoback.set_alpha(ALPHA_MAX)
            )
            self.screen.blit(self.spr_logoback, (0, 0))
            spr_logoRescale = pg.transform.scale(
                self.spr_logo, (301 + self.screen_value[1], 306 + self.screen_value[1])
            )
            self.draw_sprite(
                ((WIDTH - self.screen_value[1]) / 2, 40 - self.screen_value[1] / 2),
                spr_logoRescale,
                screen_alpha,
            )
        elif self.screen_mode == 2:  # main screen
            select_index = [
                True if self.screen_value[1] == i + 1 else False for i in range(4)
            ]

            if self.screen_value[2] == 0:
                self.draw_sprite(
                    (0, 0), self.spr_logoback, ALPHA_MAX - self.screen_value[3]
                )
            else:
                self.spr_logoback.set_alpha(screen_alpha)
                logoback_coord = (
                    0
                    if self.screen_value[2] == 2
                    else round((screen_alpha - ALPHA_MAX) / 10)
                )
                self.screen.blit(self.spr_logoback, (logoback_coord, 0))

            if self.screen_value[2] == 2:
                help_surface = pg.Surface((WIDTH - 60, HEIGHT - 60))
                help_surface.fill(COLOR1)
                help_surface.set_alpha(200)
                self.screen.blit(help_surface, pg.Rect(30, 30, 0, 0))
                self.draw_text(
                    "- " + self.load_language(5) + " -", 36, COLOR2, 320, 50, 255
                )
                self.draw_text(self.load_language(9), 16, COLOR2, 320, 150)
                self.draw_text(self.load_language(10), 16, COLOR2, 320, 220)
                self.draw_text(self.load_language(11), 16, COLOR2, 320, 290)
            else:
                self.draw_text(
                    self.load_language(2),
                    36,
                    COLOR2,
                    480,
                    105,
                    screen_alpha,
                    select_index[0],
                )
                self.draw_text(
                    self.load_language(3),
                    36,
                    COLOR2,
                    480,
                    175,
                    screen_alpha,
                    select_index[1],
                )
                self.draw_text(
                    self.load_language(4),
                    36,
                    COLOR2,
                    480,
                    245,
                    screen_alpha,
                    select_index[2],
                )
                self.draw_text(
                    self.load_language(0),
                    24,
                    COLOR2,
                    480,
                    315,
                    screen_alpha,
                    select_index[3],
                )
        elif self.screen_mode == 3:  # song select screen
            surface = pg.Surface((WIDTH, HEIGHT))
            surface.fill(COLOR1)
            surface.set_alpha(max(screen_alpha - 50, 0))
            circle_coord = (round(WIDTH * 1.2), round(HEIGHT / 2))
            pg.draw.circle(
                surface, COLOR2, circle_coord, round(0.78 * WIDTH + screen_alpha), 1
            )
            pg.draw.circle(
                surface, COLOR2, circle_coord, round(0.32 * WIDTH + screen_alpha), 1
            )
            pg.draw.circle(
                surface,
                COLOR2,
                circle_coord,
                max(round(-0.1 * WIDTH + screen_alpha), 1),
                1,
            )
            pg.draw.circle(
                surface,
                COLOR3,
                circle_coord,
                max(round(-0.12 * WIDTH + screen_alpha), 1),
                1,
            )
            pg.draw.circle(
                surface,
                COLOR4,
                circle_coord,
                max(round(-0.08 * WIDTH + screen_alpha), 1),
                1,
            )
            self.screen.blit(surface, (0, 0))

            if self.song_select > 2:
                self.draw_text(
                    self.song_list[self.song_select - 3],
                    16,
                    COLOR2,
                    0.29 * WIDTH,
                    0.25 * HEIGHT - 20,
                    max(screen_alpha - 220, 0),
                )

            if self.song_select > 1:
                self.draw_text(
                    self.song_list[self.song_select - 2],
                    18,
                    COLOR2,
                    0.27 * WIDTH,
                    0.375 * HEIGHT - 20,
                    max(screen_alpha - 180, 0),
                )

            self.draw_text(
                self.song_list[self.song_select - 1],
                24,
                COLOR2,
                0.25 * WIDTH,
                0.5 * HEIGHT - 20,
                screen_alpha,
            )

            if self.song_select < self.song_num:
                self.draw_text(
                    self.song_list[self.song_select],
                    18,
                    COLOR2,
                    0.27 * WIDTH,
                    0.625 * HEIGHT - 20,
                    max(screen_alpha - 180, 0),
                )

            if self.song_select < self.song_num - 1:
                self.draw_text(
                    self.song_list[self.song_select + 1],
                    16,
                    COLOR2,
                    0.29 * WIDTH,
                    0.75 * HEIGHT - 20,
                    max(screen_alpha - 220, 0),
                )

            button_songUp = "▲" if self.screen_value[1] == 1 else "△"
            button_songDown = "▼" if self.screen_value[1] == 2 else "▽"
            select_index = [
                True if self.screen_value[1] == i + 3 else False for i in range(2)
            ]
            self.draw_text(
                button_songUp,
                24,
                COLOR2,
                0.31 * WIDTH,
                0.125 * HEIGHT - 20,
                screen_alpha,
            )
            self.draw_text(
                button_songDown,
                24,
                COLOR2,
                0.31 * WIDTH,
                0.875 * HEIGHT - 30,
                screen_alpha,
            )

            if self.song_highScore[self.song_select - 1] == -1:
                self.draw_text(
                    self.load_language(12),
                    32,
                    COLOR3,
                    0.71 * WIDTH,
                    HEIGHT / 2 - 100,
                    screen_alpha,
                )
            else:
                if (
                    self.song_highScore[self.song_select - 1]
                    >= self.song_perfectScore[self.song_select - 1]
                ):
                    try:
                        font = pg.font.Font(self.gameFont, 36)
                    except:
                        font = pg.font.Font(
                            os.path.join(self.fnt_dir, DEFAULT_FONT), 36
                        )

                    font.set_bold(True)
                    cleartext_surface = font.render(
                        self.load_language(14), False, COLOR4
                    )
                    rotated_surface = pg.transform.rotate(cleartext_surface, 25)
                    rotated_surface.set_alpha(max(screen_alpha - 180, 0))
                    cleartext_rect = rotated_surface.get_rect()
                    cleartext_rect.midtop = (
                        round(0.71 * WIDTH),
                        round(HEIGHT / 2 - 150),
                    )
                    self.screen.blit(rotated_surface, cleartext_rect)

                self.draw_text(
                    self.load_language(8),
                    28,
                    COLOR2,
                    0.69 * WIDTH,
                    HEIGHT / 2 - 130,
                    screen_alpha,
                )
                self.draw_text(
                    str(self.song_highScore[self.song_select - 1]),
                    28,
                    COLOR2,
                    0.69 * WIDTH,
                    HEIGHT / 2 - 70,
                    screen_alpha,
                )
                self.draw_text(
                    self.load_language(7),
                    32,
                    COLOR2,
                    0.69 * WIDTH,
                    HEIGHT / 2 + 25,
                    screen_alpha,
                    select_index[0],
                )

            self.draw_text(
                self.load_language(6),
                32,
                COLOR2,
                0.73 * WIDTH,
                HEIGHT / 2 + 85,
                screen_alpha,
                select_index[1],
            )
        elif self.screen_mode == 4:  # play screen
            surface = pg.Surface((WIDTH, HEIGHT))
            surface.fill(COLOR1)
            surface.set_alpha(max(screen_alpha - 240, 0))
            pg.draw.circle(
                surface, COLOR2, (round(WIDTH / 2), round(HEIGHT / 2)), 200, 1
            )
            self.screen.blit(surface, (0, 0))
            self.draw_sprite(
                ((WIDTH - 99) / 2, (HEIGHT - 99) / 2),
                self.spr_circle,
                screen_alpha,
                self.circle_rot,
            )
            time_m = self.game_tick // 60000
            time_s = str(round(self.game_tick / 1000) - time_m * 60)

            if len(time_s) == 1:
                time_s = "0" + time_s

            time_str = str(time_m) + " : " + time_s
            score_str = self.load_language(13) + " : " + str(self.score)
            self.draw_text(
                time_str, 24, COLOR2, 10 + len(time_str) * 6, 15, screen_alpha
            )
            self.draw_text(
                score_str, 24, COLOR2, WIDTH - 10 - len(score_str) * 6, 15, screen_alpha
            )
        else:
            surface = pg.Surface((WIDTH, HEIGHT))
            surface.fill(COLOR1)
            surface.set_alpha(max(screen_alpha - 50, 0))
            circle_coord = (round(WIDTH / 2), round(HEIGHT / 2))
            pg.draw.circle(surface, COLOR4, circle_coord, round(HEIGHT / 2 - 30), 1)
            pg.draw.circle(surface, COLOR2, circle_coord, round(HEIGHT / 2), 1)
            pg.draw.circle(surface, COLOR3, circle_coord, round(HEIGHT / 2 + 30), 1)
            self.screen.blit(surface, (0, 0))
            self.draw_text(
                self.load_language(15)
                + " : "
                + str(self.song_perfectScore[self.song_select - 1]),
                32,
                COLOR2,
                WIDTH / 2,
                HEIGHT / 2 - 65,
                screen_alpha,
            )
            self.draw_text(
                self.load_language(13) + " : " + str(self.score),
                32,
                COLOR2,
                WIDTH / 2,
                HEIGHT / 2 - 5,
                screen_alpha,
            )
            select_index = [
                True if self.screen_value[2] == i + 1 else False for i in range(2)
            ]
            self.draw_text(
                self.load_language(17),
                24,
                COLOR2,
                WIDTH / 2 - 100,
                HEIGHT / 2 + 125,
                ALPHA_MAX,
                select_index[0],
            )
            self.draw_text(
                self.load_language(16),
                24,
                COLOR2,
                WIDTH / 2 + 100,
                HEIGHT / 2 + 125,
                ALPHA_MAX,
                select_index[1],
            )

    def load_language(self, index):
        try:
            return self.language_list[self.language_mode][index]
        except:
            return "Font Error"

    def load_songData(self):
        with open(
            self.song_dataPath[self.song_select - 1], "r", encoding="UTF-8"
        ) as data_file:
            data_fileLists = data_file.read().split("\n")

        for data_line in data_fileLists:
            if data_line != "" and data_line[0] != "s":
                data_fileList = data_line.split(" - ")
                time_list = data_fileList[0].split(":")
                shot_list = data_fileList[1].split(", ")
                current_songData = list()
                current_songData.append(
                    int(time_list[0]) * 60000
                    + int(time_list[1]) * 1000
                    + int(time_list[2]) * 10
                )

                for shot in shot_list:
                    if shot[0] == "E":
                        shot_color = -1
                    elif shot[0] == "W":
                        shot_color = 1
                    elif shot[0] == "B":
                        shot_color = 2
                    elif shot[0] == "D":
                        shot_color = 3
                    else:
                        shot_color = 4

                    if shot_color != -1:
                        if shot[1] == "D":
                            shot_mode = 0
                        elif shot[1] == "R":
                            shot_mode = 90
                        elif shot[1] == "U":
                            shot_mode = 180
                        else:
                            shot_mode = 270

                        if shot[2] == "D":
                            shot_dir = 0
                        elif shot[2] == "R":
                            shot_dir = 90
                        elif shot[2] == "U":
                            shot_dir = 180
                        else:
                            shot_dir = 270

                        shot_data = (shot_color, shot_mode, shot_dir, int(shot[3]))
                        current_songData.append(shot_data)
                    else:
                        shot_data = -1
                        current_songData.append(shot_data)

                self.song_data.append(current_songData)

    def create_shot(self):
        if self.game_tick >= self.song_data[self.song_dataIndex][0]:
            if self.song_data[self.song_dataIndex][1] != -1:
                shot_num = len(self.song_data[self.song_dataIndex]) - 1

                for shot in range(shot_num):
                    shot_data = self.song_data[self.song_dataIndex][shot + 1]

                    obj_shot = Shot(
                        self, shot_data[0], shot_data[1], shot_data[2], shot_data[3]
                    )
                    self.all_sprites.add(obj_shot)
                    self.shots.add(obj_shot)

                self.song_dataIndex += 1
            else:
                if self.score >= self.song_highScore[self.song_select - 1]:
                    with open(
                        self.song_dataPath[self.song_select - 1], "r", encoding="UTF-8"
                    ) as file:
                        file_lists = file.read().split("\n")

                    file_list = (
                        "score:"
                        + str(self.score)
                        + ":"
                        + str(self.song_perfectScore[self.song_select - 1])
                        + "\n"
                    )

                    for shot_file in file_lists:
                        if shot_file != "" and shot_file[0] != "s":
                            file_list += "\n" + shot_file

                    with open(
                        self.song_dataPath[self.song_select - 1], "w+", encoding="UTF-8"
                    ) as song_file:
                        song_file.write(file_list)

                    self.song_highScore[self.song_select - 1] = self.score

                self.screen_value[1] = 1

    def draw_sprite(self, coord, spr, alpha=ALPHA_MAX, rot=0):
        if rot == 0:
            spr.set_alpha(alpha)
            self.screen.blit(spr, (round(coord[0]), round(coord[1])))
        else:
            rotated_spr = pg.transform.rotate(spr, rot)
            rotated_spr.set_alpha(alpha)
            self.screen.blit(
                rotated_spr,
                (
                    round(coord[0] + spr.get_width() / 2 - rotated_spr.get_width() / 2),
                    round(
                        coord[1] + spr.get_height() / 2 - rotated_spr.get_height() / 2
                    ),
                ),
            )

    def draw_text(self, text, size, color, x, y, alpha=ALPHA_MAX, boldunderline=False):
        try:
            font = pg.font.Font(self.gameFont, size)
        except:
            font = pg.font.Font(os.path.join(self.fnt_dir, DEFAULT_FONT), size)

        font.set_underline(boldunderline)
        font.set_bold(boldunderline)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (round(x), round(y))

        if alpha == ALPHA_MAX:
            self.screen.blit(text_surface, text_rect)
        else:
            surface = pg.Surface((len(text) * size, size + 20))
            surface.fill(COLOR1)
            surface.blit(text_surface, pg.Rect(0, 0, 10, 10))
            surface.set_alpha(alpha)
            self.screen.blit(surface, text_rect)


class Spritesheet:
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert()

    def get_image(self, x, y, width, height):
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))

        return image


class Shot(pg.sprite.Sprite):  # Shot Class
    def __init__(
        self, game, color, mode, direction, speed
    ):  # color(WBDR) mode(DRUL) direction(DRUL)
        pg.sprite.Sprite.__init__(self)
        self.game = game
        self.color = color
        self.mode = mode
        self.direction = direction
        self.speed = speed
        self.alpha = ALPHA_MAX
        self.correct_code = [1, 2, 3, 4]
        self.correct = 0
        image = self.game.spr_shot.get_image((color - 1) * 45, 0, 45, 61)

        if self.mode == 0:
            self.image = pg.transform.rotate(image, 270)
            self.touch_coord = (
                round(-self.image.get_width() / 2),
                round(23 - self.image.get_height() / 2),
            )
        elif self.mode == 90:
            self.image = image
            self.touch_coord = (
                round(23 - self.image.get_width() / 2),
                round(-self.image.get_height() / 2),
            )
        elif self.mode == 180:
            self.image = pg.transform.rotate(image, 90)
            self.touch_coord = (
                round(-self.image.get_width() / 2),
                round(-23 - self.image.get_height() / 2),
            )
        else:
            self.image = pg.transform.rotate(image, 180)
            self.touch_coord = (
                round(-23 - self.image.get_width() / 2),
                round(-self.image.get_height() / 2),
            )

        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = round(WIDTH / 2), round(HEIGHT / 2)

        if self.direction == 0:
            self.rect.y += round(WIDTH / 2 + 100)
        elif self.direction == 90:
            self.rect.x += round(WIDTH / 2 + 100)
        elif self.direction == 180:
            self.rect.y -= round(WIDTH / 2 + 100)
        else:
            self.rect.x -= round(WIDTH / 2 + 100)

        self.rect.x += self.touch_coord[0]
        self.rect.y += self.touch_coord[1]

    def update(self):
        self.image.set_alpha(self.alpha)

        if self.alpha > 0:
            if self.correct == 1:
                self.alpha -= ALPHA_MAX / 5
            else:
                if self.correct == -1:
                    self.alpha -= ALPHA_MAX / 85

                if self.direction == 0:
                    self.rect.y -= self.speed
                elif self.direction == 90:
                    self.rect.x -= self.speed
                elif self.direction == 180:
                    self.rect.y += self.speed
                else:
                    self.rect.x += self.speed

            if (
                self.rect.x > WIDTH * 2
                or self.rect.x < -WIDTH
                or self.rect.y > HEIGHT * 2
                or self.rect.y < -HEIGHT
            ):
                self.kill()
        else:
            self.kill()

        if (
            self.correct == 0
            and self.rect.x == round(WIDTH / 2) + self.touch_coord[0]
            and self.rect.y == round(HEIGHT / 2) + self.touch_coord[1]
        ):
            if (
                self.game.circle_dir
                == self.correct_code[round(self.mode / 90 - self.color + 1)]
            ):
                self.game.score += 100
                self.correct = 1

                if self.color == 1:
                    self.game.sound_drum1.play()
                elif self.color == 2:
                    self.game.sound_drum2.play()
                elif self.color == 3:
                    self.game.sound_drum3.play()
                else:
                    self.game.sound_drum4.play()
            else:
                self.correct = -1


game = Game()

while game.running:
    game.run()

pg.quit()
