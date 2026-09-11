import os
import sys
import random
import tkinter as tk
from PIL import Image, ImageTk
import pygame

# --- PYINSTALLER DOSYA YOLU DÜZELTİCİSİ ---
def resource_path(relative_path):
    """ PyInstaller paketlemesi (.exe) sonrasında dosyaların doğru bulunmasını sağlar """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- SES YÖNETİCİSİ (Pygame Mixer) ---
pygame.mixer.init()

def play_sound(sound_file, loop=False, volume=1.0):
    full_path = resource_path(sound_file)
    if os.path.exists(full_path):
        try:
            sound = pygame.mixer.Sound(full_path)
            sound.set_volume(volume)
            loops = -1 if loop else 0
            sound.play(loops=loops)
            return sound
        except Exception as e:
            print(f"Ses yükleme hatası ({sound_file}): {e}")
    return None

class FullGameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Coin Collector Game")
        self.root.geometry("1000x700")
        self.root.configure(bg='black')

        self.coins_collected = 0
        self.total_coins = 5
        self.timer_seconds = 90  # 01:30
        self.game_running = False

        # Görselleri Yükle
        self.load_assets()

        # Aşama 1: Giriş / Jumpscare
        self.show_jumpscare()

    def safe_load_img(self, path, size=None):
        full_path = resource_path(path)
        if os.path.exists(full_path):
            try:
                img = Image.open(full_path)
                if size:
                    img = img.resize(size, Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
            except Exception:
                pass
        return None

    def load_assets(self):
        # Görseller
        self.img_attack = self.safe_load_img('attack_face.png', (120, 120)) or self.safe_load_img('ransom_face.png', (120, 120))
        self.img_pot = self.safe_load_img('honeypot.png', (120, 120))
        self.img_coin = self.safe_load_img('coin_token.png', (50, 50))
        self.img_thank = self.safe_load_img('thank_you.png', (450, 320))
        self.img_stop = self.safe_load_img('stop_reference.png', (150, 150))
        self.img_ransom_note = self.safe_load_img('ransom_note.png', (500, 350))

        # Glitch Görselleri
        self.glitch_paths = [f'glitch_{i}.png' for i in range(1, 7) if os.path.exists(resource_path(f'glitch_{i}.png'))]

    # --- 1. AŞAMA: GİRİŞ / JUMPSCARE ---
    def show_jumpscare(self):
        self.jump_frame = tk.Frame(self.root, bg='black')
        self.jump_frame.pack(expand=True, fill='both')

        # Giriş Sesleri
        jumpscare_sound = random.choice(['jumpscare1.mp3', 'jumpscare2.mp3', 'attack.wav'])
        play_sound(jumpscare_sound)

        if self.img_attack:
            lbl = tk.Label(self.jump_frame, image=self.img_attack, bg='black')
            lbl.pack(expand=True)
        else:
            lbl = tk.Label(self.jump_frame, text="💀 GAME START 💀", fg='red', bg='black', font=('Impact', 60))
            lbl.pack(expand=True)

        self.root.after(1500, self.show_loading)

    # --- 2. AŞAMA: YÜKLENİYOR EKRANI ---
    def show_loading(self):
        self.jump_frame.destroy()
        self.load_frame = tk.Frame(self.root, bg='black')
        self.load_frame.pack(expand=True)

        self.load_label = tk.Label(self.load_frame, text="LOADING GAME ASSETS... %0", fg='lime', bg='black', font=('Courier', 24, 'bold'))
        self.load_label.pack(pady=20)

        self.percent = 0
        self.update_loading_progress()

    def update_loading_progress(self):
        self.percent += random.randint(15, 30)
        if self.percent >= 100:
            self.load_label.config(text="LOADING GAME ASSETS... %100")
            self.root.after(500, self.start_main_game)
        else:
            self.load_label.config(text=f"LOADING GAME ASSETS... %{self.percent}")
            self.root.after(250, self.update_loading_progress)

    # --- 3. AŞAMA: ANA OYUN ALANI ---
    def start_main_game(self):
        self.load_frame.destroy()

        # Arka Plan Müziği ve Statik Ses
        play_sound('stop_static.wav', loop=True, volume=0.2)
        play_sound('ransom_loop.wav', loop=True, volume=0.7) or play_sound('ransom_ost_to_jumpscare.mp3', loop=True, volume=0.7)

        self.game_frame = tk.Frame(self.root, bg='#110000')
        self.game_frame.pack(expand=True, fill='both')

        # Ana Arayüz Kutusu
        self.main_box = tk.Frame(self.game_frame, bg='red', bd=4, relief='solid')
        self.main_box.place(relx=0.5, rely=0.4, anchor='center', width=520, height=360)

        # Üst Panel
        header = tk.Frame(self.main_box, bg='red')
        header.pack(fill='x', pady=5)

        if self.img_attack:
            tk.Label(header, image=self.img_attack, bg='red').pack(side='left', padx=10)

        tk.Label(header, text="COLLECT ALL COINS\nBEFORE TIME EXPIRES!", fg='white', bg='red', font=('Arial Black', 16, 'bold')).pack(side='left', padx=5)

        # Hedef Çömlek Alanı
        self.target_frame = tk.Frame(self.main_box, bg='black', bd=2, relief='solid')
        self.target_frame.pack(fill='both', expand=True, padx=10, pady=5)

        if self.img_pot:
            self.pot_label = tk.Label(self.target_frame, image=self.img_pot, bg='black')
            self.pot_label.pack(expand=True)
        else:
            self.pot_label = tk.Label(self.target_frame, text="🍯 DROP HERE 🍯", fg='gold', bg='black', font=('Impact', 20))
            self.pot_label.pack(expand=True)

        # Alt Panel
        bottom_frame = tk.Frame(self.main_box, bg='red')
        bottom_frame.pack(fill='x', padx=10, pady=10)

        # Coin Sayacı
        coin_box = tk.Frame(bottom_frame, bg='black', bd=2, relief='solid', width=180, height=50)
        coin_box.pack_propagate(False)
        coin_box.pack(side='left', padx=5)

        self.coin_lbl = tk.Label(coin_box, text=f"0 / {self.total_coins}", fg='gold', bg='black', font=('Impact', 22))
        self.coin_lbl.pack(expand=True)

        # Zaman Sayacı
        timer_box = tk.Frame(bottom_frame, bg='red', bd=2, relief='solid', width=200, height=50)
        timer_box.pack_propagate(False)
        timer_box.pack(side='right', padx=5)

        self.timer_lbl = tk.Label(timer_box, text="TIME: 01:30", fg='black', bg='red', font=('Impact', 20))
        self.timer_lbl.pack(expand=True)

        self.game_running = True
        self.start_countdown()
        self.spawn_coins()
        self.trigger_random_glitches()

    # --- SAYAÇ ---
    def start_countdown(self):
        if not self.game_running:
            return

        mins, secs = divmod(self.timer_seconds, 60)
        self.timer_lbl.config(text=f"TIME: {mins:02d}:{secs:02d}")

        if self.timer_seconds <= 0:
            self.game_over(success=False)
        else:
            self.timer_seconds -= 1
            self.root.after(1000, self.start_countdown)

    # --- SÜRÜKLENEBİLİR COIN'LER ---
    def spawn_coins(self):
        for _ in range(self.total_coins):
            if self.img_coin:
                lbl = tk.Label(self.game_frame, image=self.img_coin, bg='#110000', cursor='hand2')
            else:
                lbl = tk.Label(self.game_frame, text="🪙", font=('Arial', 28), bg='#110000', fg='gold', cursor='hand2')

            x = random.randint(50, 900)
            y = random.randint(50, 600)
            lbl.place(x=x, y=y)

            lbl.bind('<Button-1>', self.drag_start)
            lbl.bind('<B1-Motion>', self.drag_motion)
            lbl.bind('<ButtonRelease-1>', self.drag_stop)

    def drag_start(self, event):
        w = event.widget
        w.startX = event.x
        w.startY = event.y

    def drag_motion(self, event):
        w = event.widget
        x = w.winfo_x() - w.startX + event.x
        y = w.winfo_y() - w.startY + event.y
        w.place(x=x, y=y)

    def drag_stop(self, event):
        w = event.widget
        rx = self.target_frame.winfo_rootx()
        ry = self.target_frame.winfo_rooty()
        rw = self.target_frame.winfo_width()
        rh = self.target_frame.winfo_height()

        wx = w.winfo_rootx() + w.winfo_width() // 2
        wy = w.winfo_rooty() + w.winfo_height() // 2

        if rx <= wx <= rx + rw and ry <= wy <= ry + rh:
            w.destroy()
            play_sound('coin.wav')
            self.coins_collected += 1
            self.coin_lbl.config(text=f"{self.coins_collected} / {self.total_coins}")

            if self.coins_collected >= self.total_coins:
                self.game_over(success=True)

    # --- GEÇİCİ GLITCH EKRANLARI ---
    def trigger_random_glitches(self):
        if not self.game_running:
            return

        if self.glitch_paths and random.random() < 0.4:
            self.show_single_glitch()

        self.root.after(random.randint(2000, 4500), self.trigger_random_glitches)

    def show_single_glitch(self):
        glitch_win = tk.Toplevel(self.root)
        glitch_win.overrideredirect(True)
        glitch_win.attributes('-topmost', True)

        path = random.choice(self.glitch_paths)
        img = Image.open(resource_path(path)).resize((180, 180))
        tk_img = ImageTk.PhotoImage(img)

        lbl = tk.Label(glitch_win, image=tk_img, bg='black')
        lbl.image = tk_img
        lbl.pack()

        x = random.randint(100, 800)
        y = random.randint(100, 500)
        glitch_win.geometry(f"180x180+{x}+{y}")

        self.root.after(250, glitch_win.destroy)

    # --- OYUN BİTİŞİ ---
    def game_over(self, success):
        self.game_running = False
        pygame.mixer.stop()

        self.game_frame.destroy()

        end_frame = tk.Frame(self.root, bg='black')
        end_frame.pack(expand=True, fill='both')

        if success:
            play_sound('ransom_success.ogg')
            if self.img_thank:
                lbl = tk.Label(end_frame, image=self.img_thank, bg='black')
                lbl.pack(expand=True)
            else:
                tk.Label(end_frame, text="🎉 THANK YOU! YOU WIN! 🎉", fg='lime', bg='black', font=('Impact', 40)).pack(expand=True)
        else:
            play_sound('failure.wav') or play_sound('jumpscare2.mp3')
            if self.img_stop:
                lbl = tk.Label(end_frame, image=self.img_stop, bg='black')
                lbl.pack(expand=True)
            else:
                tk.Label(end_frame, text="⌛ TIME EXPIRED! GAME OVER ⌛", fg='red', bg='black', font=('Impact', 40)).pack(expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = FullGameApp(root)
    root.mainloop()