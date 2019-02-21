with open('src\Test.bat', 'w') as ofile:
    out = ''
    for i in range(0, 100):
        for j in range(1):
            out += ('python.exe ' +
                    'src\\acpc_hand_converter.py ' +
                    'src\\ACPC_2018_logs\\2018-6pn-test-competition\\6pn.Myteam2.Paco2.PhantomX2.G5.Francois.Jackson.' +
                    str(i) + '.' + str(j) + '.log ' +
                    'out\\Test\\6pn.Myteam2.Paco2.PhantomX2.G5.Francois.Jackson.' +
                    str(i) + '.' + str(j) + '.out' + '\n')
    ofile.write(out)
