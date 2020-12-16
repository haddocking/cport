class Predictor:
    def __init__(self, pdb, rank=None, score=None, success=None):
        self.pdb = pdb
        self.cutoff_rank = rank
        self.cutoff_score = score
        self.success = success
        self.cutoff_surface = 15
        self.passive_radius = 6.5
        self.active_res = []
        self.passive_res = []
        self.name = pdb.name


def update_res(predictor_list, surface, distance_list):
    for pred in predictor_list:
        res_score = pred.pdb.return_res_number_score()
        rank = pred.cutoff_rank
        score = pred.cutoff_score

        # Get only the residues on the surface
        exposed_res = []
        for res in res_score:
            if res[0] in surface:
                exposed_res.append(res)

        active_res = []
        # Get the first x residues with the highest score
        # (the x is determined by the threshold)
        if rank is not None:
            active_res = exposed_res[:int(rank)]
        # Get only the residues with score larger than the cutoff
        # (the cutoff is determined by the threshold)
        if score is not None:
            active_res = [i for i in exposed_res if i[1] > float(score)]

        active_res.sort()

        # Get the residues within an acceptable distance
        # (I copied the distance from Cport)
        # List of tuples(res1, res2, distance)
        acceptable_radius = [i for i in distance_list if i[2] < pred.passive_radius]

        # Remove the scores (I only need the residue numbers)
        ac_list = list(zip(*active_res))[0]
        ex_list = list(zip(*exposed_res))[0]

        # I copied this filter from Cport
        passive_list = []
        for dist in acceptable_radius:
            if dist[0] in ac_list:
                if dist[1] in ex_list:
                    passive_list.append(dist[1])
            elif dist[1] in ac_list:
                if dist[0] in ex_list:
                    passive_list.append(dist[0])

        passive_res = []
        for r in passive_list:
            if r not in ac_list:
                passive_res.append(r)
        passive_res = list(set(passive_res))
        passive_res.sort()

        # Update the list of the Predictor object
        pred.active_res = ac_list

        pred.passive_res = passive_res

    return predictor_list
