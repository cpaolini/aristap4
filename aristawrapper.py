#aristawrapper
#author: David Korder

# import importlib.util
# import sys
# spec = importlib.util.spec_from_file_location("BfRtStubWrapper", "./BfRunTimeWrapper.py")
# foo = importlib.util.module_from_spec(spec)
# sys.modules["BfRtStubWrapper"] = foo
# spec.loader.exec_module(foo)
# foo.MyClass()


#!/usr/bin/env python
from BfRunTimeWrapper import BfRtStubWrapper
from bfrt_grpc import bfruntime_pb2

stubWrapper = BfRtStubWrapper("127.0.0.1:5555", "custom_switch_16", "/mnt/flash/custom_profiles/custom_switch_16/bf-rt.json")
stubWrapper.setUp()
target = stubWrapper.Target(device_id=0, pipe_id=0xffff, direction=0xff, prsr_id=0xff)

try:
    stubWrapper.set_entry_scope_table_attribute( target, "SwitchIngress.test_table", predefined_pipe_scope_val=bfruntime_pb2.Mode.ALL)
    #stubWrapper.set_entry_scope_table_attribute( target, "SwitchIngress.test_table")
    stubWrapper.insert_table_entry(target, "SwitchIngress.test_table", [stubWrapper.KeyField("ig_intr_md.ingress_port", stubWrapper.to_bytes(215, 2))], "SwitchIngress.test_action2", [])
    
    #Read the entry back
    resp = stubWrapper.get_table_entry(target,"SwitchIngress.test_table",[stubWrapper.KeyField("ig_intr_md.ingress_port",stubWrapper.to_bytes(215,2))],{})
    entry_iter = stubWrapper.bfRuntimeTest.parseEntryGetResponse(resp)
    
    for i in entry_iter:
        print(i)

finally:
    stubWrapper.tearDown()