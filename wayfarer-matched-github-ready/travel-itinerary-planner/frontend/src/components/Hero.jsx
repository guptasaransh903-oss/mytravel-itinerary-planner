function statusLabel(apiStatus) {
  switch (apiStatus) {
    case "online":
      return "API online";
    case "offline":
      return "API offline — start the backend";
    case "unexpected":
      return "API responded unexpectedly";
    default:
      return "Checking API…";
  }
}

function Hero({ apiStatus }) {
  return (
    <header className="hero">
      <p className="brand">WanderPlan</p>
      <h1>Personalized Travel Itinerary Planner</h1>
      <p className="tagline">
        Build smarter trip plans with React, FastAPI, and Supabase.
      </p>
      <div className="cta-row">
        <a className="btn primary" href="#get-started">
          Get started
        </a>
        <span className={`status status-${apiStatus}`} role="status">
          {statusLabel(apiStatus)}
        </span>
      </div>
    </header>
  );
}

export default Hero;
