import math
import random
import threading
import tkinter as tk
from tkinter import messagebox

try:
	import winsound
except ImportError:
	winsound = None


class ZombieAimGame:
	WIDTH = 900
	HEIGHT = 560
	PLAYER_SPEED = 7

	def __init__(self, window):
		self.window = window
		self.window.title("Zombie Aim: Last Stand")
		self.window.resizable(False, False)
		self.window.configure(bg="#15191c")

		self.canvas = tk.Canvas(
			window, width=self.WIDTH, height=self.HEIGHT,
			bg="#20272b", highlightthickness=0
		)
		self.canvas.pack(padx=12, pady=(12, 0))

		controls = tk.Frame(window, bg="#15191c")
		controls.pack(fill="x", padx=12, pady=10)
		self.info_label = tk.Label(
			controls, text="", font=("Consolas", 11, "bold"),
			bg="#15191c", fg="#dce7e9", anchor="w"
		)
		self.info_label.pack(side="left")
		self.weapon_choice = tk.StringVar(value="Pistol")
		self.weapon_menu = tk.OptionMenu(
			controls, self.weapon_choice, "Pistol", "Shotgun", "Rifle",
			command=self.change_weapon
		)
		self.weapon_menu.config(width=9, bg="#d88b47", fg="#15191c", relief="flat")
		self.weapon_menu.pack(side="right", padx=(8, 0))
		self.restart_button = tk.Button(
			controls, text="New Game", command=self.show_start,
			bg="#4d9a76", fg="white", relief="flat", padx=10
		)
		self.restart_button.pack(side="right")

		self.keys = set()
		self.player_x = self.WIDTH / 2
		self.player_y = self.HEIGHT / 2
		self.mouse_x = self.player_x
		self.mouse_y = self.player_y
		self.zombies = []
		self.bullets = []
		self.score = 0
		self.health = 100
		self.running = False
		self.spawn_timer = 0
		self.last_bite_time = 0
		self.muzzle_flash = 0
		self.effects = []
		self.name = ""
		self.weapons = {
			"Pistol": {"damage": 34, "cooldown": 260, "pellets": 1, "color": "#f4c95d"},
			"Shotgun": {"damage": 22, "cooldown": 650, "pellets": 5, "color": "#ef8354"},
			"Rifle": {"damage": 18, "cooldown": 100, "pellets": 1, "color": "#80ced7"},
		}
		self.last_shot_time = 0

		window.bind("<KeyPress>", self.key_down)
		window.bind("<KeyRelease>", self.key_up)
		self.canvas.bind("<Motion>", self.aim)
		self.canvas.bind("<Button-1>", self.shoot)
		self.show_start()

	def show_start(self):
		self.running = False
		self.canvas.delete("all")
		self.canvas.create_text(
			self.WIDTH / 2, 130, text="ZOMBIE AIM: LAST STAND",
			font=("Consolas", 30, "bold"), fill="#ef8354"
		)
		self.canvas.create_text(
			self.WIDTH / 2, 190, text="Name your survivor and hold the line.",
			font=("Consolas", 13), fill="#dce7e9"
		)
		self.canvas.create_text(
			self.WIDTH / 2, 270, text="Move: WASD / arrows     Aim: mouse     Fire: click",
			font=("Consolas", 11), fill="#9db4b8"
		)
		self.name_entry = tk.Entry(self.window, justify="center", font=("Consolas", 14), width=22)
		self.name_entry.place(x=self.WIDTH / 2 - 125, y=315)
		self.start_button = tk.Button(
			self.window, text="Enter the fight", command=self.start_game,
			bg="#ef8354", fg="white", relief="flat", font=("Consolas", 11, "bold")
		)
		self.start_button.place(x=self.WIDTH / 2 - 80, y=360, width=160, height=34)
		self.name_entry.focus_set()
		self.info_label.config(text="Choose a character name to begin.")

	def start_game(self):
		self.name = self.name_entry.get().strip() or "Survivor"
		self.name_entry.destroy()
		self.start_button.destroy()
		self.health = 100
		self.score = 0
		self.zombies = []
		self.bullets = []
		self.player_x = self.WIDTH / 2
		self.player_y = self.HEIGHT / 2
		self.spawn_timer = 0
		self.running = True
		self.game_loop()

	def change_weapon(self, weapon):
		if self.running:
			self.info_label.config(text=f"{self.name} | Weapon switched to {weapon}")

	def key_down(self, event):
		self.keys.add(event.keysym.lower())

	def key_up(self, event):
		self.keys.discard(event.keysym.lower())

	def aim(self, event):
		self.mouse_x = event.x
		self.mouse_y = event.y

	def shoot(self, event):
		if not self.running:
			return
		self.mouse_x = event.x
		self.mouse_y = event.y
		current_time = self.window.winfo_toplevel().tk.call("clock", "milliseconds")
		weapon = self.weapons[self.weapon_choice.get()]
		if current_time - self.last_shot_time < weapon["cooldown"]:
			return
		self.last_shot_time = current_time
		angle = math.atan2(self.mouse_y - self.player_y, self.mouse_x - self.player_x)
		spread = 0.16 if weapon["pellets"] > 1 else 0
		for _ in range(weapon["pellets"]):
			shot_angle = angle + random.uniform(-spread, spread)
			self.bullets.append({
				"x": self.player_x, "y": self.player_y,
				"dx": math.cos(shot_angle) * 13, "dy": math.sin(shot_angle) * 13,
				"damage": weapon["damage"], "color": weapon["color"],
			})
		self.muzzle_flash = 3
		self.play_sound("shot")

	def play_sound(self, sound):
		if winsound is None:
			return
		tones = {"shot": (170, 45), "hit": (90, 35), "bite": (55, 100), "death": (35, 220)}
		frequency, duration = tones[sound]
		threading.Thread(target=winsound.Beep, args=(frequency, duration), daemon=True).start()

	def spawn_zombie(self):
		side = random.choice(("top", "bottom", "left", "right"))
		if side == "top":
			x, y = random.randint(20, self.WIDTH - 20), -25
		elif side == "bottom":
			x, y = random.randint(20, self.WIDTH - 20), self.HEIGHT + 25
		elif side == "left":
			x, y = -25, random.randint(20, self.HEIGHT - 20)
		else:
			x, y = self.WIDTH + 25, random.randint(20, self.HEIGHT - 20)
		self.zombies.append({
			"x": x, "y": y, "health": 70, "speed": random.uniform(0.8, 1.5),
			"variant": random.choice(("walker", "runner", "brute")),
		})

	def update(self):
		dx = ("d" in self.keys or "right" in self.keys) - ("a" in self.keys or "left" in self.keys)
		dy = ("s" in self.keys or "down" in self.keys) - ("w" in self.keys or "up" in self.keys)
		if dx or dy:
			length = math.sqrt(dx * dx + dy * dy)
			self.player_x = max(22, min(self.WIDTH - 22, self.player_x + dx / length * self.PLAYER_SPEED))
			self.player_y = max(22, min(self.HEIGHT - 22, self.player_y + dy / length * self.PLAYER_SPEED))

		self.spawn_timer += 1
		spawn_gap = max(22, 65 - self.score // 5)
		if self.spawn_timer >= spawn_gap:
			self.spawn_timer = 0
			self.spawn_zombie()

		for bullet in self.bullets[:]:
			bullet["x"] += bullet["dx"]
			bullet["y"] += bullet["dy"]
			if not (0 <= bullet["x"] <= self.WIDTH and 0 <= bullet["y"] <= self.HEIGHT):
				self.bullets.remove(bullet)
				continue
			for zombie in self.zombies[:]:
				if math.hypot(bullet["x"] - zombie["x"], bullet["y"] - zombie["y"]) < 22:
					zombie["health"] -= bullet["damage"]
					self.effects.append({"x": bullet["x"], "y": bullet["y"], "life": 5})
					self.play_sound("hit")
					self.bullets.remove(bullet)
					if zombie["health"] <= 0:
						self.zombies.remove(zombie)
						self.score += 1
					break

		for zombie in self.zombies:
				angle = math.atan2(self.player_y - zombie["y"], self.player_x - zombie["x"])
				zombie["x"] += math.cos(angle) * zombie["speed"]
				zombie["y"] += math.sin(angle) * zombie["speed"]
				if math.hypot(self.player_x - zombie["x"], self.player_y - zombie["y"]) < 28:
					current_time = self.window.tk.call("clock", "milliseconds")
					if current_time - self.last_bite_time >= 900:
						self.health -= 10
						self.last_bite_time = current_time
						self.play_sound("bite")
						if self.health <= 0:
							self.health = 0
							self.running = False
							self.play_sound("death")
							messagebox.showinfo("Overrun", f"{self.name} was overwhelmed. Score: {self.score}")
		for effect in self.effects[:]:
			effect["life"] -= 1
			if effect["life"] <= 0:
				self.effects.remove(effect)

	def draw(self):
		self.canvas.delete("all")
		self.draw_background()
		for bullet in self.bullets:
			self.canvas.create_oval(bullet["x"] - 3, bullet["y"] - 3, bullet["x"] + 3, bullet["y"] + 3, fill="#fff2a8", outline="")
		for effect in self.effects:
			radius = (6 - effect["life"]) * 3
			self.canvas.create_oval(effect["x"] - radius, effect["y"] - radius, effect["x"] + radius, effect["y"] + radius, outline="#ffcf70", width=2)
		for zombie in self.zombies:
			self.draw_zombie(zombie)

		angle = math.atan2(self.mouse_y - self.player_y, self.mouse_x - self.player_x)
		self.draw_soldier(angle)
		if self.muzzle_flash:
			flash_x = self.player_x + math.cos(angle) * 56
			flash_y = self.player_y + math.sin(angle) * 56
			self.canvas.create_polygon(
				self.player_x + math.cos(angle) * 38, self.player_y + math.sin(angle) * 38,
				flash_x + math.cos(angle + 2.4) * 13, flash_y + math.sin(angle + 2.4) * 13,
				flash_x, flash_y,
				flash_x + math.cos(angle - 2.4) * 13, flash_y + math.sin(angle - 2.4) * 13,
				fill="#ffe08a", outline="#ff9d43"
			)
			self.muzzle_flash -= 1
		self.canvas.create_text(14, 14, anchor="nw", text=f"{self.name}   |   SCORE {self.score}   |   {self.weapon_choice.get()}", font=("Consolas", 12, "bold"), fill="#dce7e9")
		self.canvas.create_text(self.WIDTH - 14, 14, anchor="ne", text=f"HEALTH {self.health}/100", font=("Consolas", 12, "bold"), fill="#e85d75" if self.health <= 30 else "#dce7e9")
		self.info_label.config(text="Bite damage: 10 health (one tenth) | Move with WASD/arrows | Click to fire")

	def draw_background(self):
		self.canvas.create_rectangle(0, 0, self.WIDTH, self.HEIGHT, fill="#172126", outline="")
		for y in range(0, self.HEIGHT, 40):
			shade = "#1c292d" if (y // 40) % 2 else "#202e31"
			self.canvas.create_rectangle(0, y, self.WIDTH, y + 20, fill=shade, outline="")
		for x in range(-self.HEIGHT, self.WIDTH, 70):
			self.canvas.create_line(x, 0, x + self.HEIGHT, self.HEIGHT, fill="#263638", width=2)
		for x, y in ((70, 110), (760, 145), (170, 470), (690, 420)):
			self.canvas.create_rectangle(x, y, x + 45, y + 10, fill="#101719", outline="")
			self.canvas.create_line(x + 10, y + 10, x + 2, y + 30, fill="#080c0d", width=3)
			self.canvas.create_line(x + 35, y + 10, x + 48, y + 27, fill="#080c0d", width=3)
			self.canvas.create_text(x + 22, y - 8, text="DANGER", fill="#814d48", font=("Consolas", 7, "bold"))

	def draw_zombie(self, zombie):
		x, y = zombie["x"], zombie["y"]
		scale = 1.25 if zombie["variant"] == "brute" else 1
		body = "#596b4c" if zombie["variant"] != "runner" else "#69784f"
		self.canvas.create_oval(x - 20 * scale, y - 9 * scale, x + 20 * scale, y + 25 * scale, fill="#11191a", outline="")
		self.canvas.create_oval(x - 16 * scale, y - 23 * scale, x + 16 * scale, y + 10 * scale, fill=body, outline="#adbb79", width=2)
		self.canvas.create_oval(x - 9 * scale, y - 13 * scale, x - 4 * scale, y - 7 * scale, fill="#e7dca1", outline="#202a24")
		self.canvas.create_oval(x + 4 * scale, y - 13 * scale, x + 9 * scale, y - 7 * scale, fill="#e7dca1", outline="#202a24")
		self.canvas.create_oval(x - 7 * scale, y - 12 * scale, x - 5 * scale, y - 9 * scale, fill="#a53131", outline="")
		self.canvas.create_oval(x + 5 * scale, y - 12 * scale, x + 7 * scale, y - 9 * scale, fill="#a53131", outline="")
		self.canvas.create_line(x - 9 * scale, y - 17 * scale, x - 3 * scale, y - 20 * scale, fill="#c7c995", width=2)
		self.canvas.create_line(x + 4 * scale, y - 19 * scale, x + 11 * scale, y - 16 * scale, fill="#c7c995", width=2)
		self.canvas.create_line(x - 9 * scale, y + 1 * scale, x - 3 * scale, y + 4 * scale, fill="#2a1b1b", width=2)
		self.canvas.create_line(x + 3 * scale, y + 4 * scale, x + 10 * scale, y + 1 * scale, fill="#2a1b1b", width=2)
		self.canvas.create_line(x - 17 * scale, y + 4 * scale, x - 28 * scale, y + 17 * scale, fill=body, width=5)
		self.canvas.create_line(x + 17 * scale, y + 4 * scale, x + 28 * scale, y + 17 * scale, fill=body, width=5)
		self.canvas.create_rectangle(x - 19, y - 31, x + 19, y - 26, fill="#11191a", outline="")
		self.canvas.create_rectangle(x - 19, y - 31, x - 19 + 38 * zombie["health"] / 70, y - 26, fill="#c55252", outline="")

	def draw_soldier(self, angle):
		x, y = self.player_x, self.player_y
		self.canvas.create_oval(x - 24, y - 10, x + 24, y + 27, fill="#0b1112", outline="")
		self.canvas.create_rectangle(x - 15, y - 5, x + 15, y + 20, fill="#435c49", outline="#91a784", width=2)
		self.canvas.create_rectangle(x - 13, y + 2, x + 13, y + 12, fill="#2e4235", outline="")
		self.canvas.create_oval(x - 14, y - 25, x + 14, y + 4, fill="#b57e5f", outline="#d9b18a", width=2)
		self.canvas.create_arc(x - 17, y - 29, x + 17, y - 7, start=0, extent=180, fill="#324c3c", outline="#9cb18e", width=2)
		self.canvas.create_rectangle(x - 16, y - 19, x + 16, y - 15, fill="#26382e", outline="")
		self.canvas.create_oval(x - 8, y - 14, x - 4, y - 11, fill="#101719", outline="")
		self.canvas.create_oval(x + 4, y - 14, x + 8, y - 11, fill="#101719", outline="")
		gun_x = x + math.cos(angle) * 42
		gun_y = y + math.sin(angle) * 42
		self.canvas.create_line(x, y + 2, gun_x, gun_y, fill="#171d1e", width=9)
		self.canvas.create_line(x, y + 1, gun_x, gun_y, fill="#6d7770", width=4)
		self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="#d9b18a", outline="")

	def game_loop(self):
		if self.running:
			self.update()
			self.draw()
			self.window.after(30, self.game_loop)


if __name__ == "__main__":
	root = tk.Tk()
	game = ZombieAimGame(root)
	root.mainloop()
