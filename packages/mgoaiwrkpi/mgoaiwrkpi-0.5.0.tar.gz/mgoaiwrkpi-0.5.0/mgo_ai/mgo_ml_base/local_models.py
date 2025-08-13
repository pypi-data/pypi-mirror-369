from models.db import Db
from h2o import load_model as h2_load_model
import pandas as pd
from models.db import Db
from h2o import load_model as h2_load_model
import pandas as pd
import h2o  # Import the h2o library
import os
from  mgo_ai.mgo_ml_base import formatter
import ast
print(os.getcwd())
try:
 h2o.cluster().shutdown()
except:
 pass




class H2oModel:
    def __init__(self, model: dict, columns, training_params, performance):
        self.model_id = model['model_id']
        self.model_category = model['model_category']
        self.model_version = model['model_version']
        self.format_class = None
        if model['format_class']:
            try:
                self.format_class = getattr(formatter, model['format_class'])
            except:
                pass
        self.features = columns.loc[columns['column_type'] == 'feature', 'column_name'].to_list()
        self.targets = columns.loc[columns['column_type'] == 'target', 'column_name'].to_list()
        if len(self.targets) < 2:
            self.targets = self.targets[0]
        self.h2o_model = self._load_h2o_model(self.model_id, model['model_binary'])  # Load the H2O model
        self.performance = performance
        self.training_params = {v[0]: ast.literal_eval(v[1])  if '[' in v[1] else float(v[1]) if '.' in v[1] else int(v[1])
                                for v in training_params.drop(columns='model_id').to_dict('split')['data']}


    @staticmethod
    def _load_h2o_model(model_id, binary):

        h2o.init()
        """Loads the H2O model from the binary data."""
        try:
            # Write the binary data to a temporary file (required by h2o.load_model)
            with open(f"{os.getcwd()}/{model_id}", "wb") as f:
                f.write(binary)

            # Load the model from the temporary file

            model = h2o.load_model(f"{os.getcwd()}/{model_id}")

            # remove the temp file
            # import os
            os.remove(f"{os.getcwd()}/{model_id}")

            return model
        except Exception as e:
            print(f"Error loading H2O model: {e}")
            return None  # Or raise an exception, depending on your error handling strategy

    @classmethod
    def from_db(cls, db, model_id, category=None, version=None, foreign=True):
        """Loads an H2oModel from the database."""
        registry = MLRegistry(db, foreign=foreign)  # Use MLRegistry to access the database
        model = registry.get_model(model_id, category, version)
        if model:
            return model
        else:
            return None

    @staticmethod
    def load_models_from_db(db, model_name=None, model_category=None, version=None, foreign=True, limit=6, **kw):
        registry = MLRegistry(db, foreign=foreign)  # Use MLRegistry to access the database
        return registry.get_models_ranked(model_name, model_category, version, limit=limit)

    def predict(self, data: pd.DataFrame, join_index='order_id'):
            if self.h2o_model is None:
                raise Exception("H2O model not loaded correctly.")
            
            data = data.copy().reset_index(drop=True)
            p_data, features, target = self.format_class.format(data.copy(), self)
            # Convert Pandas DataFrame to H2OFrame
            h2o_data = h2o.H2OFrame(p_data[features])
    
            # Make predictions
            predictions = self.h2o_model.predict(h2o_data)
            predictions = predictions.as_data_frame()
            predictions['ph'] = predictions['p1']
            data = data.join(predictions)
            # Convert predictions back to Pandas DataFrame (optional)
            return data


class MLLogLocal(Db):
    def __init__(self, db):
        Db.__init__(self, db, 'processing', 'ml_log')
        self.set_constraint('ml_log_pkey', ['crm_id', 'order_id', 'child_id'])


class RollingApproval(Db):
    def __init__(self, db):
        Db.__init__(self, db, 'processing', 'rolling_approval')
        self.set_constraint('rolling_approval_pkey',
                            ['cc_type', 'processor', 'bc_inferred', 'campaign_class', 'attempt_count', 'mid_id'])


class MLColumnData(Db):
    def __init__(self, db, foreign=True):
        Db.__init__(self, db, f'{"foreign_" if foreign else ""}ml_models', 'column_data')
        self.set_constraint('column_data_pkey', ['model_id', 'column_name'])


class MLTrainingData(Db):
    def __init__(self, db, foreign=True):
        Db.__init__(self, db, f'{"foreign_" if foreign else ""}ml_models', 'training_params')
        self.set_constraint('training_params_pkey', ['model_id', 'param'])


class MLTopLevelPerf(Db):
    def __init__(self, db, foreign=True):
        Db.__init__(self, db, f'{"foreign_" if foreign else ""}ml_models', 'top_level_perf')
        self.set_constraint('top_level_perf_pkey', ['model_id'])


class MLConfusionMatrix(Db):
    def __init__(self, db, foreign=True):
        Db.__init__(self, db, f'{"foreign_" if foreign else ""}ml_models', 'confusion_matrix')
        self.set_constraint('confusion_matrix_pkey', ['model_id', 'Error'])


class MLMaximumMetrics(Db):
    def __init__(self, db, foreign=True):
        Db.__init__(self, db, f'{"foreign_" if foreign else ""}ml_models', 'maximum_metrics')
        self.set_constraint('maximum_metrics_pkey', ['model_id', 'idx'])


class MLMetricsForThresholds(Db):
    def __init__(self, db, foreign=True):
        Db.__init__(self, db, f'{"foreign_" if foreign else ""}ml_models', 'metrics_for_thresholds')
        self.set_constraint('metrics_for_thresholds_pkey', ['model_id', 'idx'])


class MLGainsLift(Db):
    def __init__(self, db, foreign=True):
        Db.__init__(self, db, f'{"foreign_" if foreign else ""}ml_models', 'gains_lift')
        self.set_constraint('gains_lift_pkey', ['model_id', 'group_'])


class MLRegistry(Db):
    def __init__(self, db, foreign=True):
        Db.__init__(self, db, f'{"foreign_" if foreign else ""}ml_models', 'registry')
        self.set_constraint('registry_pkey', ['model_id'])
        self.db_col_reg = MLColumnData(db, foreign=foreign)
        self.db_tr_reg = MLTrainingData(db, foreign=foreign)
        self.db_gains_lift = MLGainsLift(db, foreign=foreign)
        self.db_max_metrics = MLMaximumMetrics(db, foreign=foreign)
        self.db_metrics_for_thresholds = MLMetricsForThresholds(db, foreign=foreign)
        self.db_top_level_perf = MLTopLevelPerf(db, foreign=foreign)
        self.db_confusion_matrix = MLConfusionMatrix(db, foreign=foreign)

    def get_model(self, model_id, *args, **kw):
        model = self.engine.execute(f" select * from {self.schema}.{self.table} where model_id='{model_id}'").fetchone()
        if model is None or not len(model):
            return None
        model = dict(model)
        columns = self.db_col_reg.get(where=f"where model_id='{model_id}'")

        performance = {
            'gains_lift': self.db_gains_lift.get(where=f"where model_id='{model_id}'"),
            'max_metrics': self.db_max_metrics.get(where=f"where model_id='{model_id}'"),
            'metrics_for_thresholds': self.db_metrics_for_thresholds.get(where=f"where model_id='{model_id}'"),
            'top_level_perf': self.db_top_level_perf.get(where=f"where model_id='{model_id}'"),

        }
        training_data = self.db_tr_reg.get(where=f"where model_id='{model_id}'")
        return H2oModel(model, columns, training_data, performance)

    def get_models_ranked(self, model_name=None,  model_category=None,  model_version=None, order='auc desc', limit=6, min_auc=0.8, max_mean_sq=.2):
        whr = "where enabled"
        if model_name:
            whr += f" {' and ' if whr else ' where '} model_name='{model_name}'"
        if model_version:
            whr += f" {' and ' if whr else ' where '} model_version='{model_version}'"
        if model_category:
            whr += f" {' and ' if whr else ' where '} model_category='{model_category}'"

        qry = f"""
            select a.model_id, auc from (select model_id from {self.schema}.{self.table} {whr}) as a
            inner join {self.schema}.top_level_perf  b on b.model_id =a.model_id
            --where auc::numeric > {min_auc} and mean_per_class_error::numeric < {max_mean_sq}
            order by {order}
            limit {limit}
        """

        return [self.get_model(m[0]) for m in self.engine.execute(qry)]

    def delete_model(self, model_id):
        self.engine.execute(f"delete from {self.schema}.{self.table} where model_id='{model_id}'")

    def set_model(self,
                  model_id,
                  model_name,
                  model_category,
                  model_class,
                  data_table_view,
                  version, features: list,
                  targets: list,
                  performance_metrics,
                  format_class,
                  model_path,
                  **training_params):

        if not isinstance(features, list):
            features = [features]
        if not isinstance(targets, list):
            targets = [targets]

        # Save the model as a binary file in memory
        # model = h2_load_model(model_id)
        # model_path = model.download_model(model_id)  # Download to a temp dir

        try:
            with open(model_path, "rb") as f:  # Open in binary read mode
                binary_model = f.read()
        except FileNotFoundError:
            print(f"Error: Model file not found at {model_id}")
            return False  # Or raise an exception

        data = {
            'model_id': model_id,
            'model_category': model_category,
            'model_class': model_class,
            'model_name': model_name,
            'model_version': version,
            'model_binary': binary_model,
            'data_table_view': data_table_view,
            'format_class': format_class,
        }

        res = self.insert(data, return_id='model_id')
        if not res.success():
            self.delete_model(model_id)
            res = self.insert(data, return_id='model_id')
            if not res.success():
                raise Exception(f'Save Model {model_id} failed')

        col_data = [{'model_category': model_category,
                     'model_id': model_id,
                     'model_version': version,
                     'column_name': col,
                     'column_type': 'feature',
                     } for col in features]
        col_data += [{
                      'model_id': model_id,
                      'column_name': col,
                      'column_type': 'target',
                      } for col in targets]
        tr = [{
               'model_id': model_id,
               'param': k,
               'value': v
              } for k, v in training_params.items()]
        self.db_tr_reg.upsert(tr)
        self.db_col_reg.upsert(col_data)

        # Performance
        j = performance_metrics._metric_json
        gen = {k.lower(): j[k] for k in
               ['MSE', 'RMSE', 'r2', 'AIC', 'AUC', 'Gini', 'pr_auc', 'mean_per_class_error', 'logloss', 'loglikelihood']
               if k in j}
        gen['model_id'] = model_id
        self.db_top_level_perf.upsert([gen])

        gl = j['gains_lift_table']
        glt = pd.DataFrame(gl.cell_values, columns=gl.col_header).rename(columns={'group': 'group_'})
        glt['model_id'] = model_id
        self.db_gains_lift.upsert(glt)

        # cm = pd.DataFrame(j['cm']['table'].cell_values, columns=j['cm']['table'].col_header)
        # cm['model_id'] = model_id
        # self.db_confusion_matrix.upsert(cm)

        trh = j['thresholds_and_metric_scores']
        trh = pd.DataFrame(trh.cell_values, columns=trh.col_header)
        trh['model_id'] = model_id
        self.db_metrics_for_thresholds.upsert(trh)

        mm = j['max_criteria_and_metric_scores']
        mm = pd.DataFrame(mm.cell_values, columns=mm.col_header)
        mm['model_id'] = model_id
        return self.db_max_metrics.upsert(mm)







