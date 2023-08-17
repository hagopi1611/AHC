with open('hh.bat', 'w') as ofile:
    out = ''
    for i in range(50):
        for j in range(2):
            out += ('python3 ' +
                    'ACPCHandConverter.py ' +
                    '\"input/2011-2p-limit.Calamari.Hyperborean-2011-2p-limit-iro.run-' +
                    str(i) + '.perm-' + str(j) + '.log\" ' +
                    '\"Out/2011-2p-limit.Calamari.Hyperborean-2011-2p-limit-iro.run-' +
                    str(i) + '.perm-' + str(j) + '.out\" ' + '2011\n')
    ofile.write(out)
