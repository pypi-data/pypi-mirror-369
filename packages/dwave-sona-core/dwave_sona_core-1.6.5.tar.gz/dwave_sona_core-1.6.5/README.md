# Dwave SONA Core

迪威智能 SONA 服務專用核心開發套件

## 安裝與使用

### 開發環境需求

- Python 3.8 或更新版本
- poetry
- ffmpeg

### 安裝與使用

1. 環境建構

```sh
$ pip install poetry
```

2. 下載與安裝

```sh
$ export PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring
$ poetry add git+ssh://git@github.com/DeepWaveInc/dwave-sona-core.git
```

3. 撰寫 Inferencer 模組

```python
from typing import Dict, List

from loguru import logger
from pydantic import BaseModel, Field
from sona.core.inferencer import InferencerBase
from sona.core.messages import File, Result


class InputParamSchema(BaseModel):
    param1: int = Field(42, description="this is the value of param1")
    param2: str = Field("43", description="this is the value of param2")


class InputFilesSchema(BaseModel):
    origin: str = Field("data/test.mp3", description="this is the value of origin")


class SimpleInferencer(InferencerBase):
    name = "mock"
    description = "This is a simple inferencer"
    input_params_schema = InputParamSchema()
    input_files_schema = InputFilesSchema()

    def on_load(self) -> None:
        logger.info(f"Download {self.__class__.__name__} models...")

    def inference(self, params: Dict, files: List[File]) -> Result:
        logger.info(f"Get params {params}")
        logger.info(f"Get files {files}")
        return Result(
            files=[File(label="output", path=files[0].path)],
            data={"output_key": "output_val"},
        )


if __name__ == "__main__":
    inferencer = SimpleInferencer()
    inferencer.cmd()
```

4. 測試指令

```sh
$ python simple.py --help
Usage: simple.py [OPTIONS] <filepath:origin>

  This is a simple inferencer

Options:
  --param2 <string>   this is the value of param2
  --param1 <integer>  this is the value of param1
  --help              Show this message and exit.
```

```sh
$ python tests/simple.py tests/simple.py
2023-10-17 02:18:41.702 | INFO     | __main__:on_load:25 - Download SimpleInferencer models...
2023-10-17 02:18:41.702 | INFO     | __main__:inference:28 - Get params {'param2': '43', 'param1': 42}
2023-10-17 02:18:41.703 | INFO     | __main__:inference:29 - Get files [File(label='origin', path='tests/simple.py', metadata={})]
{"files":[{"label":"output","path":"tests/simple.py","metadata":{}}],"data":{"output_key":"output_val"}}
```