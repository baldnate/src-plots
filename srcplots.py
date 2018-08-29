# Import the libraries
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import srcomapi, srcomapi.datatypes as dt
import warnings

def find_game(api, name):
	# order of preference:
	# no hits (error), 1 hit, >1 hit exact, whatever
	result = api.search(srcomapi.datatypes.Game, {"name": name})
	if not result:
		raise Exception('Search for game {} found no results.'.format(name))
	if len(result) == 1:
		return result[0]
	for hit in result:
		if hit.name == name:
			return hit
	print('Search for game {} hit for {}'.format(name, len(result)))
	return result[0] # give up and return something

def find_category(api, game, name):
	result = []
	for cat in game.categories:
		if name == cat.name:
			return cat
		if name in cat.name:
			result.append(cat)
	if not result:
		raise Exception('Search for cat {} in game {} found no results.'.format(name, game.name))
	print('Search for cat {} in game {} found {} results.'.format(name, game.name, len(result)))
	return result[0]

def bin_explorer(data, bins, xlabel, ylabel):
	for i, binwidth in enumerate(bins):
	    ax = plt.subplot(2, 2, i + 1)
	    ax.hist(data, bins = int(180/binwidth),
	             color = 'blue', edgecolor = 'black')
	    ax.set_title('binwidth = %d' % binwidth, size = 16)
	    ax.set_xlabel(xlabel, size = 12)
	    ax.set_ylabel(ylabel, size= 12)
	plt.tight_layout()

def pd_explorer(data, bins, xlabel, ylabel):
	for i, binwidth in enumerate(bins):
	    ax = plt.subplot(2, 2, i + 1)
	    ax = sns.distplot(data, ax=ax, hist=True, kde=True,
             bins=int(180/binwidth), color = 'darkblue',
             hist_kws={'edgecolor':'black'},
             kde_kws={'linewidth': 4})
	    ax.set_title('binwidth = %d' % binwidth, size = 16)
	    ax.set_xlabel(xlabel, size = 12)
	    ax.set_ylabel(ylabel, size= 12)
	plt.tight_layout()

def get_lb_run_times(api, gamename, catname):
	game = find_game(api, gamename)
	cat = find_category(api, game, catname)
	times = []
	lb = dt.Leaderboard(api, data=api.get("leaderboards/{}/category/{}?embed=variables".format(game.id, cat.id)))
	for run in lb.runs:
		times.append(run['run'].times['primary_t'])

	return pd.DataFrame(data = {'time': times})

def comp_density_plots(datasets, title, xlabel, ylabel):
	for set in datasets:
		label = set['label']
		data = set['data']
		sns.distplot(data, hist = False, kde = True,
			kde_kws = {'shade': True, 'linewidth': 3},
			label = label)
	plt.legend()
	plt.title(title)
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	plt.yticks([])

api = srcomapi.SpeedrunCom(); api.debug = 0
datasets = []
for doob in ['', ' Deathless']:
	for cat in ['Any%', 'All Bosses', '100%']:
		datasets.append(
			{
				'label': '{}{}'.format(cat, doob),
				'data': get_lb_run_times(api, 'Metroid', '{}{}'.format(cat, doob))
			}
		)

comp_density_plots(datasets, 'Metroid - Category Probability Density Plots', 'duration', 'runs')
#pd_explorer(data = timedf['time'], bins = [1, 5, 10, 15], xlabel = 'duration', ylabel = 'runs')
plt.savefig("node.png")
