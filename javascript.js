// 全局变量
let blogs = [];
const blogsPerPage = 6;
let currentPage = 1;

// 获取元素
const sidebar = document.querySelector('.sidebar-sticky');
const blogsSection = document.getElementById('blogs');
const blogsContainer = document.getElementById('blogs-container');
const pagination = document.getElementById('pagination');

// 监听滚动事件
window.addEventListener('scroll', function() {
  // 获取博文区域的顶部位置
  const blogsTop = blogsSection.getBoundingClientRect().top;

  // 当滚动到博文区域时显示侧边栏
  if (blogsTop < window.innerHeight / 2) {
    sidebar.classList.add('show');
  } else {
    sidebar.classList.remove('show');
  }
});

// 从JSON文件加载博客数据
async function loadBlogs() {
  try {
    const response = await fetch('./blogs.json');
    blogs = await response.json();
    renderBlogs();
    renderPagination();
  } catch (error) {
    console.error('加载博客数据失败:', error);
  }
}

// 渲染博客卡片
function renderBlogs() {
  // 清空容器
  blogsContainer.innerHTML = '';

  // 计算当前页的博客索引范围
  const startIndex = (currentPage - 1) * blogsPerPage;
  const endIndex = startIndex + blogsPerPage;
  const currentBlogs = blogs.slice(startIndex, endIndex);

  // 生成博客卡片
  currentBlogs.forEach(blog => {
    const blogCard = document.createElement('div');
    blogCard.className = 'bg-white rounded-lg shadow-md overflow-hidden card-hover';
    blogCard.innerHTML = `
      <div class="aspect-square overflow-hidden">
        <img src="${blog.image}" alt="${blog.title}" 
             class="w-full h-full object-cover transition-transform duration-500 hover:scale-105">
      </div>
      <div class="p-6">
        <h3 class="text-xl font-semibold mb-2 hover:text-primary transition-colors">
          ${blog.title}
        </h3>
        <p class="text-gray-600 mb-4 line-clamp-3">
          ${blog.description}
        </p>
        <div class="flex justify-between items-center">
          <span class="text-sm text-gray-500">${blog.date}</span>
          <a href="${blog.url}" class="inline-flex items-center text-primary font-medium hover:underline" onclick="return checkBlogExists('${blog.url}')">
            阅读更多 <i class="fa-solid fa-arrow-right ml-2 text-sm"></i>
          </a>
        </div>
      </div>
    `;
    blogsContainer.appendChild(blogCard);
  });
}

// 渲染分页控件
function renderPagination() {
  // 清空分页容器
  pagination.innerHTML = '';

  // 计算总页数
  const totalPages = Math.ceil(blogs.length / blogsPerPage);

  // 如果只有一页，不需要分页
  if (totalPages <= 1) return;

  // 上一页按钮
  const prevButton = document.createElement('button');
  prevButton.className = `px-4 py-2 rounded-lg border ${currentPage === 1 ? 'opacity-50 cursor-not-allowed' : 'hover:bg-primary hover:text-white transition-colors'}`;
  prevButton.innerHTML = '<i class="fa-solid fa-chevron-left"></i>';
  prevButton.disabled = currentPage === 1;
  prevButton.addEventListener('click', () => {
    if (currentPage > 1) {
      currentPage--;
      renderBlogs();
      renderPagination();
      // 滚动到博客区域顶部
      blogsSection.scrollIntoView({ behavior: 'smooth' });
    }
  });
  pagination.appendChild(prevButton);

  // 页码按钮
  for (let i = 1; i <= totalPages; i++) {
    const pageButton = document.createElement('button');
    pageButton.className = `px-4 py-2 rounded-lg border ${currentPage === i ? 'bg-primary text-white' : 'hover:bg-primary hover:text-white transition-colors'}`;
    pageButton.textContent = i;
    pageButton.addEventListener('click', () => {
      currentPage = i;
      renderBlogs();
      renderPagination();
      // 滚动到博客区域顶部
      blogsSection.scrollIntoView({ behavior: 'smooth' });
    });
    pagination.appendChild(pageButton);
  }

  // 下一页按钮
  const nextButton = document.createElement('button');
  nextButton.className = `px-4 py-2 rounded-lg border ${currentPage === totalPages ? 'opacity-50 cursor-not-allowed' : 'hover:bg-primary hover:text-white transition-colors'}`;
  nextButton.innerHTML = '<i class="fa-solid fa-chevron-right"></i>';
  nextButton.disabled = currentPage === totalPages;
  nextButton.addEventListener('click', () => {
    if (currentPage < totalPages) {
      currentPage++;
      renderBlogs();
      renderPagination();
      // 滚动到博客区域顶部
      blogsSection.scrollIntoView({ behavior: 'smooth' });
    }
  });
  pagination.appendChild(nextButton);
}

// 检查博文页面是否存在
async function checkBlogExists(url) {
  try {
    const response = await fetch(url, { method: 'HEAD' });
    if (!response.ok) {
      window.location.href = './404.html';
      return false;
    }
    return true;
  } catch (error) {
    // 网络错误或其他错误，跳转到404页面
    console.error('检查博客页面存在失败:', error);
    // 不跳转404，允许浏览器尝试访问
    return true;
  }
}

// 页面加载完成后执行
window.addEventListener('DOMContentLoaded', () => {
  loadBlogs();
  // 初始化触发一次滚动检查
  window.dispatchEvent(new Event('scroll'));
});
