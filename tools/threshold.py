import os


def run(predictors, tools_dir, main_dir):
    """
    I load the threshold files and separate each one to a dictionary
    Each threshold contains the possible combinations between the predictors
    """
    cportthresholds = []
    for n in (1, 2, 3):
        f = os.path.join(tools_dir, "tools/threshold{}.stat".format(n))
        lines = [line.split() for line in open(f).readlines()]
        curr_thresholds = {}
        for line in lines:
            dic = {}
            for predictor in line:
                key, val1, val2 = predictor.split(":")
                if val1 == "None":
                    val1 = None
                if val2 == "None":
                    val2 = None
                dic[key] = val1, val2
            curr_thresholds[frozenset(dic.keys())] = dic
        cportthresholds.append(curr_thresholds)
    """
    The dictionary keys are organised in a specific order
    Based on the successful predictors I recreate this order
    """
    predictorlist = ["WHISCY", "ProMate", "PIER", "PPISP", "PINUP", "SPPIDER"]
    succ_list = [p.name for p in predictors if p.success is True]
    suc = []
    for i in predictorlist:
        if i in succ_list:
            suc.append(i)

    suc_set = frozenset(suc)
    thress = curr_thresholds[suc_set]
    """
    I upgrade predictors
    """
    final_suc_predictors = []
    for pred in predictors:
        if pred.success is True:
            pred.cutoff_rank, pred.cutoff_score = thress[pred.name]
            final_suc_predictors.append(pred)
    return final_suc_predictors
