with open('ACPC2017.bat', 'w') as ofile:
    out = ''
    for i in range(1, 101):
        for j in range(2):
            out += ('"python.exe" ' +
                    'ACPCHandConverter.py ' +
                    '"logs_2pn_2017\\Feste.Intermission.' +
                    str(i) + '.' + str(j) + '.log" ' +
                    '"2017ACPCOut\\Feste.Intermission.' +
                    str(i) + '.' + str(j) + '.out" ' +
                    '2017' + str(i).zfill(3) + str(j) + ' ' +
                    'N\n')
    ofile.write(out)
