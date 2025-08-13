import pandas as pd
import os
from mgo_ai.mgo_ml_base import MLRegistry, H2oModel, formatter
import h2o
import _pickle as pickle


class Trainer():
    def __init__(self, db, model_name, model_class, model_category,  data_table_view, exclude_features_from_cb=False, version=1, format_class=None, **kw):
        self.db = db
        self.data_table_view = data_table_view
        self.data = None
        self.model_name = model_name
        if isinstance(model_class, str):
            self.model_class_name = model_class
            self.model_class = getattr(h2o.estimators, model_class)
        else:
            self.model_class_name = model_class.__name__
            self.model_class = model_class
        self.model_category = model_category
        self.version = int(version)
        self.features = None
        self.target = None
        self.exclude_features = exclude_features_from_cb
        self.h2o_model = H2oModel.from_db(db,  f"{model_category}_{model_name}_{self.model_class_name}_{version}", model_category, version, foreign=False)
        if self.h2o_model and self.h2o_model.format_class:
            self._format_class = self.h2o_model.format_class
        else:
            self._format_class = format_class
        if self.h2o_model and self.h2o_model.targets:
            self.target = self.h2o_model.targets

    def set_model_class(self, model_class):
        if isinstance(model_class, str):
            self.model_class_name = model_class
            self.model_class = getattr(h2o.estimators, model_class)
        else:
            self.model_class_name = model_class.__name__
            self.model_class = model_class
        self.h2o_model = H2oModel.from_db(self.db, f"{self.model_category}_{self.model_name}_{self.model_class_name}_{self.version}", self.model_category, self.version, foreign=False)

    def get_model(self, model_id):
        if not self.h2o_model:
            self.h2o_model = H2oModel.from_db(self.db, model_id, foreign=False)
            if self.h2o_model and self.h2o_model.format_class:
                self._format_class = self.h2o_model.format_class
                if isinstance(self._format_class, str):
                    self._format_class = getattr(formatter, self._format_class)
            if self.h2o_model and self.h2o_model.targets:
                self.target = self.h2o_model.targets
                if isinstance(self.target, list) and len(self.target) == 1:
                    self.target = self.target[0]

        return self.h2o_model

    def refresh_data(self, exclude_features=None):
        self.data = pd.read_sql(f"select * from {self.data_table_view}", self.db.engine).dropna()
        return self

    def format_data(self):
        if self.data is None:
            self.refresh_data()
        if self._format_class:
            _fc = self._format_class
            if isinstance(_fc, str):
                _fc = getattr(formatter, self._format_class)
            self.data, self.features, self.target = _fc.format(self.data, self.h2o_model)

        return self

    @property
    def varimp(self):
        if self.h2o_model:
            return self.h2o_model.h2o_model.varimp(use_pandas=True)

    def train(self,  save=True, version=None, ratios: list=[0.8], seed=42, rewrite=False, **training_params):
        try:
            h2o.init()
            if not version:
                version = int(self.version)
            if self.data is None:
                self.refresh_data()
            self.format_data()
            if not isinstance(self.data, h2o.H2OFrame):
                data = h2o.H2OFrame(self.data)  # H2O can usually infer types well
            else:
                data = self.data

            # Initialize and train the model (Random Forest in this example)

            model_id = f"{self.model_category}_{self.model_name}_{self.model_class_name}_{int(version)}"
            model = self.get_model(model_id)
            # Ensure the target variable is a factor (categorical)
            data[self.target] = data[self.target].asfactor()

            # Split data into training and testing sets (80/20 split)
            train, test = data.split_frame(ratios=ratios, seed=seed)

            if model is None:
                model = self.model_class(
                    seed=seed,  # Random seed for reproducibility
                    model_id=model_id,
                    **training_params
                )
            else:
                model = self.model_class(**model.training_params)
            model.train(x=self.features, y=self.target, training_frame=train)

            # Evaluate model performance on the test set
            performance = model.model_performance(test)
            print(performance)


            # Save the trained model
            model_path = h2o.save_model(model=model, path=f"{os.getcwd()}", force=True)
            res = MLRegistry(self.db, foreign=False).set_model(
                   model_id,
                   self.model_name,
                   self.model_category,
                   self.model_class_name,
                   self.data_table_view,
                   version,
                   self.features,
                   self.target,
                   performance_metrics=performance,
                   format_class=self._format_class.__name__,
                   model_path = model_path,
                   seed=seed,
                   **training_params
            )


            print(f"Model saved to: {model_path}")
            os.remove(model_path)
        except Exception as e:
            print(f"An error occurred: {e}")
            h2o.cluster().shutdown()
            raise e

        return self

    @staticmethod
    def retrain(db, train_enabled=True, train_disabled=False, save=True, foreign=False, **kw):
        whr = ""
        if not train_enabled and not train_disabled:
            print('training is disabled according to your inputs')
            return
        if train_disabled:
            whr = f" where not enabled "
        if train_enabled:
            if not whr:
                whr = " where enabled "
            else:
                whr = ""
        print(f'training {whr}')
        models = MLRegistry(db, foreign=foreign).get([
            "model_id", "model_name", "model_class", "model_category", "model_version", "data_table_view", "format_class"
        ], where=whr).rename(columns={'model_version': 'version'}).to_dict('records')
        print(len(models), 'models found')
        for m in models:
            Trainer(db, **m).train(save=save)






