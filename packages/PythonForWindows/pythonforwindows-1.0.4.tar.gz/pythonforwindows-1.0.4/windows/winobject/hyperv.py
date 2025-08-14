import windows


class HyperVWmiManager(object):
    def __init__(self):
        self.namespace = windows.system.wmi[r"Root\Virtualization\V2"]

    @property
    def computer_systems(self):
        return self.namespace.select("Msvm_ComputerSystem")

    @property
    def vms(self):
        # https://learn.microsoft.com/en-us/windows/win32/hyperv_v2/msvm-computersystem
        return [HyperVVM(x) for x in self.computer_systems if x["Caption"] == "Virtual Machine"]

    @property
    def svc(self):
        return self.namespace.select("Msvm_VirtualSystemManagementService")[0]

class HyperVVM(object):
    def __init__(self, wmi_vm):
        assert wmi_vm["__Class"] == "Msvm_ComputerSystem"
        self.obj = wmi_vm

    @property
    def name(self):
        return self.obj["ElementName"]

    def stop(self):
        inparam = self.obj.class_.get_method("RequestStateChange").inparam
        inparam["RequestedState"] = 3

    def request_state_change(self, state):
        res = self.obj.methods["RequestStateChange"](RequestedState=state)
        if res["ReturnValue"] == 4096:
            return self.obj.namespace.get_object(res["Job"])
        return 0

    def __repr__(self):
        return """<HyperVVM "{0}">""".format(self.name)
