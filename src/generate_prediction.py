""" Imports """
import os
import argparse
import pandas as pd

from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree      import DecisionTreeClassifier
from sklearn.ensemble  import RandomForestClassifier
from sklearn.linear_model  import LogisticRegression
from sklearn.decomposition import PCA

def features_expert():
    df = pd.read_csv("../data/important_genes.csv", sep=",")
    return list(df["value"].unique())

def features_to_keep():
    df_important_genes = pd.read_csv("../data/important_genes.csv", sep=",")
    important_genes = list(df_important_genes["value"].unique())
    
    df_test = pd.read_csv("../data/normalized_test.csv")
    genes_test = list(df_test.columns)
    
    return [gene for gene in important_genes if gene in genes_test]
    

def load_dataset(path_dataset, training=True, features=None):
    # Open CSV
    df = pd.read_csv(path_dataset, sep=",")
    # Keep only common features
    if features is None:
        features = features_to_keep()
    X = df[features].values
    
    if training:
        # Get y for training
        y           = df["label"].values
        return X, y
    else:
        full_labels = df["full_label"].values
        return X, full_labels

def get_default_model(type_model):
    # Return model with default values
    if type_model == "KNN":
        return KNeighborsClassifier(2, weights="distance")
    if type_model == "DecisionTrees":
        return DecisionTreeClassifier()
    if type_model == "LogReg":
        return LogisticRegression(penalty='l2', solver='saga', max_iter=10000, multi_class='multinomial', C=1)
    if type_model == "RndForest":
        return RandomForestClassifier(n_estimators=100)
    else:
        raise Exception("Model type is not valid")

def preprocess_data(X_train, X_pred, model_type):
    if model_type == "KNN":
        pca = PCA(n_components=9)
        X_train = pca.fit_transform(X_train)
        X_pred  = pca.transform(X_pred)
    
    return X_train, X_pred


def main(model_type, saving_path, dataset_path, unlabeled_dataset_path):
    # Load datasets
    X_train, y_train    = load_dataset(dataset_path, training=True)
    X_pred, full_labels = load_dataset(unlabeled_dataset_path, training=False)
    
    # Get model
    model = get_default_model(model_type)

    # Preprocess data
    X_train, X_pred = preprocess_data(X_train, X_pred, model_type)

    # Train model
    model.fit(X_train, y_train)

    # Make predictions
    y_preds = model.predict(X_pred)
    y_proba = model.predict_proba(X_pred)

    # Create dataframe and save it
    df_predictions = pd.DataFrame()
    df_predictions["full_label"] = full_labels
    df_predictions["predicted"]  = y_preds
    df_predictions["proba_0"]    = y_proba[:,0]
    df_predictions["proba_1"]    = y_proba[:,1]
    df_predictions["proba_2"]    = y_proba[:,2]
    
    name_output = os.path.join(saving_path, model_type+"_preds.csv")
    df_predictions.to_csv(saving_path, index=False)


if __name__ == "__main__":
    # Managing the arguments
    
    ap = argparse.ArgumentParser()
    ap.add_argument("-model", "--model", required=True,
                    help="The model do to the predictions with KNN, DecisionTrees, LogReg, RndForest")    
    ap.add_argument("-saving_path", "--saving_path", required=False,
                    help="To path were to save the predictions")
    ap.add_argument("-dataset_path", "--dataset_path", required=False,
                    help="The path of the dataset to use in order to train the model")
    ap.add_argument("-unlabeled_dataset_path", "--unlabeled_dataset_path", required=False,
                    help="The path of the dataset to predict")

    args = vars(ap.parse_args())

    # Get arguments
    model_type  = args["model"]
    model_types = ["KNN", "DecisionTrees", "LogReg", "RndForest"]
    if model_type not in model_types:
        raise Exception("Model type is not valid, valid types are: " + str(model_types))
        exit()
    
    saving_path = args["saving_path"]

    # Defaults values
    if args["saving_path"] == None:
        dataset_path = "../data/predictions/"
    
    if args["dataset_path"] == None:
        dataset_path = "../data/normalized_train.csv"

    if args["unlabeled_dataset_path"] == None:
        unlabeled_dataset_path = "../data/normalized_test.csv"

    # Call main
    main(model_type, saving_path, dataset_path, unlabeled_dataset_path)
