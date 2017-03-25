with open('ACPC2013.bat', 'w') as ofile:
    out = ''
    for i in range(100):
        for j in range(2):
            out += ('"c:\\program files (x86)\\python36-32\\python.exe" ' +
                    'ACPCHandConverter.py ' +
                    '"ACPC_in2013\\2pl.hyperborean_iro.zbot.' +
                    str(i) + '.' + str(j) + '.log" ' +
                    '"ACPC_out2013\\2pl.hyperborean_iro.zbot.' +
                    str(i) + '.' + str(j) + '.out" ' +
                    '1' + str(i).zfill(2) + str(j) + ' '
                    'L\n')
    ofile.write(out)
