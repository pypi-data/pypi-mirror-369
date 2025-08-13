class DefaultFormatter:
    @staticmethod
    def format(data, h2o_model):
        drop_cols = ['declined', 'mid_id', 'order_id', 'parent_processor', 'project', 'time_stamp']
        data = data.drop(columns=drop_cols, errors='ignore')  # errors='ignore' prevents error if column doesn't exist
        data = data.rename(columns={'destination_processor': 'processor'})
        lag_cols = [col for col in data.columns if "approval" in col.lower()]
        data[lag_cols] = (data[lag_cols].fillna(0) * 100).round(0).astype(int)
        if h2o_model:
            features = h2o_model.features
            target = h2o_model.targets
        else:
            features = list(set(data.columns) - set(['approved']))
            target = 'approved'
        return data, features, target


class V2Formatter:
    @staticmethod
    def format(data, h2o_model):
        lag_cols = ['order_total']
        data[lag_cols] = (data[lag_cols].astype(float)).round(0).astype(int)
        if h2o_model:
            features = h2o_model.features
            target = h2o_model.targets
        else:
            features = list(set(['cc_type', 'order_total', 'campaign_class', 'processor', 'iin']) - set(['approved']))
            target = 'approved'
        return data, features, target


class V3Formatter:
    @staticmethod
    def format(data, h2o_model):
        drop_cols = ['declined', 'mid_id', 'order_id', 'parent_processor', 'project', 'time_stamp']
        data = data.rename(columns={'destination_processor': 'processor'})
        data = data.drop(columns=drop_cols, errors='ignore')  # errors='ignore' prevents error if column doesn't exist
        lag_cols = [col for col in data.columns if "approval" in col.lower()]
        data[lag_cols] = (data[lag_cols].fillna(0) * 100).round(0).astype(int)
        data['order_total'] = data['order_total'].astype(float).round(0).astype(int)
        if h2o_model:
            features = h2o_model.features
            target = h2o_model.targets
        else:
            features = list(set(data.columns) - set(['approved']))
            target = 'approved'
        return data, features, target


class CV1Formatter:
    @staticmethod
    def format(data, h2o_model):
        drop_cols = ['declined', 'mid_id', 'order_id', 'project', 'parent_processor', 'bc_inferred', 'time_stamp']
        data = data.rename(columns={'destination_processor': 'processor'})

        data = data.drop(columns=drop_cols, errors='ignore')  # errors='ignore' prevents error if column doesn't exist
        lag_cols = [col for col in data.columns if "approval" in col.lower()]
        data[lag_cols] = (data[lag_cols].fillna(0) * 100).round(0).astype(int)
        #data['order_total'] = data['order_total'].astype(float).round(0).astype(int)
        if h2o_model:
            features = h2o_model.features
            target = h2o_model.targets
        else:
            features = list(set(data.columns) - set(['approved']))
            target = 'approved'
        return data, features, target



class DSV1:
    @staticmethod
    def format(data, h2o_model):
        drop_cols = ['project', 'first_message', 'decline_reason', 'approved_value', 'order_approved', 'decline_reason_', 'result_message','last_message', 'mid_id', 'parent_id', 'order_id', 'transaction_cost', 'chargeback_cost','',  'amount_refunded_to_date', 'order_appoved', 'maximum_attempt']
        data = data.drop(columns=drop_cols,
                         errors='ignore')  # errors='ignore' prevents error if column doesn't exist
        lag_cols = [col for col in data.columns if "approval" in col.lower()]
        data[lag_cols] = (data[lag_cols].fillna(0) * 100).round(0).astype(int)
        data['order_total'] = data['order_total'].astype(float).round(0).astype(int)
        if h2o_model:
            features = h2o_model.features
            target = h2o_model.targets
        else:
            features = list(set(data.columns) - set(['cycle_approved']))
            target = 'cycle_approved'
        return data, features, target


VERSIONS = {
    'capfill_naturals': {
        1: DefaultFormatter,
        2: V2Formatter,
        3: V3Formatter
    },
    'decline_salvage': {
      1: DSV1
    },
    'cascade_naturals': {
      1: CV1Formatter,
      2: CV1Formatter
    }

}