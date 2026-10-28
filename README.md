# Zombie Aim: Last Stand

Zombie Aim: Last Stand is a small desktop shooting game built with Python and Tkinter. Move your survivor around the arena, aim with the mouse, and hold off incoming zombies for as long as possible.

## Requirements

- Python 3
- Tkinter (included with most standard Python installations)

The game uses only Python's standard library. On Windows, it can also use `winsound` for simple sound effects; sound is optional.

## Run the game

Open a terminal in this folder and run:

```powershell
python "SHOOTING.PY"
```

If `python` is not recognized on Windows, try:

```powershell
py "SHOOTING.PY"
```

## How to play

1. Enter a survivor name, or leave the name blank to use `Survivor`.
2. Move with **WASD** or the **arrow keys**.
3. Aim with the mouse and click to fire.
4. Choose a weapon from the menu:
   - **Pistol**: balanced damage and firing speed.
   - **Shotgun**: fires several pellets with a spread.
   - **Rifle**: rapid fire with lower damage per shot.
5. Avoid contact with zombies. Each bite removes 10 health, and the game ends when health reaches zero.
6. Select **New Game** to start another round.

Your score increases when you defeat a zombie. Zombies spawn more frequently as your score grows.
