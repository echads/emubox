import logging
import os
import time
import traceback
import zipfile

import gevent.monkey
from gevent.lock import BoundedSemaphore

import VMStateManager.vbox_monitor
from manager_constants import CHECKOUT_TIME, VBOX_PROBETIME
from Workshop_Queue import Workshop_Queue
from Workshop_Unit import Workshop_Unit

gevent.monkey.patch_all()
aggregatedInfo = []
availableWorkshops = []
unitsOnHold = []
aggregatedInfoSem = BoundedSemaphore(1)


def cleanup():
    logging.info("Cleaning up webdata aggregator...")
    try:

        logging.info("Clean up complete. Exiting...")
    except Exception as e:
        logging.error("Error during cleanup"+str(e))


def getAvailableUnits():
    availableUnits = []
    getGroupToVms = VMStateManager.vbox_monitor.getGroupToVms().copy()
    while(getGroupToVms):
        unit = getGroupToVms.popitem()
        if VMStateManager.vbox_monitor.unitIsAvailable(unit[1]):
            workshopName = unit[0].split('/')[1]
            rdp_files = getRDPPath(unit, workshopName)
            rdesktop_files = getRDesktopPath(unit, workshopName)
            if len(rdp_files) and (len(rdp_files) == len(rdesktop_files)):
                availableUnits.append(Workshop_Unit(workshopName, unit[1], rdp_files, rdesktop_files))
    return availableUnits


def aggregateData():
    """ Communicates with VBox Manager to gather and consolidate virtual machine information into Workshop Units """
    global aggregatedInfo
    global availableWorkshops

    while True:
        try:
            # should scan file system and then aggregate any information at the unit level
            availableUnits = getAvailableUnits()
            aggregatedInfoSem.wait()
            aggregatedInfoSem.acquire()
            for unit in availableUnits:
                workshopName = unit.workshopName
                workshopExists = False
                for workshop in availableWorkshops:
                    if workshopName == workshop.workshopName:
                        workshopExists = True
                        break
                if not workshopExists:
                    filesPaths = []
                    materialsPath = os.path.join("WorkshopData", workshopName, "Materials")
                    if os.path.isdir(materialsPath):
                        files = os.listdir(materialsPath)
                        for file in files:
                            if os.path.isfile(os.path.join(materialsPath, file)):
                                filesPaths.append((os.path.join(materialsPath, file).replace('\\', '/'), file))
                    curr_workshop_queue = Workshop_Queue(workshopName, filesPaths)
                    curr_workshop_queue.q.put(unit)
                    availableWorkshops.append(curr_workshop_queue)
                elif workshopExists:
                    workshop_queue = filter(lambda x: x.workshopName == workshopName, availableWorkshops)[0]
                    if unit not in workshop_queue.q.queue and unit not in unitsOnHold:
                        workshop_queue.q.put(unit)
            time.sleep(VBOX_PROBETIME)
            for workshop in availableWorkshops:
                workshop.q.queue.clear()
            aggregatedInfoSem.release()
        except Exception as e:
            logging.error("AGGREGATION: An error occurred: " + str(e))
            traceback.print_exc()
            exit()
            time.sleep(VBOX_PROBETIME)


def getAggregatedInfo():
    """ Returns: List of Workshop Units that are aggregated from the VBox Monitor. """
    #aggregatedInfoSem.wait()
    return aggregatedInfo


def getAvailableWorkshops():
    """ Returns: List of Workshop objects whose queues contain Workshop Units that are "Available". """
    return availableWorkshops


def checkoutUnit(unit):
    time.sleep(CHECKOUT_TIME)
    unitsOnHold.remove(unit)


def putOnHold(unit):
    unitsOnHold.append(unit)


def getRDPPath(unit, workshopName):
    rdpPaths = []
    for vm in unit[1]:
        if VMStateManager.vbox_monitor.vms[vm]["vrde"]:
            rdpPath = os.path.join("WorkshopData", workshopName, "RDP",
                               VMStateManager.vbox_monitor.vms[vm]["name"] + "_" +
                                       VMStateManager.vbox_monitor.vms[vm]["vrdeproperty[TCP/Ports]"] +
                                       ".rdp").replace('\\', '/')
            rdpPaths.append(rdpPath)
    return rdpPaths


def getRDesktopPath(unit, workshopName):
    rdesktopPaths = []
    for vm in unit[1]:
        if VMStateManager.vbox_monitor.vms[vm]["vrde"]:
            rdesktopPath = os.path.join("WorkshopData", workshopName, "RDP",
                                   VMStateManager.vbox_monitor.vms[vm]["name"] + "_" +
                                   VMStateManager.vbox_monitor.vms[vm]["vrdeproperty[TCP/Ports]"] +
                                   ".sh").replace('\\', '/')
            rdesktopPaths.append(rdesktopPath)
    return rdesktopPaths


''' 
    zip_files:
        @src: Iterable object containing one or more element
        @dst: filename (path/filename if needed)
        @arcname: Iterable object containing the names we want to give to the elements in the archive (has to correspond to src) 
'''
def zip_files(src, dst, arcname=None):
    zip_ = zipfile.ZipFile(dst, 'w')
    for i in range(len(src)):
        if arcname is None:
            zip_.write(src[i], os.path.basename(src[i]), compress_type = zipfile.ZIP_DEFLATED)
        else:
            zip_.write(src[i], arcname[i], compress_type = zipfile.ZIP_DEFLATED)
    zip_.close()
