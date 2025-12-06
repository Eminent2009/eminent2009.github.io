from flask import Flask, request, jsonify, render_template_string
import os
import json
from project_editor import ProjectHTMLManager, ProjectInfo

app = Flask(__name__)

# 初始化项目管理器
try:
    manager = ProjectHTMLManager("project.html")
except FileNotFoundError:
    # 如果文件不存在，创建一个空的基础文件
    with open("project.html", 'w', encoding='utf-8') as f:
        f.write('''<!DOCTYPE html>
<html>
<body>
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <!-- 加载更多按钮 -->
        <div class="text-center mt-16 col-span-1 md:col-span-2 lg:col-span-3">
            <button>加载更多</button>
        </div>
    </div>
</body>
</html>''')
    manager = ProjectHTMLManager("project.html")

# 读取HTML生成器页面
with open("project-card-generator.html", 'r', encoding='utf-8') as f:
    generator_html = f.read()


@app.route('/')
def index():
    """提供项目生成器页面"""
    return render_template_string(generator_html)


@app.route('/api/projects', methods=['GET'])
def list_projects():
    """获取所有项目列表"""
    projects = manager.list_projects()
    return jsonify({
        "success": True,
        "projects": projects
    })


@app.route('/api/projects', methods=['POST'])
def add_project():
    """添加新项目"""
    data = request.json

    try:
        project = ProjectInfo(
            title=data.get('title', ''),
            link=data.get('link', ''),
            category=data.get('category', ''),
            category_text=data.get('categoryText', ''),
            image_path=data.get('imagePath', ''),
            image_alt=data.get('imageAlt', ''),
            description=data.get('description', ''),
            tech_stack=data.get('techStack', [])
        )

        success = manager.add_project(project)
        return jsonify({
            "success": success,
            "message": "项目添加成功" if success else "项目添加失败"
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


@app.route('/api/projects/<title>', methods=['DELETE'])
def delete_project(title):
    """删除指定项目"""
    success = manager.remove_project(title)
    return jsonify({
        "success": success,
        "message": "项目删除成功" if success else "项目删除失败"
    })


@app.route('/api/projects/export', methods=['GET'])
def export_projects():
    """导出项目信息"""
    projects = manager.export_projects()
    return jsonify({
        "success": True,
        "projects": projects
    })


@app.route('/api/backup', methods=['POST'])
def restore_backup():
    """恢复备份"""
    backup_path = "project.html.backup"
    if os.path.exists(backup_path):
        with open(backup_path, 'r', encoding='utf-8') as f:
            content = f.read()
        with open("project.html", 'w', encoding='utf-8') as f:
            f.write(content)
        return jsonify({
            "success": True,
            "message": "备份恢复成功"
        })
    else:
        return jsonify({
            "success": False,
            "message": "备份文件不存在"
        }), 404


if __name__ == '__main__':
    # 修改网页生成器，添加API调用
    modified_html = generator_html.replace(
        '</script>',
        '''
        // 添加API交互功能
        async function saveToServer() {
            const formData = {
                title: document.getElementById('projectTitle').value,
                link: document.getElementById('projectLink').value,
                category: document.getElementById('projectCategory').value,
                categoryText: document.getElementById('categoryText').value || document.getElementById('customCategoryText').value,
                imagePath: document.getElementById('imagePath').value,
                imageAlt: document.getElementById('imageAlt').value,
                description: document.getElementById('projectDesc').value,
                techStack: techStacks
            };

            try {
                const response = await fetch('/api/projects', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });

                const result = await response.json();
                if (result.success) {
                    showToast('项目已保存到服务器！');
                } else {
                    showToast(result.message, 'error');
                }
            } catch (error) {
                showToast('保存失败：' + error.message, 'error');
            }
        }

        // 重写表单提交，添加保存到服务器功能
        document.getElementById('projectForm').addEventListener('submit', function(e) {
            e.preventDefault();

            // 原有生成代码逻辑
            // ... (保持原有代码)

            // 新增：保存到服务器
            saveToServer();
        });

        // 添加加载项目列表功能
        async function loadProjects() {
            try {
                const response = await fetch('/api/projects');
                const result = await response.json();
                if (result.success) {
                    const projects = result.projects;
                    const projectList = document.createElement('div');
                    projectList.className = 'mt-4 p-3 bg-gray-50 rounded-md';
                    projectList.innerHTML = `
                        <h4 class="text-sm font-medium mb-2">服务器上的项目 (${projects.length}):</h4>
                        <div class="flex flex-wrap gap-2">
                            ${projects.map(proj => `
                                <span class="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded flex items-center gap-1">
                                    ${proj}
                                    <button type="button" onclick="deleteProject('${proj}')" class="text-gray-500 hover:text-red-500">
                                        <i class="fa fa-times"></i>
                                    </button>
                                </span>
                            `).join('')}
                        </div>
                    `;

                    // 添加到表单区域
                    const form = document.getElementById('projectForm');
                    form.appendChild(projectList);
                }
            } catch (error) {
                console.error('加载项目列表失败:', error);
            }
        }

        // 删除项目
        async function deleteProject(title) {
            if (!confirm(`确定删除项目：${title}？`)) return;

            try {
                const response = await fetch(`/api/projects/${encodeURIComponent(title)}`, {
                    method: 'DELETE'
                });

                const result = await response.json();
                if (result.success) {
                    showToast('项目已删除！');
                    // 重新加载列表
                    loadProjects();
                } else {
                    showToast('删除失败：' + result.message, 'error');
                }
            } catch (error) {
                showToast('删除失败：' + error.message, 'error');
            }
        }

        // 页面加载时加载项目列表
        window.addEventListener('load', function() {
            loadProjects();
        });

        </script>'''
    )

    # 保存修改后的HTML
    with open("project-card-generator.html", 'w', encoding='utf-8') as f:
        f.write(modified_html)

    # 启动服务器
    app.run(debug=True, host='0.0.0.0', port=5000)