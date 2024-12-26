def extract_article_info(self, xml_content):
    """从XML中提取文章信息"""
    try:
        articles = []
        root = ET.fromstring(xml_content)
        print("\n开始解析XML内容...")
        
        # 查找所有包含文章信息的LinearLayout节点
        article_groups = root.findall(".//node[@resource-id='com.tencent.mm:id/cpb']")
        if not article_groups:
            print("未找到文章组，尝试查找其他可能的节点...")
            article_groups = root.findall(".//node[@class='android.widget.LinearLayout']")
        
        print(f"找到 {len(article_groups)} 个文章组")
        
        current_date = None
        max_retries = 3
        
        for group in article_groups:
            try:
                # 查找日期节点
                date_node = group.find(".//node[@resource-id='com.tencent.mm:id/cp2']")
                if date_node is not None and 'text' in date_node.attrib:
                    current_date = date_node.attrib['text']
                    print(f"\n找到日期: {current_date}")
                else:
                    print("未找到日期节点，尝试其他日期格式...")
                    # 尝试查找其他可能的日期节点
                    all_text_nodes = group.findall(".//node[@class='android.widget.TextView']")
                    for node in all_text_nodes:
                        if 'text' in node.attrib:
                            text = node.attrib['text']
                            if any(month in text for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']):
                                current_date = text
                                print(f"找到替代日期节点: {current_date}")
                                break
                
                # 查找文章节点
                article_nodes = group.findall(".//node[@resource-id='com.tencent.mm:id/ek8']")
                if not article_nodes:
                    print("未找到文章节点，尝试其他可能的节点...")
                    article_nodes = group.findall(".//node[@class='android.widget.LinearLayout']")
                
                for node in article_nodes:
                    article = {}
                    retry_count = 0
                    
                    while retry_count < max_retries:
                        try:
                            # 设置发布日期
                            if current_date:
                                try:
                                    date_str = current_date.strip()
                                    try:
                                        date_obj = datetime.datetime.strptime(date_str, "%b %d, %Y")
                                    except ValueError:
                                        date_str = f"{date_str} {datetime.datetime.now().year}"
                                        date_obj = datetime.datetime.strptime(date_str, "%b %d %Y")
                                    
                                    article['publish_date'] = date_obj.strftime("%Y-%m-%d")
                                    print(f"解析日期: {article['publish_date']}")
                                except Exception as e:
                                    print(f"日期解析错误: {e}")
                                    article['publish_date'] = time.strftime("%Y-%m-%d")
                                
                                # 查找标题节点
                                title_node = node.find(".//node[@resource-id='com.tencent.mm:id/ek_']")
                                if title_node is not None and 'text' in title_node.attrib:
                                    article['title'] = title_node.attrib['text']
                                    print(f"找到文章标题: {article['title']}")
                                else:
                                    # 尝试查找其他可能的标题节点
                                    title_nodes = node.findall(".//node[@class='android.widget.TextView']")
                                    for t_node in title_nodes:
                                        if 'text' in t_node.attrib and len(t_node.attrib['text']) > 10:
                                            article['title'] = t_node.attrib['text']
                                            print(f"找到替代标题节点: {article['title']}")
                                            break
                                
                                # 查找阅读量和点赞数节点
                                stats_node = node.find(".//node[@resource-id='com.tencent.mm:id/eka']")
                                if stats_node is not None and 'text' in stats_node.attrib:
                                    stats_text = stats_node.attrib['text']
                                    print(f"找到统计信息: {stats_text}")
                                    parts = stats_text.strip().split()
                                    if len(parts) >= 1:
                                        reads = parts[0]
                                        article['reads'] = int(reads.replace(',', ''))
                                        
                                        if len(parts) >= 4 and parts[2].isdigit():
                                            likes = parts[2]
                                            article['likes'] = int(likes)
                                        else:
                                            article['likes'] = 0
                                else:
                                    # 尝试查找其他可能的统计信息节点
                                    stats_nodes = node.findall(".//node[@class='android.widget.TextView']")
                                    for s_node in stats_nodes:
                                        if 'text' in s_node.attrib and 'reads' in s_node.attrib['text'].lower():
                                            stats_text = s_node.attrib['text']
                                            print(f"找到替代统计信息节点: {stats_text}")
                                            parts = stats_text.strip().split()
                                            if len(parts) >= 1:
                                                reads = parts[0]
                                                article['reads'] = int(reads.replace(',', ''))
                                                article['likes'] = 0
                                                break
                                
                                # 检查是否获取到所有必要信息
                                required_fields = {'title', 'publish_date', 'reads', 'likes'}
                                if all(field in article for field in required_fields):
                                    articles.append(article)
                                    print(f"成功提取文章信息: {article}")
                                    break
                                
                                print("信息不完整，等待1秒后重试...")
                                time.sleep(1)
                                retry_count += 1
                                
                            except Exception as e:
                                print(f"处理节点时出错: {e}")
                                retry_count += 1
                                time.sleep(1)
                
            except Exception as e:
                print(f"处理文章组时出错: {e}")
                continue
            
        print(f"\n总共提取到 {len(articles)} 篇文章的信息")
        return articles
            
    except Exception as e:
        print(f"提取文章信息时出错: {e}")
        return [] 