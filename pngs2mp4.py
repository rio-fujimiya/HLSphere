import os
import cv2

def pngs2mp4(png_list, title: str="output"):
    # PNGファイルのリストを取得し、ファイル名順にソートする
    png_list = sorted([f for f in os.listdir() if f.endswith('.png')])

    # 画像サイズを取得する
    img = cv2.imread(png_list[0])
    height, width, layers = img.shape

    # MP4動画のファイル名とフレームレートを指定する
    filename = title+".mp4"
    fps = 30

    # MP4動画を書き出すための準備をする
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(filename, fourcc, fps, (width, height))

    # PNGファイルを1秒あたり30枚のフレームレートでMP4動画に変換する
    for png_file in png_list:
        img = cv2.imread(png_file)
        video.write(img)
        print(png_file)

    # MP4動画を終了する
    video.release()

if __name__ == "__main__":
    png_list = sorted([f for f in os.listdir() if f.endswith('.png')])
    pngs2mp4(png_list)