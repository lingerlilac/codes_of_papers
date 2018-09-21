c = [11, 12, 14, 16, 18, 20, 23, 26, 27, 30]
d = [12, 13, 14, 15, 17, 19, 20]


def get_dic(a, b):
    a_2_b = {}
    last_index = 0
    len_b = len(b)
    min_b = b[0]
    for i in range(0, len(a)):
        if a[i] >= min_b:
            break
    a = a[i:]
    print a
    for m in a:
        # print last_index
        if last_index == (len_b - 1):
            a_2_b[m] = b[len_b - 1]
        for n in range(last_index, len_b):
            if b[n] > m:
                # print b[n]
                a_2_b[m] = b[n - 1]
                last_index = n - 1
                break
            elif b[n] == m:
                a_2_b[m] = b[n]
                last_index = n
                break
            else:
                last_index = n
    return a_2_b


x = get_dic(c, d)
for key in x.keys():
    print key, x[key]
