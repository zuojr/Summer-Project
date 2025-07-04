const API_BASE = '';
let previousPage = 'home-page';
let recommendSpots = [], recommendIndex = 0, selectedIds = [];

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

document.getElementById('search-input')
        .addEventListener('keydown', handleSearch);

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

function swipeRight() {
  selectedIds.push(recommendSpots[recommendIndex].id);
  recommendIndex++; renderTinderCard();
}
function swipeLeft() { recommendIndex++; renderTinderCard(); }

document.getElementById('generate-trip-btn')
        .addEventListener('click', async()=>{
  const body = { selected_ids:selectedIds, days:1, preferences:['文化'] };
  const res = await fetch(`${API_BASE}/itinerary`, {
    method:'POST', headers:{'Content-Type':'application/json'},
    body:JSON.stringify(body)
  });
  const iti=await res.json(); renderItinerary(iti); initMap(iti); showPage('trip-detail-page');
});

// 4. 行程列表 & 地图
function renderItinerary(items) {
  const ul=document.getElementById('itinerary-list'); ul.innerHTML='';
  items.forEach(i=>{
    const li=document.createElement('li');
    li.innerHTML=`Day${i.day}. ${i.attraction.name} - ${i.notes}`;
    ul.appendChild(li);
  });
}

function initMap(items) {
  document.getElementById('map').style.display='block';
  const map=L.map('map').setView([39.9,116.4],11);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',{
    attribution:'© OpenStreetMap'
  }).addTo(map);
  const latlngs=items.map(i=>[i.attraction.lat,i.attraction.lon]);
  L.polyline(latlngs,{color:'blue'}).addTo(map);
  items.forEach(i=>L.marker([i.attraction.lat,i.attraction.lon])
    .bindPopup(`<b>Day${i.day} ${i.attraction.name}</b><br/>${i.notes}`)
    .addTo(map));
  map.fitBounds(latlngs,{padding:[50,50]});
}

// 首次显示
showPage('home-page');