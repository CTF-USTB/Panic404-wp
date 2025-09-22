document.addEventListener('DOMContentLoaded', function() {
  var calendarEl = document.getElementById('calendar');
  if (!calendarEl) return; // 不是 index.md 就直接返回
  var calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'dayGridMonth',
    validRange: function(nowDate) {
    let endDate = new Date();
    endDate.setDate(endDate.getDate() + 7);
    return {
        start: '2025-09-01',
        end: endDate
    }; // 可预览未来7天的事件
    },
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'dayGridMonth'
    },
    events: './data/calendar.json', // 加载 WP JSON 数据
    eventContent: function(arg) {
      // 自定义事件显示样式
      let color = '#fff'; // 默认白色
      let type = "wp";
      if (!arg.event.type) {
        if (arg.event.extendedProps.status === 'done') {
            type = "";
        }
      }
      return { html: `<div style="color:${color}; font-weight:bold">${arg.event.title + " " + type}</div>` };
    },
    eventDidMount: function(info) {
      let status = info.event.extendedProps.status;
      let color, textColor;

      // 从 url 中提取方向
      let url = info.event.url || "";
      let direction = url.split("/")[0].toLowerCase(); // web/misc/pwn/...

      // 定义方向对应的颜色
      const directionColors = {
          web:    '#3498db', // 蓝
          misc:   '#9b59b6', // 紫
          pwn:    '#e74c3c', // 红
          reverse:'#27ae60', // 绿
          crypto: '#34495e', // 深灰蓝
          ai:     '#e67e22'  // 橙
      };

      if(!info.event.extendedProps.desc) {
        if (directionColors[direction]) {
              // 如果有方向，就按方向颜色
              color = directionColors[direction];
              // 让文字颜色自动根据背景深浅决定
              textColor = (direction === 'crypto') ? '#000' : '#fff';
          } else {
              // 默认灰
              color = '#9ca3af';
              textColor = '#fff';
          }
      } else {
          // 有 desc = 特殊事件
          color = '#f1c40f'; // 亮黄色（特殊事件）
          textColor = '#fff';
      }

      let title = info.event.extendedProps.desc ? info.event.extendedProps.desc : (info.event.url ? info.event.url : "wp");
      // 鼠标悬浮显示完整标题
      info.el.title = title;
      info.el.style.backgroundColor = color;
      info.el.style.borderColor = color;
      info.el.style.color = textColor;
      info.el.style.borderRadius = '4px';
      info.el.style.fontWeight = 'bold';
      info.el.style.padding = '2px 4px';
      info.el.style.cursor = 'pointer';
    },
    // 点击事件跳转
    eventClick: function(info) {
      if (info.event.extendedProps.status === 'done' && info.event.url) {
        window.location.href = info.event.url;  // 跳转到对应 wp 页面
      }
    }
  });
  calendar.render();
});
