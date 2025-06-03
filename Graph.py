import matplotlib.pyplot as plt

# Données
stopLines = {'right': 590, 'down': 330, 'left': 800, 'up': 535}
defaultStop = {'right': 580, 'down': 320, 'left': 810, 'up': 545}
stops = {
    'right': [580, 580, 580],
    'down': [320, 320, 320],
    'left': [810, 810, 810],
    'up': [545, 545, 545]
}
mid = {
    'right': {'x': 705, 'y': 445},
    'down': {'x': 695, 'y': 450},
    'left': {'x': 695, 'y': 425},
    'up': {'x': 695, 'y': 400}
}

# Couleurs personnalisées pour chaque mid
mid_colors = {
    'right': 'orange',
    'down': 'purple',
    'left': 'cyan',
    'up': 'magenta'
}

# Création du graphique
fig, ax = plt.subplots(figsize=(8, 8))

# Tracer les stopLines
for direction, pos in stopLines.items():
    if direction in ['right', 'left']:
        ax.plot([pos]*3, [420, 430, 440], 'ro', label=f'stopLine {direction}')
    else:
        ax.plot([690, 700, 710], [pos]*3, 'ro', label=f'stopLine {direction}')

# Tracer les defaultStop
for direction, pos in defaultStop.items():
    if direction in ['right', 'left']:
        ax.plot([pos]*3, [420, 430, 440], 'bx', label=f'defaultStop {direction}')
    else:
        ax.plot([690, 700, 710], [pos]*3, 'bx', label=f'defaultStop {direction}')

# Tracer les stops
for direction, values in stops.items():
    if direction in ['right', 'left']:
        x_vals = values
        y_vals = [420, 430, 440]
    else:
        x_vals = [690, 700, 710]
        y_vals = values
    ax.plot(x_vals, y_vals, 'gs', label=f'stops {direction}')

# Tracer les mid avec couleur unique
for direction, coords in mid.items():
    color = mid_colors.get(direction, 'yellow')  # fallback au jaune
    ax.plot(coords['x'], coords['y'], '*', markersize=14, color=color, label=f'mid {direction}')

# Éviter doublons dans la légende
handles, labels = ax.get_legend_handles_labels()
unique = dict(zip(labels, handles))
ax.legend(unique.values(), unique.keys(), loc='upper right', fontsize=8)

# Lignes d'intersection pour situer le centre
ax.axvline(700, color='gray', linestyle='--', linewidth=1)
ax.axhline(430, color='gray', linestyle='--', linewidth=1)

# Centrage de la carte
ax.set_xlim(500, 900)
ax.set_ylim(300, 600)

# Mise en page
ax.set_title("Visualisation des points de stop et milieux avec couleurs personnalisées")
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_aspect('equal')
ax.grid(True)

plt.show()
