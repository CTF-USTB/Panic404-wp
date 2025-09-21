document.addEventListener('DOMContentLoaded', function() {
  var calendarEl = document.getElementById('calendar');
  if (!calendarEl) return; // 不是 index.md 就直接返回
  var calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'dayGridMonth',
    validRange: function(nowDate) {
    let endDate = new Date();
    endDate.setDate(endDate.getDate() + 6);
    return {
        start: '2025-09-01',
        end: endDate
    }; // 可预览未来6天的事件
    },
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'dayGridMonth'
    },
    events: '/data/schedule.json', // 加载 WP JSON 数据
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
        // 根据状态修改整个事件块样式
        let status = info.event.extendedProps.status;
        let color, textColor;
        if(!info.event.type) {
            if (status === 'done') {
                // color = '#4CAF50';
                color = '#4ecd7cff';    // 亮绿色
                textColor = '#fff';
            } else if (status === 'pending') {
                const tomorrow = new Date();
                tomorrow.setHours(0, 0, 0, 0);
                tomorrow.setDate(tomorrow.getDate() + 1);
                if (info.event.start < tomorrow) {
                    color = '#dc2626';    // 暗红
                    textColor = '#fff';
                } else {
                    color = '#9ca3af';    // 灰色
                    textColor = '#fff';
                }
            } else {
                color = '#9ca3af';    // 灰色
                textColor = '#fff';
            }
        } else {
            // 如果有 type 字段，表示是节假日或特殊事件
            color = '#fbbf24'; // 黄色
            textColor = '#000';
        }
        // 鼠标悬浮显示完整标题
        info.el.title = info.event.title + " wp";
        info.el.style.backgroundColor = color;
        info.el.style.borderColor = color;
        info.el.style.color = textColor;
        info.el.style.borderRadius = '4px';
        info.el.style.fontWeight = 'bold';
        info.el.style.padding = '2px 4px';
        info.el.style.cursor = 'pointer'; // 提示可点击
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
