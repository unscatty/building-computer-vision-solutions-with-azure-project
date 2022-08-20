from time import sleep
from uuid import uuid4
from datetime import datetime
from .create_project import trainer, custom_vision_config

custom_project_id = custom_vision_config.custom_project.project_id
custom_project_name = custom_vision_config.custom_project.name

# Training the project
SLEEP_TIME = 30
print(f'Started project training for project {custom_project_name}, id: {custom_project_id}')

# Show time training started
training_started_at = datetime.now()
print(f"Training started: {training_started_at.strftime('%A, %B the %dth, %Y at %H:%M:%S ')}")

iteration = trainer.train_project(custom_project_id)

while (iteration.status != "Completed"):
    iteration = trainer.get_iteration(custom_project_id, iteration.id)
    print ("Training status: " + iteration.status)
    print (f"Waiting {SLEEP_TIME} seconds...")
    sleep(SLEEP_TIME)

training_finished_at = datetime.now()
print(f"Training finished: {training_finished_at.strftime('%A, %B the %dth, %Y at %H:%M:%S ')}")

# Show info about iterations
print(f'Iterations in project {custom_project_name}, id: {custom_project_id}')
iteration_list = trainer.get_iterations(custom_project_id)
for iteration_item in iteration_list:
    print(iteration_item)

# Show model performance statistics
print(f'Performance for iteration {iteration_list[0].id}')
model_perf = trainer.get_iteration_performance(custom_project_id, iteration_list[0].id)
print(model_perf.as_dict())

publish_iteration_name = custom_project_name + '-' + iteration_list[0].name

# # The iteration is now trained. Publish it to the project endpoint
print(f'Publishing iteration "{publish_iteration_name}" to project {custom_project_name}')
trainer.publish_iteration(custom_project_id, iteration.id, publish_iteration_name, custom_vision_config.prediction.resource_id)
print ("Done!")