# -*-coding:utf-8-*-

all_items = [67, 22, 33, 44, 55, 66, 77, 88, 99]


def dictsort():
    dic = dict()

    # loop
    for value in all_items:
        if value > 66:
            if "k1" in dic.keys():
                dic["k1"].append(value)
            else:
                dic["k1"] = [value]
        else:
            if "k2" in dic.keys():
                dic["k2"].append(value)
            else:
                dic["k2"] = [value]
    print(dic)


if __name__ == '__main__':
    dictsort()

