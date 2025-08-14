from DrugAutoML.data_preprocess import DataPreprocessor
from DrugAutoML.featurization import Featurizer
from DrugAutoML.data_split import DataSplitter
from DrugAutoML.model_selection import ModelSelector
from DrugAutoML.model_finalization import ModelFinalization
from DrugAutoML.explainability import Explainability
from DrugAutoML.prediction import Predictor

def run_pipeline(config):
    """
    Full DrugAutoML pipeline:
    1) Preprocessing
    2) Featurization
    3) Data Splitting
    4) Model Selection
    5) Model Finalization
    6) Explainability (optional)
    7) Prediction (optional)
    """
    # Step 1 — Data Preprocessing
    preprocess_result = DataPreprocessor(config["preprocessing"]).run()
    preprocessed_df = preprocess_result.data

    # Step 2 — Featurization
    featurizer = Featurizer(config["featurization"])
    featurizer.run(preprocessed_df)
    featurized_df = featurizer.data

    # Step 3 — Data Splitting
    splitter = DataSplitter(config["splitting"])
    splitter.run(featurized_df)

    # Step 4 — Model Selection
    selector = ModelSelector(config["model_selection"])
    selector.run()

    # Step 5 — Model Finalization
    finalizer = ModelFinalization(config["model_finalization"])
    finalizer.run()

    # Step 6 — Explainability (optional)
    if "explainability" in config and config["explainability"]:
        explainer = Explainability(config["explainability"])
        explainer.run()

    # Step 7 — Prediction (optional)
    if "prediction" in config and config["prediction"]:
        predictor = Predictor(config["prediction"])
        predictor.run()

    return {
        "preprocessing": preprocess_result,
        "featurization": featurizer,
        "splitting": splitter,
        "model_selection": selector,
        "model_finalization": finalizer
    }

if __name__ == "__main__":
    import json
    import argparse

    parser = argparse.ArgumentParser(description="DrugAutoML Full Pipeline Runner")
    parser.add_argument("--config", required=True, help="Path to JSON config file")
    args = parser.parse_args()

    with open(args.config, "r") as f:
        config = json.load(f)

    run_pipeline(config)
