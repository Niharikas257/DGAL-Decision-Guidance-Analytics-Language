#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import json
import copy

sys.path.append("./lib")
import lib.dgalPy as dgal

import ams

dgal.startDebug()
#f = open("exampleSCinput.json", "r")
#input = json.loads(f.read())
f = open("example_input_output/combined_supply_in_var.json","r")
varInput = json.loads(f.read())

def constraints(o):
    mat1_total = o['services']['combinedSupply']['outFlow']['mat1_sup1']['qty'] + o['services']['combinedSupply']['outFlow']['mat1_sup2']['qty']
    mat2_total = o['services']['combinedSupply']['outFlow']['mat2_sup1']['qty'] + o['services']['combinedSupply']['outFlow']['mat2_sup2']['qty']

    # Defining the constraints
    constraint_mat1 = mat1_total >= 1000
    constraint_mat2 = mat2_total == 2000

    # Combining with existing constraints
    existing_constraints = o.get("constraints", True)

    # Use dgal.all to combine constraints
    return dgal.all([existing_constraints, constraint_mat1, constraint_mat2])


# Before Optimization call declaring in dictionary
optimization_parameters = {
    "model": ams.combinedSupply,
    "input": varInput,
    "obj": lambda o: o["cost"],
    "constraints": constraints,
    "options": {"problemType": "mip", "solver": "glpk", "debug": True}
}


# Optimization call
optAnswer = dgal.min(optimization_parameters)


if optAnswer.get("solution") != "none":
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
else:
    print("No valid solution was found.")
