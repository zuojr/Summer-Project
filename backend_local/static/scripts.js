const API_BASE = '';
let previousPage = 'home-page';
let recommendSpots = [], recommendIndex = 0, selectedIds = [];
let itineraryItems = [];

function showPage(id) {
  document.querySelectorAll('.container').forEach(div => {
    div.style.display = div.id === id ? 'block' : 'none';
  });
  previousPage = id;
}

function goBack() { showPage(previousPage); }
function goHome() { showPage('home-page'); }

// 1. 搜索
async function handleSearch(e) {
  if (e.key !== 'Enter') return;
  const dest = e.target.value.trim(); if (!dest) return;
  showPage('search-results-page');
  document.getElementById('search-results-title').textContent = `搜索：${dest}`;
  const params = new URLSearchParams({ destination: dest, days: 1 });
  params.append('preferences', '文化');
  const res = await fetch(`${API_BASE}/attractions?${params}`);
  const list = await res.json(); renderSearchResults(list);
}

function renderSearchResults(list) {
  const c = document.getElementById('search-results-container'); c.innerHTML='';
  list.forEach(sp => {
    const card = document.createElement('div'); card.className='trip-card';
    card.innerHTML = `<div class="trip-image" style="background-image:url('${sp.images?.[0]||''}')">
      <div class="trip-overlay">
        <div class="trip-title">${sp.name}</div>
        <div class="trip-meta">${sp.tags.join('、')}</div>
      </div>
    </div>`;
    card.onclick = () => showAttractionDetail(sp.id);
    c.appendChild(card);
  });
}

window.onload = function() {
  document.getElementById('search-input')
        .addEventListener('keydown', handleSearch);

  document.getElementById('generate-trip-btn')
        .addEventListener('click', async()=>{
    const days = parseInt(document.getElementById('days-input').value) || 1;
    const body = { selected_ids:selectedIds, days:days, preferences:['文化'] };
    const res = await fetch(`${API_BASE}/itinerary`, {
      method:'POST', headers:{'Content-Type':'application/json'},
      body:JSON.stringify(body)
    });
    const iti=await res.json();
    showPage('trip-detail-page');
    renderItinerary(iti);
  });
}

// 2. 详情
async function showAttractionDetail(id) {
  showPage('attraction-detail-page');
  const res = await fetch(`${API_BASE}/attractions/${id}`);
  const sp = await res.json();
  document.querySelector('.attraction-title').innerText = sp.name;
  document.querySelector('.attraction-location span').innerText = sp.address || '';
  document.querySelector('.attraction-description').innerText = sp.description || '';
  const prosBox = document.querySelector('.reviews-title + div');
  prosBox.innerHTML = `<ul>${sp.pros.map(p=>`<li>${p}</li>`).join('')}</ul>
                        <ul>${sp.cons.map(c=>`<li>${c}</li>`).join('')}</ul>`;
  const srcBox = prosBox.nextElementSibling;
  srcBox.innerHTML = sp.source_posts.map(u=>`<a href="${u}" target="_blank">${u}</a>`).join('');
}

// 3. 推荐
async function showRecommendPage() {
  const res = await fetch(`${API_BASE}/attractions?destination=北京&days=1&preferences=文化`);
  recommendSpots = await res.json(); recommendIndex =0; selectedIds=[];
  renderTinderCard(); showPage('recommend-page');
}

function renderTinderCard() {
  const stack = document.getElementById('recommend-card-stack'); stack.innerHTML='';
  if (recommendIndex>=recommendSpots.length) {
    stack.innerHTML='<p>没有更多了</p>';
    document.getElementById('generate-trip-btn').style.display='inline-block';
    return;
  }
  const sp = recommendSpots[recommendIndex];
  const card = document.createElement('div'); card.className='tinder-card';
  card.innerHTML = `<img class="tinder-card-img" src='${sp.images?.[0]||''}' />
    <div class="tinder-card-info"><div class="tinder-card-title">${sp.name}</div>
    ${sp.tags.join('、')}</div>`;
  stack.appendChild(card);
}

// 为方便地图前端测试，暂改成了滑十个景点就会跳出行程规划页面
function swipeRight() {
  selectedIds.push(recommendSpots[recommendIndex].id);
  if (selectedIds.length >= 10) {
    const stack = document.getElementById('recommend-card-stack');
    stack.innerHTML = '<p>沒有更多了</p>';
    document.getElementById('generate-trip-btn').style.display = 'inline-block';
    return;
  }
  recommendIndex++;
  renderTinderCard();
}
function swipeLeft() { recommendIndex++; renderTinderCard(); }

// 4. 行程列表 & 地图
function renderItinerary(items) {
  itineraryItems = items; // 保存全局
  const ul=document.getElementById('itinerary-list'); ul.innerHTML='';
  items.forEach(i=>{
    const li=document.createElement('li');
    li.innerHTML=`Day${i.day}. ${i.attraction.name} - ${i.notes}`;
    ul.appendChild(li);
  });
  // 根据行程天数生成下拉选单
  const days = [...new Set(items.map(i=>i.day))].sort((a,b)=>a-b);
  const select = document.getElementById('day-select');
  select.innerHTML = days.map(d=>`<option value="${d}">Day${d}</option>`).join('');
  select.value = days[0];
  select.onchange = ()=>renderMapForDay(Number(select.value));
  renderMapForDay(days[0]); // 默认渲染 Day1
}

function renderMapForDay(day) {
  const items = itineraryItems.filter(i=>i.day===day);
  document.getElementById('map').innerHTML = '';
  if(items.length===0) return;
  // 插入固定出发点（清华）
  const qinghua = {
    attraction: {
      id: 130886805,
      name: '清华（暂定住宿点）',
      lat: 40.003147,
      lon: 116.326539
    },
    day: day,
    notes: '出发点'
  };
  const itemsWithStart = [qinghua, ...items];
  const map=L.map('map').setView([itemsWithStart[0].attraction.lat,itemsWithStart[0].attraction.lon],11);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{
    attribution:'© OpenStreetMap'
  }).addTo(map);
  const latlngs=itemsWithStart.map(i=>[i.attraction.lat,i.attraction.lon]);
  L.polyline(latlngs,{color:'blue'}).addTo(map);
  itemsWithStart.forEach(i=>{
    // 若为清华（暂定住宿点），用红色 marker
    if(i.attraction.id === 130886805) {
      const redIcon = L.icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
        shadowSize: [41, 41]
      });
      L.marker([i.attraction.lat,i.attraction.lon], {icon: redIcon})
        .bindPopup(`<b>Day${i.day} ${i.attraction.name}</b><br/>${i.notes}`)
        .bindTooltip(i.attraction.name, {permanent:true, direction:'top', offset:[0,-10]})
        .addTo(map);
    } else {
      L.marker([i.attraction.lat,i.attraction.lon])
        .bindPopup(`<b>Day${i.day} ${i.attraction.name}</b><br/>${i.notes}`)
        .bindTooltip(i.attraction.name, {permanent:true, direction:'top', offset:[0,-10]})
        .addTo(map);
    }
  });
  map.fitBounds(latlngs,{padding:[50,50]});
}

// 首次显示
showPage('home-page');