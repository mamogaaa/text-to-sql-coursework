import pandas as pd
import argparse
from xmlrpc.server import SimpleXMLRPCServer

from dumb_extract_cat_features import get_dumb_feature_hash

wpns = pd.read_csv('data/wpns.csv')
wpns

items_categories = []
for ind, row in wpns[['type', 'translation']].iterrows():
    items_categories.append([row['type'], row['translation']])
items_categories

def get_data():
    return [
        {
            "id": 1,
            "sql_query": "select market_hash_name, sum(price)/sum(quantity) as mean_price from extended_steam_history_sellings where type = '{category}' group by market_hash_name order by mean_price desc limit {limit}",
            "templates": [
                "топ/рейтинг/покажи/_ {limit} самых/наиболее/_ дорогих скинов_в_категории_{category}/предметов_в_категории_{category}/{category} за_все_время/_",
                "какие скины_в_категории_{category}/предметы_в_категории_{category}/{category} были наиболее/самыми дорогими за_все_время/_"
            ],
            "possible_features_values": {
                "limit": [*range(1, 200, 4)],
                "category": items_categories
            }
        },
        {
            "id": 2,
            "sql_query": "select * from extended_steam_history_sellings where market_hash_name = '{market_hash_name}' limit 5000",
            "templates": [
                "открой/покажи/_ график_цены/график/динамика_цен/динамика скина/предмета/_ {market_hash_name}"
            ],
            "possible_features_values": {
                "market_hash_name": [get_dumb_feature_hash('market_hash_name')]
            },
        },
        {
            "id": 3,
            "sql_query": "select * from extended_steam_history_sellings where market_hash_name = '{market_hash_name}' and dateDiff('day', timestamp, now()) < {number_of_days} +200 limit 5000",
            "templates": [
                "открой/покажи/_ график_цены/график/динамика_цен/динамика скина/предмета/_ {market_hash_name} за_последние_{number_of_days}_дней/за_{number_of_days}_дней/за_{number_of_days}_д"
            ],
            "possible_features_values": {
                "market_hash_name": [get_dumb_feature_hash('market_hash_name')],
                "number_of_days": [*range(1, 60, 5)]
            }
        },
        {
            "id": 4,
            "sql_query": "select * from extended_steam_history_sellings where market_hash_name = '{market_hash_name}' and dateDiff('week', timestamp, now()) < {number_of_weeks} +60 limit 5000",
            "templates": [
                "открой/покажи/_ график_цены/график/динамика_цен/динамика скина/предмета/_ {market_hash_name} за_последние_{number_of_weeks}_недель/за_{number_of_weeks}_недель/за_{number_of_weeks}_н"
            ],
            "possible_features_values": {
                "market_hash_name": [get_dumb_feature_hash('market_hash_name')],
                "number_of_weeks": [*range(1, 20, 4)]
            }
        },
        {
            "id": 5,
            "sql_query": "select * from extended_steam_history_sellings where market_hash_name = '{market_hash_name}' and dateDiff('month', timestamp, now()) < {number_of_months} +5 limit 5000",
            "templates": [
                "открой/покажи/_ график_цены/график/динамика_цен/динамика скина/предмета/_ {market_hash_name} за_последние_{number_of_months}_месяцев/за_{number_of_months}_месяцев/за_{number_of_months}_м"
            ],
            "possible_features_values": {
                "market_hash_name": [get_dumb_feature_hash('market_hash_name')],
                "number_of_months": [*range(1, 30, 4)]
            }
        },

    ]

from model import Text2SQLDataset, Text2SQLModel

dataset = Text2SQLDataset.generate_by_templates(get_data())
train_dataset, test_dataset, val_dataset = dataset.train_test_val_split()
train_dataset.df.shape, test_dataset.df.shape, val_dataset.df.shape

market_hash_names = pd.read_csv('data/market_hash_names.csv')
market_hash_names = list(market_hash_names['market_hash_name'].unique())
model = Text2SQLModel(dumb_features_dict={ 'market_hash_name': market_hash_names })
model.fit(train_dataset, val_dataset)


def evaluate(req):
    results = model.evaluate([req])
    print(results)

    return {
        'results': next(
            map(
                lambda x: {
                    **x,
                    'intent_id': str(x['intent_id'])
                },
                results
            )
        )
    }

def main(args=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', '-p', type=int, default=3004, help='port (default "3004")')
    args = parser.parse_args(args)

    server = SimpleXMLRPCServer(('0.0.0.0', args.port))
    print("serving on 0.0.0.0:{}".format(args.port))
    server.register_introspection_functions()
    server.register_function(evaluate)
    server.serve_forever() 

if __name__ == '__main__':
    main()

