import logging
import os
import sys

from AgentUtils.clientInfo import clientInfo
from AgentUtils.ExpiringDictStorage import ExpiringDictStorage
from AgentUtils.metric import print_metrics
from AgentUtils.span import Span_Mgr
from Business.filesscopes import filescopeAgent
from Business.translate import translateAgent
from Business.translateConfig import TranslationContext
from utils import validate_inputs

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
storage = ExpiringDictStorage(expiry_days=7)

## system
LLM_Client = clientInfo(
    api_key=os.getenv("api_key"),
    base_url=os.getenv("base_url", "https://api.deepseek.com"),
    model=os.getenv("model", "deepseek-chat"),
    dryRun=os.getenv("dryRun", False),
    local_cache=storage,
    usecache=os.getenv("usecache", True),
)
LLM_Client.show_config()
span_mgr = Span_Mgr(storage)
root_span = span_mgr.create_span("Root operation")

args = sys.argv
try:
    configfile_path, doc_folder, reserved_word = validate_inputs(args)
    logging.info(
        f"Config: {configfile_path}, doc folder: {doc_folder}, reserved_word: {reserved_word}"
    )
except ValueError as e:
    logging.info(f"错误: {e}", file=sys.stderr)
    logging.info(
        "用法: python script.py <configfile_path> <doc_folder> <reserved_word>",
        file=sys.stderr,
    )
    sys.exit(1)

file_list = args[4] if len(args) > 4 else None
max_files = os.getenv("max_files", 20)
target_language = os.getenv("target_language", "support")
context = TranslationContext(
    target_language=target_language,
    file_list=file_list,
    doc_folder=doc_folder,
    reserved_word=reserved_word,
    disclaimers=os.getenv("disclaimers", False),
)
context.load_config("./config.yaml")
context.show_config()
FSAgent = filescopeAgent(LLM_Client, span_mgr)
TsAgent = translateAgent(LLM_Client, span_mgr)
### Start a span
## Workflow 1 missing files
### Phase 1
json_todo_list = FSAgent.filesscopes(
    configfile_path, file_list, doc_folder, target_language, max_files, root_span
)
### Phase 2
TsAgent.translate_files(json_todo_list, context, root_span)
### Finish the span
span_mgr.end_span(root_span.hash)
### Display historical spans

### show metrics
print_metrics()
print(span_mgr.display_all_spans())
