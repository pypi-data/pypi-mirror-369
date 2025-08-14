from gmsPython.auxfuncs import *
_ftype_inputs, _ftype_outputs = ('CES','CES_scaled','CES_norm','MNL'), ('CET','CET_scaled','CET_norm','MNL_out')
_scalePreserving = ('CES_norm','CET_norm','MNL','MNL_out')

def checkOrIgnore(d,k):
	return d[k] if k in d else k
def reverseDict(d):
	return {v:k for k,v in d.items()}

class Tree:
	def __init__(self, name, tree = None, db = None, f = None, io = None, **ns):
		self.name = name
		self.db = noneInit(db,{})
		self.addFunctionandIO(f, io = None)
		self.scalePreserving = True if self.f in _scalePreserving else False
		self.ns = self.standardNamespace | ns
		self.tree = noneInit(tree,[])

	@property
	def standardNamespace(self):
		return {k: f'{self.name}_{k}' for k in ('map','knot','branch','input','output','int')}

	def addFunctionandIO(self,f,io = None):
		self.f = noneInit(f, 'CES')
		self.io = noneInit(io, 'output' if self.f in _ftype_outputs else 'input')

	def __getitem__(self,item):
		try:
			return self.db[self.ns[item]]
		except KeyError:
			return self.db[item]

	def __setitem__(self,item,value):
		try:
			self.db[self.ns[item]] = gpyDB.gpy(value,**{'name': self.ns[item]})
		except KeyError:
			self.db[item] = gpyDB.gpy(value,**{'name': item})

	def get(self,item):
		return self[item].vals

	def attrsFromTree_input(self):
		self['map'] = pd.MultiIndex.from_tuples(self.tree, names = ['s', 'n','nn'])
		self['knot'] = self.get('map').droplevel('nn').unique()
		self['branch'] = self.get('map').droplevel('n').unique().rename(['s','n'])
		self['n'] = self.get('knot').union(self.get('branch')).droplevel('s').unique()
		self['s'] = self.get('map').get_level_values('s').unique()
		self['input'] = self.get('branch').difference(self.get('knot'))
		self['output'] = self.get('knot').difference(self.get('branch'))
		self['int'] = (self.get('branch').union(self.get('knot'))).difference(self.get('input').union(self.get('output')))

	def attrsFromTree_output(self):
		self['map'] = pd.MultiIndex.from_tuples(self.tree, names = ['s', 'n','nn'])
		self['knot'] = self.get('map').droplevel('n').rename(['s','n']).unique()
		self['branch'] = self.get('map').droplevel('nn').unique()
		self['n'] = self.get('knot').union(self.get('branch')).droplevel('s').unique()
		self['s'] = self.get('map').get_level_values('s').unique()
		self['input'] = self.get('knot').difference(self.get('branch'))
		self['output'] = self.get('branch').difference(self.get('knot'))
		self['int'] = (self.get('branch').union(self.get('knot'))).difference(self.get('input').union(self.get('output')))

	def __call__(self):
		getattr(self, f'attrsFromTree_{self.io}')()
		return self

class TreeFromData(Tree):
	def __init__(self,workbook,sheet,name=None,f=None,**ns):
		""" Workbook, sheet has to be supplied"""
		if type(workbook) is str:
			workbook = gpyDB.DbFromExcel.simpleLoad(workbook)
		super().__init__(sheet if name is None else name, db = gpyDB.DbFromExcel.var(workbook[sheet]),f=f,**ns)
		self.tree = self['mu'].index.to_list()

class AggTree:
	def __init__(self,name="",trees=None, ws = None, **ns):
		self.name=name
		self.ns = self.standardNamespace | ns
		self.trees = noneInit(trees,{})
		self.prune = ('n','nn','nnn','s','input','output','int')
		self.db = gpyDB.GpyDB(ws = ws, alias=[(self.n('n'),self.n('nn')), (self.n('n'),self.n('nnn'))], name = self.name)

	@property
	def standardNamespace(self):
		return {k:k for k in ('n','nn','nnn','s')} | {k: f'{self.name}_{k}' for k in ('map','int','input','output','map_spinp','map_spout','knout','kninp','spinp','spout')}

	def n(self,item,local=None):
		return self.ns[item] if local is None else self.trees[local].ns[item]

	def get(self,item,local=None):
		return self.db[self.n(item,local=local)].vals

	def __setitem__(self,item,value):
		self.db[self.n(item)] = value

	def __call__(self,namespace=None):
		[tree() for tree in self.trees.values()]; 
		self.attrsFromTrees()
		self.adjustTrees()
		[self.addDbAndPrune(tree) for tree in self.trees.values()];
		self.namespace = namespace
		if namespace:
			gpyDB.AggDB.updSetElements(self.db,self.n('n'),namespace)
		return self

	def addDbAndPrune(self,tree):
		[self.db.aom_gpy(s) for name,s in tree.db.items() if checkOrIgnore(reverseDict(tree.ns), name) not in self.prune];

	def attrsFromTrees(self):
		self.ioTypes = set([ti.io for ti in self.trees.values()])
		self['n'] = pd.Index(set.union(*[set(tree.get('n')) for tree in self.trees.values()]), name = self.n('n'))
		self['s'] = pd.Index(set.union(*[set(tree.get('s')) for tree in self.trees.values()]), name = self.n('s'))
		self['map'] = concatMultiIndices([tree.get('map') for tree in self.trees.values()])
		self['map_spinp'] = concatMultiIndices([tree.get('map') for tree in self.trees.values() if tree.scalePreserving and tree.io == 'input'], names = self.get('map').names)
		self['map_spout'] = concatMultiIndices([tree.get('map') for tree in self.trees.values() if tree.scalePreserving and tree.io == 'output'], names = self.get('map').names)
		self['knout'] = concatMultiIndices([tree.get('knot') for tree in self.trees.values() if tree.io == 'output'],  names=[self.n('s'),self.n('n')])
		self['kninp'] = concatMultiIndices([tree.get('knot') for tree in self.trees.values() if tree.io == 'input'],  names=[self.n('s'),self.n('n')])
		self['spout'] = self.get('map_spout').droplevel(self.n('nn')).unique()
		self['spinp'] = self.get('map_spinp').droplevel(self.n('n')).unique().rename([self.n('s'),self.n('n')])
		inputs = set.union(*[set(tree.get('input')) for tree in self.trees.values()])
		outputs= set.union(*[set(tree.get('output')) for tree in self.trees.values()])
		ints = set.union(*[set(tree.get('int')) for tree in self.trees.values()])
		self['input'] = pd.MultiIndex.from_tuples(inputs-outputs,names = [self.n('s'),self.n('n')])
		self['output']= pd.MultiIndex.from_tuples(outputs-inputs,names = [self.n('s'),self.n('n')])
		self['int'] = pd.MultiIndex.from_tuples((inputs.intersection(outputs)).union(ints), names = [self.n('s'),self.n('n')])		

	def adjustTrees(self):
		[getattr(self, f'adjustTree_{tree.io}')(tree) for tree in self.trees.values()];

	def adjustTree_input(self,tree):
		[tree.ns.__setitem__(k,f'{tree.name}_{k}') for k in ('knot_o','knot_no','branch2o','branch2no')];
		tree['knot_o'] = tree.get('knot').intersection(self.get('output'))
		tree['knot_no'] = tree.get('knot').difference(self.get('output'))
		tree['branch2o'] = pyDatabases.adj.rc_pd(tree['map'], self.get('output')).droplevel(self.n('n')).rename([self.n('s'),self.n('n')])
		tree['branch2no'] = pyDatabases.adj.rc_pd(tree['map'], ('not', self.get('output'))).droplevel(self.n('n')).rename([self.n('s'),self.n('n')])

	def adjustTree_output(self,tree):
		[tree.ns.__setitem__(k,f'{tree.name}_{k}') for k in ('branch_o','branch_no')];
		tree['branch_o'] = tree.get('branch').intersection(self.get('output'))
		tree['branch_no'] = tree.get('branch').difference(tree.get('branch_o'))

	# Additional methods after __call__ has been called  

	def applyNamespace(self, symbol, level = -1):
		if self.namespace:
			return symbol.set_levels(symbol.levels[level].map({k: self.namespace[k] if k in self.namespace else k for k in symbol.levels[level]}), level = level)
		else:
			return symbol

	@property
	def mapOut(self):
		if 'output' in self.ioTypes:
			return self.applyNamespace(stackIndices([ti.get('map') for ti in self.trees.values() if ti.io == 'output']))
		else:
			return pd.MultiIndex.from_tuples([], names = ['s','n','nn'])
	@property
	def knotOutTree(self):
		if 'output' in self.ioTypes:
			return self.applyNamespace(stackIndices([ti.get('knot') for ti in self.trees.values() if ti.io == 'output']))
		else:
			return pd.MultiIndex.from_tuples([], names = ['s','n'])
	@property
	def branchOut(self):
		if 'output' in self.ioTypes:
			return self.applyNamespace(stackIndices([ti.get('branch_o') for ti in self.trees.values() if ti.io == 'output']))
		else:
			return pd.MultiIndex.from_tuples([], names = ['s','n'])
	@property
	def branchNOut(self):
		if 'output' in self.ioTypes:
			return self.applyNamespace(stackIndices([ti.get('branch_no') for ti in self.trees.values() if ti.io == 'output']))
		else:
			return pd.MultiIndex.from_tuples([], names = ['s','n'])
	@property
	def mapInp(self):
		if 'input' in self.ioTypes:
			return self.applyNamespace(stackIndices([ti.get('map') for ti in self.trees.values() if ti.io == 'input']))
		else:
			return pd.MultiIndex.from_tuples([], names = ['s','n','nn'])
	@property
	def knotOut(self):
		if 'input' in self.ioTypes:
			return self.applyNamespace(stackIndices([ti.get('knot_o') for ti in self.trees.values() if ti.io == 'input']))
		else:
			return pd.MultiIndex.from_tuples([], names = ['s','n'])
	@property
	def knotNOut(self):
		if 'input' in self.ioTypes:
			return self.applyNamespace(stackIndices([ti.get('knot_no') for ti in self.trees.values() if ti.io == 'input']))
		else:
			return pd.MultiIndex.from_tuples([], names = ['s','n'])
	@property
	def branch2Out(self):
		if 'input' in self.ioTypes:
			return self.applyNamespace(stackIndices([ti.get('branch2o') for ti in self.trees.values() if ti.io == 'input']))
		else:
			return pd.MultiIndex.from_tuples([], names = ['s','n'])
	@property
	def branch2NOut(self):
		if 'input' in self.ioTypes:
			return self.applyNamespace(stackIndices([ti.get('branch2no') for ti in self.trees.values() if ti.io == 'input']))
		else:
			return pd.MultiIndex.from_tuples([], names = ['s','n'])


class AggTreeFromData(AggTree):
	def __init__(self,file_path,read_trees=None,name="",**ns):
		""" read_trees are passed to tree_from_data """
		super().__init__(name=name,**ns)
		wb = gpyDB.DbFromExcel.simpleLoad(file_path)
		if read_trees is None:
			read_trees = {sheet: {} for sheet in gpyDB.DbFromExcel.sheetnames_from_wb(wb)}
		self.trees = {t.name: t for t in (TreeFromData(wb,k,**v) for k,v in read_trees.items())}

def trimNestingStructure(m, sparsity, type = 'input', maxIter = 10, keepIntKnots = False):
	""" Trim nesting structure in pandas multiindex 'm' with a 'sparsity' pattern on the inputs. NB: Currently only works on pure input-like trees. """
	return trimNestInput(m, sparsity, maxIter = maxIter, keepIntKnots = keepIntKnots)

def trimNestInput(m, sparsity, maxIter = 10, keepIntKnots = False):
	# Step 1: Split into sectors with only one input type and sectors with more than one
	t = Tree('test', tree = m.tolist())()
	nInputs = sparsity.to_frame(index=False).groupby('s').count().n
	oneInputSectors = nInputs[nInputs == 1] # don't do anything for these
	mapOneInput = pyDatabases.adjMultiIndex.applyMult(pyDatabases.adj.rc_pd(t.get('output'), oneInputSectors),
	                                                  pyDatabases.adj.rc_pd(sparsity, oneInputSectors).rename(['s','nn']))
	mMultipleGoods = pyDatabases.adj.rc_pd(m, ('not', oneInputSectors))
	t = Tree('test', tree = mMultipleGoods.to_list())()
	# Step 2: For sectors with multiple goods, use sparsity to remove inputs that are not in use
	notUsed = pyDatabases.adj.rc_pd(t.get('input'), ('not', sparsity))
	mMultipleGoods = pyDatabases.adj.rc_pd(t.get('map'), ('not', pyDatabases.adj.rc_pd(notUsed, alias = {'n':'nn'})))	
	# Step 3: Iterate over trimming
	t = Tree(name = 'test', tree = mMultipleGoods.tolist())()
	i, status = 0, False
	while status is False:
		t, status = trimNestInput_ite(t, sparsity, keepIntKnots = keepIntKnots)
		i += 1
		if i==maxIter:
			raise StopIteration("Tree trimming did not converge in {maxIter} iterations")
	return t.get('map').union(mapOneInput)

def trimNestInput_ite(t, sparsity, keepIntKnots = False):
	# i. If a branch is identified as in input in the nesting tree, but this is not an input in the sparsity tree --> remove branch entirely from the nesting tree.
	delBranch = pyDatabases.adj.rc_pd(t.get('input'), ('not', sparsity))
	t = Tree(name = 'test', tree = pyDatabases.adj.rc_pd(t.get('map'), ('not', delBranch.rename(['s','nn']))).tolist())()

	# ii. If a parent node (n) has a single branch (nn) --> remove this specifik link (n,nn) and replace parent name with branch name in the set (nn).
	nNodes = t.get('map').to_frame(index=False).groupby(['s','n']).count()
	nodesOneBranch = nNodes[nNodes['nn']==1].index
	links = pyDatabases.adj.rc_pd(t.get('map'), nodesOneBranch)
	# Exception: If a node is in both sets 'n' and 'nn', we do not remove the branch link (nn) and replace relevant parent link.
	links = pyDatabases.adj.rc_pd(links, links.droplevel('n').difference(links.droplevel('nn').rename(['s','nn'])))
	# Remove links, then replace parent node with branch in the set (n):
	m = pyDatabases.adj.rc_pd(t.get('map'), ('not', links))
	newLinks = pyDatabases.adjMultiIndex.applyMult(m, links.rename(['s','nn','x'])).droplevel('nn').rename(m.names)
	unrelated = pyDatabases.adj.rc_pd(m, ('not', links.droplevel('nn').rename(['s','nn'])))
	t = Tree(name = 'test', tree = (newLinks.union(unrelated)).tolist())()
	return t, all([delBranch.empty, links.empty])

	# # ii. If a parent node (n) has a single branch (nn) *and* this branch is not an input in the nesting tree --> remove this specific link (n,nn) and replace branch name with parent name in the set (n).
	# nNodes = t.get('map').to_frame(index=False).groupby(['s','n']).count() # number of nodes per parent node
	# nodesOneBranch = nNodes[nNodes['nn']==1].index # parent nodes with one branch
	# links = pyDatabases.adj.rc_pd(t.get('map'), ('and', [nodesOneBranch, ('not', t.get('input').rename(['s','nn']))])) # relevant links in the nesting structure 
	# # Remove links, then replace branch with parent name in the set n:
	# m = pyDatabases.adj.rc_pd(t.get('map'), ('not', links))
	# newLinks = pyDatabases.adjMultiIndex.applyMult(m, links.rename(['s','x','n'])).droplevel('n').reorder_levels(['s','x','nn']).rename(m.names)
	# unrelated = pyDatabases.adj.rc_pd(m, ('not', links.droplevel('n').rename(['s','n'])))
	# t = Tree(name = 'test', tree = (newLinks.union(unrelated)).tolist())()

	# # iii. If a parent node (n) has a single branch (nn) *and* this branch is an input in the nesting tree --> remove this specific link (n,nn) and replace parent name with branch name in the set (nn).
	# if not keepIntKnots:
	# 	nNodes = t.get('map').to_frame(index=False).groupby(['s','n']).count()
	# 	nodesOneBranch = nNodes[nNodes['nn']==1].index
	# 	linksInp = pyDatabases.adj.rc_pd(t.get('map'), ('and', [nodesOneBranch, t.get('input').rename(['s','nn'])]))
	# 	# Remove links, then replace parent node with branch in the set (n):
	# 	m = pyDatabases.adj.rc_pd(t.get('map'), ('not', linksInp))
	# 	newLinks = pyDatabases.adjMultiIndex.applyMult(m, linksInp.rename(['s','nn','x'])).droplevel('nn').rename(m.names)
	# 	unrelated = pyDatabases.adj.rc_pd(m, ('not', linksInp.droplevel('nn').rename(['s','nn'])))
	# 	t = Tree(name = 'test', tree = (newLinks.union(unrelated)).tolist())()
	# 	return t, all([delBranch.empty, links.empty, linksInp.empty])
	# else:
	# 	return t, all([delBranch.empty, links.empty])

