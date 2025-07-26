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
#f = open("exampleSCinput.json", "r")
#input = json.loads(f.read())
f = open("example_input_output/combined_manuf_in_var.json","r")
varInput = json.loads(f.read())

def constraints(o):
    # Accessing the total produced amounts from the model output
    prod1_total = o["services"]["combinedManuf"]["outFlow"]["prod1_manuf2"]["qty"]
    prod2_total = o["services"]["combinedManuf"]["outFlow"]["prod2_manuf2"]["qty"]

    # Verifying both model constraints and additional product conditions
    condition = prod1_total >= 1000 and prod2_total >= 2000
    return dgal.all([o["constraints"], condition])

optAnswer = dgal.min({
    "model": ams.combinedManuf,
    "input": varInput,
    "obj": lambda o: o["cost"],
    "constraints": constraints,
    "options": {"problemType": "mip", "solver":"glpk","debug": True}
})

optOutput = ams.combinedManuf(optAnswer["solution"])
dgal.debug("optOutput",optOutput)
dgal.debug("constraints", optOutput["constraints"])

output = {
#    "input":input,
#    "varInput":varInput,
    "optAnswer": optAnswer,
    "optOutput": optOutput
}
f = open("answers/outOptManuf.json","w")
#f.write(str(output))
f.write(json.dumps(output))
#f.write(str(output))

#print("\n dgal opt output \n", optAnswer)
#print(json.dumps(optAnswer))
