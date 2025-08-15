# elemem-vector-sdk

提供向量的增删改查

## 注意事项

- 支持pip安装，import需要改为绝对路径导入。
```
1. sdk_pb2_grpc.py中的
import sdk_pb2 as sdk__pb2
改为
from . import sdk_pb2 as sdk__pb2

2. hilbert_client.py中的
import sdk_pb2
import sdk_pb2_grpc
改为
from . import sdk_pb2
from . import sdk_pb2_grpc

3. demo中的
from hilbert_client import HilbertClient, get_data_from_hdf5
改为
from elemem_sdk import hilbert_client

```

## 上传到pypi上，支持任意位置安装

```
bash upload.sh
```


## 安装

```bash
pip install elemem-vector-sdk
```