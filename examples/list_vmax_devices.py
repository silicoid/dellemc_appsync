#!/usr/bin/python3

import argparse
import DellEMC_AppSync
import xml.etree.ElementTree as ET

cliargs = argparse.ArgumentParser(
    description="List VMAX/PowerMax devices created by AppSync")

cliargs.add_argument("-a", "--appsynchost", help="AppSync host", type=str,
                     required=True)
cliargs.add_argument("-u", "--user", help="AppSync user", type=str,
                     required=True)
cliargs.add_argument("-p", "--password", help="AppSync password", type=str,
                     required=True)
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

response = appsync.get("/types/storageSystem/instances")

if response.status_code != 200:
    print("Could not get storage arrays.")
    exit(1)
else:
    array_dom = ET.ElementTree(ET.fromstring(response.text))
    if args.verbose >= 3:
        ET.dump(array_dom)

    for array in array_dom.findall(".//storageSystem"):
        if args.verbose >= 1:
            print("Array:", array.find("displayName").text,
                  "ID:", array.find("id").text)

        # Get devices from array
        array_dev_response = appsync.get("/instances/managedStorageSystem::" +
                                         array.find("id").text +
                                         "/relationships/PoolCopyDevices")

        # If we couldn't retreive devices for an array continue
        if array_dev_response.status_code != 200:
            continue

        array_dev_dom = ET.ElementTree(ET.fromstring(array_dev_response.text))
        if args.verbose >= 3:
            ET.dump(array_dev_dom)

        for device in array_dev_dom.findall(".//vmaxDevice"):
            cap_gb = round(int(device.find("capacity").text) / 1073741824, 0)
            print(device.find("storageArrayId").text,
                  device.find("name").text,
                  device.find("id").text,
                  cap_gb, "GB",
                  "InUse:" + device.find("inUseForReplication").text)
