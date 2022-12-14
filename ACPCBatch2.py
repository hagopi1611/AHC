with open('src\Test.bat', 'w') as ofile:
    out = ''
    for i in range(30, 36):
        out += ('python.exe ' +
                'src\\ACPChandConverter.py ' +
                'src\\5H1AI_logs\\sample_game_' +
                str(i) + '.log ' +
                'out\\5H1AI_out\\sample_game_' +
                str(i) + '.out' + '\n')
    for i in range(40, 46):
        out += ('python.exe ' +
                'src\\ACPChandConverter.py ' +
                'src\\5H1AI_logs\\sample_game_' +
                str(i) + '.log ' +
                'out\\5H1AI_out\\sample_game_' +
                str(i) + '.out' + '\n')
        out += ('python.exe ' +
                'src\\ACPChandConverter.py ' +
                'src\\5H1AI_logs\\sample_game_' +
                str(i) + 'b.log ' +
                'out\\5H1AI_out\\sample_game_' +
                str(i) + 'b.out' + '\n')
    for i in range(50, 54):
        out += ('python.exe ' +
                'src\\ACPChandConverter.py ' +
                'src\\5H1AI_logs\\sample_game_' +
                str(i) + '.log ' +
                'out\\5H1AI_out\\sample_game_' +
                str(i) + '.out' + '\n')
        out += ('python.exe ' +
                'src\\ACPChandConverter.py ' +
                'src\\5H1AI_logs\\sample_game_' +
                str(i) + 'b.log ' +
                'out\\5H1AI_out\\sample_game_' +
                str(i) + 'b.out' + '\n')

    for i in range(60, 66):
        out += ('python.exe ' +
                'src\\ACPChandConverter.py ' +
                'src\\5H1AI_logs\\sample_game_' +
                str(i) + '.log ' +
                'out\\5H1AI_out\\sample_game_' +
                str(i) + '.out' + '\n')
    for i in range(70, 75):
        out += ('python.exe ' +
                'src\\ACPChandConverter.py ' +
                'src\\5H1AI_logs\\sample_game_' +
                str(i) + '.log ' +
                'out\\5H1AI_out\\sample_game_' +
                str(i) + '.out' + '\n')
    for i in range(75, 78):
        out += ('python.exe ' +
                'src\\ACPChandConverter.py ' +
                'src\\5H1AI_logs\\sample_game_' +
                str(i) + '.log ' +
                'out\\5H1AI_out\\sample_game_' +
                str(i) + '.out' + '\n')
        out += ('python.exe ' +
                'src\\ACPChandConverter.py ' +
                'src\\5H1AI_logs\\sample_game_' +
                str(i) + 'b.log ' +
                'out\\5H1AI_out\\sample_game_' +
                str(i) + 'b.out' + '\n')
    for i in range(78, 79):
        out += ('python.exe ' +
                'src\\ACPChandConverter.py ' +
                'src\\5H1AI_logs\\sample_game_' +
                str(i) + '.log ' +
                'out\\5H1AI_out\\sample_game_' +
                str(i) + '.out' + '\n')
    for i in range(83, 94):
        out += ('python.exe ' +
                'src\\ACPChandConverter.py ' +
                'src\\5H1AI_logs\\sample_game_' +
                str(i) + '.log ' +
                'out\\5H1AI_out\\sample_game_' +
                str(i) + '.out' + '\n')
    for i in range(94, 98):
        out += ('python.exe ' +
                'src\\ACPChandConverter.py ' +
                'src\\5H1AI_logs\\sample_game_' +
                str(i) + '.log ' +
                'out\\5H1AI_out\\sample_game_' +
                str(i) + '.out' + '\n')
        out += ('python.exe ' +
                'src\\ACPChandConverter.py ' +
                'src\\5H1AI_logs\\sample_game_' +
                str(i) + 'b.log ' +
                'out\\5H1AI_out\\sample_game_' +
                str(i) + 'b.out' + '\n')
    for i in range(98, 100):
        out += ('python.exe ' +
                'src\\ACPChandConverter.py ' +
                'src\\5H1AI_logs\\sample_game_' +
                str(i) + '.log ' +
                'out\\5H1AI_out\\sample_game_' +
                str(i) + '.out' + '\n')
    for i in range(100, 104):
        out += ('python.exe ' +
                'src\\ACPChandConverter.py ' +
                'src\\5H1AI_logs\\sample_game_' +
                str(i) + '.log ' +
                'out\\5H1AI_out\\sample_game_' +
                str(i) + '.out' + '\n')
        out += ('python.exe ' +
                'src\\ACPChandConverter.py ' +
                'src\\5H1AI_logs\\sample_game_' +
                str(i) + 'b.log ' +
                'out\\5H1AI_out\\sample_game_' +
                str(i) + 'b.out' + '\n')
    for i in range(104, 111):
        out += ('python.exe ' +
                'src\\ACPChandConverter.py ' +
                'src\\5H1AI_logs\\sample_game_' +
                str(i) + '.log ' +
                'out\\5H1AI_out\\sample_game_' +
                str(i) + '.out' + '\n')
    for i in range(111, 115):
        out += ('python.exe ' +
                'src\\ACPChandConverter.py ' +
                'src\\5H1AI_logs\\sample_game_' +
                str(i) + '.log ' +
                'out\\5H1AI_out\\sample_game_' +
                str(i) + '.out' + '\n')
        out += ('python.exe ' +
                'src\\ACPChandConverter.py ' +
                'src\\5H1AI_logs\\sample_game_' +
                str(i) + 'b.log ' +
                'out\\5H1AI_out\\sample_game_' +
                str(i) + 'b.out' + '\n')
    for i in range(115, 119):
        out += ('python.exe ' +
                'src\\ACPChandConverter.py ' +
                'src\\5H1AI_logs\\sample_game_' +
                str(i) + '.log ' +
                'out\\5H1AI_out\\sample_game_' +
                str(i) + '.out' + '\n')
    ofile.write(out)