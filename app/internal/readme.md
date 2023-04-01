# Coding convention

## Celery
- every different tasks should has base = BaseTasks define in base, it handle slack notify error when something comes up
- each tasks should be defined in their folder
- tasks.py in the outmost celery folder should contains entry point of each tasks
- tasks naming should be prefix with task_
- tasks currently only config to run at specific time so no need to define constants. If any further usage of one tasks comes up, we should define a new crontab file
- to prevent circular import, any tasks on_after_configure.connect should be import in that function
- use celery auto discover tasks for periodic tasks

## DAO (data access object)
- new model must be import in init.py to create mapper for sqlalchemy
- any model import except basemodel should be in if type_checking to prevent circular mapping

## Model
each model should have 3 require properties:
1. data loader: handle loading training data, it should handle preprocess training data, and modified input for prediction in case user input might different from what model input data should be
1. output: output class that should implement get value, currently we only implement count for mosquitto count output so currently is hardcode, but any further usage should implement this class.
1. metrics provider: handle any further custom metrics we want, it should has an output instance in get custom metrics and use get value to load custom output

currently we do not use any test train split to validate so our model does not has it, our probability method should not use it too so if any, but should be separate it from data loader
currently we only have 1 negative binomial type 2 model so every class is define in same file with their abstract base class, if any further model usage comes up, we should split it into base file in outmost model folder and each folder will implement their specific module