#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import json
import copy
# replace path below with a path to aaa_dgalPy
# sys.path.append("/Users/alexbrodsky/Documents/OneDrive - George Mason University - O365 Production/aaa_python_code")
#sys.path.append(r'//K:/SEM-3/CS787/Assignment/HW-2/cs787_ha2_supp_manuf_transp_sn_template /cs787_ha2_supp_manuf_transp_sn_template/lib/')

#import aaa_dgalPy.lib.dgalPy as dgal
sys.path.append("./lib")

import dgalPy as dgal
import ams

dgal.startDebug()
#f = open("exampleSCinput.json", "r")
#input = json.loads(f.read())
f = open("example_input_output/combined_supply_in_var.json","r")
varInput = json.loads(f.read())

def constraints(o):
    # Extract model-wide constraints status
    model_constraints_met = o["constraints"]
    mat1_sup1_value = o['services']['combinedSupply']['outFlow']['mat1_sup1']['qty']
    mat1_sup2_value = o['services']['combinedSupply']['outFlow']['mat1_sup2']['qty']
    mat2_sup1_value = o['services']['combinedSupply']['outFlow']['mat2_sup1']['qty']
    mat2_sup2_value = o['services']['combinedSupply']['outFlow']['mat2_sup2']['qty']

    # Calculate total supplied amounts of mat1 and mat2
    total_mat1 = mat1_sup1_value + mat1_sup2_value
    total_mat2 = mat2_sup1_value + mat2_sup2_value

    # Define additional constraints based on supplied amounts
    if total_mat1 >= 1000 and total_mat2 == 2000:
        print("Constraints met")
        additional_constraints_met=True
    else:
        print("Constraints not met")
        additional_constraints_met=False

    # Combine model constraints with additional constraints
    all_constraints_met = model_constraints_met and additional_constraints_met

    return all_constraints_met


optAnswer = dgal.min({
    "model": ams.combinedSupply,
    "input": varInput,
    "obj": lambda o: o["cost"],
    "constraints": constraints,
    "options": {"problemType": "mip", "solver":"glpk","debug": True}
})
print("Optimized cost:", opt_answer["solution"]["cost"])
optOutput = ams.combinedSupply(optAnswer["solution"])
dgal.debug("optOutput",optOutput)
dgal.debug("constraints", optOutput["constraints"])

output = {
#    "input":input,
#    "varInput":varInput,
    "optAnswer": optAnswer,
    "optOutput": optOutput
}
f = open("answers/outOptSupply.json","w")
f.write(json.dumps(output))
