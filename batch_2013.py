with open('test', 'w') as ofile:
    out = ''
    for i in range(0, 20):
        for j in range(2, 5):
            out += ('python3 ' +
                    'acpc_hand_converter.py ' +
                    '"3pl_logs/3pl.neo_poker_lab.littlerock.hyperborean_iro.' +
                    str(i) + '.' + str(j) + '.log" ' +
                    '"out/' + '3pl.neo_poker_lab.littlerock.hyperborean_iro.' +
                    str(i) + '.' + str(j) + '.out"' + '\n')
    ofile.write(out)
