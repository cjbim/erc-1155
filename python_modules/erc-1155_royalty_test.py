from web3 import Web3, HTTPProvider
import json
import utill
import solcx
import datetime
import os
version = solcx.install_solc('0.8.2') # 최초 1회에만 사용
'''
2022-11-15


'''
def erc1155_contract_deploy(web3, file_path, address, pk_key):
    '''
    컨트랙트 배포 함수
    :param web3: 이더리움 네트워크
    :param file_path: sol파일 경로
    :param address: 배포하는 사람의 주소값
    :param pk_key: 배포하는 사람의 pk값
    :param name: 컨트랙트 이름
    :param symbol: 컨트랙트 심볼
    :return: 컨트랙트 주소
    '''
    res = solcx.compile_files(
        [file_path],
        output_values=["abi", "bin"],
        solc_version="0.8.2"
    )
    abi = res[file_path+':MyNFT']['abi']
    with open(f'royaltyABI', 'w') as f:
        json.dump(abi, f)
    bin = res[file_path+':MyNFT']['bin']
    with open(f'royaltybin', 'w') as f:
        json.dump(bin, f)
    mycontract = web3.eth.contract(abi=abi, bytecode=bin)
    address = web3.toChecksumAddress(address)
    acct = web3.eth.account.privateKeyToAccount(pk_key)
    nonce = web3.eth.get_transaction_count(address)
    gas_price = utill.get_gas_price("average")
    print(gas_price)
    tx = mycontract.constructor( "TEST1155ROYALTY", "RYT").build_transaction(
        {
            "from": address,
            "nonce": nonce,
            "gasPrice": web3.toWei(gas_price, 'gwei')
        }
    )
    signed = acct.signTransaction(tx)
    tx_hash = web3.eth.send_raw_transaction(signed.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    return tx_receipt.contractAddress


def erc1155_setroyalty_minting(web3,erc1155_contract, owner_add, owner_pk,token_id,  amt, meta_data, fee_receiver, fee_ratio):
    '''
    발행 함수
    :param web3:
    :param erc1155_contract:
    :param owner_add:
    :param owner_pk:
    :param amt:
    :param meta_data:
    :return:
    '''
    owner_add = web3.toChecksumAddress(owner_add)
    nonce = web3.eth.get_transaction_count(owner_add)
    feeNumerator = int(fee_ratio * 10000)  # 2.5 % = 0.025 = 0.025 * 10000 = 250
    gas_estimate = erc1155_contract.functions.setroyalty_mint(meta_data, token_id, amt, fee_receiver, feeNumerator).estimate_gas({'from': owner_add})
    gas_price = utill.get_gas_price("average")
    tx = erc1155_contract.functions.mint(meta_data, token_id, amt, fee_receiver, feeNumerator).build_transaction(
        {
            'from': owner_add,
            'nonce': nonce,
            'gas': gas_estimate * 2,
            "gasPrice": web3.toWei(gas_price, 'gwei')*10
        }
    )
    signed_txn = web3.eth.account.sign_transaction(tx, owner_pk)
    amtTxHash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    gncHash = web3.eth.wait_for_transaction_receipt(amtTxHash)
    return gncHash

def erc1155_transfer(web3, erc1155_contract, sender_add, sender_pk, receiver_add, token_id, amt):
    '''
    단일 보내기 함수
    :param web3: 이더리움 네트워크
    :param erc1155_contract: 컨트랙트
    :param sender_add: 보내는 사람 주소
    :param sender_pv: 보내는 사람 pk
    :param receiver_Add: 받는 사람 주소
    :param token_id: 보낼 토큰id
    :param amt: 보낼 양
    :return:
    '''
    web3.toChecksumAddress(sender_add)
    web3.toChecksumAddress(receiver_add)
    nonce = web3.eth.get_transaction_count(sender_add)
    gas_estimate = erc1155_contract.functions.safeTransferFrom(sender_add, receiver_add, token_id, amt, "").estimate_gas({'from': sender_add})
    gas_price = utill.get_gas_price("average")
    tx = erc1155_contract.functions.safeTransferFrom(sender_add, receiver_add, token_id, amt, "").build_transaction(
        {
            'from': sender_add,
            'nonce': nonce,
            'gas': gas_estimate * 2,
            "gasPrice": web3.toWei(gas_price, 'gwei')
        }
    )
    signed_txn = web3.eth.account.sign_transaction(tx, sender_pk)
    amtTxHash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    gncHash = web3.eth.wait_for_transaction_receipt(amtTxHash)
    return gncHash


def erc1155_multisend(web3, erc1155_contract, sender_add, sender_pv, receiver_Adds, token_ids, amts):
    '''
    다중 보내기 함수
    :param web3: 이더리움 네트워크
    :param erc1155_contract: 컨트렉트
    :param sender_add: 보내는 사람 주소
    :param sender_pv: 보내는 사람 pk
    :param receiver_Adds: 받는 사람 주소
    :param token_ids: 보낼 토큰 id
    :param amts: 보낼 양
    :return: gncHash
    수수료 약 50프로 절감
    '''
    nonce = web3.eth.get_transaction_count(sender_add)
    web3.toChecksumAddress(sender_add)
    for i in range(len(receiver_Adds)):
        receiver_Adds[i] = web3.toChecksumAddress(receiver_Adds[i])
    gas_estimate = erc1155_contract.functions.multisend(sender_add, receiver_Adds, token_ids, amts).estimate_gas({'from': sender_add})
    print(gas_estimate)
    gas_price = utill.get_gas_price("average")
    tx = erc1155_contract.functions.multisend(sender_add, receiver_Adds, token_ids, amts).build_transaction(
        {
            'from': sender_add,
            'nonce': nonce,
            'gas': gas_estimate * 2,
            "gasPrice": web3.toWei(gas_price, 'gwei')
        }
    )
    signed_txn = web3.eth.account.sign_transaction(tx, sender_pv)
    amtTxHash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    gncHash = web3.eth.wait_for_transaction_receipt(amtTxHash)
    return gncHash

def erc1155_get_first_block(web3, erc1155_contract):
    '''
    use              : NFT 컨트랙트 첫거래 Block number를 가져옴
    input parameter  : 1. web3 : web3 네트워크 연결
                       2. mycontract : abi로 활성화한 컨트랙트 함수들
    output parameter : first_block_num
    '''
    myFilter = erc1155_contract.events.TransferSingle.createFilter(fromBlock=0)
    txs = myFilter.get_all_entries()

    try:
        first_block_num = txs[0].blockNumber
    except Exception as e:
        raise e

    return first_block_num


def erc1155_NFT_list(web3, erc1155_contract, startBlock, token_id=None):
    '''
    use              : 해당 컨트랙트 거래내역 조회후 리스트로 저장
    input parameter  : 1. web3 : web3 네트워크 연결
                       2. mycontract : abi로 활성화한 컨트랙트 함수들
                       3. startBlock : 탐색 시작 블록 넘버
                       4. token_id=None : 특정 token id 거래기록 (선택 사항)
    output parameter : tx_list
    '''

    tx_list = []
    if token_id is None:
        myFilter = erc1155_contract.events.TransferSingle.createFilter(fromBlock=startBlock)
    else:
        myFilter = erc1155_contract.events.TransferSingle.createFilter(fromBlock=startBlock, argument_filters={ 'id': token_id})
    txs = myFilter.get_all_entries()

    for tx in txs:
        tx_hash = (tx.transactionHash).hex()
        getblock = web3.eth.get_block(tx.blockNumber).timestamp
        date = datetime.datetime.fromtimestamp(int(getblock)).strftime('%Y-%m-%d %H:%M:%S')
        tx_data = {'from': tx.args['from'], 'to': tx.args['to'], 'id': tx.args['id'],'value': tx.args['value'], 'event': tx.event,'transactionHash': tx_hash, 'blockNumber': tx.blockNumber, 'date': date }
        tx_list.append(tx_data)
    return tx_list


def setRoyalties(web3, mycontract, owner_add, owner_pv,token_id, fee_reciever, feeNumerator):
    web3.toChecksumAddress(owner_add)
    web3.toChecksumAddress(fee_reciever)
    nonce = web3.eth.get_transaction_count(owner_add)
    feeNumerator = int(feeNumerator * 10000)    # 2.5 % = 0.025 = 0.025 * 10000 = 250
    gas_estimate = mycontract.functions.setRoyalties(token_id, fee_reciever,feeNumerator).estimate_gas({'from': owner_add})
    print(gas_estimate)
    gas_price = utill.get_gas_price("average")
    tx = mycontract.functions.setRoyalties(token_id, fee_reciever,feeNumerator).build_transaction(
        {
            'from': owner_add,
            'nonce': nonce,
            'gas': gas_estimate * 2,
            "gasPrice": web3.toWei(gas_price, 'gwei')
        }
    )
    signed_txn = web3.eth.account.sign_transaction(tx, owner_pv)
    amtTxHash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    gncHash = web3.eth.wait_for_transaction_receipt(amtTxHash)
    print(gncHash)
    return gncHash

def setDefaultRoyalties(web3, mycontract, owner_add, owner_pv, fee_reciever, feeNumerator):
    '''
    온체인에선 바꾸면 적용이 되지만 여러 market place 에서는 refresh가 안된다.
    보류
    '''
    web3.toChecksumAddress(owner_add)
    web3.toChecksumAddress(fee_reciever)
    nonce = web3.eth.get_transaction_count(owner_add)
    feeNumerator = int(feeNumerator * 10000)    # 2.5 % = 0.025 = 0.025 * 10000 = 250
    gas_estimate = mycontract.functions.setDefaultRoyalty( fee_reciever,feeNumerator).estimate_gas({'from': owner_add})
    print(gas_estimate)
    gas_price = utill.get_gas_price("average")
    tx = mycontract.functions.setDefaultRoyalty( fee_reciever,feeNumerator).build_transaction(
        {
            'from': owner_add,
            'nonce': nonce,
            'gas': gas_estimate * 2,
            "gasPrice": web3.toWei(gas_price, 'gwei')
        }
    )
    signed_txn = web3.eth.account.sign_transaction(tx, owner_pv)
    amtTxHash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    gncHash = web3.eth.wait_for_transaction_receipt(amtTxHash)
    print(gncHash)
    return gncHash

def royaltyinfo(web3, mycontract,token_id,amt):
    amt = amt * web3.toWei(1, 'ether')
    info = mycontract.functions.royaltyInfo(token_id,amt).call()
    fee = info[1] * web3.fromWei(1, 'ether')
    print(info)
    print(fee)



if __name__ == "__main__":
    web3 = utill.connectWeb3("infuracid", "goerli")
    address = ""
    pk_key = ""
    reciever_add = ""
    reciever_pk = ""
    mycontract = erc1155_contract_deploy(web3,  r"./contract/ERC1155royaltyfee2.sol", address, pk_key)
    print()
    erc1155_contract = utill.getContract(web3,mycontract,"royaltyABI")
    mint = erc1155_minting(web3, erc1155_contract, address, pk_key, 3, 20, "", "", 0.035)
    print(mint)
    #setRoyalties(web3, erc1155_contract, address, pk_key, 1, reciever_add, 0.035 )
    #setDefaultRoyalties(web3, erc1155_contract, address, pk_key, reciever_add, 0.035)
    #royaltyinfo(web3,erc1155_contract, 1, 1)
    #transfer = erc1155_transfer(web3, erc1155_contract, address, pk_key, reciever_add, 1, 5)
    #print(transfer)
    #multisend = erc1155_multisend(web3, erc1155_contract, address, pk_key, reciever_adds, token_ids, amts)
    #print(multisend)
    #first_block = erc1155_get_first_block(web3, erc1155_contract)
    #print(first_block)
    #lists = erc1155_NFT_list(web3, erc1155_contract, first_block,1)
    #print(lists)




