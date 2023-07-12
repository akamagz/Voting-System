import os
from pyteal import *

def approval():
    handle_creation = Seq(
        App.globalPut(Bytes("Count1"), Int(0)),
        App.globalPut(Bytes("Count2"), Int(0)),
        App.globalPut(Bytes("Count3"), Int(0)),
        Return(Int(1))
    )

    handle_optin = Return(Int(1))

    handle_closeout = Return(Int(1))

    handle_updateapp = Return(Int(0))

    handle_deleteapp = Return(Int(0))

    scratchCount = ScratchVar(TealType.uint64)
    voted = App.localGetEx(Int(0), App.id(), Bytes("voted"))
    voted_accounts = App.globalGetEx(Int(0), Bytes("voted_accounts"))

    def add_count(count_key):
        return Seq(
                voted,
                If(voted.hasValue(), Return(Int(0))),
                scratchCount.store(App.globalGet(count_key)),
                App.globalPut(count_key, scratchCount.load() + Int(1)),
                App.localPut(Int(0), Bytes("voted"), Int(1)),
                App.globalPut(Bytes("voted_accounts"), Txn.sender()),
                Return(Int(1))
        )

    def account_has_voted():
        return Seq(
            voted_accounts,
            If(
                voted_accounts.hasValue(),
                Return(Int(0))
            )
        )

    check_vote = Seq(
            voted,
            If(voted.hasValue(), Return(Int(0))),
            account_has_voted(),
            If(voted_accounts.hasValue(), Return(Int(0))),
            add_count(Bytes("Count1")),
            add_count(Bytes("Count2")),
            add_count(Bytes("Count3")),
            App.localPut(Int(0), Bytes("voted"), Int(1)),
            App.globalPut(Bytes("voted_accounts"), Txn.sender()),
            Return(Int(1)) 
    )

    handle_noop = Seq(
        Assert(Global.group_size() == Int(1)),
        Cond(
            [Txn.application_args[0] == Bytes("Add1"), add_count(Bytes("Count1"))],
            [Txn.application_args[0] == Bytes("Add2"), add_count(Bytes("Count2"))],
            [Txn.application_args[0] == Bytes("Add3"), add_count(Bytes("Count3"))],
            [Txn.application_args[0] == Bytes("vote"), check_vote]
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
