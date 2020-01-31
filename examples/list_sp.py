#!/usr/bin/python3

import argparse
import DellEMC_AppSync
import xml.etree.ElementTree as ET

cliargs = argparse.ArgumentParser(
    description="List AppSync SPs ")

cliargs.add_argument("-a", "--appsynchost", help="AppSync host", type=str,
                     required=True)
cliargs.add_argument("-u", "--user", help="AppSync user", type=str,
                     required=True)
cliargs.add_argument("-p", "--password", help="AppSync password", type=str,
                     required=True)
cliargs.add_argument("-i", "--sp_id", help="ID of service plan", type=str,
                     required=False)
cliargs.add_argument("-v", "--verbose", help="Verbose output. Add " +
                     "additional v to increase level.",
                     action="count", default=0)

args = cliargs.parse_args()

appsync = DellEMC_AppSync.DellEMC_AppSync(username=args.user,
                                          password=args.password,
                                          host=args.appsynchost,
                                          ssl=True,
                                          verify=False,
                                          verbose=args.verbose)

if args.sp_id is None:
    response = appsync.get("/types/servicePlan/instances")
    splist_dom = ET.ElementTree(ET.fromstring(response.text))

    if args.verbose >= 3:
        ET.dump(splist_dom)

    for sp in splist_dom.findall(".//servicePlan"):
        print("\"" + sp.find("name").text + "\" has ID:", sp.find("id").text)
else:
    response = appsync.get("/instances/servicePlan::" + args.sp_id)
    if response.status_code != 200:
        print("Requesting", args.sp_id, "failed")
    else:
        sp_dom = ET.ElementTree(ET.fromstring(response.text))
        for sp in sp_dom.findall(".//servicePlan"):
            print("ServicePlan:", sp.find("name").text)
            print("Display Name:", sp.find("displayName").text)
            print("Description:", sp.find("description").text)

        response = appsync.get("/instances/servicePlan::" + args.sp_id +
                               "/relationships/phases")
        sp_dom = ET.ElementTree(ET.fromstring(response.text))
        if args.verbose >= 3:
            ET.dump(sp_dom)

        for phase in sp_dom.findall(".//phase"):
            if phase.find("enabled").text == "false" and args.verbose == 0:
                continue
            print("")
            print(phase.find("displayName").text, "==> Enabled: ",
                  phase.find("enabled").text)

            for option in phase.findall("options/option"):
                if option.find("name").text == "expireKeepCopyCountStorage":
                    expire_dom = ET.ElementTree(
                        ET.fromstring(option.find("value").text))
                    for copy in expire_dom.findall(".//keepCopyCountList"):
                        print(copy.find("stoageTechnology").text, ":",
                              copy.find("keepCopyCount").text)
                else:
                    print(option.find("name").text, ":",
                          option.find("value").text)
