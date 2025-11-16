 const apiBase = 'http://localhost:8000/api'
 document.getElementById('send').addEventListener('click', async ()=>{
 const message = document.getElementById('message').value
 const name = document.getElementById('name').value
 const contact = document.getElementById('contact').value
 const payload = { message, citizen_name: name, contact }
 const res = await fetch(apiBase + '/complaints', {
 method: 'POST', headers: {'Content-Type':'application/json'}, body:
 JSON.stringify(payload)
 })
 const data = await res.json()
 document.getElementById('resp').innerText = JSON.stringify(data, null, 2)
 })