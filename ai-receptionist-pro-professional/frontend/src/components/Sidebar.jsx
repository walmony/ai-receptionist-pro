import { Bot, MessageSquareText, PhoneCall, Settings, LogOut } from "lucide-react";

const items = [
  ["assistants", Bot, "Assistenti"],
  ["faqs", MessageSquareText, "FAQ"],
  ["calls", PhoneCall, "Chiamate"],
  ["test", Settings, "Test AI"],
];

export default function Sidebar({ page, setPage, onLogout }) {
  return <aside className="sidebar">
    <div className="brand"><Bot size={26}/><div><strong>AI Receptionist</strong><span>Admin Panel</span></div></div>
    <nav>{items.map(([id, Icon, label]) => <button key={id} className={page===id ? "active" : ""} onClick={() => setPage(id)}><Icon size={18}/>{label}</button>)}</nav>
    <button className="logout" onClick={onLogout}><LogOut size={18}/>Esci</button>
  </aside>
}
