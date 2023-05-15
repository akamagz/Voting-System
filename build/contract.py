import os
from pyteal import *

def approval():
    handle_creation = Seq(
        App.globalPut(Bytes("Count1"), Int(0)),
        App.globalPut(Bytes("Count2"), Int(1)),
        App.globalPut(Bytes("Count3"), Int(2)),
        Return(Int(1))
    )

    handle_optin = Return(Int(0))

    handle_closeout = Return(Int(0))

    handle_updateapp = Return(Int(0))

    handle_deleteapp = Return(Int(0))

    scratchCount = ScratchVar(TealType.uint64)


    add1 = Seq(
        scratchCount.store(App.globalGet(Bytes("Count1"))), 
        App.globalPut(Bytes("Count1"), scratchCount.load() + Int(1)),
        Return(Int(1))
    )

    add2 = Seq(
        scratchCount.store(App.globalGet(Bytes("Count2"))), 
        App.globalPut(Bytes("Count2"), scratchCount.load() + Int(1)),
        Return(Int(1))
    )

    add3 = Seq(
        scratchCount.store(App.globalGet(Bytes("Count3"))), 
        App.globalPut(Bytes("Count3"), scratchCount.load() + Int(1)),
        Return(Int(1))
    )

    handle_noop = Seq(
        Assert(Global.group_size() == Int(1)),
        Cond(
            [Txn.application_args[0] == Bytes("Add1"), add1], 
            [Txn.application_args[0] == Bytes("Add2"), add2],
            [Txn.application_args[0] == Bytes("Add3"), add3]
        )
    )

    program = Cond(
        [Txn.application_id() == Int(0), handle_creation],
        [Txn.on_completion() == OnComplete.OptIn, handle_optin],
        [Txn.on_completion() == OnComplete.CloseOut, handle_closeout],
        [Txn.on_completion() == OnComplete.UpdateApplication, handle_updateapp],
        [Txn.on_completion() == OnComplete.DeleteApplication, handle_deleteapp],
        [Txn.on_completion() == OnComplete.NoOp, handle_noop]
    )
    return compileTeal(program, Mode.Application, version=5)

def clear():
    program = Return(Int(1))
    return compileTeal(program, Mode.Application, version=5)

appFile = open('approval.teal', 'w')
appFile.write(approval())
appFile.close()

clearFile = open('clear.teal', 'w')
clearFile.write(clear())
clearFile.close()
