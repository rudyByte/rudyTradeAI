import { StrictMode, useEffect, useState, type ReactNode } from 'react';
import { createRoot } from 'react-dom/client';
import { Activity, Bell, Cloud, Gauge, LayoutDashboard, ShieldCheck, WifiOff } from 'lucide-react';
import './styles.css';

const pages = ['Overview','Paper Trading','Live Account','Market Terminal','Options Scanner','AI Laboratory','News Centre','Strategy Backtesting','Risk Management','Infrastructure Guard','API Usage','Logs and Alerts','Settings'];
type Overview = { capital: number | null; dailyPnl: number | null; activePositions: number | null; model: string | null };
const unavailable: Overview = { capital: null, dailyPnl: null, activePositions: null, model: null };
const display = (v: number | null, prefix = '') => v === null ? 'Unavailable' : `${prefix}${v.toLocaleString('en-IN')}`;

export default function App() {
  const [page, setPage] = useState('Overview');
  const [overview, setOverview] = useState(unavailable);
  useEffect(() => { fetch('/api/overview').then(r => r.ok ? r.json() : Promise.reject()).then(setOverview).catch(() => setOverview(unavailable)); }, []);
  return <div className="shell"><aside><div className="brand"><div className="brandmark">R</div><div><strong>RUDYTRADE</strong><small>COMMAND CENTRE</small></div></div><nav>{pages.map((item, i) => <button className={item === page ? 'active' : ''} onClick={() => setPage(item)} key={item}>{i === 0 ? <LayoutDashboard size={16}/> : i === 9 ? <ShieldCheck size={16}/> : <Activity size={16}/>}<span>{item}</span></button>)}</nav><div className="paper-badge"><ShieldCheck size={16}/><div><b>PAPER ONLY</b><small>Live execution disabled</small></div></div></aside><main><header><div><span className="eyebrow">TRADING OPERATIONS / {page.toUpperCase()}</span><h1>{page}</h1></div><div className="header-status"><span className="dot"/>System operational<div className="icon"><Bell size={18}/></div></div></header><section className="notice"><WifiOff size={18}/><div><b>Backend data connection unavailable</b><span>Metrics are not fabricated. Connect the API service to populate this command centre.</span></div></section>{page === 'Overview' ? <><div className="grid metrics"><Metric label="Simulated capital" value={display(overview.capital, '₹')} icon={<Gauge/>}/><Metric label="Daily net P&L" value={display(overview.dailyPnl, '₹')} icon={<Activity/>}/><Metric label="Active positions" value={display(overview.activePositions)} icon={<ShieldCheck/>}/><Metric label="AI model" value={overview.model ?? 'Unavailable'} icon={<Cloud/>}/></div><div className="grid lower"><div className="panel chart"><div className="panel-head"><div><span className="eyebrow">EQUITY CURVE</span><h2>Portfolio performance</h2></div><div className="pills"><button>Today</button><button>7D</button><button>30D</button><button>All</button></div></div><div className="empty"><Activity size={30}/><b>Awaiting paper-trading data</b><span>Equity history will appear here when the backend is connected.</span></div></div><div className="panel"><div className="panel-head"><div><span className="eyebrow">SYSTEM HEALTH</span><h2>Live services</h2></div></div>{['Broker connectivity','Market-data collector','Risk manager','Paper execution engine','Database'].map(x => <div className="health" key={x}><span>{x}</span><em><i/>Unavailable</em></div>)}</div></div></> : <div className="panel page-placeholder"><Cloud size={34}/><h2>{page}</h2><p>This module is wired to the data-connected command centre. Its backend connector is not available yet, so no placeholder metrics are shown.</p></div>}</main></div>;
}
function Metric({label,value,icon}:{label:string,value:string,icon:ReactNode}) { return <div className="panel metric"><div className="metric-icon">{icon}</div><span>{label}</span><strong>{value}</strong><small>Source: backend / unavailable</small></div>; }

const root = document.getElementById('root');
if (!root) throw new Error('RudyTrade root element was not found');
createRoot(root).render(<StrictMode><App /></StrictMode>);
