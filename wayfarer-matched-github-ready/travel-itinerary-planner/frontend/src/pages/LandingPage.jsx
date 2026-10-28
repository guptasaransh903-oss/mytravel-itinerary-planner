import { useEffect, useState } from "react";
import Hero from "../components/Hero.jsx";
import TripForm from "../components/TripForm.jsx";
import ItineraryView from "../components/ItineraryView.jsx";
import {
  checkHealth,
  generateItinerary,
  saveTrip,
  listTrips,
  deleteTrip,
} from "../api/client.js";

function formatDate(date) {
  if (!date) return "";
  return new Intl.DateTimeFormat("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(new Date(`${date}T00:00:00`));
}

function formatInr(amount) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount ?? 0);
}

function LandingPage() {
  const [apiStatus, setApiStatus] = useState("checking");
  const [lastRequest, setLastRequest] = useState(null);
  const [itinerary, setItinerary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [deletingId, setDeletingId] = useState(null);
  const [error, setError] = useState("");
  const [saveMessage, setSaveMessage] = useState("");
  const [trips, setTrips] = useState([]);
  const [tripsLoading, setTripsLoading] = useState(false);
  const [tripsError, setTripsError] = useState("");

  async function loadSavedTrips() {
    setTripsLoading(true);
    setTripsError("");

    try {
      const result = await listTrips();
      setTrips(result?.trips ?? []);
    } catch (err) {
      setTripsError(err?.message || "Could not load saved trips.");
    } finally {
      setTripsLoading(false);
    }
  }

  useEffect(() => {
    let cancelled = false;

    checkHealth()
      .then((data) => {
        if (!cancelled) {
          setApiStatus(data?.status === "ok" ? "online" : "unexpected");
        }
      })
      .catch(() => {
        if (!cancelled) setApiStatus("offline");
      });

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    loadSavedTrips();
  }, []);

  async function requestItinerary(tripData) {
    setLoading(true);
    setError("");
    setSaveMessage("");
    setLastRequest(tripData);

    try {
      const result = await generateItinerary(tripData);
      setItinerary(result);
    } catch (err) {
      setItinerary(null);
      setError(err?.message || "Could not generate itinerary. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  async function handleSaveTrip() {
    if (!lastRequest || !itinerary || saving) return;

    setSaving(true);
    setError("");
    setSaveMessage("");

    try {
      const saved = await saveTrip({
        preferences: lastRequest,
        itinerary,
        title: `${itinerary.destination} Trip`,
      });

      setSaveMessage(`Trip saved successfully: ${saved.title}`);
      await loadSavedTrips();
    } catch (err) {
      setError(err?.message || "Could not save your trip. Please try again.");
    } finally {
      setSaving(false);
    }
  }

  async function handleDeleteTrip(tripId) {
    const confirmed = window.confirm(
      "Are you sure you want to delete this saved trip?"
    );

    if (!confirmed || deletingId) return;

    setDeletingId(tripId);
    setTripsError("");

    try {
      await deleteTrip(tripId);
      setTrips((current) => current.filter((trip) => trip.id !== tripId));
    } catch (err) {
      setTripsError(err?.message || "Could not delete this trip.");
    } finally {
      setDeletingId(null);
    }
  }

  function handleRegenerate() {
    if (!lastRequest || loading) return;
    requestItinerary(lastRequest);
  }

  return (
    <main className="page">
      <Hero apiStatus={apiStatus} />

      <section className="section" id="get-started">
        <h2>Plan your trip</h2>
        <p>
          Enter your destination, dates, budget, and interests. WanderPlan will
          build a day-by-day plan you can regenerate anytime.
        </p>

        <TripForm onSubmit={requestItinerary} loading={loading} />

        {error && (
          <div className="alert error" role="alert">
            {error}
          </div>
        )}

        {loading && !itinerary && (
          <p className="loading-note" role="status">
            Generating your itinerary...
          </p>
        )}
      </section>

      <ItineraryView
        itinerary={itinerary}
        onRegenerate={handleRegenerate}
        onSave={handleSaveTrip}
        loading={loading}
        saving={saving}
      />

      {saveMessage && (
        <p className="success-message" role="status">
          {saveMessage}
        </p>
      )}

      <section className="saved-trips-section" id="my-trips">
        <div className="saved-trips-heading">
          <div>
            <h2>My Trips</h2>
            <p>Your itineraries saved to your WanderPlan account on this browser.</p>
          </div>

          <button
            type="button"
            className="btn secondary"
            onClick={loadSavedTrips}
            disabled={tripsLoading}
          >
            {tripsLoading ? "Loading..." : "Refresh"}
          </button>
        </div>

        {tripsError && (
          <div className="alert error" role="alert">
            {tripsError}
          </div>
        )}

        {tripsLoading && trips.length === 0 && (
          <p className="loading-note">Loading your saved trips...</p>
        )}

        {!tripsLoading && !tripsError && trips.length === 0 && (
          <div className="empty-trips">
            <h3>No saved trips yet</h3>
            <p>Generate an itinerary and select Save Trip to see it here.</p>
          </div>
        )}

        {trips.length > 0 && (
          <div className="saved-trips-grid">
            {trips.map((trip) => (
              <article className="saved-trip-card" key={trip.id}>
                <div className="saved-trip-card-top">
                  <div>
                    <h3>{trip.title}</h3>
                    <p className="saved-trip-destination">{trip.destination}</p>
                  </div>
                  <span className="saved-trip-days">
                    {trip.trip_days} days
                  </span>
                </div>

                <p>
                  {formatDate(trip.start_date)} – {formatDate(trip.end_date)}
                </p>

                <div className="saved-trip-details">
                  <p>
                    <span>Budget</span>
                    <strong>{formatInr(trip.budget_inr)}</strong>
                  </p>
                  <p>
                    <span>Estimated cost</span>
                    <strong>
                      {formatInr(trip.total_estimated_cost_inr)}
                    </strong>
                  </p>
                  <p>
                    <span>Travel style</span>
                    <strong>{trip.travel_style}</strong>
                  </p>
                </div>

                {trip.interests?.length > 0 && (
                  <div className="interest-tags">
                    {trip.interests.map((interest) => (
                      <span className="tag" key={interest}>
                        {interest}
                      </span>
                    ))}
                  </div>
                )}

                <button
                  type="button"
                  className="btn secondary delete-trip-button"
                  onClick={() => handleDeleteTrip(trip.id)}
                  disabled={deletingId === trip.id}
                >
                  {deletingId === trip.id ? "Deleting..." : "Delete Trip"}
                </button>
              </article>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}

export default LandingPage;