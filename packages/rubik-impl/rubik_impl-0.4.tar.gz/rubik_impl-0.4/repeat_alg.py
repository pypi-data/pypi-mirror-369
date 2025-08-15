import rubik_impl

cube,scrambled_alg = rubik_impl.Cube.scrambled()
print(cube)
print(scrambled_alg)
alg = rubik_impl.Alg("R U R' U'")
print(alg.reverse())
ALG = "R U R' U' R U R U R' U'"
cube = rubik_impl.Cube.solved()
alg = cube.scramble(2) + ["R"]
alg+=["R"]
print(type(alg))
print(alg)
print(cube)
cube_init = cube.copy()
n = 0
while True:
    cube.apply(ALG)
    n+=1
    if cube==cube_init:
        break
print(n)
