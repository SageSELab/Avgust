# Avgust
This repository holds the source code and data for the paper "Avgust: Automating Usage-Based Test Generation from Videos of App Executions". This paper was accepted in ESEC/FSE 2022 research track. You can find the accepted paper [here]().

Avgust is a human-in-the-loop technique that assists developers in generating usage-based tests for mobile apps by learning from videos of app usage.

1. The main code base is under [`code`](https://github.com/SageSELab/Avgust/tree/main/code) folder. You can find the code related to the 4 main stages of Avgust algorithm:
        - [`Step Extraction`](https://github.com/SageSELab/Avgust/tree/main/code/1_step_extraction): Processing app video to UI events
        - [`IR Classification`](https://github.com/SageSELab/Avgust/tree/main/code/2_ir_classification): Classifying UI screens and widgets
        - [`Model Generation`](https://github.com/SageSELab/Avgust/tree/main/code/3_model_generation): Generating app-independent usage models
        - [`Dynamic Test Generation`](https://github.com/SageSELab/Avgust/tree/main/code/4_dynamic_generation): Dynamically generating tests for new apps
2. the KNN and MLP screen and widget classifiers are under [`KNNClassifier`](https://github.com/SageSELab/Avgust/tree/main/KNNClassifier) and [`MLP_Screen_Widget_Classification`](https://github.com/SageSELab/Avgust/tree/main/MLP_Screen_Widget_Classification), respectively.
3. the definitions of canonical screens and canonical widgets are under [`IR`](https://github.com/SageSELab/Avgust/tree/main/IR) folder
4. the intermediate embeddings output by our classifiers are under [`embeddings`](https://github.com/SageSELab/Avgust/tree/main/embeddings) folder.
5. the IR Models, generated tests, and intermediate results (e.g., screenshots, cropped widgets, reverse engineered UI layout hierarchy) are under [`output`](https://github.com/SageSELab/Avgust/tree/main/output/models) folder.
6. the processed video frames, screenshots, cropped widgets, keyboard classifier's results of all the usages are under [`usage_data`](https://github.com/SageSELab/Avgust/tree/main/usage_data) folde.

This repository also contains the [`software requirements`]() and [`installation instructions`]() for the provided artifact.
