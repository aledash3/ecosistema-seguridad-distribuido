import shutil
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROTO_DIR = BASE_DIR / "proto"
PROTO_FILE = PROTO_DIR / "archivo.proto"

TARGET_DIRS = [
    PROTO_DIR,
    BASE_DIR / "nodo_logico_grpc",
    BASE_DIR / "dashboard_streamlit"
]

def compile_proto():
    print(f"[INFO] Compilando contrato protobuf: {PROTO_FILE}")
    cmd = [
        sys.executable, "-m", "grpc_tools.protoc",
        f"-I{PROTO_DIR}",
        f"--python_out={PROTO_DIR}",
        f"--grpc_python_out={PROTO_DIR}",
        str(PROTO_FILE)
    ]
    subprocess.check_call(cmd)
    print("[OK] Compilación exitosa en proto/")

    # Sincronizar archivos generados en nodo_logico_grpc y dashboard_streamlit
    generated_files = ["archivo_pb2.py", "archivo_pb2_grpc.py"]
    for target in TARGET_DIRS[1:]:
        target.mkdir(parents=True, exist_ok=True)
        for gf in generated_files:
            src = PROTO_DIR / gf
            dst = target / gf
            shutil.copy2(src, dst)
            print(f"[SYNC] Copiado {gf} -> {target.name}/")

    print("[LISTO] Todos los stubs gRPC sincronizados.")

if __name__ == "__main__":
    compile_proto()
