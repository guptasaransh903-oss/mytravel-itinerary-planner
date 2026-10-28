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
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(`${isoDate}T00:00:00`));
}

function SavedTrips({
  trips,
  loading,
  error,
  activeTripId,
  openingId,
  deletingId,
  onOpen,
  onDelete,
  onRefresh,
}) {
  return (
    <section className="section saved-trips" id="saved-trips">
      <div className="saved-trips-header">
        <div>
          <h2>Saved trips</h2>
          <p>Reopen a trip you saved from this browser.</p>
        </div>
        <button
          type="button"
          className="btn secondary"
          onClick={onRefresh}
          disabled={loading}
        >
          {loading ? "Refreshing…" : "Refresh"}
        </button>
      </div>

      {loading && trips.length === 0 && (
        <p className="loading-note" role="status">
          Loading saved trips…
        </p>
      )}

      {error && (
        <div className="alert error" role="alert">
          {error}
        </div>
      )}

      {!loading && !error && trips.length === 0 && (
        <p className="empty-note">
          No saved trips yet. Generate an itinerary and click Save Trip.
        </p>
      )}

      {trips.length > 0 && (
        <ul className="saved-trip-list">
          {trips.map((trip) => {
            const isActive = trip.id === activeTripId;
            const isOpening = openingId === trip.id;
            const isDeleting = deletingId === trip.id;
            return (
              <li
                key={trip.id}
                className={`saved-trip-item${isActive ? " active" : ""}`}
              >
                <div className="saved-trip-main">
                  <h3>{trip.title}</h3>
                  <p>
                    {trip.destination} · {formatDate(trip.start_date)} →{" "}
                    {formatDate(trip.end_date)}
                  </p>
                  <p className="saved-trip-meta">
                    {trip.trip_days} day{trip.trip_days === 1 ? "" : "s"} ·{" "}
                    {trip.travel_style} · {formatInr(trip.total_estimated_cost_inr)}
                  </p>
                </div>
                <div className="saved-trip-actions">
                  <button
                    type="button"
                    className="btn primary"
                    onClick={() => onOpen(trip.id)}
                    disabled={isOpening || isDeleting}
                  >
                    {isOpening ? "Opening…" : "Open"}
                  </button>
                  <button
                    type="button"
                    className="btn secondary"
                    onClick={() => onDelete(trip.id)}
                    disabled={isOpening || isDeleting}
                  >
                    {isDeleting ? "Deleting…" : "Delete"}
                  </button>
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}

export default SavedTrips;
