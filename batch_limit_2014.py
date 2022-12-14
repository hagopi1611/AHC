with open('test', 'w') as ofile:
    out = ''
    for i in range(0, 94):
        for j in range(2):
            out += ('python3 ' +
                    'acpc_hand_converter.py ' +
                    '"2014_2pl/2pl.SmooCT.Cleverpiggy.' +
                    str(i) + '.' + str(j) + '.log" ' +
                    '"out/' + '2pl.SmooCT.Cleverpiggy.' +
                    str(i) + '.' + str(j) + '.out"' + '\n')
    ofile.write(out)
