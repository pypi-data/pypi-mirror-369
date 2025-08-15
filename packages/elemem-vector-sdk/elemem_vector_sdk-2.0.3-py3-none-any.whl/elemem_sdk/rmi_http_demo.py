import requests
import json

BASE_URL = "http://192.168.0.166:7000/elemem.rmi.ResourceManagerService/"

def test_add_card(cardid, card_dna):
    url = f"{BASE_URL}/AddCard"
    data = {
        "host_id": "192.168.0.51:8000",
        "cardid": cardid,
        "card_dna": card_dna,
    }
    resp = requests.post(url, json=data)
    print("AddCard:", resp.status_code, resp.text)

def test_allocate_columns():
    url = f"{BASE_URL}/AllocateColumns"
    data = {
        "index_name": "test_index",
        "bytes_per_vec": 128,
        "vec_size": 10
    }
    resp = requests.post(url, json=data)
    print("AllocateColumns:", resp.status_code, resp.text)

def test_allocate_ddr():
    url = f"{BASE_URL}/AllocateDDR"
    data = {
        "index_name": "test_alloc_ddr_index",
        "bytes_per_vec": 128,
        "vec_size": 10
    }
    resp = requests.post(url, json=data)
    print("AllocateDDR:", resp.status_code, resp.text)

def test_release_columns():
    url = f"{BASE_URL}/ReleaseColumns"
    data = {
        "index_name": "test_alloc_ddr_index"
    }
    resp = requests.post(url, json=data)
    print("ReleaseColumns:", resp.status_code, resp.text)

def test_query_status():
    url = f"{BASE_URL}/QueryStatus"
    resp = requests.get(url)
    print("QueryStatus:", resp.status_code, resp.text)

def test_freeze_group():
    url = f"{BASE_URL}/UnfreezeGroup"
    data = {
        "host": "host1",
        "vpu_idx": 0,
        "group_idx": 0
    }
    resp = requests.post(url, json=data)
    print("FreezeGroup:", resp.status_code, resp.text)

def test_unfreeze_group():
    url = f"{BASE_URL}/UnfreezeGroup"
    data = {
        "host": "host1",
        "vpu_idx": 0,
        "group_idx": 0
    }
    resp = requests.post(url, json=data)
    print("UnfreezeGroup:", resp.status_code, resp.text)

def test_query_all_group_ddr_status():
    url = f"{BASE_URL}/QueryAllGroupDDRStatus"
    resp = requests.get(url)
    print("QueryAllGroupDDRStatus:", resp.status_code, resp.text)

def test_query_index_allocation():
    url = f"{BASE_URL}/QueryIndexAllocation"
    data = {
        # "index_name": "test_alloc_ddr_index"
        "index_name": "test_index"
    }
    resp = requests.post(url, json=data)
    print("QueryIndexAllocation:", resp.status_code, resp.text)
def test_query_all_index_allocation():
    url = f"{BASE_URL}/QueryAllIndexAllocation"
    data = {
        # "index_name": "test_alloc_ddr_index"
        # "index_name": "test_index"
    }
    resp = requests.post(url, json=data)
    print("QueryAllIndexAllocation:", resp.status_code, resp.text)

def test_allocate_ddr_by_group():
    url = f"{BASE_URL}/AllocateDDRByGroup"
    data = {
        "host": "192.168.0.51:8000",   # 根据你的实际host填写
        "vpu_idx": 2,
        "group_idx": 1,
        "index_name": "test_alloc_ddr_index",
        "bytes_per_vec": 128,
        "vec_size": 1
    }
    resp = requests.post(url, json=data)
    print("AllocateDDRByGroup:", resp.status_code, resp.text)

def test_query_global_ddr_status():
    url = f"{BASE_URL}/QueryGlobalDDRStatus"
    resp = requests.get(url)
    print("QueryGlobalDDRStatus:", resp.status_code, resp.text)

if __name__ == "__main__":
    #test_add_card(1, "vpu1_dna")
    #test_allocate_ddr()
    #test_allocate_ddr_by_group()
    # test_query_all_group_ddr_status()
    # test_release_columns()
    # test_query_global_ddr_status()
    # test_query_index_allocation()
    test_query_all_index_allocation()
    #test_allocate_columns()
    #test_query_status()
    #test_freeze_group()
    #test_unfreeze_group()