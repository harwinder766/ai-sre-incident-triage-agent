# import time 
# x = time.perf_counter()
# time.sleep(3)
# y = time.perf_counter()

# print(round(x-y, 2))

from langchain_community.document_loaders import (
    TextLoader,
    WebBaseLoader,
    DirectoryLoader,
    PyPDFLoader,
)
