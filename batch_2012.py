with open('test', 'w') as ofile:
    out = ''
    for i in range(0, 50):
        for j in range(1, 4):
            out += ('python3 ' +
                    'acpc_hand_converter.py ' +
                    '"3p_limit/2012-3p-limit.hyperborean.neo_poker_lab.little_rock.run-' +
                    str(i) + '.perm-' + str(j) + '.log" ' +
                    '"out/' + '2012-3p-limit.hyperborean.neo_poker_lab.little_rock.run-' +
                    str(i) + '.perm-' + str(j) + '.out"' + '\n')
    ofile.write(out)
