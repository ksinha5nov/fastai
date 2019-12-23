# AUTOGENERATED! DO NOT EDIT! File to edit: dev/42_tabular.learner.ipynb (unless otherwise specified).

__all__ = ['TabularLearner', 'tabular_learner']

# Cell
from ..basics import *
from .core import *
from .model import *

# Cell
class TabularLearner(Learner):
    "`Learner` for tabular data"
    def predict(self, row):
        tst_to = self.dbunch.valid_ds.new(pd.DataFrame(row).T)
        tst_to.process()
        dl = self.dbunch.valid_dl.new(tst_to)
        inp,preds,_,dec_preds = self.get_preds(dl=dl, with_input=True, with_decoded=True)
        i = getattr(self.dbunch, 'n_inp', -1)
        b = (*tuplify(inp),*tuplify(dec_preds))
        full_dec = self.dbunch.decode((*tuplify(inp),*tuplify(dec_preds)))
        return full_dec,dec_preds[0],preds[0]

# Cell
@delegates(Learner.__init__)
def tabular_learner(dbunch, layers, emb_szs=None, config=None, **kwargs):
    "Get a `Learner` using `data`, with `metrics`, including a `TabularModel` created using the remaining params."
    if config is None: config = tabular_config()
    to = dbunch.train_ds
    emb_szs = get_emb_sz(dbunch.train_ds, {} if emb_szs is None else emb_szs)
    model = TabularModel(emb_szs, len(dbunch.cont_names), get_c(dbunch), layers, **config)
    return TabularLearner(dbunch, model, **kwargs)

# Cell
@typedispatch
def show_results(x:Tabular, y:Tabular, samples, outs, ctxs=None, max_n=10, **kwargs):
    df = x.all_cols[:max_n]
    for n in x.y_names: df[n+'_pred'] = y[n][:max_n].values
    display_df(df)