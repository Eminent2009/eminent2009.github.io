// 全局变量
let blogs = [];          // blogs.json 的原始数据
let filteredBlogs = [];  // 当前筛选后的数据
const blogsPerPage = 6;
let currentPage = 1;

// 当前筛选条件，'all' 表示不限
const filters = {
  type: 'all',
  tag: 'all',
  date: 'all'
};

// 获取元素
const sidebar = document.querySelector('.sidebar-sticky');
const blogsSection = document.getElementById('blogs');
const blogsContainer = document.getElementById('blogs-container');
const pagination = document.getElementById('pagination');
const typeContainer = document.getElementById('filter-type');
const tagContainer = document.getElementById('filter-tag');
const dateSelect = document.getElementById('filter-date');
const filterCount = document.getElementById('filter-count');
const clearButton = document.getElementById('clear-filters');

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
    renderFilterOptions();
    applyFilters();
  } catch (error) {
    console.error('加载博客数据失败:', error);
  }
}

// 数组去重，保留原有顺序
function unique(values) {
  return [...new Set(values)];
}

// 生成筛选胶囊的类名：选中态用主色实心，未选中态为描边
function chipClass(isActive) {
  return 'px-3.5 py-1.5 rounded-full text-sm border transition-colors ' +
    (isActive
      ? 'bg-primary text-white border-primary'
      : 'bg-white text-gray-600 border-gray-200 hover:border-primary hover:text-primary');
}

// 根据数据生成类型、标签胶囊和日期下拉选项
function renderFilterOptions() {
  // 类型：取所有数据的 type，缺省归入“未分类”
  const typeOptions = unique(blogs.map(blog => blog.type || '未分类'));
  buildChips(typeContainer, typeOptions, 'type');

  // 标签：把所有文章的 tags 摊平后去重
  const tagOptions = unique(blogs.flatMap(blog => Array.isArray(blog.tags) ? blog.tags : []));
  buildChips(tagContainer, tagOptions, 'tag');

  // 日期：按年月去重并倒序，最近的月份排在最前
  const monthOptions = unique(blogs
    .map(blog => (blog.date || '').slice(0, 7))
    .filter(Boolean))
    .sort()
    .reverse();

  dateSelect.innerHTML = '<option value="all">全部时间</option>';
  monthOptions.forEach(month => {
    const [year, mon] = month.split('-');
    const option = document.createElement('option');
    option.value = month;
    option.textContent = `${year} 年 ${Number(mon)} 月`;
    dateSelect.appendChild(option);
  });

  updateFilterUI();
}

// 生成一组筛选胶囊（含“全部”）
function buildChips(container, values, group) {
  container.innerHTML = '';

  const options = [{ value: 'all', label: '全部' }]
    .concat(values.map(value => ({ value, label: value })));

  options.forEach(option => {
    const chip = document.createElement('button');
    chip.type = 'button';
    chip.dataset.value = option.value;
    chip.textContent = option.label;
    chip.className = chipClass(false);
    chip.setAttribute('aria-pressed', 'false');

    chip.addEventListener('click', () => {
      filters[group] = option.value;
      currentPage = 1; // 切换条件后回到第一页
      updateFilterUI();
      applyFilters();
    });

    container.appendChild(chip);
  });
}

// 同步筛选控件的选中状态
function updateFilterUI() {
  setChipState(typeContainer, filters.type);
  setChipState(tagContainer, filters.tag);
  dateSelect.value = filters.date;

  // 有任何条件生效时才显示“清除筛选”
  const hasFilter = filters.type !== 'all' || filters.tag !== 'all' || filters.date !== 'all';
  clearButton.style.display = hasFilter ? 'inline-flex' : 'none';
}

// 把一组胶囊中与当前值相同的项标记为选中
function setChipState(container, activeValue) {
  container.querySelectorAll('button[data-value]').forEach(chip => {
    const isActive = chip.dataset.value === activeValue;
    chip.className = chipClass(isActive);
    chip.setAttribute('aria-pressed', String(isActive));
  });
}

// 按当前条件筛选，并重新渲染列表与分页
function applyFilters() {
  filteredBlogs = blogs.filter(blog => {
    const type = blog.type || '未分类';
    const tags = Array.isArray(blog.tags) ? blog.tags : [];
    const month = (blog.date || '').slice(0, 7);

    // 类型、标签、日期三个条件同时满足才保留
    return (filters.type === 'all' || type === filters.type)
      && (filters.tag === 'all' || tags.includes(filters.tag))
      && (filters.date === 'all' || month === filters.date);
  });

  // 数据变少时，避免停留在不存在的页码
  const totalPages = Math.max(1, Math.ceil(filteredBlogs.length / blogsPerPage));
  if (currentPage > totalPages) currentPage = totalPages;

  filterCount.textContent = filteredBlogs.length;
  renderBlogs();
  renderPagination();
}

// 重置所有筛选条件
function resetFilters() {
  filters.type = 'all';
  filters.tag = 'all';
  filters.date = 'all';
  currentPage = 1;
  updateFilterUI();
  applyFilters();
}

// 日期下拉变化
dateSelect.addEventListener('change', () => {
  filters.date = dateSelect.value;
  currentPage = 1;
  updateFilterUI();
  applyFilters();
});

// 清除筛选
clearButton.addEventListener('click', resetFilters);

// 渲染博客卡片
function renderBlogs() {
  // 清空容器
  blogsContainer.innerHTML = '';

  // 计算当前页的博客索引范围（使用筛选后的数据）
  const startIndex = (currentPage - 1) * blogsPerPage;
  const endIndex = startIndex + blogsPerPage;
  const currentBlogs = filteredBlogs.slice(startIndex, endIndex);

  // 没有符合条件的数据时显示空状态
  if (currentBlogs.length === 0) {
    blogsContainer.innerHTML = `
      <div class="col-span-full flex flex-col items-center justify-center py-16 text-center">
        <i class="fa-regular fa-folder-open text-3xl text-gray-300 mb-4"></i>
        <p class="text-gray-500 mb-4">没有找到符合条件的内容</p>
        <button id="empty-clear" type="button"
                class="px-4 py-2 rounded-lg bg-primary text-white text-sm hover:bg-primary/90 transition-colors">
          清除筛选
        </button>
      </div>
    `;
    document.getElementById('empty-clear').addEventListener('click', resetFilters);
    return;
  }

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
        <span class="inline-block text-xs px-2 py-0.5 rounded-full bg-primary/10 text-primary mb-2">
          ${blog.type || '未分类'}
        </span>
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

  // 计算总页数（按筛选后的数量）
  const totalPages = Math.ceil(filteredBlogs.length / blogsPerPage);

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
