#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import json
import copy
# replace path below with a path to aaa_dgalPy
sys.path.append("./lib")

import dgalPy as dgal
import ams

dgal.startDebug()

f = open("example_input_output/combined_transp_in_var.json","r")
varInput = json.loads(f.read())

def constraints(o):
    # Extracting total delivered amounts from the output
    mat1_delivered = o["services"]["combinedTransp"]["outFlow"]["mat1_manuf1"]["qty"]
    mat2_delivered = o["services"]["combinedTransp"]["outFlow"]["mat2_manuf1"]["qty"]

    # Verifying both model constraints and additional material delivery conditions
    condition = mat1_delivered >= 1000 and mat2_delivered >= 2000
    return dgal.all([o["constraints"], condition])
optAnswer = dgal.min({
    "model": ams.combinedTransp,
    "input": varInput,
    "obj": lambda o: o["cost"],
    "constraints": constraints,
    "options": {"problemType": "mip", "solver":"glpk","debug": True}
})
optOutput = ams.combinedTransp(optAnswer["solution"])
dgal.debug("optOutput",optOutput)
dgal.debug("constraints", optOutput["constraints"])

output = {
#    "input":input,
#    "varInput":varInput,
    "optAnswer": optAnswer,
    "optOutput": optOutput
}
f = open("answers/outOptTransp.json","w")
#f.write(str(output))
f.write(json.dumps(output))
#f.write(str(output))

#print("\n dgal opt output \n", optAnswer)
#print(json.dumps(optAnswer))
