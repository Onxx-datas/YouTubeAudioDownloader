n = int(input("n sonini kiriting: "))
for b in range(1, n+1):
    if b % 3 == 0 and b % 5 != 0:
        print(b)

a = int(input("Son kiriting: "))
tub_sonlar = []
for x in range(1, a+1):
    if not x % x == 0 and x % 1 == 0:
        tub_sonlar.append(x)
    else:
        print("Xato")
print(tub_sonlar)