import os
import grpc
import logging
from .proto import sdk_pb2, sdk_pb2_grpc
import numpy as np
from tqdm import tqdm
import h5py
import json
from google.protobuf.json_format import MessageToDict
import concurrent.futures
import threading

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('HilbertClient')
logger.setLevel(logging.DEBUG)

def get_data_from_hdf5(hdf5_path: str, dataset_name: str = 'train') -> tuple:

    if not os.path.exists(hdf5_path):
        logger.error(f"HDF5文件不存在: {hdf5_path}")
        raise FileNotFoundError(f"HDF5文件不存在: {hdf5_path}")

    with h5py.File(hdf5_path, 'r') as f:
        data = f[dataset_name][()]

    num, dim = data.shape
    return data, num, dim
'''
    logger.info(f"Loaded HDF5 dataset '{dataset_name}' with shape {data.shape}")

    with open(bin_path, 'wb') as bf:
        bf.write(data.astype('float32').tobytes())
    logger.info(f"Wrote binnary file: {bin_path}, size={data.nbytes} bytes")
    return num, dim
'''

class HilbertClient:
    def __init__(self, server_address, debug=False):
        options = [
                # 客户端最多能接收 200 MB 的单条响应
                ('grpc.max_receive_message_length', 200 * 1024 * 1024),
                # 客户端最多能发送 200 MB 的单条请求
                ('grpc.max_send_message_length',    200 * 1024 * 1024),
                ]
        self.channel = grpc.insecure_channel(server_address, options=options)
        self.stub = sdk_pb2_grpc.SdkServiceStub(self.channel)
        self.debug = debug
        logger.info(f"Connected to server at {server_address}")

    def _log_full_response(self, response, method_name):
        if self.debug:
            try:
                response_dict = MessageToDict(
                        response,
                        preserving_proto_field_name=True,
                        always_print_fields_with_no_presence=True
                )
                formatted = json.dumps(
                        response_dict,
                        indent=2,
                        ensure_ascii=False,
                        default=lambda x: str(x)
                        )
                logger.debug(f"FULL RESPONSE FOR {method_name}:\n{formatted}")
            except Exception as e:
                logger.error(f"Failed to log full response: {str(e)}")

    def _check_response(self, code, method_name):
        if code.code != 0:
            err_msg = f"{method_name} failed: {code.message} (code={code.code})"
            logger.error(err_msg)
            raise RuntimeError(err_msg)

    def create_index(self, name, dim, replica_num=1, index_type=1, card_num=1):
        logger.info(f"Creating index: {name}, dim={dim}, replicas{replica_num}")
        request = sdk_pb2.CreateIndexRequest(
                name=name,
                dim=dim,
                replica_num=replica_num,
                index_type=index_type,
                card_num=card_num
        )
        response = self.stub.create_index(request)
        self._log_full_response(response, "create_index")
        self._check_response(response.code, "create_index")
        logger.info(f"Index {name} created successfully")
        return True

    def delete_index(self, name):
        logger.info(f"Deleting index: {name}")
        request = sdk_pb2.DeleteIndexRequest(name=name)
        response = self.stub.delete_index(request)
        self._log_full_response(response, "delete_index")
        self._check_response(response.code, "delete_index")
        logger.info(f"Index {name} deleted successfully")
        return True

    def query_all_index(self):
        logger.info("Querying all indexes")
        request = sdk_pb2.QueryAllIndexRequest()
        response = self.stub.query_all_index(request)
        self._log_full_response(response, "query_all_index")
        self._check_response(response.code, "query_all_index")

        indexes = []
        for idx in response.indices:
            indexes.append({
                'name': idx.name,
                'nlist': idx.nlist,
                'dim': idx.dim,
                'nb': idx.nb,
                'replica_num': idx.replica_num,
                'index_type': idx.index_type
            })
        logger.info(f"Found {len(indexes)} indices")
        logger.debug(f"Indices details: {json.dumps(indexes, indent=2)}")
        return indexes

    def train(self, name, data, nlist=128):

        if not isinstance(data, np.ndarray):
            raise TypeError("data must be a numpy array")
        if data.dtype != np.float32:
            data = data.astype(np.float32)
        if len(data.shape) != 2:
            raise ValueError("Data must be 2D array [num_vectors, dim]")

        nb, dim = data.shape
        logger.info(f"Starting training: {name}, vector={nb}, dim={dim}, nlist={nlist}")

        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write(data.tobytes())
            temp_file.flush()

            request = sdk_pb2.TrainRequest(
                name=name,
                nb=nb,
                nlist=nlist,
                file_path=temp_path
            )
            response = self.stub.train(request)
            self._log_full_response(response, "Train")
            self._check_response(response.code, "Train")

        logger.info(f"Training completed for index {name}")
        return True

    def add(self, name, data, mode_flag=0):

        if not isinstance(data, np.ndarray):
            raise TypeError("data must be a numpy array")
        if data.dtype != np.float32:
            data = data.astype(np.float32)
        if len(data.shape) != 2:
            raise ValueError("Data must be 2D array [num_vectors, dim]")

        nb, dim = data.shape
        logger.info(f"Starting add: {name}, vectors={nb}, dim={dim}, mode_flag={mode_flag}")

        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write(data.tobytes())
            temp_file.flush()

            request = sdk_pb2.AddRequest(
                name=name,
                nb=nb,
                mode_flag=mode_flag,
                file_path=temp_path
            )

            response = self.stub.add(request)
            self._log_full_response(response, "Add")
            self._check_response(response.code, "Add")
            logger.info(f"Add {nb} vectors to index {name}")
            logger.info(f"Generated {len(response.ids)} IDs")

        if response.ids:
            sample_ids = response.ids[:5] if len(response.ids) > 5 else response.ids
            logger.debug(f"Sample IDs: {sample_ids}")

        return response.ids

    def stream_train(self, name, nb, dim, data_generator, nlist=128):
        logger.info(f"Starting stream training: {name}, vector={nb}, dim={dim}, nlist={nlist}")

        def request_generator():
            meta_request = sdk_pb2.TrainRequest(
                name=name,
                nb=nb,
                nlist=nlist
            )
            logger.debug(f"Sending training metadata: {MessageToDict(meta_request)}")
            yield meta_request

            chunk_size = 1024 * 1024
            total_chunks = (nb * dim * 4 + chunk_size - 1) // chunk_size
            progress = tqdm(total=total_chunks, desc="Uploading training data")

            for i, chunk in enumerate(data_generator(chunk_size)):
                data_request = sdk_pb2.TrainRequest(
                        data_chunk=chunk,
                        is_last_chunk=False
                )
                if i%100 == 0:
                    logger.debug(f"Sending training chunk {i}/{total_chunks}, size={len(chunk)} bytes")
                yield data_request
                progress.update(1)

            end_request = sdk_pb2.TrainRequest(is_last_chunk=True)
            logger.debug("Sending training end marker")
            yield end_request
            progress.close()

        response = self.stub.StreamTrain(request_generator())
        self._log_full_response(response, "StreamTrain")
        self._check_response(response.code, "StreamTrain")
        logger.info(f"Training completed for index {name}")
        return True

    def stream_add(self, name, nb, dim, data_generator, mode_flag=0):
        logger.info(f"Starting stream add: {name}, vectors={nb}, dim={dim}, mode_flag={mode_flag}")

        def request_generator():
            meta_request = sdk_pb2.AddRequest(
                    name=name,
                    nb=nb,
                    mode_flag=mode_flag
            )
            logger.debug(f"Sending add metadata: {MessageToDict(meta_request)}")
            yield meta_request

            chunk_size = 1024 * 1024
            total_chunks = (nb * dim * 4 + chunk_size - 1) // chunk_size
            progress = tqdm(total=total_chunks, desc="Upload vectors")

            for i, chunk in enumerate(data_generator(chunk_size)):
                data_request = sdk_pb2.AddRequest(
                        data_chunk=chunk,
                        is_last_chunk=False
                )
                if i%100 == 0:
                    logger.debug(f"Sending add chunk {i}/{total_chunks}, size={len(chunk)} bytes")

                yield data_request
                progress.update(1)

            end_request = sdk_pb2.AddRequest(is_last_chunk=True)
            logger.debug("Sending add end marker")
            yield end_request
            progress.close()

        response = self.stub.StreamAdd(request_generator())
        self._log_full_response(response, "StreamAdd")
        self._check_response(response.code, "StreamAdd")
        logger.info(f"Add {nb} vectors to index {name}")
        logger.info(f"Generated {len(response.ids)} IDs")

        if response.ids:
            sample_ids = response.ids[:5] if len(response.ids) > 5 else response.ids
            logger.debug(f"Sample IDs: {sample_ids}")

        return response.ids

    def search(self, name, queries, k=10, nprob=32, batch_size=100, max_workers=8):
        nq = queries.shape[0]
        dim = queries.shape[1]
        logger.info(f"Searching: {name}, queries={nq}, k={k}, nprob={nprob}")

        all_distances = np.empty((nq, k), dtype=np.float32)
        all_labels = np.empty((nq, k), dtype=np.int64)

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            for start_idx in range(0, nq, batch_size):
                end_idx = min(start_idx + batch_size, nq)
                batch_queries = queries[start_idx:end_idx]
                batch_nq = batch_queries.shape[0]
                future = executor.submit(
                    self._process_batch,
                    name=name,
                    queries=batch_queries,
                    nprob=nprob,
                    k=k,
                    start_idx=start_idx,
                    end_idx=end_idx
                )
                futures[future] = (start_idx, end_idx)

            for future in concurrent.futures.as_completed(futures):
                start_idx, end_idx = futures[future]
                try:
                    batch_distances, batch_labels = future.result()
                    all_distances[start_idx:end_idx] = batch_distances
                    all_labels[start_idx:end_idx] = batch_labels
                    logger.debug(f"Batch {start_idx}-{end_idx-1} completed")
                except Exception as e:
                    logger.error(f"Batch {start_idx}-{end_idx-1} failed: {str(e)}")
                    raise
        logger.info(f"Search completed. Top{k} results per query")
        return all_distances, all_labels

    def _process_batch(self, name, queries, nprob, k, start_idx, end_idx):
        batch_nq = queries.shape[0]
        flat_queries = queries.flatten().tolist()
        request = sdk_pb2.SearchRequest(
            name=name,
            nq=batch_nq,
            query=flat_queries,
            nprobe=nprob,
            k=k
        )

        if not hasattr(self, "_thread_local"):
            self._thread_local = threading.local()
        if not hasattr(self._thread_local, "stub"):
            self._thread_local.stub = self._create_stub()

        response = self._thread_local.stub.search(request)
        #self._log_full_response(response, "search")
        self._check_response(response.code, "search")

        batch_distances = np.array(response.distances).reshape(batch_nq, k)
        batch_labels = np.array(response.labels).reshape(batch_nq, k)

        return batch_distances, batch_labels

    def _create_stub(self):
        return sdk_pb2_grpc.SdkServiceStub(self.channel)

    def query_vector(self, name, vector_id, out_flag=0):
        logger.info(f"Querying vector: index={name}, id={vector_id}")
        request = sdk_pb2.QueryRequest(
                name=name,
                id=vector_id,
                out_flag=out_flag
        )

        response = self.stub.query(request)
        self._log_full_response(response, "query")
        self._check_response(response.code, "query")

        logger.info(f"Vector {vector_id} queried successfully")
        logger.debug(f"Vector data length: {len(response.data)} floats")
        logger.debug(f"Digital data length: {len(response.digital_data)} floats")
        logger.debug(f"ReRAM data length: {len(response.reram_data)} ints")

        return response

    def update_vector(self, name, vector_id, data):
        logger.info(f"Updating vector: index={name}, id={vector_id}")
        request = sdk_pb2.UpdateRequest(
                name=name,
                id=vector_id,
                data=data
        )

        response = self.stub.update(request)
        self._log_full_response(response, "update")
        self._check_response(response.code, "update")
        logger.info(f"Vector {vector_id} updated successfully")
        return True

    def delete_vector(self, name, vector_id):
        logger.info(f"Deleting vector: index={name}, id={vector_id}")
        request = sdk_pb2.RemoveRequest(
                name=name,
                id=vector_id
        )

        response = self.stub.remove(request)
        self._log_full_response(response, "remove")
        self._check_response(response.code, "remove")
        logger.info(f"Vector {vector_id} deleted successfully")
        return True

def float32_generator(total_size, chunk_size):
    remaining = total_size
    while remaining > 0:
        size = min(remaining, chunk_size)
        yield np.random.rand(size // 4).astype(np.float32).tobytes()
        remaining -= size

