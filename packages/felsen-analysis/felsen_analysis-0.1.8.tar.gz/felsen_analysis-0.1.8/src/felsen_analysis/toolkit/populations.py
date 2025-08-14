from felsen_analysis.toolkit.process import AnalysisObject
import unit_localizer as ul
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from scipy.ndimage.filters import gaussian_filter1d


def defineQualityUnits(h5file, clusterFile):
    """
    This function filters all units by quality metrics and returns a list of unit cluster numbers assigned to good quality units
    Not necessary to use if using one of the definePopulation functions as it is built in to those functions (ie definePremotorPopulation)
    Helpful if you want to use all units in a recording, not just a predefined population, but want good quality units only
    """
    session = AnalysisObject(h5file)
    population = session._population()
    ampCutoff = session.load('metrics/ac')
    presenceRatio = session.load('metrics/pr')
    firingRate = session.load('metrics/fr')
    isiViol = session.load('metrics/rpvr')
    qualityLabels = session.load('metrics/ql')
    qualityUnits = list()
    for index, unit in enumerate(population):
        if qualityLabels is not None and qualityLabels[index] in (0, 1):
            continue
        if ampCutoff[index] <= 0.1:
            if presenceRatio[index] >= 0.9:
             if firingRate[index] >= 0.2:
                if isiViol[index] <= 0.5:
                    qualityUnits.append(unit.cluster)
    return qualityUnits

def definePremotorPopulation(h5file, clusterFile):
    """
    This function filters your population of neurons and pulls out premotor neurons based on ZETA test results
    """
    session = AnalysisObject(h5file)
    labels = session.load('nptracer/labels')
    brainAreas = ul.translateBrainAreaIdentities(labels, '/home/jbhunt/Downloads/structure_graph_with_sets.json') 

    #spikeClustersFile = session.home.joinpath('ephys/sorting/manual/spike_clusters.npy') #fix
    spikeClustersFile = clusterFile
    uniqueSpikeClusters = np.unique(np.load(spikeClustersFile))
    zetaNasal = session.load('zeta/saccade/nasal/p')
    zetaTemporal = session.load('zeta/saccade/temporal/p')
    ampCutoff = session.load('metrics/ac')
    presenceRatio = session.load('metrics/pr')
    firingRate = session.load('metrics/fr')
    isiViol = session.load('metrics/rpvr')
    qualityLabels = session.load('metrics/ql')
    premotorUnitsZeta = list()
    for index, pVal in enumerate(zetaNasal):
        if brainAreas[index] in ['SCsg','SCop', 'SCig', 'SCiw', 'SCdg']:
            pNasal = pVal
            pTemporal = zetaTemporal[index]
            if pNasal < pTemporal:
                p = pNasal
            elif pTemporal < pNasal:
                p = pTemporal
            if p < 0.05:
                if qualityLabels is not None and qualityLabels[index] in (0, 1):
                        continue
                if ampCutoff[index] <= 0.1:
                    if presenceRatio[index] >= 0.9:
                        if firingRate[index] >= 0.2:
                            if isiViol[index] <= 0.5:
                                unit = uniqueSpikeClusters[index]
                                premotorUnitsZeta.append(unit)

    return premotorUnitsZeta

def definePremotorPopulationExclusive(h5file, clusterFile):
    """
    This function defines the population of neurons that have only premotor and no visual activity
    """
    premotorUnitsExclusive = list()
    premotorUnitsAll = definePremotorPopulation(h5file, clusterFile)
    visualUnitsAll = defineVisualPopulation(h5file, clusterFile)
    visuomotorUnits = defineVisuomotorPopulation(premotorUnitsAll, visualUnitsAll)
    for unit in premotorUnitsAll:
        if unit not in visuomotorUnits:
            premotorUnitsExclusive.append(unit)
    return premotorUnitsExclusive

def defineVisualPopulationExclusive(h5file, clusterFile):
    """
    This function defines the population of neurons that have only premotor and no visual activity
    """
    visualUnitsExclusive = list()
    premotorUnitsAll = definePremotorPopulation(h5file, clusterFile)
    visualUnitsAll = defineVisualPopulation(h5file, clusterFile)
    visuomotorUnits = defineVisuomotorPopulation(premotorUnitsAll, visualUnitsAll)
    for unit in visualUnitsAll:
        if unit not in visuomotorUnits:
            visualUnitsExclusive.append(unit)
    return visualUnitsExclusive
    
def defineVisualPopulation(h5file, clusterFile):
    """
    This function filters your population of neurons and pulls out visual neurons based on ZETA test results
    """
    session = AnalysisObject(h5file)
    labels = session.load('nptracer/labels')
    #spikeClustersFile = session.home.joinpath('ephys/sorting/manual/spike_clusters.npy')
    spikeClustersFile = clusterFile
    uniqueSpikeClusters = np.unique(np.load(spikeClustersFile))
    brainAreas = ul.translateBrainAreaIdentities(labels) 
    zetaLeft = session.load('zeta/probe/left/p')
    zetaRight = session.load('zeta/probe/right/p')
    ampCutoff = session.load('metrics/ac')
    presenceRatio = session.load('metrics/pr')
    firingRate = session.load('metrics/fr')
    isiViol = session.load('metrics/rpvr')
    qualityLabels = session.load('metrics/ql')
    visualUnitsZeta = list()
    for index, pVal in enumerate(zetaLeft):
        if brainAreas[index] in ['SCsg','SCop', 'SCig', 'SCiw', 'SCdg']:
            pLeft = pVal
            pRight = zetaRight[index]
            if pLeft < pRight:
                p = pLeft
            elif pRight < pLeft:
                p = pRight
            if p < 0.05:
                if qualityLabels is not None and qualityLabels[index] in (0, 1):
                        continue
                if ampCutoff[index] <= 0.1:
                    if presenceRatio[index] >= 0.9:
                        if firingRate[index] >= 0.2:
                            if isiViol[index] <= 0.5:
                                unit = uniqueSpikeClusters[index]
                                visualUnitsZeta.append(unit)
    return visualUnitsZeta

def defineVisuomotorPopulation(premotorUnits, visualUnits):
    """
    This function finds which units are both visual and motor
    """
    visuomotorUnits = list()
    for unit in premotorUnits:
        if unit in visualUnits:
            visuomotorUnits.append(unit)
    return visuomotorUnits

def createTrialArray(h5file, timeBins, units, trials):
    """
    This function creates a list of len(trials) where each line is a units x 11 time bins array of spiking activity 
    This is the first step to running a PCA analysis that looks at population activity over time
    """
    trialList = list()
    session = AnalysisObject(h5file)
    #population = Population(session)
    population = session._population()
    for trial in trials:
        unitArray = np.zeros((len(units), 10))
        ind = 0
        for unit in population:
            if unit.cluster in units:
                spikeTimes = unit.timestamps
                t1 = trial + timeBins[0]
                t2 = trial + timeBins[1]
                t3 = trial + timeBins[2]
                t4 = trial + timeBins[3]
                t5 = trial + timeBins[4]
                t6 = trial + timeBins[5]
                t7 = trial + timeBins[6]
                t8 = trial + timeBins[7]
                t9 = trial + timeBins[8]
                t10 = trial + timeBins[9]
                t11 = trial + timeBins[10]
                mask1 = np.logical_and(spikeTimes >= t1, spikeTimes < t2)
                a = len(spikeTimes[mask1])/0.3
                mask2 = np.logical_and(spikeTimes >= t2, spikeTimes < t3)
                b = len(spikeTimes[mask2])/0.3
                mask3 = np.logical_and(spikeTimes >= t3, spikeTimes < t4)
                c = len(spikeTimes[mask3])/0.3
                mask4 = np.logical_and(spikeTimes >= t4, spikeTimes < t5)
                d = len(spikeTimes[mask4])/0.3
                mask5 = np.logical_and(spikeTimes >= t5, spikeTimes < t6)
                e = len(spikeTimes[mask5])/0.3
                mask6 = np.logical_and(spikeTimes >= t6, spikeTimes < t7)
                f = len(spikeTimes[mask6])/0.3
                mask7 = np.logical_and(spikeTimes >= t7, spikeTimes < t8)
                g = len(spikeTimes[mask7])/0.3
                mask8 = np.logical_and(spikeTimes >= t8, spikeTimes < t9)
                h = len(spikeTimes[mask8])/0.3
                mask9 = np.logical_and(spikeTimes >= t9, spikeTimes < t10)
                i = len(spikeTimes[mask9])/0.3
                mask10 = np.logical_and(spikeTimes >= t10, spikeTimes < t11)
                j = len(spikeTimes[mask10])/0.3
                fr = [a, b, c, d, e, f, g, h, i, j]
                unitArray[ind, :] = fr
                ind = ind + 1
        trialList.append(unitArray)
    return trialList

def specifyTrialTypes(h5file, saccade=True): 
    """
    Lets you specify what different trial types you want to measure population responses to
    """
    session = AnalysisObject(h5file)
    if saccade==True:
        trial_type_tmp = session.load('saccades/predicted/left/labels') #contra = 1, ipsi = -1
    elif saccade==False:
        tts = session.load('stimuli/dg/probe/tts')
        typeCode = list() #perisaccadic = 0, extrasaccadic = 2
        for t in tts:
            if abs(t) < 0.1:
                typeCode.append(0)
            else:
                typeCode.append(2)
        trial_type_tmp = np.array(typeCode)
    trial_type = list()
    for element in trial_type_tmp:
        if element == -1:
            trial_type.append('Ipsi')
        elif element == 1:
            trial_type.append('Contra')
        elif element == 0:
            trial_type.append('Perisaccadic')
        elif element == 2:
            trial_type.append('Extrasaccadic')
    trial_types = np.unique(trial_type)
    t_type_ind = [np.argwhere(np.array(trial_type) == t_type)[:, 0] for t_type in trial_types]
    return t_type_ind, trial_types

def z_score(X):
    # X: ndarray, shape (n_features, n_samples)
    ss = StandardScaler(with_mean=True, with_std=True)
    Xz = ss.fit_transform(X.T).T
    return Xz


def trialAveragedPCA(trialList, t_type_ind, trial_types, n_components):
    """
    A form of PCA that finds principal components across time bins around the time of a trial
    First computes average of trials of each type, then reduces dimensions
    Returns a 3D array with the average population activity for each component for each trial type
    """
    trial_averages = []
    trial_size = trialList[0].shape[1]
    for ind in t_type_ind:
        trial_averages.append(np.array(trialList)[ind].mean(axis=0))
    Xa = np.hstack(trial_averages)
    Xa = z_score(Xa) #Xav_sc = center(Xav)
    pca = PCA(n_components=n_components)
    Xa_p = pca.fit_transform(Xa.T).T
    pcs = np.zeros((n_components, 10, 2))
    for comp in range(n_components):
        for kk, type in enumerate(trial_types):
            x = Xa_p[comp, kk * trial_size :(kk+1) * trial_size]
            x = gaussian_filter1d(x, sigma=3)
            pcs[comp, :, kk] = x
    return pcs

def getUnitDepth(h5file, premotorUnits, visualUnits, visuomotorUnits, depthDict=None):
    """
    Function that returns the coordinates for each unit in a recording & a list of identities for easy indexing
    """
    session = AnalysisObject(h5file)
    points = session.load('nptracer/points')
    population = session._population()
    if depthDict is None:
        depthDict = {identity:[] for identity in ['premotor', 'visual', 'visuomotor']}
    for i, unit in enumerate(population):
        depth = points[i, 2]
        if unit.cluster in premotorUnits:
            depthDict['premotor'].append(depth)
        elif unit.cluster in visualUnits:
            depthDict['visual'].append(depth)
        elif unit.cluster in visuomotorUnits:
            depthDict['visuomotor'].append(depth)
    return depthDict

def getUnitCoords(h5file, premotorUnits, visualUnits, visuomotorUnits, coordDict=None):
    """
    Function that returns the coordinates for each unit in a recording & a list of identities for easy indexing
    """
    session = AnalysisObject(h5file)
    points = session.load('nptracer/points')
    population = session._population()
    if coordDict is None:
        coordDict = {identity:[] for identity in ['premotor', 'visual', 'visuomotor']}
    for i, unit in enumerate(population):
        x = points[i, 1]
        y = points[i, 2]
        coords = [x, y]
        if unit.cluster in premotorUnits:
            coordDict['premotor'].append(coords)
        elif unit.cluster in visualUnits:
            coordDict['visual'].append(coords)
        elif unit.cluster in visuomotorUnits:
            coordDict['visuomotor'].append(coords)
    return coordDict
