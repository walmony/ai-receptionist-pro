import React, { useEffect, useState } from "react";
import { api } from "./lib/api";
import Sidebar from "./components/Sidebar";
import "./style.css";

const emptyAssistant = { name:"", business_name:"", system_prompt:"", language:"it", voice:"alloy", email_to:"" };

export default function App(){
  const [logged,setLogged]=useState(localStorage.getItem("admin") === "yes");
  const [email,setEmail]=useState("");
  const [password,setPassword]=useState("");
  const [page,setPage]=useState("assistants");
  const [assistants,setAssistants]=useState([]);
  const [faqs,setFaqs]=useState([]);
  const [calls,setCalls]=useState([]);
  const [form,setForm]=useState(emptyAssistant);
  const [selected,setSelected]=useState("");
  const [faq,setFaq]=useState({question:"", answer:""});
  const [msg,setMsg]=useState("");
  const [reply,setReply]=useState("");
  const [error,setError]=useState("");

  function login(e){e.preventDefault(); if(email && password){localStorage.setItem("admin","yes"); setLogged(true)} else setError("Inserisci email e password")}
  function logout(){localStorage.removeItem("admin"); setLogged(false)}
  async function load(){try{ const a=await api.assistants(); setAssistants(a.items||[]); if(!selected && a.items?.[0]) setSelected(a.items[0].id); const c=await api.calls(); setCalls(c.items||[]);}catch(e){setError(e.message)}}
  async function loadFaqs(id=selected){ if(!id) return; try{const r=await api.faqs(id); setFaqs(r.items||[])}catch(e){setError(e.message)} }
  useEffect(()=>{ if(logged) load(); },[logged]);
  useEffect(()=>{ if(selected) loadFaqs(selected); },[selected]);
  async function saveAssistant(e){e.preventDefault(); setError(""); await api.createAssistant(form); setForm(emptyAssistant); await load();}
  async function addFaq(e){e.preventDefault(); if(!selected) return setError("Seleziona un assistente"); await api.createFaq({assistant_id:selected,...faq}); setFaq({question:"",answer:""}); await loadFaqs();}
  async function askAi(e){e.preventDefault(); setReply("Sto pensando..."); try{const r=await api.testChat({assistant_id:selected,message:msg}); setReply(r.reply)}catch(e){setReply(e.message)}}

  if(!logged) return <div className="loginPage"><form className="loginCard" onSubmit={login}><div className="robot">🤖</div><h1>AI Receptionist Pro</h1><p>Accesso amministratore</p><input placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)}/><input placeholder="Password" type="password" value={password} onChange={e=>setPassword(e.target.value)}/><button>Entra</button>{error && <span className="err">{error}</span>}</form></div>

  return <div className="app"><Sidebar page={page} setPage={setPage} onLogout={logout}/><main><header><h1>{pageTitle(page)}</h1><p>Gestisci il tuo receptionist AI online.</p></header>{error && <div className="alert">{error}</div>}{page==="assistants" && <section className="grid"><div className="card"><h2>Nuovo assistente</h2><form onSubmit={saveAssistant} className="stack"><input placeholder="Nome assistente" value={form.name} onChange={e=>setForm({...form,name:e.target.value})}/><input placeholder="Nome attività" value={form.business_name} onChange={e=>setForm({...form,business_name:e.target.value})}/><textarea placeholder="Prompt di sistema" value={form.system_prompt} onChange={e=>setForm({...form,system_prompt:e.target.value})}/><input placeholder="Email riepiloghi" value={form.email_to} onChange={e=>setForm({...form,email_to:e.target.value})}/><button>Salva assistente</button></form></div><div className="card"><h2>Assistenti</h2>{assistants.map(a=><div className="row" key={a.id}><div><strong>{a.name}</strong><small>{a.business_name}</small></div><button onClick={async()=>{await api.deleteAssistant(a.id); await load();}}>Elimina</button></div>)}</div></section>}{page==="faqs" && <section className="grid"><div className="card"><h2>Nuova FAQ</h2><select value={selected} onChange={e=>setSelected(e.target.value)}>{assistants.map(a=><option value={a.id} key={a.id}>{a.name}</option>)}</select><form onSubmit={addFaq} className="stack"><input placeholder="Domanda" value={faq.question} onChange={e=>setFaq({...faq,question:e.target.value})}/><textarea placeholder="Risposta" value={faq.answer} onChange={e=>setFaq({...faq,answer:e.target.value})}/><button>Aggiungi FAQ</button></form></div><div className="card"><h2>FAQ inserite</h2>{faqs.map(f=><div className="row" key={f.id}><div><strong>{f.question}</strong><small>{f.answer}</small></div><button onClick={async()=>{await api.deleteFaq(f.id); await loadFaqs();}}>Elimina</button></div>)}</div></section>}{page==="calls" && <div className="card"><h2>Storico chiamate</h2>{calls.length===0 && <p>Nessuna chiamata registrata.</p>}{calls.map(c=><div className="row" key={c.id}><div><strong>{c.from_number||"Numero sconosciuto"}</strong><small>{c.summary||c.status}</small></div><small>{new Date(c.created_at).toLocaleString()}</small></div>)}</div>}{page==="test" && <section className="grid"><div className="card"><h2>Test AI</h2><select value={selected} onChange={e=>setSelected(e.target.value)}>{assistants.map(a=><option value={a.id} key={a.id}>{a.name}</option>)}</select><form onSubmit={askAi} className="stack"><textarea placeholder="Scrivi una domanda di prova" value={msg} onChange={e=>setMsg(e.target.value)}/><button>Chiedi all'AI</button></form></div><div className="card"><h2>Risposta</h2><p>{reply || "La risposta comparirà qui."}</p></div></section>}</main></div>
}
function pageTitle(p){return {assistants:"Assistenti",faqs:"FAQ",calls:"Chiamate",test:"Test AI"}[p]}
