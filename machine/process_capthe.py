# 255 是白
import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
def split_bool_arr(bool_index):
    lis = []
    temp = []
    for i in range(len(bool_index)-1):
        if bool_index[i] != bool_index[i+1]:
            temp.append(i)
            lis.append(temp)
            temp = []
        else:
           temp.append(i)
    return [lis[i] for i in range(len(lis)) if i% 2 ==1]
def get_img_data(filename):
    img = Image.open(filename)
    img = img.convert("L")
    return img
def get_img_arr(img):
    x, y = img.size
    threshold = 100
    img_list = []
    for j in range(y):
        img_han = []
        for i in range(x):
            if threshold > img.load()[i, j]:
                img.load()[i, j] = 0
            else:
                img.load()[i, j] = 1
            img_han.append(img.load()[i, j])
        img_list.append(img_han)
    img_arr = np.array(img_list)
    return img_arr
def split_arr(img_arr):
    han_sum = np.sum(img_arr, axis=0)
    bool_col_index = han_sum < np.max(han_sum)
    ans = split_bool_arr(bool_col_index)
    split_imgs = [img_arr[:, index] for index in ans]
    return split_imgs
def change_img(split_arr_img):
    col_sum = np.sum(split_arr_img, axis=1)
    bool_col_index = col_sum < np.max(col_sum)
    a = Image.fromarray(split_arr_img[bool_col_index, :])
    x, y = a.size
    for j in range(y):
        for i in range(x):
            if 1 == a.load()[i, j]:
                a.load()[i, j] = 255
            else:
                a.load()[i, j] = 0
    return a
def write(lis,data):
    new_lis = lis+[0]*(254-len(lis)) +[data]
    with open("data.txt","a+",encoding="utf-8") as f:
        for li in new_lis:
            f.write(str(li)+" ")
        f.write("\n")

if __name__ == '__main__':
    for i in range(1000):
        filename = "%d.jpg"%(i)
        if not os.path.exists(filename):
            continue
        print("第%d张"%(i+1))
        img = get_img_data(filename)
        img_arr = get_img_arr(img)
        split_arr_imgs = split_arr(img_arr)
        for split_arr_img in split_arr_imgs:
            split_img = change_img(split_arr_img)
            plt.imshow(split_img)
            plt.show()
            data = input("输入结果:")

            ans = split_arr_img.reshape((1,-1))
            write(ans[0].tolist(),data)
        os.remove(filename)
