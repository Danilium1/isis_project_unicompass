const API_BASE = 'http://127.0.0.1:8000';

function setToken(token){
  if(token) localStorage.setItem('token', token);
  else localStorage.removeItem('token');
  refreshAuthUI();
}
function getToken(){ return localStorage.getItem('token'); }

function refreshAuthUI(){
  const token = getToken();
  document.querySelectorAll('.auth-only').forEach(el=>el.style.display = token ? 'inline-flex' : 'none');
  document.querySelectorAll('.anon-only').forEach(el=>el.style.display = token ? 'none' : 'inline-flex');
  const badge = document.getElementById('token-badge');
  if(badge) badge.textContent = token ? 'token: checking...' : 'not logged';
}

// update admin link visibility by checking /user/me when token exists
async function refreshAdminLink(){
  const token = getToken();
  const adminLink = document.getElementById('admin-link');
  if(!adminLink) return;
  const badge = document.getElementById('token-badge');
  if(!token){
    adminLink.style.display = 'none';
    if(badge) badge.textContent = 'not logged';
    document.querySelectorAll('.admin-only').forEach(el=> el.style.display = 'none');
    return;
  }
  // hide admin controls until role is confirmed
  document.querySelectorAll('.admin-only').forEach(el=> el.style.display = 'none');
  try{
    const res = await fetch(API_BASE + '/user/me', { headers: { 'Authorization': 'Bearer ' + token } });
    if(!res.ok){
      // token invalid -> clear and update UI
      try{ localStorage.removeItem('token'); }catch(e){}
      if(badge) badge.textContent = 'invalid token';
      document.querySelectorAll('.auth-only').forEach(el=>el.style.display = 'none');
      document.querySelectorAll('.anon-only').forEach(el=>el.style.display = 'inline-flex');
      document.querySelectorAll('.admin-only').forEach(el=> el.style.display = 'none');
      adminLink.style.display = 'none';
      return;
    }
    const user = await res.json();
    if(badge) badge.textContent = 'token: OK';
    if(user.is_admin){ adminLink.style.display = 'inline-flex'; }
    else { adminLink.style.display = 'none'; }
    // show/hide admin-only elements
    document.querySelectorAll('.admin-only').forEach(el=> el.style.display = user.is_admin ? 'inline-flex' : 'none');
    // ensure auth/anon visibility consistent
    document.querySelectorAll('.auth-only').forEach(el=>el.style.display = 'inline-flex');
    document.querySelectorAll('.anon-only').forEach(el=>el.style.display = 'none');
  }catch(err){
    adminLink.style.display = 'none';
    if(badge) badge.textContent = 'invalid token';
    document.querySelectorAll('.admin-only').forEach(el=> el.style.display = 'none');
  }
}

async function loginFromHeader(e){
  e && e.preventDefault();
  const email = document.getElementById('header-email').value;
  const password = document.getElementById('header-password').value;
  const res = await fetch(API_BASE + '/user/login', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({email,password}) });
  if(!res.ok){ alert('Login failed'); return }
  const data = await res.json();
  setToken(data.token);
  alert('Logged in');
}

async function logout(){
  const token = getToken();
  if(!token) return;
  await fetch(API_BASE + '/user/logout', { method:'POST', headers:{'Authorization': 'Bearer ' + token} });
  setToken(null);
  alert('Logged out');
}

// Registration (register.html)
async function registerForm(e){
  e && e.preventDefault();
  const first_name = document.getElementById('r-first').value;
  const last_name = document.getElementById('r-last').value;
  const email = document.getElementById('r-email').value;
  const password = document.getElementById('r-pass').value;
  const res = await fetch(API_BASE + '/user/register', { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({first_name,last_name,email,password}) });
  if(!res.ok){ alert('Register failed'); return }
  const data = await res.json();
  alert('Registered: id=' + data.id);
}

// Profile page
async function loadProfile(){
  const token = getToken();
  if(!token) { document.getElementById('profile-root').innerHTML = '<p class="small">Not logged in</p>'; return }
  const res = await fetch(API_BASE + '/user/me', { headers:{ 'Authorization':'Bearer ' + token } });
  if(!res.ok){ document.getElementById('profile-root').innerHTML = '<p class="small">Failed to fetch</p>'; return }
  const user = await res.json();
  const root = document.getElementById('profile-root');
  root.innerHTML = `
    <div class="card"><strong>${user.first_name} ${user.last_name}</strong><div class="small">email: ${user.email}</div></div>
    <div id="extra" class="card small">school: ${user.school || '-'}<br>study_group: ${user.study_group || '-'}<br>citezenship: ${user.citezenship || '-'}</div>
    <button class="button" onclick="document.getElementById('edit-form').style.display='block'">Edit profile</button>
    <div id="edit-form" class="hidden" style="margin-top:12px">
      <div class="form-row"><input id="e-school" class="input" placeholder="school" value="${user.school || ''}"></div>
      <div class="form-row"><input id="e-study" class="input" placeholder="study_group" value="${user.study_group || ''}"></div>
      <div class="form-row"><input id="e-cit" class="input" placeholder="citezenship" value="${user.citezenship || ''}"></div>
      <div class="form-row"><button class="button" onclick="saveProfile(${user.id})">Save</button></div>
    </div>
  `;
}
async function saveProfile(userId){
  const token = getToken();
  const payload = {
    school: document.getElementById('e-school').value || null,
    study_group: document.getElementById('e-study').value || null,
    citezenship: document.getElementById('e-cit').value || null,
  };
  const res = await fetch(API_BASE + '/user/' + userId, { method:'PUT', headers:{'Content-Type':'application/json','Authorization':'Bearer ' + token}, body:JSON.stringify(payload)});
  if(!res.ok){ alert('Update failed'); return }
  alert('Updated');
  loadProfile();
}

// Tasks
async function loadTasks(){
  const el = document.getElementById('tasks-root');
  el.innerHTML = '<p class="small">Loading...</p>';
  const token = getToken();
  if(!token){ el.innerHTML = '<p class="small">Login as admin to view tasks</p>'; return }
  const res = await fetch(API_BASE + '/task/', { headers: { 'Authorization': 'Bearer ' + token } });
  if(!res.ok){ el.innerHTML='Failed or forbidden'; return }
  const list = await res.json();
  el.innerHTML = list.map(t=>`<div class="card"><strong>${t.title}</strong><div class="small">${t.description || ''}</div></div>`).join('');
}
async function seedTasks(){
  const token = getToken();
  if(!token){ alert('Not logged in'); return }
  const res = await fetch(API_BASE + '/task/seed', {
    method:'POST',
    headers: { 'Authorization': 'Bearer ' + token }
  });
  if(!res.ok) { alert('Seed failed'); return }
  const data = await res.json();
  alert('Seeded ' + data.length + ' tasks');
  loadTasks();
}

window.addEventListener('DOMContentLoaded', ()=>{
  refreshAuthUI();
  // wire header login form if present
  const loginForm = document.getElementById('header-login-form');
  if(loginForm) loginForm.addEventListener('submit', loginFromHeader);
  // update admin link visibility
  refreshAdminLink();
});

// also refresh admin link when token changes
const originalSetToken = setToken;
setToken = function(token){ originalSetToken(token); refreshAdminLink(); };

// --- My assignments UI ---
async function loadMyAssignments(){
  const root = document.getElementById('my-tasks-root');
  if(!root) return;
  const token = getToken();
  if(!token){ root.innerHTML = '<p class="small">Log in to see your assignments</p>'; return }
  const res = await fetch(API_BASE + '/student_task/my', { headers: { 'Authorization': 'Bearer ' + token } });
  if(!res.ok){ root.innerHTML = '<p class="small">Failed to load</p>'; return }
  const list = await res.json();
  if(!list.length) { root.innerHTML = '<p class="small">No assignments</p>'; return }
  root.innerHTML = list.map(item=>{
    const completed = item.status === 'completed' || item.completed_at;
    return `
      <div class="card">
        <strong>${item.task ? item.task.title : 'Задание #' + item.id}</strong>
        <div class="small">${item.task ? item.task.description || '' : ''}</div>
        <div class="small">status: ${item.status || 'open'}</div>
        <div style="margin-top:8px">
          ${completed ? '<span class="small">Выполнено</span>' : `<button class="button" onclick="completeAssignment(${item.id})">Отметить выполненным</button>`}
        </div>
      </div>
    `;
  }).join('');
}

async function completeAssignment(studentTaskId){
  const token = getToken();
  if(!token){ alert('Not logged in'); return }
  const res = await fetch(API_BASE + '/student_task/' + studentTaskId + '/complete', { method: 'POST', headers: { 'Authorization': 'Bearer ' + token } });
  if(!res.ok){ alert('Failed to complete'); return }
  alert('Marked completed');
  loadMyAssignments();
}

// try loading my assignments on pages that have that section
window.addEventListener('DOMContentLoaded', ()=>{
  loadMyAssignments();
});
