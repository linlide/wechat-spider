import os
import sys
import json
import time
import subprocess
import xml.etree.ElementTree as ET
import datetime

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from utils.mysqldb import MysqlDB

class WeChatCrawler:
    def __init__(self):
        """初始化爬虫"""
        # 数据库配置
        db_config = {
            'ip': 'localhost',
            'port': 3306,
            'db': 'wechat',
            'user': 'root',
            'passwd': ''
        }
        self.db = MysqlDB(**db_config)
        self.processed_articles = set()  # 用于存储已处理的文章标题，防止重复

    def dump_ui_hierarchy(self):
        """获取当前屏幕的UI层次结构"""
        try:
            # 使用uiautomator dump获取当前屏幕信息
            subprocess.run(['adb', 'shell', 'uiautomator', 'dump', '/sdcard/window_dump.xml'])
            # 将文件拉取到本地
            xml_path = os.path.join(os.getcwd(), 'window_dump.xml')
            subprocess.run(['adb', 'pull', '/sdcard/window_dump.xml', xml_path])
            print(f"\nXML文件保存路径: {xml_path}")
            
            with open(xml_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"\nXML文件内容预览 (前500字符):\n{content[:500]}...")
                return content
        except Exception as e:
            print(f"获取屏幕内容失败: {e}")
            return None

    def scroll_screen(self):
        """滑动屏幕"""
        try:
            # 获取屏幕尺寸
            screen_size = subprocess.check_output(['adb', 'shell', 'wm', 'size']).decode().strip()
            width, height = map(int, screen_size.split(': ')[1].split('x'))
            
            # 计算滑动的起点和终点（从屏幕3/4处滑动到1/4处）
            start_y = int(height * 0.75)
            end_y = int(height * 0.25)
            x = width // 2

            # 执行滑动
            subprocess.run([
                'adb', 'shell', 'input', 'swipe',
                str(x), str(start_y),
                str(x), str(end_y),
                '500'  # 滑动时间(ms)
            ])
            time.sleep(1)  # 等待内容加载
            return True
        except Exception as e:
            print(f"滑动屏幕失败: {e}")
            return False

    def extract_article_info(self, xml_content):
        """从XML中提取文章信息"""
        try:
            articles = []
            root = ET.fromstring(xml_content)
            print("\n开始解析XML内容...")
            
            # 查找所有包含文章信息的节点
            article_groups = root.findall(".//node[@resource-id='com.tencent.mm:id/cpb']")
            print(f"找到 {len(article_groups)} 个文章组")
            
            current_date = None
            for group in article_groups:
                try:
                    # 查找日期节点
                    date_node = group.find(".//node[@resource-id='com.tencent.mm:id/cp2']")
                    if date_node is not None and 'text' in date_node.attrib:
                        current_date = date_node.attrib['text']
                        print(f"\n找到日期: {current_date}")
                    
                    # 查找文章节点
                    article_nodes = group.findall(".//node[@resource-id='com.tencent.mm:id/ek8']")
                    for node in article_nodes:
                        article = {}
                        
                        # 设置发布日期
                        if current_date:
                            article['publish_date'] = current_date
                            print(f"设置发布日期: {article['publish_date']}")
                        
                        # 查找标题节点
                        title_node = node.find(".//node[@resource-id='com.tencent.mm:id/ek_']")
                        if title_node is not None and 'text' in title_node.attrib:
                            article['title'] = title_node.attrib['text']
                            print(f"找到文章标题: {article['title']}")
                        
                        # 查找阅读量和点赞数节点
                        stats_node = node.find(".//node[@resource-id='com.tencent.mm:id/eka']")
                        if stats_node is not None and 'text' in stats_node.attrib:
                            stats_text = stats_node.attrib['text']
                            print(f"找到统计信息: {stats_text}")
                            # 格式示例: "1818 reads  15 likes  "
                            parts = stats_text.strip().split()
                            if len(parts) >= 1:  # 至少有阅读数
                                reads = parts[0]  # 阅读数
                                article['reads'] = int(reads.replace(',', ''))
                                
                                # 检查是否有点赞数
                                if len(parts) >= 4 and parts[2].isdigit():
                                    likes = parts[2]  # 点赞数
                                    article['likes'] = int(likes)
                                else:
                                    article['likes'] = 0  # 如果没有点赞数,设为0
                                    
                                print(f"解析后的数据 - 阅读量: {article['reads']}, 点赞数: {article['likes']}")
                        
                        # 如果收集到完整信息，添加到文章列表
                        required_fields = {'title', 'publish_date', 'reads', 'likes'}
                        if all(field in article for field in required_fields):
                            articles.append(article)
                            print(f"成功提取文章信息: {article}")
                        else:
                            missing = required_fields - set(article.keys())
                            print(f"文章信息不完整，缺少字段: {missing}。当前收集到的字段: {list(article.keys())}")
                
                except Exception as e:
                    print(f"处理文章节点时出错: {e}")
                    continue
            
            print(f"\n总共提取到 {len(articles)} 篇文章的信息")
            return articles
        except Exception as e:
            print(f"提取文章信息时出错: {e}")
            return []

    def save_to_db(self, articles):
        """保存文章信息到数据库"""
        try:
            print("\n开始保存文章信息到数据库...")
            for article in articles:
                try:
                    # 检查是否已经处理过这篇文章
                    if article['title'] in self.processed_articles:
                        print(f"文章已处理过，跳过: {article['title']}")
                        continue

                    # 生成唯一ID
                    unique_id = f"id_{int(time.time())}_{hash(article['title']) % 10000:04d}"

                    # 使用参数化查询
                    article_sql = """
                        INSERT INTO wechat.wechat_topic (
                            uniqueid, title, origin_title, read_num, like_num, 
                            publish_time, create_time, update_time, available,
                            words, url, avatar, abstract, content, source, wechat_id
                        ) VALUES (
                            %s, %s, %s, %s, %s,
                            %s, NOW(6), NOW(6), 'true',
                            0, '', '', '', '', '', 1
                        );
                    """
                    
                    params = (
                        unique_id,
                        article['title'],
                        article['title'],
                        article['reads'],
                        article['likes'],
                        article['publish_date']
                    )

                    # 实际保存到数据库
                    if self.db.add(article_sql, params):
                        # 添加到已处理集合
                        self.processed_articles.add(article['title'])
                        print(f"成功保存文章: {article['title']}")
                    else:
                        print(f"保存文章失败: {article['title']}")
                        print(f"SQL语句: \n{article_sql}")
                        print(f"参数: {params}")

                except Exception as e:
                    print(f"处理单篇文章时出错: {e}")
                    print(f"文章数据: {article}")
                    continue

        except Exception as e:
            print(f"保存到数据库时出错: {e}")
            print(f"出错的SQL语句: \n{article_sql}")
            print(f"参数: {params}")

    def run(self):
        """运行爬虫"""
        print("\n=== 启动微信文章爬虫 ===")
        print("请确保当前页面显示的是微信公众号文章列表")
        while True:
            try:
                # 获取当前屏幕信息
                print("\n正在获取屏幕内容...")
                xml_content = self.dump_ui_hierarchy()
                if not xml_content:
                    print("获取屏幕内容失败，重试...")
                    continue

                # 提取文章信息
                print("\n正在提取文章信息...")
                articles = self.extract_article_info(xml_content)
                if articles:
                    print(f"\n找到 {len(articles)} 篇文章，准备保存...")
                    # 保存到数据库
                    self.save_to_db(articles)
                else:
                    print("\n当前屏幕未找到文章信息")

                # 滑动屏幕
                print("\n正在滑动屏幕...")
                if not self.scroll_screen():
                    print("滑动屏幕失败，停止运行")
                    break

                # 简单的防爬延迟
                time.sleep(2)

            except KeyboardInterrupt:
                print("\n\n收到停止信号，正在停止爬虫...")
                break
            except Exception as e:
                print(f"\n运行出错: {e}")
                time.sleep(5)

if __name__ == "__main__":
    crawler = WeChatCrawler()
    crawler.run() 