import os
from tools import pdb


def run(init_pdb, predictors_list, main_dir):
    active_res = []
    passive_res = []
    for predictor in predictors_list:
        pred_active_list = predictor.active_res
        for res in pred_active_list:
            if res not in active_res:
                active_res.append(res)
        pred_passive_list = predictor.passive_res
        for res in pred_passive_list:
            if res in active_res:
                continue
            passive_res.append(res)

    pdb_file = init_pdb

    pdb_string = ""
    for line in pdb_file.as_string.split(os.linesep):
        if line.startswith("ATOM"):
            res = int(line[22:26])
            b_string = line[60:77]
            score = '  0.00           '
            if res in active_res:
                score = '100.00           '
            if res in passive_res:
                score = ' 50.00           '
            new_line = line.replace(b_string, score)
        else:
            new_line = line
        pdb_string = pdb_string+new_line+os.linesep

    final_pdb = pdb.from_string(pdb_string,
                                name=f"{os.path.basename(main_dir)[:-5]}_final",
                                main_dir=main_dir)
    final_dir = os.path.join(main_dir, f"{os.path.basename(main_dir)[:-5]}_final")
    final_pdb.save_file(final_dir)
