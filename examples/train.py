

from model import Text2SQLModel

train_dataset, test_dataset, val_dataset = dataset.train_test_val_split()
model = Text2SQLModel(dumb_features_dict={ 'my_dumb_feature': ['dumb1', 'dumb2'] })
model.fit(train_dataset, val_dataset)


