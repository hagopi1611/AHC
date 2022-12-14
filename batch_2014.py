with open('test', 'w') as ofile:
    out = ''
    for i in range(0, 20):
        for j in range(3):
            out += ('python3 ' +
                    'acpc_hand_converter.py ' +
                    '"2014_3pl/3pl.KEmpfer.Hyperborean_iro.SmooCT.' +
                    str(i) + '.' + str(j) + '.log" ' +
                    '"out/' + '3pl.KEmpfer.Hyperborean_iro.SmooCT.' +
                    str(i) + '.' + str(j) + '.out"' + '\n')
    ofile.write(out)
