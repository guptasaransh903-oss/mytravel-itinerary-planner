import {useEffect, useState} from "react";
import LandingPage from "./pages/LandingPage.jsx";
import "./styles/wayfarer.css";

const destinations = [
  {name:"Kyoto",country:"Japan",region:"Asia",desc:"Temples, tea houses, and maple-lined paths",days:4,budget:180,image:"photo-1493976040374-85c8e12f0c0e"},
  {name:"Amalfi Coast",country:"Italy",region:"Europe",desc:"Cliffside villages above a turquoise sea",days:5,budget:240,image:"photo-1533105079780-92b9be482077"},
  {name:"Patagonia",country:"Chile",region:"Americas",desc:"Granite towers and glacial lakes",days:6,budget:210,image:"photo-1464822759023-fed622ff2c3b"},
  {name:"Marrakech",country:"Morocco",region:"Africa",desc:"Riads, souks, and Atlas mountain air",days:4,budget:140,image:"photo-1489749798305-4fea3ae63d43"},
  {name:"South Iceland",country:"Iceland",region:"Europe",desc:"Waterfalls, black sand, and northern lights",days:5,budget:260,image:"photo-1476610182048-b716b8518aae"},
  {name:"Ubud, Bali",country:"Indonesia",region:"Asia",desc:"Rice terraces and jungle wellness",days:5,budget:110,image:"photo-1537996194471-e657df975ab4"}
];
function App(){
  const [path,setPath]=useState(window.location.pathname);
  const [query,setQuery]=useState(""); const [region,setRegion]=useState("All regions"); const [menu,setMenu]=useState(false);
  useEffect(()=>{const handler=()=>setPath(window.location.pathname);window.addEventListener('popstate',handler);return()=>window.removeEventListener('popstate',handler)},[]);
  useEffect(()=>{document.body.classList.toggle('wf-mode',path==='/');return()=>document.body.classList.remove('wf-mode')},[path]);
  const go=(route)=>{history.pushState({},'',route);setPath(route);setMenu(false);window.scrollTo(0,0)};
  const filtered=destinations.filter(d=>(region==='All regions'||d.region===region)&&`${d.name} ${d.country} ${d.desc}`.toLowerCase().includes(query.toLowerCase()));
  if(path!=='/')return <><div className="wf-back"><button onClick={()=>go('/')}>← Back to Wayfarer</button></div><LandingPage/></>;
  return <div className="wf">
    <header className="wf-header"><button className="wf-logo" onClick={()=>go('/')}>✳ wayfarer<span>.</span></button><nav className={menu?'wf-open':''}><a href="#destinations" onClick={()=>setMenu(false)}>Explore</a><button onClick={()=>go('/planner')}>Plan a Trip</button><button onClick={()=>go('/planner')}>My Trips</button><button onClick={()=>go('/planner')}>Join a Trip</button></nav><button className="wf-menu" onClick={()=>setMenu(!menu)} aria-label="Toggle navigation">☰</button></header>
    <main><section className="wf-hero"><div className="wf-hero-photo" role="img" aria-label="Mountain landscape"/><div className="wf-hero-content"><span className="wf-eyebrow">✦ TRIP PLANNING, UNHURRIED</span><h1>Plan the trip you'll<br/><em>talk about for years.</em></h1><p>Find a destination, shape each day around what you love, and invite your travel companions into the plan.</p><button className="wf-primary" onClick={()=>go('/planner')}>Start planning ↗</button></div></section>
    <section className="wf-search-wrap" aria-label="Search destinations"><div className="wf-search"><label>Where to?<input value={query} onChange={e=>setQuery(e.target.value)} placeholder="City, country, or vibe — e.g. hiking"/></label><label>Region<select value={region} onChange={e=>setRegion(e.target.value)}>{['All regions','Asia','Europe','Americas','Africa'].map(r=><option key={r}>{r}</option>)}</select></label><button className="wf-primary" onClick={()=>document.getElementById('destinations').scrollIntoView({behavior:'smooth'})}>Search ↗</button></div></section>
    <section id="destinations" className="wf-section"><div className="wf-section-heading"><div><span className="wf-kicker">POPULAR RIGHT NOW</span><h2>Destinations with<br/><em>ready-made itineraries</em></h2></div><a href="#destinations">View all destinations ↗</a></div><div className="wf-grid">{filtered.map(d=><article className="wf-card" key={d.name}><img loading="lazy" src={`https://images.unsplash.com/${d.image}?auto=format&fit=crop&w=900&q=80`} alt={`${d.name}, ${d.country}`}/><div className="wf-card-body"><span className="wf-region">{d.region}</span><h3>{d.name}</h3><p className="wf-country">{d.country}</p><p>{d.desc}</p><div className="wf-stats"><span>Suggested length <b>{d.days} days</b></span><span>Typical daily budget <b>~${d.budget}/day</b></span></div><button onClick={()=>go('/planner')}>Plan this trip ↗</button></div></article>)}</div>{filtered.length===0&&<p>No destinations match your search. Try a different keyword or region.</p>}</section>
    <section className="wf-steps wf-section"><span className="wf-kicker">THE WAYFARER WAY</span><h2>From daydream to day one,<br/><em>in three steps</em></h2><div className="wf-steps-grid"><div><span>01</span><h3>Discover</h3><p>Browse hand-picked destinations with honest seasons, budgets, and the pace each place rewards.</p></div><div><span>02</span><h3>Shape the days</h3><p>Pick your dates, pace, and interests to get a day-by-day draft you can build on.</p></div><div><span>03</span><h3>Travel together</h3><p>Bring your people into the plan. Collaboration requires a connected sharing service.</p></div></div></section>
    <section className="wf-cta"><span className="wf-kicker">YOUR JOURNEY AWAITS</span><h2>Your next trip starts<br/><em>with a single day.</em></h2><p>Choose a destination and dates — Wayfarer helps draft the rest so you can focus on the good parts.</p><button className="wf-primary" onClick={()=>go('/planner')}>Plan a Trip ↗</button></section></main>
    <footer className="wf-footer"><div><strong>✳ wayfarer.</strong><p>Thoughtful trip planning for curious travelers.</p></div><div><a href="#destinations">Explore</a><button onClick={()=>go('/planner')}>Plan a Trip</button><button onClick={()=>go('/planner')}>My Trips</button></div><small>© 2026 Wayfarer. Budgets and seasons are guide estimates.</small></footer>
  </div>;
}
export default App;
