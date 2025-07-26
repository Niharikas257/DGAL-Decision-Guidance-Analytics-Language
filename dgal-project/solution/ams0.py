import copy
import json
import importlib.util
import sys
# sys.path.append("../aaa_dgalPy")
sys.path.append("./lib")
# sys.path.append("/Users/alexbrodsky/Documents/OneDrive - George Mason University - O365 Production/aaa_python_code/aaa_dgalPy")
import dgalPy as dgal

# the following is a useful Boolean function returning True if all qty's in newFlow are non-negative
# and greater than or equal to the lower bounds (lb) in flow (inFlow or outFlow)
# replace below with correct implementation if you'd like to use it in analytic models below
def flowBoundConstraint(flow,newFlow):
    return True

#--------------------------------------------------------------------
#assumptions on input data
#1. root service inFlows and outFlows are disjoint
#2. every inFlow of every subService must have a corresponding root inFlow
#   and/or a corresponding subService outFlow (i.e., an inFlow of a subService can't
#   come from nowhere)
#3. every outFlow of every subService must have a corresponding root outFlow
#   and/or a corresponding subService inFlows (i.e., an outFlow of a subService can't
#  go nowhere)
#4. every root outFlow must have at least one corresponding subService outFlow
#5. every root inFlow must have at least one corresponding subService inFlow
#----------------------------------------------------------------
# you may want to use this template for combinedSupply(input), combindManuf(input)
# and combinedTransp(input) below

def computeMetrics(shared,root,services):
    type = services[root]["type"]
    inFlow = services[root]["inFlow"]
    outFlow = services[root]["outFlow"]

    if type == "supplier":
        return {root: supplierMetrics(services[root])}
    elif type == "manufacturer":
        return {root: manufMetrics(services[root])}
    elif type == "transport":
        return {root: transportMetrics(services[root],shared)}
    else:
        subServices = services[root]["subServices"]
        subServiceMetrics = dgal.merge([computeMetrics(shared,s,services) for s in subServices])
# replace below with correct cost computation
        cost = 1000

# replace below with computation of new InFlow and new OutFlow of the root service
    newInFlow = "TBD"
    newOutFlow = "TBD"
    inFlowConstraints = flowBoundConstraint(inFlow,newInFlow)
    outFlowConstraints = flowBoundConstraint(outFlow,newOutFlow)

# replace below with internal flow constraints
    internalSupplySatisfiesDemand = True

    constraints = dgal.all([ internalSupplySatisfiesDemand,
                            inFlowConstraints,
                            outFlowConstraints,
                            subServiceConstraints
                      ])
    rootMetrics = {
        root : {
            "type": type,
            "cost": cost,
            "constraints": constraints,
            "inFlow": newInFlow,
            "outFlow": newOutFlow,
            "subServices": subServices
        }
    }
    return dgal.merge([ subServiceMetrics , rootMetrics ])

# end of Compute Metrics function
# ------------------------------------------------------------------------------
def supplierMetrics(supInput):
    type = supInput["type"]
    inFlow = supInput["inFlow"]
    outFlow = supInput["outFlow"]

    cost = 0
    newOutFlow={}
    constraints_met=True

    for item_id, details in outFlow.items():
        qty=details["qty"]
        ppu=details["ppu"]
        lb=details.get("lb",0)
        item_cost=qty*ppu
        cost = cost+item_cost

        newOutFlow[item_id]={"qty":qty, "item":details["item"]}

        if qty<0 or qty<lb:
            constraints_met=False

    return {
        "type": type,
        "cost": cost,
        "constraints_met": constraints_met,
        "inFlow": dict(),
        "outFlow": newOutFlow
    }
#-------------------------------------------------------------------------------
def manufMetrics(manufInput):
    type = manufInput["type"]
    inFlow = manufInput["inFlow"]
    outFlow = manufInput["outFlow"]
    qtyInPer1out = manufInput["qtyInPer1out"]

    cost = 0
    newInFlow = {}
    newOutFlow = {}
    for a, b in outFlow.items():
        qty = b["qty"]
        ppu = b["ppu"]
        cost += qty * ppu

    for a, b in qtyInPer1out.items():
        for c, d in b.items():
            if a in outFlow:
                required_qty = outFlow[a]["qty"] * d
                if c in newInFlow:
                    newInFlow[c]["qty"] += required_qty
                else:
                    newInFlow[c] = {"qty": required_qty, "item": c.split("_")[0]}
    newOutFlow = {k: {"qty": v["qty"], "item": v["item"]} for k, v in outFlow.items()}

    inFlowConstraints = True
    for item, details in newInFlow.items():
        lb = inFlow.get(item, {}).get("lb", 0)
        if details["qty"] < lb:
            inFlowConstraints = False
            break

    outFlowConstraints = True
    for item, details in newOutFlow.items():
        lb = outFlow.get(item, {}).get("lb", 0)
        if details["qty"] < lb:
            outFlowConstraints = False
            break
    constraints = inFlowConstraints and outFlowConstraints

    return {
        "type": type,
        "cost": cost,
        "constraints": constraints,
        "inFlow": newInFlow,
        "outFlow": newOutFlow
    }

#--------------------------------------------------
def transportMetrics(transportInput, shared):
    type = transportInput["type"]
    inFlow = {item: {"qty": 0, "item": transportInput["inFlow"][item]["item"]} for item in transportInput["inFlow"]}
    outFlow = {item: {"qty": 0, "item": transportInput["outFlow"][item]["item"]} for item in transportInput["outFlow"]}
    pplbFromTo = transportInput["pplbFromTo"]
    orders = transportInput["orders"]
    total_cost = 0
    sourceLocations = set()
    destsPerSource = {}
    tempSourceDest = {}
    weightCostPerSourceDest = []

    for order in orders:
        in_item = order['in']
        out_item = order['out']
        sender = order['sender']
        recipient = order['recipient']
        qty = order['qty']
        item = in_item.split("_")[0]

        weight = shared["items"][item]["weight"] * qty

        inFlow[in_item]["qty"] += qty
        outFlow[out_item]["qty"] += qty

        source_loc = shared["busEntities"][sender]["loc"]
        dest_loc = shared["busEntities"][recipient]["loc"]
        sourceLocations.add(source_loc)
        if source_loc not in destsPerSource:
            destsPerSource[source_loc] = set()
        destsPerSource[source_loc].add(dest_loc)

        cost_per_lb = pplbFromTo[source_loc][dest_loc]
        shipment_cost = weight * cost_per_lb
        total_cost += shipment_cost

        if (source_loc, dest_loc) not in tempSourceDest:
            tempSourceDest[(source_loc, dest_loc)] = {"weight": weight, "cost": shipment_cost}
        else:
            tempSourceDest[(source_loc, dest_loc)]["weight"] += weight
            tempSourceDest[(source_loc, dest_loc)]["cost"] += shipment_cost

    for (source, dest), info in tempSourceDest.items():
        weightCostPerSourceDest.append({
            "source": source,
            "dest": dest,
            "weight": info["weight"],
            "cost": info["cost"]
        })

    destsPerSource = {k: list(v) for k, v in destsPerSource.items()}

    constraints = True

    return {
        "type": type,
        "cost": total_cost,
        "constraints": constraints,
        "inFlow": inFlow,
        "outFlow": outFlow,
        "debug": {
            "busEntities":shared["busEntities"],
            "sourceLocations": list(sourceLocations),
            "destsPerSource": destsPerSource,
            "weightCostPerSourceDest": weightCostPerSourceDest
        }
    }
#-------------------------------------------------------------------------------
def combinedSupply(input):
    total_cost = 0
    aggregated_outFlow = {}
    subServiceMetrics = {}

    for supplier_name in input["services"]["combinedSupply"]["subServices"]:
        supplier_data = input["services"][supplier_name]
        supplier_outFlow = supplier_data["outFlow"]
        supplier_cost = sum(item["qty"] * item["ppu"] for item in supplier_outFlow.values())

        total_cost += supplier_cost

        for item_key, item_value in supplier_outFlow.items():
            if item_key in aggregated_outFlow:
                aggregated_outFlow[item_key]["qty"] += item_value["qty"]
            else:
                aggregated_outFlow[item_key] = {"qty": item_value["qty"], "item": item_value["item"]}

        subServiceMetrics[supplier_name] = {
            "type": "supplier",
            "cost": supplier_cost,
            "constraints": True,
            "inFlow": {},
            "outFlow": {k: {"qty": v["qty"], "item": v["item"]} for k, v in supplier_outFlow.items()}
        }

    combined_supply_out = {
        "cost": total_cost,
        "constraints": True,
        "rootService": "combinedSupply",
        "services": {
            "combinedSupply": {
                "type": "composite",
                "cost": total_cost,
                "constraints": True,
                "inFlow": {},
                "outFlow": aggregated_outFlow,
                "subServices": input["services"]["combinedSupply"]["subServices"],
                "debug": {
                    "flowKeys": list(aggregated_outFlow.keys()),
                    "subServiceMetrics": subServiceMetrics,
                    "subServicesFlowSupply": {k: v["qty"] for k, v in aggregated_outFlow.items()},
                    "subServicesFlowDemand": {k: 0 for k in aggregated_outFlow},
                    "inFlowKeys": [],
                    "outFlowKeys": list(aggregated_outFlow.keys()),
                    "internalFlowKeys": None,
                    "internalSupplySatisfiesDemand": True,
                    "inFlowConstraints": True,
                    "outFlowConstraints": True,
                    "subServiceConstraints": True
                }
            },
            **subServiceMetrics

        }
    }

    return combined_supply_out
#-------------------------------------------------------------------------------

import json

def newflowBoundConstraint(newService_inFlow, newService_outFlow):
    result = False

    if newService_outFlow.keys() == newService_inFlow.keys():
        result = True
    else:
        return result

    for key in newService_inFlow.keys():
        if newService_inFlow[key]["qty"] != newService_outFlow[key]["qty"]:
            return False

    return True

def Merge(dict1, dict2):
    return(dict2.update(dict1))

import copy

def combinedManuf(input):
    root_service = input["rootService"]
    services = input["services"]
    sub_services = services["combinedManuf"]["subServices"]
    total_cost = 0

    newServices = copy.deepcopy(services)
    sub_services_matrics = {}
    inFlow_collection = {}
    outFlow_collection = {}
    '''debug = {
        "flowKeys": [],
        "subServiceMetrics": {},
        "subServicesFlowSupply": {},
        "subServicesFlowDemand": {},
        "inFlowKeys": [],
        "outFlowKeys": [],
        "internalFlowKeys": [],
        "internalSupplySatisfiesDemand": True,
        "inFlowConstraints": True,
        "outFlowConstraints": True,
        "subServiceConstraints": True
    }'''

    qty_map = {}

    for subserv in sub_services:
        inflow = newServices[subserv]["inFlow"]
        outflow = newServices[subserv]["outFlow"]

        current_cost = 0

        if subserv not in sub_services_matrics:
            sub_services_matrics[subserv] = {
                "type": "manufacturer",
                "cost": 0,
                "constraints": None,
                "inFlow": {},
                "outFlow": {}
            }

        for key in outflow.keys():

            qty = outflow[key]["qty"]
            ppu = outflow[key]["ppu"]

            if key not in qty_map:
                qty_map[key] = qty

            current_cost += qty * ppu

            if key not in sub_services_matrics[subserv]["outFlow"]:
                sub_services_matrics[subserv]["outFlow"][key] = {"qty": 0, "item": outflow[key]["item"]}
                outFlow_collection[key] = {"qty": 0, "item": outflow[key]["item"]}

            sub_services_matrics[subserv]["outFlow"][key]["qty"] += qty
            outFlow_collection[key]["qty"] += qty

        sub_services_matrics[subserv]["cost"] = current_cost
        total_cost += current_cost


        for item_key in newServices[subserv]["qtyInPer1out"].keys():
            for manuf in newServices[subserv]["qtyInPer1out"][item_key].keys():
                qtyInPer1out = newServices[subserv]["qtyInPer1out"][item_key][manuf]

                if manuf not in sub_services_matrics[subserv]["inFlow"]:
                    sub_services_matrics[subserv]["inFlow"][manuf] = {"qty": 0, "item": inflow[manuf]["item"]}
                    inFlow_collection[manuf] = {"qty": 0, "item": inflow[manuf]["item"]}

                sub_services_matrics[subserv]["inFlow"][manuf]["qty"] += qtyInPer1out * qty_map[item_key]
                inFlow_collection[manuf]["qty"] += qtyInPer1out * qty_map[item_key]

        sub_services_matrics[subserv]["constraints"] = all([flowBoundConstraint(inflow, sub_services_matrics[subserv]["inFlow"]), flowBoundConstraint(outflow, sub_services_matrics[subserv]["outFlow"])])

    constraints = newflowBoundConstraint(sub_services_matrics["tier2manuf"]["inFlow"], sub_services_matrics["tier1manuf"]["outFlow"]) and sub_services_matrics["tier1manuf"]["constraints"] and sub_services_matrics["tier2manuf"]["constraints"]


    newServices["combinedManuf"]["cost"] = total_cost
    newServices["combinedManuf"]["constraints"] = constraints

    inFlow_keys = []
    outFlow_keys = []

    for inflow_key in newServices["combinedManuf"]["inFlow"].keys():
        inFlow_keys.append(inflow_key)
        newServices["combinedManuf"]["inFlow"][inflow_key]["qty"] = inFlow_collection[inflow_key]["qty"]
        del newServices["combinedManuf"]["inFlow"][inflow_key]["lb"]

    for outflow_key in newServices["combinedManuf"]["outFlow"].keys():
        outFlow_keys.append(outflow_key)
        newServices["combinedManuf"]["outFlow"][outflow_key]["qty"] = outFlow_collection[outflow_key]["qty"]
        del newServices["combinedManuf"]["outFlow"][outflow_key]["lb"]

    #newServices["combinedManuf"]["debug"] = debug
    #newServices["combinedManuf"]["subServiceMetrics"] = sub_services_matrics
    #Merge(newServices,sub_services_matrics)

    del newServices["tier1manuf"]
    del newServices["tier2manuf"]
    newServices.update(sub_services_matrics)

    #newServices["combinedManuf"]["inFlowKeys"] = inFlow_keys
    #newServices["combinedManuf"]["outFlowKeys"] = outFlow_keys

    #debug["subServiceMetrics"] = sub_services_matrics
    #debug["inFlowKeys"] = inFlow_keys
    #debug["outFlowKeys"] = outFlow_keys

    result = {
        "cost": total_cost,
        "constraints": constraints,
        "rootService": root_service,
        "services": newServices
    }

    return result
#-------------------------------------------------------------------------------
import collections

def combinedTransp(input_data):
    root_service = input_data["rootService"]
    services = input_data["services"]
    sub_services = services["combinedTransport"]["subServices"]
    shared = input_data["shared"]

    combinedTransport = {
        "type": "composite",
        "cost": 0,
        "constraints": True,
        "inFlow": {},
        "outFlow": {},
        "subServices": sub_services

    }

    detailed_services = {}

    for subserv in sub_services:
        service = services[subserv]
        orders = service.get("orders", [])
        pplbFromTo = service.get("pplbFromTo", {})

        serviceMetrics = {
            "type": service["type"],
            "cost": 0,
            "constraints": True,
            "inFlow": {},
            "outFlow": {}

        }

        for order in orders:
            in_flow_key = order["in"]
            out_flow_key = order["out"]
            in_item = services[subserv]["inFlow"][in_flow_key]["item"]
            item_weight = shared["items"][in_item]["weight"]
            sender_loc = shared["busEntities"][order["sender"]]["loc"]
            recipient_loc = shared["busEntities"][order["recipient"]]["loc"]
            order_cost = order["qty"] * item_weight * pplbFromTo[sender_loc][recipient_loc]

            serviceMetrics["cost"] += order_cost
            combinedTransport["cost"] += order_cost

            update_flow(serviceMetrics["inFlow"], in_flow_key, order["qty"], in_item)
            update_flow(serviceMetrics["outFlow"], out_flow_key, order["qty"], in_item)
            update_flow(combinedTransport["inFlow"], in_flow_key, order["qty"], in_item)
            update_flow(combinedTransport["outFlow"], out_flow_key, order["qty"], in_item)

            src_dest_pair = f"{sender_loc}-{recipient_loc}"
            #serviceMetrics["debug"]["weightCostPerSourceDest"][src_dest_pair]["weight"] += order["qty"] * item_weight
            #serviceMetrics["debug"]["weightCostPerSourceDest"][src_dest_pair]["cost"] += order_cost

            #serviceMetrics["debug"]["sourceLocations"].append(sender_loc)
            #if sender_loc != recipient_loc:
                #serviceMetrics["debug"]["destsPerSource"][sender_loc].append(recipient_loc)

        #serviceMetrics["debug"]["weightCostPerSourceDest"] = [{**v, "source": k.split('-')[0], "dest": k.split('-')[1]} for k, v in serviceMetrics["debug"]["weightCostPerSourceDest"].items()]
        #combinedTransport["debug"]["subServiceMetrics"][subserv] = serviceMetrics

        detailed_services[subserv] = serviceMetrics

    result = {
        "cost": combinedTransport["cost"],
        "constraints": combinedTransport["constraints"],
        "rootService": root_service,
        "services": {
            "combinedTransport": combinedTransport,
            **detailed_services
        }
    }

    return result

def update_flow(flow_dict, key, qty, item):
    if key not in flow_dict:
        flow_dict[key] = {"qty": 0, "item": item}
    flow_dict[key]["qty"] += qty
#----------------------------------
