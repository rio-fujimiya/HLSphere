import matplotlib.pyplot as plt
import numpy as np
from PIL import ImageGrab, Image
import math, os, io, colorsys, re


def get_image():
    img = ImageGrab.grabclipboard()
    f = io.StringIO()
    print(img, file=f)
    description = f.getvalue()

    if isinstance(img, Image.Image):
        print(f"clipboard:{img}")
    else:
        f = io.StringIO()
        print(img, file=f)
        try:
            filepath = f.getvalue().split("'")[1]
            img = Image.open(filepath)
            print(f"clipboard:{filepath}")
        except:
            print("no image on clipboard")

        if isinstance(img, Image.Image):
            print(filepath)
            description = filepath
        else:
            files = sorted(os.listdir(), key=lambda x: os.stat(x).st_mtime)
            for f in files:
                try:
                    img = Image.open(f)
                    if isinstance(img, Image.Image):
                        print(f"latest image in dir:{f}")
                        description = f
                        break
                except:
                    img = None
    return img, description


def img_to_rgb(img):
    width, height = img.size
    img = img.convert("RGB")
    rgb = np.array(img.getdata()).reshape(height, width, 3)
    return rgb, height, width


def init_plot(title: str = ""):
    plt.style.use("fast")
    fig = plt.figure(f"[HLS sphere] {title}")
    ax = fig.add_subplot(111, projection="3d")
    ax.view_init(elev=30, azim=150)
    xylim = 0.7
    ax.set_xlim(-xylim, xylim)
    ax.set_ylim(-xylim, xylim)
    ax.set_zlim(-0.425, 0.55)
    ax.axis("off")
    ax.quiver(
        0,
        0,
        -1,
        0,
        0,
        2.1,
        color="gray",
        linewidth=0.5,
        linestyle="solid",
        arrow_length_ratio=0.03,
    )
    return ax


def solveHLSxyz(points):
    x = [0] * len(points)
    y, z = x.copy(), x.copy()
    for i in range(len(points)):
        h, l, s = colorsys.rgb_to_hls(points[i][0], points[i][1], points[i][2])
        x[i] = s * math.sin(2 * math.pi * h) * math.sin(math.pi * l)
        y[i] = s * math.cos(2 * math.pi * h) * math.sin(math.pi * l)
        z[i] = -math.cos(math.pi * l)
    return x, y, z


def draw_H_ring(ax):
    ring_counts = 36
    h = np.array(range(ring_counts)) / ring_counts
    l = [0.5] * ring_counts
    s = [1] * ring_counts
    ringc = [[0, 0, 0]] * ring_counts
    for i in range(ring_counts):
        ringc[i] = colorsys.hls_to_rgb(h[i], l[i], s[i])
    rx, ry, rz = solveHLSxyz(ringc)
    ax.scatter(rx, ry, rz, color=ringc, alpha=1, s=3, marker=".")
    return ax


def draw_points(ax, rgb):
    target_point_count = 2**12
    spd = math.ceil((height + width) / (target_point_count**0.5) / 2)

    white = [1, 1, 1]
    points = np.array([white])
    for r in range(math.floor(height / spd)):
        for c in range(math.floor(width / spd)):
            rp = math.floor((r + 0.5) * spd)
            cp = math.floor((c + 0.5) * spd)
            pcolor = rgb[rp, cp] / 255
            if not np.allclose(pcolor, white):
                points = np.append(points, [pcolor], axis=0)
    print(f"plot points:{len(points)}")

    x, y, z = solveHLSxyz(points)
    ax.scatter(x, y, z, color=points, alpha=1, s=100, marker=".")
    return ax


if __name__ == "__main__":
    img, description = get_image()
    if img:
        rgb, height, width = img_to_rgb(img)
        ax = init_plot(description)

        draw_H_ring(ax)
        draw_points(ax, rgb)

        prevsize = 0.4
        plt.axes([0, 0, prevsize, prevsize * width / height])
        plt.imshow(img)
        plt.axis("off")

        if 0:  # <- true:png->mp4 / false:show
            azims = 180
            frames = []
            safe_description = re.sub(r'[\\|/|:|?|.|"|<|>|\|]', "-", description)
            for i in range(azims * 2):
                ax.view_init(
                    elev=15 + 30 * math.cos(math.pi * (i) / azims), azim=i * 360 / azims
                )
                frame = f"HSLsphere_{safe_description}_{i:03}.png"
                frames.append(frame)
                plt.savefig(frame, dpi=300)
                print(f"draw frame {i:03}/{azims*2}")
            import pngs2mp4

            pngs2mp4.pngs2mp4(frames, f"HSLsphere_{safe_description}")
            for f in frames:
                os.remove(f)

        else:
            plt.show()
    else:
        print(">>>FAILED to get image<<<")
