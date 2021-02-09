import pandas as pd
import os


def run(predictors, init_pdb, main_dir):
    res_scores = init_pdb.return_res_number_score()
    res = list(zip(*res_scores))[0]
    res = sorted(set(res))
    df = pd.DataFrame()
    df["res"] = res
    for pred in predictors:
        final_list = []
        for r in res:
            score = ""
            if r in pred.active_res:
                score = "+"
            if r in pred.passive_res:
                score = "-"
            final_list.append(score)
        df[pred.name] = final_list
    final_dir = os.path.join(main_dir, f"{os.path.basename(main_dir)[:-5]}_final.csv")
    df.to_csv(final_dir)
