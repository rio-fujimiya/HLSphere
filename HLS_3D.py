#!/usr/bin/env python3
import matplotlib.pyplot as plt
import numpy as np
from PIL import ImageGrab, Image
import math, os, io, colorsys

### config ###

# Target number of points to plot
target_point_count = 2**12

# Size (0 to hide) and quality of the image displayed in the plot
prevsize, img_quality = 0.3, 512

# Save png or not and where to save it
export_png, export_directry = True, ".\HLSphere"

# Save rotaing animation, convert into mp4 movie, animation length, fps
export_pngs, convert_to_mp4, rotation_azims_count, mp4_fps = False, True, 240, 60

# Resolution of images to save
export_dpi = 240

# Show manipulable plot
show_plot = True

# Ask for retry on finish
retry_always, retry_on_error = False, True

### config ###


def get_image():
    img = ImageGrab.grabclipboard()
    f = io.StringIO()
    print(img, file=f)
    description = f.getvalue()

    if isinstance(img, Image.Image):
        print(f"image on clipboard>>{img}")
    else:
        f = io.StringIO()
        print(img, file=f)
        try:
            filepath = f.getvalue().split("'")[1]
            img = Image.open(filepath)
        except:
            print("no image on clipboard")

        if isinstance(img, Image.Image):
            print(f"image file on clipboard>>{filepath}")
            description = filepath
        else:
            files = sorted(os.listdir(), key=lambda x: os.stat(x).st_mtime)
            for f in files:
                try:
                    img = Image.open(f)
                    if isinstance(img, Image.Image):
                        print(f"latest image in directry>>{f}")
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
    # plt.style.use("fast")
    fig = plt.figure(f"[HLSphere] {title}", figsize=(8, 4.5), dpi=export_dpi)
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
    ax.scatter(rx, ry, rz, color=ringc, alpha=1, s=1, marker=".")
    return ax


def draw_points(ax, rgb):
    height, width = len(rgb), len(rgb[0])
    spd = math.floor((height + width) / (target_point_count**0.5) / 2)

    white = [1, 1, 1]
    points = np.array([white])
    for r in range(math.floor(height / spd)):
        for c in range(math.floor(width / spd)):
            rp = math.floor((r + 0.5) * spd)
            cp = math.floor((c + 0.5) * spd)
            pcolor = rgb[rp, cp] / 255
            if not np.allclose(pcolor, white):
                points = np.append(points, [pcolor], axis=0)
            strBar = ("X" * int(len(points) / target_point_count * 20)) + ("_" * 20)
            print(f"plotting:{strBar[:20]}\r", end="")
    print(f"\nplot points:{len(points)}")

    x, y, z = solveHLSxyz(points)
    ax.scatter(x, y, z, color=points, alpha=1, s=50, marker=".")
    return ax


def HLS_sphere():
    img, description = get_image()
    if img:
        rgb, height, width = img_to_rgb(img)
        ax = init_plot(description)

        draw_H_ring(ax)
        draw_points(ax, rgb)

        if prevsize > 0:
            diag = ((width**2) + (height**2)) ** 0.5
            img_resize = img.resize(
                (int(img_quality / diag * width), int(img_quality / diag * height))
            )

            plt.axes([0, 0, prevsize, prevsize])
            plt.imshow(img_resize)
            plt.axis("off")

        if export_png or export_pngs:
            import re

            safe_description = re.sub(
                r'[\\|/|:|?|.|"|<|>|\||=| ]', "-", description
            ).replace("\n", "")
            filename_prefix = "HLSphere"

            os.makedirs(export_directry, exist_ok=True)
            filename_body = (
                export_directry + os.sep + f"{filename_prefix}_{safe_description}"
            )

            if export_png:
                pngfile = filename_body + ".png"
                plt.savefig(pngfile, dpi=export_dpi)
                print("exported>>" + pngfile)

            if export_pngs:
                frames = []
                for i in range(rotation_azims_count * 2):
                    ax.view_init(
                        elev=15 + 30 * math.cos(math.pi * (i) / rotation_azims_count),
                        azim=i * 360 / rotation_azims_count,
                    )
                    frame = filename_body + f"_{i:05}.png"
                    frames.append(frame)
                    plt.savefig(frame, dpi=export_dpi)
                    print(f"exported>>{frame}/{rotation_azims_count*2}\r", end="")
                print()

                if convert_to_mp4:
                    import pngs2mp4

                    pngs2mp4.pngs2mp4(frames, filename_body, mp4_fps)
                    for f in frames:
                        os.remove(f)

        if show_plot:
            plt.show()

        return 1
    else:
        print(
            "FAILED to get image\ncopy image to clipboard or put image file in the same directry"
        )
        return 0


if __name__ == "__main__":
    retry = True
    print(
        "============================\nHLS sphere plotter v0.1.1\n(c)Rio Fujimiya|i2forme 2023\n============================"
    )
    while retry:
        if (not HLS_sphere() == 1 and retry_on_error) or retry_always:
            retry = str(input("Retry?[Enter]")) == ""
        else:
            retry = False
            print("FINISHED")
