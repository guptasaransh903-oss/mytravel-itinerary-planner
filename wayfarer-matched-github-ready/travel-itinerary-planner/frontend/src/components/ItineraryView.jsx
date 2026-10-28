
function formatInr(amount) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount ?? 0);
}

function formatDate(isoDate) {
  if (!isoDate) return "";

  return new Intl.DateTimeFormat("en-IN", {
    weekday: "short",
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(`${isoDate}T00:00:00`));
}

function ActivityList({ title, items }) {
  if (!items?.length) return null;

  return (
    <div className="time-block">
      <h4>{title}</h4>
      <ul>
        {items.map((item) => (
          <li key={`${title}-${item}`}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

function DayCard({ day }) {
  return (
    <article className="day-card">
      <header className="day-card-header">
        <div>
          <p className="day-label">Day {day.day}</p>
          <h3>{day.title}</h3>
          <p className="day-date">{formatDate(day.date)}</p>
        </div>

        <p className="day-cost">
          {formatInr(day.estimated_cost_inr)}
        </p>
      </header>

      <div className="time-blocks">
        <ActivityList
          title="Morning"
          items={day.activities?.morning}
        />

        <ActivityList
          title="Afternoon"
          items={day.activities?.afternoon}
        />

        <ActivityList
          title="Evening"
          items={day.activities?.evening}
        />
      </div>
    </article>
  );
}

function ItineraryView({
  itinerary,
  onRegenerate,
  onSave,
  loading,
  saving,
}) {
  if (!itinerary) return null;

  return (
    <section className="itinerary-section" aria-live="polite">
      <div className="itinerary-summary">
        <h2>Your itinerary for {itinerary.destination}</h2>

        <p>
          {formatDate(itinerary.start_date)} →{" "}
          {formatDate(itinerary.end_date)} ·{" "}
          {itinerary.trip_days} day
          {itinerary.trip_days === 1 ? "" : "s"} ·{" "}
          {itinerary.travel_style}
        </p>

        <p className="cost-line">
          Estimated total:{" "}
          <strong>
            {formatInr(itinerary.total_estimated_cost_inr)}
          </strong>
          {" · "}
          Budget: {formatInr(itinerary.budget_inr)}
        </p>

        <p className="generator-badge">
          {itinerary.generator_label}
        </p>

        {itinerary.interests?.length > 0 && (
          <p className="interest-tags">
            {itinerary.interests.map((interest) => (
              <span key={interest} className="tag">
                {interest}
              </span>
            ))}
          </p>
        )}

        <div className="itinerary-actions">
          <button
            type="button"
            className="btn secondary"
            onClick={onRegenerate}
            disabled={loading || saving}
          >
            {loading ? "Regenerating..." : "Regenerate itinerary"}
          </button>

          <button
            type="button"
            className="btn primary"
            onClick={onSave}
            disabled={loading || saving}
          >
            {saving ? "Saving Trip..." : "Save Trip"}
          </button>
        </div>
      </div>

      <div className="day-list">
        {itinerary.days?.map((day) => (
          <DayCard
            key={`${day.day}-${day.date}`}
            day={day}
          />
        ))}
      </div>
    </section>
  );
}

export default ItineraryView;
