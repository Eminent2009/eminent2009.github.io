import os
import re
import json
from dataclasses import dataclass
from typing import List, Optional, Dict


@dataclass
class ProjectInfo:
    """项目信息数据类"""
    title: str
    link: str
    category: str
    category_text: str
    image_path: str
    image_alt: str
    description: str
    tech_stack: List[str]

    def to_html(self) -> str:
        """生成项目卡片HTML代码"""
        # 生成技术栈标签
        tech_tags = ""
        for tech in self.tech_stack:
            tech_tags += f'                                <span class="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">{tech}</span>\n'

        # 生成完整HTML
        html_template = f'''                <!-- 项目：{self.title} -->
                <a href="{self.link}">
                    <div class="project-card visible bg-white rounded-xl shadow-md overflow-hidden hover-lift"
                        data-category="{self.category}">
                        <div class="h-56 overflow-hidden">
                            <img src="{self.image_path}" alt="{self.image_alt}" class="w-full h-full object-cover">
                        </div>
                        <div class="p-6">
                            <div class="flex justify-between items-center mb-3">
                                <span
                                    class="text-sm font-medium bg-blue-100 text-primary px-3 py-1 rounded-full">{self.category_text}</span>
                                <div class="flex space-x-2">
                                    <a href="{self.link}"
                                        class="text-gray-500 hover:text-primary transition-colors">
                                        <i class="fa fa-link"></i>
                                    </a>
                                </div>
                            </div>
                            <h3 class="text-xl font-semibold mb-2">{self.title}</h3>
                            <!-- 添加明确的类名确保描述可见 -->
                            <p class="project-description text-gray-600 text-sm mb-4">
                                {self.description}
                            </p>
                            <div class="flex flex-wrap gap-2">
{tech_tags}                            </div>
                        </div>
                    </div>
                </a>'''
        return html_template


class ProjectHTMLManager:
    """项目HTML文件管理器"""

    def __init__(self, file_path: str = "project.html"):
        self.file_path = file_path
        self.backup_suffix = ".backup"

        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件 {file_path} 不存在")

        # 创建备份
        self.create_backup()

    def create_backup(self):
        """创建文件备份"""
        backup_path = self.file_path + self.backup_suffix
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"已创建备份文件: {backup_path}")

    def get_insert_position(self, content: str) -> int:
        """找到插入位置（加载更多按钮之前）"""
        # 匹配加载更多按钮的注释
        marker = '                <!-- 加载更多按钮 -->'
        pos = content.find(marker)
        if pos == -1:
            # 备用匹配：直接匹配加载更多按钮的div
            marker = '                <div class="text-center mt-16 col-span-1 md:col-span-2 lg:col-span-3">'
            pos = content.find(marker)

        if pos == -1:
            # 最后备选：找到项目列表的grid容器末尾
            grid_pattern = r'<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">([\s\S]*?)</div>'
            match = re.search(grid_pattern, content)
            if match:
                pos = match.end(1) - len('\n                </div>')
            else:
                raise ValueError("未找到合适的插入位置，请检查文件格式")

        return pos

    def add_project(self, project: ProjectInfo) -> bool:
        """添加项目到HTML文件"""
        try:
            # 读取文件内容
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 生成项目HTML
            project_html = project.to_html()

            # 找到插入位置
            insert_pos = self.get_insert_position(content)

            # 插入新项目
            new_content = (
                    content[:insert_pos] +
                    project_html + '\n' +
                    content[insert_pos:]
            )

            # 写入文件
            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            print(f"✅ 项目 '{project.title}' 添加成功！")
            return True

        except Exception as e:
            print(f"❌ 添加项目失败: {str(e)}")
            return False

    def remove_project(self, project_title: str) -> bool:
        """根据标题删除项目"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 匹配项目卡片的正则表达式
            pattern = rf'<!-- 项目：{re.escape(project_title)} -->[\s\S]*?</a>'
            new_content = re.sub(pattern, '', content, count=1)

            if new_content == content:
                print(f"⚠️ 未找到项目: {project_title}")
                return False

            with open(self.file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            print(f"✅ 项目 '{project_title}' 删除成功！")
            return True

        except Exception as e:
            print(f"❌ 删除项目失败: {str(e)}")
            return False

    def list_projects(self) -> List[str]:
        """列出所有项目标题"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 提取所有项目标题
            pattern = r'<!-- 项目：(.*?) -->'
            projects = re.findall(pattern, content)
            return projects

        except Exception as e:
            print(f"❌ 读取项目列表失败: {str(e)}")
            return []

    def export_projects(self, export_path: str = "projects.json"):
        """导出所有项目信息到JSON文件"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 匹配所有项目卡片
            pattern = r'<!-- 项目：(.*?) -->[\s\S]*?<a href="(.*?)">[\s\S]*?data-category="(.*?)">[\s\S]*?bg-blue-100 text-primary px-3 py-1 rounded-full">(.*?)</span>[\s\S]*?<img src="(.*?)" alt="(.*?)"[\s\S]*?<h3 class="text-xl font-semibold mb-2">(.*?)</h3>[\s\S]*?<p class="project-description text-gray-600 text-sm mb-4">([\s\S]*?)</p>[\s\S]*?<div class="flex flex-wrap gap-2">([\s\S]*?)</div>'

            matches = re.findall(pattern, content)
            projects = []

            for match in matches:
                # 解析技术栈
                tech_stack = re.findall(
                    r'<span class="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">(.*?)</span>', match[8])

                project = {
                    "title": match[0],
                    "link": match[1],
                    "category": match[2],
                    "category_text": match[3],
                    "image_path": match[4],
                    "image_alt": match[5],
                    "description": match[6].strip(),
                    "tech_stack": tech_stack
                }
                projects.append(project)

            # 保存到JSON文件
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(projects, f, ensure_ascii=False, indent=2)

            print(f"✅ 项目信息已导出到: {export_path}")
            return projects

        except Exception as e:
            print(f"❌ 导出项目失败: {str(e)}")
            return []


def interactive_mode():
    """交互式操作模式"""
    print("=" * 50)
    print("      项目HTML文件管理器 v1.0")
    print("=" * 50)

    # 获取文件路径
    file_path = input("请输入project.html文件路径 (默认: project.html): ").strip() or "project.html"

    try:
        manager = ProjectHTMLManager(file_path)
    except FileNotFoundError as e:
        print(f"错误: {e}")
        return

    while True:
        print("\n请选择操作:")
        print("1. 添加新项目")
        print("2. 删除项目")
        print("3. 列出所有项目")
        print("4. 导出项目信息")
        print("5. 恢复备份")
        print("0. 退出")

        choice = input("\n输入操作编号: ").strip()

        if choice == "1":
            # 添加新项目
            print("\n--- 添加新项目 ---")
            title = input("项目标题: ").strip()
            link = input("项目链接 (例如: ./projects/xxx.html): ").strip()
            category = input("项目分类标识 (例如: web): ").strip()
            category_text = input("分类显示文本 (例如: 网站): ").strip()
            image_path = input("图片路径 (例如: ./imgs/dmq.png): ").strip()
            image_alt = input("图片描述: ").strip()
            description = input("项目描述: ").strip()
            tech_input = input("技术栈 (逗号分隔): ").strip()
            tech_stack = [t.strip() for t in tech_input.split(',') if t.strip()]

            project = ProjectInfo(
                title=title,
                link=link,
                category=category,
                category_text=category_text,
                image_path=image_path,
                image_alt=image_alt,
                description=description,
                tech_stack=tech_stack
            )

            manager.add_project(project)

        elif choice == "2":
            # 删除项目
            print("\n--- 删除项目 ---")
            projects = manager.list_projects()
            if not projects:
                print("暂无项目")
                continue

            print("现有项目:")
            for i, proj in enumerate(projects, 1):
                print(f"{i}. {proj}")

            proj_choice = input("输入要删除的项目序号或标题: ").strip()

            if proj_choice.isdigit():
                idx = int(proj_choice) - 1
                if 0 <= idx < len(projects):
                    manager.remove_project(projects[idx])
                else:
                    print("无效序号")
            else:
                manager.remove_project(proj_choice)

        elif choice == "3":
            # 列出项目
            print("\n--- 项目列表 ---")
            projects = manager.list_projects()
            if projects:
                for i, proj in enumerate(projects, 1):
                    print(f"{i}. {proj}")
                print(f"\n总计: {len(projects)} 个项目")
            else:
                print("暂无项目")

        elif choice == "4":
            # 导出项目
            print("\n--- 导出项目 ---")
            export_path = input("导出文件路径 (默认: projects.json): ").strip() or "projects.json"
            manager.export_projects(export_path)

        elif choice == "5":
            # 恢复备份
            print("\n--- 恢复备份 ---")
            confirm = input("确定要恢复备份吗？(y/N): ").strip().lower()
            if confirm == 'y':
                backup_path = file_path + ".backup"
                if os.path.exists(backup_path):
                    with open(backup_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print("✅ 备份恢复成功！")
                else:
                    print("❌ 备份文件不存在")

        elif choice == "0":
            print("\n👋 再见！")
            break

        else:
            print("❌ 无效选择，请重新输入")


if __name__ == "__main__":
    interactive_mode()