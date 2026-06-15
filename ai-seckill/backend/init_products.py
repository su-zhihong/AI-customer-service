"""
文件路径: backend/init_products.py
商品初始化脚本。
向数据库中添加示例商品数据，并构建向量知识库。
可单独运行：python init_products.py
"""

import asyncio
import logging

from app.database import async_session_factory, init_db
from app.models import Product
from app.agent.rag import build_product_knowledge_base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 示例商品数据
SAMPLE_PRODUCTS = [
    {
        "name": "iPhone 16 Pro Max",
        "description": "Apple 最新旗舰手机，搭载 A18 Pro 芯片，48MP 主摄，钛金属边框。支持 AI 智能功能和 5G 网络。",
        "image_url": "https://picsum.photos/seed/iphone16/400/400",
        "original_price": 9999.00,
        "category": "手机数码",
        "material": "钛金属边框，陶瓷盾玻璃面板",
        "specs": '{"屏幕":"6.9英寸 OLED","芯片":"A18 Pro","存储":"256GB/512GB/1TB","摄像头":"48MP主摄+12MP超广角+12MP长焦","电池":"4685mAh"}',
    },
    {
        "name": "MacBook Air M4",
        "description": "全新 MacBook Air 搭载 M4 芯片，超轻薄设计，15.3英寸 Liquid Retina 显示屏，18小时续航。",
        "image_url": "https://picsum.photos/seed/macbook/400/400",
        "original_price": 8999.00,
        "category": "电脑办公",
        "material": "全铝金属机身",
        "specs": '{"屏幕":"15.3英寸 Liquid Retina","芯片":"M4","内存":"16GB/24GB","存储":"256GB/512GB/1TB","续航":"18小时"}',
    },
    {
        "name": "AirPods Pro 3",
        "description": "Apple 第三代降噪耳机，H3 芯片驱动，自适应音频，个性化空间音频，USB-C 充电。",
        "image_url": "https://picsum.photos/seed/airpods/400/400",
        "original_price": 1899.00,
        "category": "手机数码",
        "material": "塑料外壳，硅胶耳塞",
        "specs": '{"芯片":"H3","降噪":"自适应降噪","音频":"空间音频","防水":"IPX4","续航":"6小时(单次)/30小时(总)"}',
    },
    {
        "name": "iPad Pro M4",
        "description": "全新 iPad Pro 搭载 M4 芯片，超 XDR 显示屏，极致轻薄，支持 Apple Pencil Pro。",
        "image_url": "https://picsum.photos/seed/ipadpro/400/400",
        "original_price": 7999.00,
        "category": "电脑办公",
        "material": "全铝金属机身",
        "specs": '{"屏幕":"11英寸/13英寸 Ultra Retina XDR","芯片":"M4","存储":"256GB/512GB/1TB/2TB","摄像头":"12MP广角+LiDAR","连接":"USB-C Thunderbolt"}',
    },
    {
        "name": "Apple Watch Ultra 3",
        "description": "专为极限运动设计的智能手表，49mm钛金属表壳，精准双频 GPS，100米防水，36小时续航。",
        "image_url": "https://picsum.photos/seed/watch/400/400",
        "original_price": 5999.00,
        "category": "穿戴设备",
        "material": "钛金属表壳，蓝宝石玻璃镜面",
        "specs": '{"表壳":"49mm钛金属","屏幕":"Always-On Retina LTPO","防水":"100米","续航":"36小时","传感器":"心率/血氧/体温/深度计"}',
    },
    {
        "name": "HomePod 3",
        "description": "Apple 智能音箱，高保真音频，空间音频支持，智能家居中枢，支持 Matter 协议。",
        "image_url": "https://picsum.photos/seed/homepod/400/400",
        "original_price": 2299.00,
        "category": "智能家居",
        "material": "织物网面外壳",
        "specs": '{"音频":"高保真+空间音频","芯片":"S9","连接":"Wi-Fi 6E/蓝牙5.3/Thread","智能":"Siri+Matter","尺寸":"高168mm"}',
    },
]


async def init_data():
    """初始化商品数据并构建向量库"""
    # 初始化数据库表
    await init_db()

    async with async_session_factory() as session:
        async with session.begin():
            # 检查是否已有商品
            from sqlalchemy import select, func
            result = await session.execute(select(func.count(Product.id)))
            count = result.scalar()
            if count > 0:
                logger.info(f"数据库中已有 {count} 个商品，跳过初始化")
                return

            # 添加示例商品
            for data in SAMPLE_PRODUCTS:
                product = Product(**data)
                session.add(product)

        await session.commit()
        logger.info(f"已添加 {len(SAMPLE_PRODUCTS)} 个示例商品")

    # 构建向量知识库
    async with async_session_factory() as session:
        await build_product_knowledge_base(session)

    logger.info("🎉 商品初始化完成！")


if __name__ == "__main__":
    asyncio.run(init_data())
