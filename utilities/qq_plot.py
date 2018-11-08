from scipy import stats
import random
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

def get_scores(path):
    sequences = []
    scores = []    
    with open(path, 'r') as f:
        for line in f:
            if len(line) > 2 and ',' in line:
                score_string = line.split(',')[1]
                sequence = line.split(',')[0]
                sequences.append(sequence)
                scores.append(float(score_string))
                
    return (sequences, scores)


def write_scores(scores, output_path):
    with open(output_path, 'w') as f:
        for score in scores:
            f.write(str(score) + '\n')
            

"""
Since targets and decoys should be the same size, we can simply sort them, pair them up, and plot.
"""
def qqplot(target_scores, decoy_scores, output_location):
    if len(target_scores) > len(decoy_scores):
        quants = list(np.linspace(0, 1, len(decoy_scores) + 2))[1:-1]
        assert(len(quants) == len(decoy_scores))
        target_scores = stats.mstats.mquantiles(target_scores, quants)
    elif len(target_scores) < len(decoy_scores):
        quants = list(np.linspace(0, 1, len(target_scores) + 2))[1:-1]
        assert(len(quants) == len(target_scores))
        decoy_scores = stats.mstats.mquantiles(target_scores, quants)
    assert(len(target_scores) == len(decoy_scores))
    target_scores.sort()
    write_scores(target_scores, 'target_scores.txt')
    decoy_scores.sort()
    write_scores(decoy_scores, 'decoy_scores.txt')
    plt.plot(target_scores, decoy_scores)
    limit = max(target_scores[-1], decoy_scores[-1])
    plt.xlim((0, limit))
    plt.ylim((0, limit))
    plt.xlabel('target scores')
    plt.ylabel('decoy scores')
    plt.savefig(output_location)

    

"""
Of the form: sequence,ic50
"""
targets= '/data1/jordan/PipelineProjects/NetMHCDecoys/NetMHC/57b5db70da2a4d489696ce5ceb658f9b-affinity'
decoys = '/data1/jordan/PipelineProjects/NetMHCDecoys/NetMHC/4627b74a92a94763a34e27c3044c63d1-affinity'

target_sequences, target_scores = get_scores(targets)

print('target scores')
print(len(target_scores))
decoy_sequences, decoy_scores = get_scores(decoys)
print(len(set(target_sequences).intersection(set(decoy_sequences))))
#assert(len(set(target_sequences).intersection(set(decoy_sequences))) == 0)
print('decoy scores')
print(len(decoy_scores))



qqplot(target_scores, decoy_scores, '10mers-Db.png')
