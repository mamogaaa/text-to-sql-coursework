


from model import Text2SQLDataset
dataset = Text2SQLDataset.generate_by_templates([
    {
        "id": 5,
        "sql_query": "select * from cats where color = '{color}' ORDER BY age DESC",
        "templates": [
            "покажи/_ список самых/наиболее старых котов/кошек {color} цвета"
        ],
        "possible_features_values": {
            "color": [
                ["red", "красного", "алого"],
                ["black", "черного"]
            ]
        }
    }
])
dataset.df.head()

