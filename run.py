import argparse
import yaml
import subprocess


DO_FILE = f"do_MIN.py"
PATH_TO_PARAMS = "Code/Python/Calibration/"
PATH_TO_FIGURES = "Code/Python/Figures/"
RESULTS_DIR = f"figures"

# Take the file as an argument
parser = argparse.ArgumentParser()
parser.add_argument(
    "config", help="A YAML config file for custom parameters for REMARKs"
)
args = parser.parse_args()


with open(args.config, "r") as stream:
    config_parameters = yaml.safe_load(stream)


dict_portfolio_keys = [
    "CRRA",
    "Rfree",
    "DiscFac",
    "T_age",
    "T_cycle",
    "T_retire",
    "LivPrb",
    "PermGroFac",
    "cycles",
    "PermShkStd",
    "PermShkCount",
    "TranShkStd",
    "TranShkCount",
    "UnempPrb",
    "UnempPrbRet",
    "IncUnemp",
    "IncUnempRet",
    "BoroCnstArt",
    "tax_rate",
    "RiskyAvg",
    "RiskyStd",
    "RiskyAvgTrue",
    "RiskyStdTrue",
    "RiskyCount",
    "RiskyShareCount",
    "aXtraMin",
    "aXtraMax",
    "aXtraCount",
    "aXtraExtra",
    "aXtraNestFac",
    "vFuncBool",
    "CubicBool",
    "AgentCount",
    "pLvlInitMean",
    "pLvlInitStd",
    "T_sim",
    "PermGroFacAgg",
    "aNrmInitMean",
    "aNrmInitStd",
]

parameters_update = [
    "from .params_init import dict_portfolio, time_params, Mu, Rfree, Std, det_income, norm_factor, age_plot_params, repl_fac, a, b1, b2, b3, std_perm_shock, std_tran_shock",
    "import numpy as np",
]
for parameter in config_parameters:
    for key, val in config_parameters[parameter].items():
        # check if it's in time_params
        if key in ["Age_born", "Age_retire", "Age_death"]:
            parameters_update.append(f"time_params['{key}'] = {val}")
            # changing time_params effect dict_portfolio elements too
            parameters_update.append(
                f"dict_portfolio['T_age'] = time_params['Age_death'] - time_params['Age_born'] + 1"
            )
            parameters_update.append(
                f"dict_portfolio['T_cycle'] = time_params['Age_death'] - time_params['Age_born']"
            )
            parameters_update.append(
                f"dict_portfolio['T_retire'] = time_params['Age_retire'] - time_params['Age_born'] + 1"
            )
            parameters_update.append(
                f"dict_portfolio['T_sim'] = (time_params['Age_death'] - time_params['Age_born'] + 1)*50"
            )
            # fix notches (income growth and more parameters depends on age parameters)
            age_varying_paramters = [
            "f = np.arange(time_params['Age_born'], time_params['Age_retire'] + 1, 1)",
            "f = a + b1*f + b2*(f**2) + b3*(f**3)",
            "det_work_inc = np.exp(f)",
            "det_ret_inc = repl_fac*det_work_inc[-1]*np.ones(time_params['Age_death'] - time_params['Age_retire'])",
            "det_income = np.concatenate((det_work_inc, det_ret_inc))",
            "gr_fac = np.exp(np.diff(np.log(det_income)))",
            "std_tran_vec = np.array([std_tran_shock]*(time_params['Age_death'] - time_params['Age_born']))",
            "std_perm_vec = np.array([std_perm_shock]*(time_params['Age_death'] - time_params['Age_born']))",
            "dict_portfolio['PermGroFac'] = gr_fac.tolist()",
            "dict_portfolio['pLvlInitMean'] = np.log(det_income[0])",
            "dict_portfolio['TranShkStd'] = std_tran_vec",
            "dict_portfolio['PermShkStd'] = std_perm_vec"
            ]
            for para_age in age_varying_paramters:
                parameters_update.append(para_age)
        # check if it's det_income
        elif key in ["det_income"]:
            parameters_update.append(f"det_income = np.array({val})")
            parameters_update.append("dict_portfolio['pLvlInitMean'] = np.log(det_income[0])")
        # check if it's in dict_portfolio
        elif key in dict_portfolio_keys:
            parameters_update.append(f"dict_portfolio['{key}'] = {val}")
        elif key in ["age_plot_params"]:
            parameters_update.append(f"age_plot_params = {val}")
        else:
            print("Parameter provided in config file not found")
    parameters_update.append(
                f"dict_portfolio['LivPrb'] = dict_portfolio['LivPrb'][(time_params['Age_born'] - 20):(time_params['Age_death'] - 20)]"
            )
    for i in parameters_update:
        print(i)
        print('\n')
    with open(f"{PATH_TO_PARAMS}params.py", "w") as f:
        for item in parameters_update:
            f.write("%s\n" % item)
    # restart parameter update list
    parameters_update = parameters_update[0:2]

    # remove previous figures from the REMARK
    subprocess.run( [f"rm {PATH_TO_FIGURES}*"], shell=True)

    # run the do_X file and get the results
    subprocess.run([f"ipython {DO_FILE}"], shell=True)

    # create a folder to store the figures for this parameter
    subprocess.run([f"mkdir -p {RESULTS_DIR}/figure_{parameter}" ], shell=True,)

    # copy the files created in figures to results
    subprocess.run([f"cp {PATH_TO_FIGURES}* {RESULTS_DIR}/figure_{parameter}/" ], shell=True,)

