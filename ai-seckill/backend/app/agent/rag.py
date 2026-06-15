"""
文件路径: backend/app/agent/rag.py
RAG（检索增强生成）模块：向量库构建、商品知识检索。
使用 ChromaDB 作为向量存储，OpenAI Embedding 生成向量。
"""

import logging
import numpy as np
from typing import List, Optional

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings

logger = logging.getLogger(__name__)

# 向量存储持久化目录
CHROMA_PERSIST_DIR = "./chroma_db"

# 全局向量存储实例
_vector_store: Optional[Chroma] = None


class LocalEmbeddings(Embeddings):
    """
    本地 ONNX 嵌入模型封装。
    使用 fastembed 库（基于 ONNX Runtime），无需联网下载模型。
    模型已在安装包中内置，支持中文和英文文本。
    """

    def __init__(self):
        """初始化嵌入模型"""
        try:
            from fastembed import TextEmbedding
            self._model = TextEmbedding(
                model_name="BAAI/bge-small-zh-v1.5",
                max_length=512,
            )
            logger.info("本地 ONNX 嵌入模型初始化成功")
        except Exception as e:
            logger.warning(f"fastembed 初始化失败: {e}，回退到简单词袋模型")
            self._model = None

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """嵌入文档列表"""
        if self._model:
            return list(self._model.embed(texts))
        # 简单回退：词袋向量
        return [self._simple_embed(t) for t in texts]

    def embed_query(self, text: str) -> List[float]:
        """嵌入查询文本"""
        if self._model:
            return list(self._model.embed([text]))[0]
        return self._simple_embed(text)

    def _simple_embed(self, text: str) -> List[float]:
        """简单的字符频率向量作为回退"""
        import hashlib
        vec = np.zeros(384)
        for i, ch in enumerate(text[:384]):
            h = int(hashlib.md5(ch.encode()).hexdigest()[:8], 16)
            vec[i % 384] += (h % 100) / 100.0
        return vec.tolist()


def get_embeddings() -> LocalEmbeddings:
    """获取本地嵌入模型实例"""
    return LocalEmbeddings()


def get_vector_store() -> Chroma:
    """
    获取 Chroma 向量存储实例。
    如果实例不存在则创建，使用持久化存储。
    """
    global _vector_store
    if _vector_store is None:
        embeddings = get_embeddings()
        _vector_store = Chroma(
            collection_name="product_knowledge",
            embedding_function=embeddings,
            persist_directory=CHROMA_PERSIST_DIR,
        )
    return _vector_store


async def build_product_knowledge_base(db: AsyncSession):
    """
    构建商品知识向量库。
    从数据库中读取所有商品，将商品信息转换为文档并生成向量索引。
    在 FastAPI 启动事件或初始化脚本中调用。

    每个商品生成多个文档片段，覆盖不同维度的信息：
    - 商品基本信息（名称、分类、价格）
    - 商品描述
    - 材质信息
    - 规格参数
    """
    from app.models import Product

    logger.info("开始构建商品知识向量库...")

    # 查询所有商品
    result = await db.execute(select(Product))
    products = result.scalars().all()

    if not products:
        logger.info("数据库中没有商品，跳过向量库构建")
        return

    documents = []
    for product in products:
        # 为每个商品生成多个知识片段
        # 片段1：商品基本信息
        doc1 = Document(
            page_content=f"商品名称：{product.name}。分类：{product.category}。原价：{product.original_price}元。",
            metadata={"product_id": product.id, "product_name": product.name, "type": "basic_info"},
        )
        documents.append(doc1)

        # 片段2：商品描述
        if product.description:
            doc2 = Document(
                page_content=f"商品名称：{product.name}。商品描述：{product.description}",
                metadata={"product_id": product.id, "product_name": product.name, "type": "description"},
            )
            documents.append(doc2)

        # 片段3：材质信息
        if product.material:
            doc3 = Document(
                page_content=f"商品名称：{product.name}。材质：{product.material}",
                metadata={"product_id": product.id, "product_name": product.name, "type": "material"},
            )
            documents.append(doc3)

        # 片段4：规格参数
        if product.specs:
            doc4 = Document(
                page_content=f"商品名称：{product.name}。规格参数：{product.specs}",
                metadata={"product_id": product.id, "product_name": product.name, "type": "specs"},
            )
            documents.append(doc4)

    # 将文档添加到向量库
    vector_store = get_vector_store()
    # 先清空已有数据（避免重复添加）
    try:
        vector_store.delete_collection()
    except Exception:
        pass
    # 重新创建并添加文档
    _vector_store = Chroma.from_documents(
        documents=documents,
        embedding=get_embeddings(),
        collection_name="product_knowledge",
        persist_directory=CHROMA_PERSIST_DIR,
    )

    logger.info(f"商品知识向量库构建完成，共添加 {len(documents)} 个文档片段")


async def search_product_info(query: str, k: int = 3) -> List[Document]:
    """
    根据用户问题从向量库检索相关商品知识。
    
    Args:
        query: 用户的问题
        k: 返回的最相关文档数量
    
    Returns:
        检索到的相关文档列表
    """
    try:
        vector_store = get_vector_store()
        # 使用相似度搜索，返回最相关的 k 个文档
        docs = vector_store.similarity_search(query, k=k)
        return docs
    except Exception as e:
        logger.error(f"向量检索失败: {e}")
        return []


def format_search_results(docs: List[Document]) -> str:
    """
    将检索到的文档格式化为可读的文本。
    用于 Agent 工具返回给 LLM 的上下文。
    """
    if not docs:
        return "未找到相关商品信息。"

    formatted = "以下是检索到的相关商品信息：\n\n"
    for i, doc in enumerate(docs, 1):
        product_name = doc.metadata.get("product_name", "未知商品")
        info_type = doc.metadata.get("type", "general")
        formatted += f"{i}. 【{product_name} - {info_type}】\n   {doc.page_content}\n\n"
    return formatted
