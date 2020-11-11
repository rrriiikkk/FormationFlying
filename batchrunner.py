'''
# =============================================================================
# When running this file the batchrunner will be used for the model. 
# No visulaization will happen.
# =============================================================================
'''
from mesa.batchrunner import BatchRunner
from formation_flying.model import FormationFlying
from formation_flying.parameters import model_params, max_steps, n_iterations, model_reporter_parameters, agent_reporter_parameters, variable_params


batch_run = BatchRunner(FormationFlying,
                            fixed_parameters=model_params,
                            variable_parameters=variable_params,
                            iterations=n_iterations,
                            max_steps=max_steps,
                            model_reporters=model_reporter_parameters,
                            agent_reporters=agent_reporter_parameters
                            )

batch_run.run_all()

run_data = batch_run.get_model_vars_dataframe()
#run_data.head()

#print((run_data["Real saved fuel"] - run_data["Total saved potential saved fuel"])/ run_data["Total Fuel Used"])
data_of_interest = run_data[["negotiation_method",
                             "communication_range",
                             "Total planned Fuel",
                             "Real saved fuel",
                             "Total planned flight time",
                             "Total flight delay",
                             "Number of flights without formation",
                             "Average time to form formation"]]
first_value_data = data_of_interest.head(n_iterations)
second_value_data = data_of_interest.iloc[n_iterations + 1 : (2 * n_iterations), : ]
last_value_data = data_of_interest.tail(n_iterations)

print(first_value_data.mean(skipna = True))
print(second_value_data.mean(skipna = True))
print(last_value_data.mean(skipna = True))


