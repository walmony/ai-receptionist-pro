import React, {useEffect, useState} from 'react';
import { createRoot } from 'react-dom/client';
import { Phone, Bot, Settings, History } from 'lucide-react';
import './style.css';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App(){
  const [settings,setSettings]=useState(null);
  const [email,setEmail]=useState('');
  const [password,setPassword]=useState('');
  const [logged,setLogged]=useState(false);
  const [error,setError]=useState('');

  useEffect(()=>{ fetch(API+'/api/settings').then(r=>r.json()).then(setSettings).catch(()=>{}); },[]);

  async function login(e){
    e.preventDefault();
    setError('');
    const r = await fetch(API+'/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email,password})});
    if(r.ok){ setLogged(true); return; }
    setError('Credenziali errate');
  }

  if(!logged){
    return <main className="login">
      <form onSubmit={login} className="card">
        <Bot size={42}/>
        <h1>AI Receptionist Pro</h1>
        <p>Accesso amministratore</p>
        <input placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} />
        <input placeholder="Password" type="password" value={password} onChange={e=>setPassword(e.target.value)} />
        <button>Entra</button>
        {error && <p className="error">{error}</p>}
      </form>
    </main>
  }

  return <main className="app">
    <aside>
      <h2>AI Receptionist</h2>
      <nav><span><Phone/> Chiamate</span><span><Settings/> Impostazioni</span><span><History/> Storico</span></nav>
    </aside>
    <section>
      <h1>Dashboard</h1>
      <div className="grid">
        <div className="panel"><h3>Assistente</h3><p>{settings?.assistant_name}</p></div>
        <div className="panel"><h3>Azienda</h3><p>{settings?.company_name}</p></div>
        <div className="panel"><h3>Webhook Twilio</h3><p>{API}/twilio/incoming-call</p></div>
      </div>
      <div className="panel wide">
        <h3>Prompt attivo</h3>
        <pre>{settings?.system_prompt}</pre>
      </div>
    </section>
  </main>
}

createRoot(document.getElementById('root')).render(<App/>);
