#!/usr/bin/env python3
"""
伪造数据脚本
生成三个用户的模拟聊天对话数据，并调用LindormMemobase.add_blob_to_buffer写入buffer中
每个用户生成10条对话记录
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import List

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lindormmemobase import LindormMemobase
from lindormmemobase.models.blob import ChatBlob, BlobType, OpenAICompatibleMessage


class FakeDataGenerator:
    """伪造数据生成器"""
    
    def __init__(self, config_path: str = "./config.yaml"):
        """初始化数据生成器"""
        self.config_path = config_path
        self.memobase = None
        
        # 定义三个测试用户
        self.users = {
            "user_001": {
                "name": "张三",
                "description": "软件工程师，喜欢技术讨论和编程",
                "personality": "技术导向，逻辑性强"
            },
            "user_002": {
                "name": "李四", 
                "description": "产品经理，关注用户体验和商业价值",
                "personality": "商业敏感，注重用户需求"
            },
            "user_003": {
                "name": "王五",
                "description": "数据分析师，热爱数据挖掘和机器学习", 
                "personality": "数据驱动，喜欢深度思考"
            }
        }
        
        # 预定义对话模板
        self.conversation_templates = self._generate_conversation_templates()
    
    def _generate_conversation_templates(self) -> dict:
        """生成对话模板"""
        return {
            "user_001": [
                {
                    "user": "你好，我最近在学习Python异步编程，有什么好的学习资源推荐吗？",
                    "assistant": "我推荐你看看《Python异步编程》这本书，还有官方的asyncio文档。你可以从简单的async/await语法开始，然后逐步学习事件循环、协程等概念。"
                },
                {
                    "user": "我在使用asyncio时遇到了一个问题，如何正确处理异常？",
                    "assistant": "在异步编程中，异常处理很重要。你可以使用try-except包围await表达式，也可以使用asyncio.gather()的return_exceptions参数来收集异常。记得在Task中也要处理异常。"
                },
                {
                    "user": "能否解释一下Python的GIL对多线程性能的影响？",
                    "assistant": "GIL（全局解释器锁）确实会限制Python多线程的CPU密集型任务性能。对于CPU密集型任务，建议使用multiprocessing；对于I/O密集型任务，asyncio通常是更好的选择。"
                },
                {
                    "user": "我正在做一个Web爬虫项目，用什么框架比较好？",
                    "assistant": "推荐使用scrapy框架，它专为爬虫设计，内置了很多有用的功能。如果是简单项目，requests + BeautifulSoup也够用。记得遵守robots.txt和合理控制请求频率。"
                },
                {
                    "user": "Docker容器化部署有什么最佳实践？",
                    "assistant": "Docker最佳实践包括：使用多阶段构建减小镜像大小、不要在容器中运行多个进程、使用.dockerignore、设置合适的健康检查、使用非root用户运行等。"
                },
                {
                    "user": "我想了解一下微服务架构的优缺点",
                    "assistant": "微服务优点包括技术多样性、独立部署、容错性好。缺点是增加了系统复杂性、网络延迟、数据一致性等挑战。需要根据团队规模和业务复杂度权衡。"
                },
                {
                    "user": "在设计API时，RESTful和GraphQL该如何选择？",
                    "assistant": "REST适合资源导向的简单场景，GraphQL适合复杂的数据查询需求。GraphQL可以减少过度获取数据，但学习成本更高。建议先评估团队技术栈和具体需求。"
                },
                {
                    "user": "如何进行有效的代码审查（Code Review）？",
                    "assistant": "有效的代码审查应该关注：代码逻辑正确性、性能优化、安全问题、编码规范、可维护性。建议使用工具辅助，保持友善的沟通态度，既要指出问题也要解释原因。"
                },
                {
                    "user": "我在学习算法，动态规划总是理解不透彻",
                    "assistant": "动态规划的核心是找到状态转移方程。建议从经典问题开始（如斐波那契、背包问题），先画出状态转移图，理解子问题如何组合成原问题，多练习就能掌握。"
                },
                {
                    "user": "现在AI发展这么快，程序员会被替代吗？",
                    "assistant": "AI工具确实提高了开发效率，但程序员的价值在于解决复杂问题、系统设计、业务理解等。建议拥抱AI工具，将它们作为提升生产力的助手，同时持续学习新技术。"
                }
            ],
            "user_002": [
                {
                    "user": "我们正在规划一个新产品，如何进行有效的用户调研？",
                    "assistant": "用户调研应该包括定性和定量方法。可以通过用户访谈了解深层需求，通过问卷调查获取大量数据，还可以进行可用性测试。关键是要定义清楚调研目标和用户画像。"
                },
                {
                    "user": "产品迭代中，如何平衡新功能开发和技术债务处理？",
                    "assistant": "这需要在业务价值和技术健康之间找平衡。建议采用70-20-10法则：70%精力用于核心功能，20%用于改进优化，10%用于技术债务。定期技术债务评估也很重要。"
                },
                {
                    "user": "怎样设计一个有效的产品路线图？",
                    "assistant": "产品路线图应该基于用户价值、商业目标和技术可行性。建议使用OKR方法设定目标，按照优先级排列功能，保持灵活性以应对变化，并定期与团队沟通更新。"
                },
                {
                    "user": "如何评估产品功能的ROI（投资回报率）？",
                    "assistant": "评估ROI需要明确投入成本（开发、维护、推广）和预期收益（用户增长、收入提升、成本节约）。可以使用A/B测试验证效果，建立数据指标体系进行量化分析。"
                },
                {
                    "user": "在敏捷开发中，产品经理应该如何与技术团队协作？",
                    "assistant": "产品经理应该参与sprint规划，明确需求优先级，及时解答团队疑问。建议定期举行需求澄清会议，使用用户故事描述需求，建立良好的沟通机制。"
                },
                {
                    "user": "如何处理来自不同利益相关者的冲突需求？",
                    "assistant": "处理冲突需求要回到产品愿景和用户价值。建议建立需求优先级矩阵，基于影响范围和紧急程度评估，通过数据和用户反馈支撑决策，保持透明沟通。"
                },
                {
                    "user": "产品上线后，如何进行效果评估和迭代？",
                    "assistant": "建立完整的数据监控体系，包括用户行为、业务指标、技术指标。定期分析用户反馈，进行用户满意度调查，基于数据洞察制定下一步迭代计划。"
                },
                {
                    "user": "B2B产品和C2C产品在设计上有什么不同？",
                    "assistant": "B2B更注重效率和功能完整性，决策周期长，需要考虑多角色使用。C2C更注重用户体验和情感连接，需要简单易用。销售模式、定价策略也有很大差异。"
                },
                {
                    "user": "如何建立和管理产品社区？",
                    "assistant": "产品社区建设需要明确目标用户群体，提供有价值的内容，建立激励机制鼓励用户参与。要培养种子用户，定期举办活动，倾听用户声音并快速响应。"
                },
                {
                    "user": "产品定价策略有哪些考虑因素？",
                    "assistant": "定价需要考虑成本结构、竞争对手、用户价值感知、市场定位等。可以采用价值定价、竞争定价、成本加成等方法，通过A/B测试验证不同价格点的转化效果。"
                }
            ],
            "user_003": [
                {
                    "user": "我正在学习机器学习，监督学习和无监督学习有什么区别？",
                    "assistant": "监督学习使用带标签的数据训练模型，如分类和回归问题。无监督学习从无标签数据中发现模式，如聚类和降维。半监督学习则结合了两者，使用少量标签数据。"
                },
                {
                    "user": "在做数据分析时，如何处理缺失值？",
                    "assistant": "处理缺失值的方法包括：删除含缺失值的记录、用均值/中位数/众数填充、使用插值方法、基于模型预测填充。选择方法要考虑数据类型、缺失比例和业务含义。"
                },
                {
                    "user": "能介绍一下大数据处理的常用工具吗？",
                    "assistant": "常用工具包括Hadoop生态（HDFS、MapReduce、Hive）、Spark（批处理和流处理）、Kafka（消息队列）、HBase/Cassandra（NoSQL数据库）。选择工具要根据数据量、实时性要求和团队技术栈。"
                },
                {
                    "user": "如何评估机器学习模型的性能？",
                    "assistant": "模型评估指标因任务而异：分类问题用准确率、精确率、召回率、F1分数；回归问题用MSE、RMSE、MAE；还要考虑过拟合、交叉验证、ROC曲线等。重要的是选择符合业务目标的指标。"
                },
                {
                    "user": "我想了解一下深度学习中的卷积神经网络",
                    "assistant": "CNN特别适合处理图像数据。核心概念包括卷积层（特征提取）、池化层（降维）、全连接层（分类）。通过参数共享和局部连接，CNN能有效学习空间特征，广泛应用于计算机视觉任务。"
                },
                {
                    "user": "数据可视化有什么最佳实践？",
                    "assistant": "好的数据可视化应该：选择合适的图表类型、保持简洁清晰、使用合理的颜色搭配、添加必要的标签和说明。工具推荐Python的matplotlib/seaborn、R的ggplot2、商业工具如Tableau。"
                },
                {
                    "user": "如何构建一个实时数据分析系统？",
                    "assistant": "实时系统通常包括数据采集（Kafka）、流处理（Spark Streaming/Flink）、存储（Redis/HBase）、可视化（Grafana）。需要考虑数据一致性、容错性、可扩展性等问题。"
                },
                {
                    "user": "在做特征工程时有什么技巧？",
                    "assistant": "特征工程技巧包括：数值特征标准化/归一化、类别特征编码（独热、标签编码）、时间特征提取、多项式特征、特征选择（相关性分析、重要性评分）。好的特征往往比复杂模型更重要。"
                },
                {
                    "user": "推荐系统有哪些常见算法？",
                    "assistant": "主要有协同过滤（基于用户/物品）、内容过滤、混合推荐、深度学习方法（深度协同过滤、Wide&Deep）。还要考虑冷启动问题、多样性、实时性等工程挑战。"
                },
                {
                    "user": "如何进行A/B测试的统计分析？",
                    "assistant": "A/B测试需要确定样本量、显著性水平、检验功效。使用t检验或卡方检验比较组间差异，计算置信区间。要注意多重检验问题、辛普森悖论等统计陷阱，确保实验设计的科学性。"
                }
            ]
        }
    
    async def initialize(self):
        """初始化LindormMemobase连接"""
        print(f"正在初始化LindormMemobase，配置文件：{self.config_path}")
        self.memobase = LindormMemobase.from_yaml_file(self.config_path)
        print("LindormMemobase初始化完成")
    
    def create_chat_blob(self, user_message: str, assistant_message: str) -> ChatBlob:
        """创建聊天Blob对象"""
        messages = [
            OpenAICompatibleMessage(
                role="user", 
                content=user_message,
                created_at=datetime.now().isoformat()
            ),
            OpenAICompatibleMessage(
                role="assistant", 
                content=assistant_message,
                created_at=datetime.now().isoformat()
            )
        ]
        
        return ChatBlob(
            messages=messages,
            type=BlobType.chat,
            created_at=datetime.now()
        )
    
    async def generate_user_data(self, user_id: str, user_info: dict) -> List[str]:
        """为指定用户生成10条对话数据并写入buffer"""
        print(f"\n正在为用户 {user_id}（{user_info['name']}）生成数据...")
        
        conversations = self.conversation_templates[user_id]
        blob_ids = []
        
        for i, conv in enumerate(conversations, 1):
            # 创建聊天blob
            chat_blob = self.create_chat_blob(
                user_message=conv["user"],
                assistant_message=conv["assistant"]
            )
            
            # 添加到buffer
            try:
                blob_id = await self.memobase.add_blob_to_buffer(
                    user_id=user_id,
                    blob=chat_blob
                )
                blob_ids.append(blob_id)
                print(f"  ✓ 对话 {i}/10 已添加到buffer，blob_id: {blob_id[:8]}...")
                
                # 添加小延迟，模拟真实对话间隔
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"  ✗ 对话 {i}/10 添加失败: {e}")
        
        print(f"用户 {user_id} 数据生成完成，共生成 {len(blob_ids)} 条记录")
        return blob_ids
    
    async def generate_all_data(self):
        """生成所有用户的数据"""
        print("="*60)
        print("开始生成伪造数据...")
        print("="*60)
        
        all_results = {}
        
        for user_id, user_info in self.users.items():
            try:
                blob_ids = await self.generate_user_data(user_id, user_info)
                all_results[user_id] = {
                    "user_info": user_info,
                    "blob_ids": blob_ids,
                    "count": len(blob_ids)
                }
            except Exception as e:
                print(f"用户 {user_id} 数据生成失败: {e}")
                all_results[user_id] = {
                    "user_info": user_info,
                    "blob_ids": [],
                    "count": 0,
                    "error": str(e)
                }
        
        return all_results
    
    def print_summary(self, results: dict):
        """打印生成结果摘要"""
        print("\n" + "="*60)
        print("数据生成摘要")
        print("="*60)
        
        total_success = 0
        total_failed = 0
        
        for user_id, result in results.items():
            user_name = result["user_info"]["name"]
            count = result["count"]
            
            if "error" in result:
                print(f"❌ {user_name} ({user_id}): 生成失败 - {result['error']}")
                total_failed += 1
            else:
                print(f"✅ {user_name} ({user_id}): 成功生成 {count} 条对话记录")
                total_success += count
        
        print(f"\n总计：")
        print(f"  - 成功用户：{len([r for r in results.values() if 'error' not in r])} 个")
        print(f"  - 失败用户：{len([r for r in results.values() if 'error' in r])} 个")  
        print(f"  - 总对话数：{total_success} 条")
        
        if total_success > 0:
            print(f"\n🎉 数据生成完成！可以使用以下用户ID进行测试：")
            for user_id, result in results.items():
                if "error" not in result and result["count"] > 0:
                    print(f"  - {user_id}")


async def main():
    """主函数"""
    # 检查配置文件
    config_path = "./config.yaml"
    if not os.path.exists(config_path):
        print(f"错误：配置文件 {config_path} 不存在")
        print("请确保在项目根目录下运行此脚本，且config.yaml文件存在")
        return
    
    # 创建数据生成器
    generator = FakeDataGenerator(config_path)
    
    try:
        # 初始化
        await generator.initialize()
        
        # 生成数据
        results = await generator.generate_all_data()
        
        # 打印摘要
        generator.print_summary(results)
        
    except Exception as e:
        print(f"数据生成过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())