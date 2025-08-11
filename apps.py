import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.special import comb

def bezier_curve(points, n=100):
    points = np.array(points)
    t = np.linspace(0, 1, n)
    n_points = len(points)
    curve = np.zeros((n, 2))
    for i in range(n_points):
        bern = comb(n_points - 1, i) * (t ** i) * (1 - t) ** (n_points - 1 - i)
        curve += np.outer(bern, points[i])
    return curve

def create_petal_points(size=1.0, angle=0):
    ctrl_points = [
        (0, 0),
        (0.2, 0.6),
        (0, 1.0),
        (-0.2, 0.6),
        (0, 0)
    ]
    ctrl_points = np.array(ctrl_points) * size
    theta = np.radians(angle)
    rotation_matrix = np.array([[np.cos(theta), -np.sin(theta)],
                                [np.sin(theta),  np.cos(theta)]])
    rotated_points = ctrl_points @ rotation_matrix.T
    right_curve = bezier_curve([rotated_points[0], rotated_points[1], rotated_points[2]])
    left_curve = bezier_curve([rotated_points[2], rotated_points[3], rotated_points[4]])
    petal_x = np.concatenate([right_curve[:,0], left_curve[:,0]])
    petal_y = np.concatenate([right_curve[:,1], left_curve[:,1]])
    return petal_x, petal_y

def stem_points(base, height, curve=0.15):
    y = np.linspace(base[1], base[1] + height, 100)
    x = base[0] + curve * np.sin(np.linspace(0, np.pi, 100)) * height * 0.15
    return x, y

class Tulip:
    def __init__(self, base_x, base_y=0, stem_height=3, petal_size=1):
        self.base_x = base_x
        self.base_y = base_y
        self.stem_height = stem_height
        self.petal_size = petal_size
        self.petal_angles = [0, 30, -30]
        self.petal_patches = []
        self.stem_line = None
        self.petal_centers = (base_x, base_y + stem_height)
        self.offset_x = 0
        self.offset_y = 0
        self.petal_removed = 0

    def draw_stem(self, ax):
        x, y = stem_points((self.base_x + self.offset_x, self.base_y + self.offset_y), self.stem_height)
        if self.stem_line is None:
            self.stem_line, = ax.plot(x, y, color='green', linewidth=3)
        else:
            self.stem_line.set_data(x, y)
        self.stem_line.set_visible(True)

    def draw_petals(self, ax):
        if not self.petal_patches:
            for angle in self.petal_angles:
                px, py = create_petal_points(size=self.petal_size, angle=angle)
                px += self.petal_centers[0] + self.offset_x
                py += self.petal_centers[1] + self.offset_y
                patch = ax.fill(px, py, color='deeppink', edgecolor='red', linewidth=1)[0]
                self.petal_patches.append(patch)
        else:
            for i, angle in enumerate(self.petal_angles):
                patch = self.petal_patches[i]
                if i < self.petal_removed:
                    patch.set_visible(False)
                else:
                    px, py = create_petal_points(size=self.petal_size, angle=angle)
                    px += self.petal_centers[0] + self.offset_x
                    py += self.petal_centers[1] + self.offset_y
                    patch.set_xy(np.c_[px, py])
                    patch.set_visible(True)

    def move_out(self):
        self.offset_x += 0.05
        if self.offset_x > 1.2:
            return True
        return False

    def remove_next_petal(self):
        if self.petal_removed < len(self.petal_patches):
            self.petal_patches[self.petal_removed].set_visible(False)
            self.petal_removed += 1
            return False
        return True

    def hide_all(self):
        if self.stem_line:
            self.stem_line.set_visible(False)
        for patch in self.petal_patches:
            patch.set_visible(False)

    def update(self, ax):
        self.draw_stem(ax)
        self.draw_petals(ax)

class Bouquet:
    def __init__(self, ax, num_tulips=5):
        self.ax = ax
        self.tulips = []
        radius = 1.5
        center_x = 2.5
        center_y = 0
        angles = np.linspace(-0.4, 0.4, num_tulips)
        for ang in angles:
            x = center_x + radius * np.sin(ang)
            y = center_y + radius * (1 - np.cos(ang)) * 0.4
            self.tulips.append(Tulip(base_x=x, base_y=y))

        self.selected_tulip = None
        self.state = 'waiting'  # waiting, moving_out, dropping_petals, fading, done
        self.drop_counter = 0
        self.drop_interval = 30
        self.fade_alpha = 0
        self.message_alpha = 0

        self.text_obj = None
        self.fade_rect = plt.Rectangle((0, 0), 5, 5, color='black', alpha=0)
        ax.add_patch(self.fade_rect)

    def draw(self):
        for tulip in self.tulips:
            tulip.update(self.ax)

    def hide_bouquet(self):
        for tulip in self.tulips:
            tulip.hide_all()

    def on_click(self, event):
        if self.state == 'waiting':
            # Hide all bouquet tulips immediately
            self.hide_bouquet()
            # Pick the middle tulip
            self.selected_tulip = self.tulips[len(self.tulips)//2]
            self.state = 'moving_out'

    def update(self, frame):
        if self.state == 'waiting':
            return

        if self.state == 'moving_out':
            done = self.selected_tulip.move_out()
            self.selected_tulip.update(self.ax)
            if done:
                self.state = 'dropping_petals'
                self.drop_counter = 0

        elif self.state == 'dropping_petals':
            self.drop_counter += 1
            if self.drop_counter % self.drop_interval == 0:
                finished = self.selected_tulip.remove_next_petal()
                if finished:
                    self.state = 'fading'
                    self.fade_alpha = 0
                    self.message_alpha = 0
                    # Hide tulip completely for fade to black
                    self.selected_tulip.hide_all()
            self.selected_tulip.update(self.ax)

        elif self.state == 'fading':
            self.fade_alpha += 0.03
            if self.fade_alpha > 1:
                self.fade_alpha = 1
                self.message_alpha += 0.03
                if self.message_alpha > 1:
                    self.message_alpha = 1
                    self.state = 'done'

            self.fade_rect.set_alpha(self.fade_alpha)

            if self.text_obj is None:
                self.text_obj = self.ax.text(2.5, 2.5, "withered",
                                             color=(1,1,1,self.message_alpha),
                                             fontsize=40, ha='center', va='center', alpha=self.message_alpha)
            else:
                self.text_obj.set_alpha(self.message_alpha)

    def redraw(self):
        if self.state == 'waiting':
            self.ax.set_facecolor('white')
        else:
            # Use transparent background so black fade rectangle is visible
            self.ax.set_facecolor('none')

        self.ax.axis('off')
        self.ax.set_xlim(0, 5)
        self.ax.set_ylim(0, 5)
        self.ax.set_aspect('equal')

        if self.state == 'waiting':
            for tulip in self.tulips:
                tulip.update(self.ax)
        elif self.state in ['moving_out', 'dropping_petals']:
            if self.selected_tulip:
                self.selected_tulip.update(self.ax)
        elif self.state in ['fading', 'done']:
            # Only show fade_rect and text (handled in update)
            pass

def main():
    fig, ax = plt.subplots(figsize=(6,6))
    bouquet = Bouquet(ax)
    bouquet.draw()

    def on_click(event):
        bouquet.on_click(event)

    fig.canvas.mpl_connect('button_press_event', on_click)

    def animate(frame):
        bouquet.update(frame)
        bouquet.redraw()

    anim = FuncAnimation(fig, animate, frames=600, interval=50, repeat=False, blit=False)
    plt.show()

if __name__ == "__main__":
    main()
